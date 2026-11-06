import json
from pathlib import Path
import re
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from generate_mario import CalendarParser, render
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
 def test_calendar_includes_real_counts_and_handles_zero_activity(self):
  calendar={'login':'test','total':3,'days':[{'date':'2026-11-01','count':0,'level':0},{'date':'2026-11-02','count':3,'level':2}]}
  source=render(calendar);ET.fromstring(source)
  self.assertIn('2026-11-02: 3 contributions',source)
  self.assertIn('3 CONTRIBUTIONS  /  1 ACTIVE DAYS',source)
  self.assertIn('2026-11-01: 0 contributions',source)
 def test_public_calendar_parser_matches_tooltips_to_days(self):
  parser=CalendarParser();parser.feed('<td id="day-1" data-date="2026-11-01" data-level="2"></td><tool-tip for="day-1">1,234 contributions on November 1st.</tool-tip>')
  self.assertEqual(parser.counts['day-1'],1234);self.assertEqual(parser.days['2026-11-01']['level'],2)
 def test_shared_sprites_match_generated_game_data(self):
  for name,rows in SPRITES.items():
   self.assertTrue(all(c in PALETTE for row in rows for c in row),name)
  source=(ROOT/'game/sprites.js').read_text().split('window.MARIO_ART = ',1)[1].rstrip(';\n')
  data=json.loads(source);self.assertEqual(data,{'palette':PALETTE,'sprites':SPRITES})

if __name__=='__main__':unittest.main()
