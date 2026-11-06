import json
from pathlib import Path
import re
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from generate_mario import CalendarParser, build_world, render
from art import PALETTE, SPRITES

class ProfileTests(unittest.TestCase):
 def test_svgs_are_safe_self_contained_and_accessible(self):
  for path in (ROOT/'assets').glob('*.svg'):
   with self.subTest(path=path.name):
    tree=ET.fromstring(path.read_text());ns='{http://www.w3.org/2000/svg}'
    self.assertIsNotNone(tree.find(ns+'title'));self.assertIsNotNone(tree.find(ns+'desc'))
    self.assertIn('prefers-reduced-motion',path.read_text())
    for element in tree.iter():
     self.assertNotIn(element.tag,[ns+'script',ns+'foreignObject'])
     for key,value in element.attrib.items():
      if key.endswith('href'):self.assertTrue(value.startswith('#'))
 def test_readme_images_resolve_and_pacman_is_removed(self):
  readme=(ROOT/'README.md').read_text()
  self.assertNotIn('pacman',readme.lower());self.assertNotIn('pac-man',readme.lower())
  self.assertFalse((ROOT/'.github/workflows/pacman.yml').exists())
  for ref in re.findall(r'src="\./([^"]+)"',readme):self.assertTrue((ROOT/ref).is_file(),ref)
 def test_weeks_drive_terrain_rewards_and_exact_final_score(self):
  calendar={'login':'test','total':3,'days':[{'date':'2026-11-01','count':0,'level':0},{'date':'2026-11-02','count':3,'level':2}]}
  world=build_world(calendar);self.assertEqual(len(world['weeks']),12)
  self.assertEqual(world['total'],3);self.assertEqual(world['activeDays'],1)
  self.assertEqual(world['weeks'][-1]['count'],3);self.assertEqual(world['weeks'][-1]['activeDays'],1)
  source=render(calendar);root=ET.fromstring(source);ns='{http://www.w3.org/2000/svg}'
  weeks=[g for g in root.iter(ns+'g') if g.get('class')=='week'];self.assertEqual(len(weeks),12)
  for g in weeks:
   rows=[r for r in g.findall(ns+'rect') if r.get('fill')=='#c86b32']
   self.assertEqual(len(rows),int(g.get('data-active-days')))
  self.assertIn('003 / 003',source);self.assertIn('3 contributions, 1 active days',source)
  self.assertNotIn('data-date',source)
 def test_rolling_window_excludes_old_activity_and_handles_partial_week(self):
  c={'login':'test','total':1003,'days':[{'date':'2025-11-01','count':1000},{'date':'2026-11-06','count':3}]}
  w=build_world(c);self.assertEqual(w['total'],3);self.assertEqual(w['start'],'2026-08-16');self.assertTrue(w['weeks'][-1]['partial'])
 def test_zero_activity_keeps_flat_terrain_and_honest_zero_score(self):
  c={'login':'test','total':0,'days':[{'date':'2026-11-06','count':0}]}
  self.assertEqual(build_world(c)['total'],0);self.assertIn('000 / 000',render(c))
 def test_duplicate_days_and_negative_counts_fail_instead_of_inventing_activity(self):
  for days in [[{'date':'2026-11-06','count':-1}],[{'date':'2026-11-06','count':1}]*2]:
   with self.assertRaises(ValueError):build_world({'login':'test','days':days})
 def test_svg_and_playable_world_share_the_same_window_and_totals(self):
  source=(ROOT/'game/activity-level.js').read_text().split('window.MARIO_WORLD = ',1)[1].rstrip(';\n')
  world=json.loads(source);svg=(ROOT/'assets/mario-contributions.svg').read_text()
  self.assertIn(f"{world['total']:03} / {world['total']:03}",svg)
  for w in world['weeks']:
   self.assertIn(f'data-start="{w["start"]}" data-contributions="{w["count"]}" data-active-days="{w["activeDays"]}"',svg)
 def test_public_calendar_parser_matches_tooltips_to_days(self):
  parser=CalendarParser();parser.feed('<td id="day-1" data-date="2026-11-01" data-level="2"></td><tool-tip for="day-1">1,234 contributions on November 1st.</tool-tip>')
  self.assertEqual(parser.counts['day-1'],1234);self.assertEqual(parser.days['2026-11-01']['level'],2)
 def test_shared_sprites_match_generated_game_data(self):
  for name,rows in SPRITES.items():
   self.assertTrue(all(c in PALETTE for row in rows for c in row),name)
  source=(ROOT/'game/sprites.js').read_text().split('window.MARIO_ART = ',1)[1].rstrip(';\n')
  data=json.loads(source);self.assertEqual(data,{'palette':PALETTE,'sprites':SPRITES})

if __name__=='__main__':unittest.main()
