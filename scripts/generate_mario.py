#!/usr/bin/env python3
"""Render a real contribution calendar as a self-contained animated Mario level.

Uses GitHub GraphQL when GITHUB_TOKEN is present, otherwise the public contribution
calendar. Failed fetches fail the job and preserve the last successfully generated art.
"""
import argparse
from datetime import date, timedelta
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
from urllib.request import Request, urlopen
from art import castle, ground, hill, pixel, rect, sprite, svg, text

ROOT=Path(__file__).resolve().parents[1]
QUERY='''query($login:String!) { user(login:$login) { contributionsCollection {
 contributionCalendar { totalContributions weeks { contributionDays {
 contributionCount contributionLevel date weekday } } } } } }'''
LEVELS={'NONE':0,'FIRST_QUARTILE':1,'SECOND_QUARTILE':2,'THIRD_QUARTILE':3,'FOURTH_QUARTILE':4}

class CalendarParser(HTMLParser):
 def __init__(self):
  super().__init__(); self.days={}; self.tooltip=None; self.counts={}
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if attrs.get('data-date') and 'data-level' in attrs:
   self.days[attrs['data-date']]={'date':attrs['data-date'],'level':int(attrs['data-level']),'id':attrs.get('id')}
  if tag=='tool-tip':self.tooltip=attrs.get('for')
 def handle_data(self,data):
  if self.tooltip:
   match=re.search(r'(No|[\d,]+) contributions?',data)
   if match:self.counts[self.tooltip]=0 if match[1]=='No' else int(match[1].replace(',',''))
 def handle_endtag(self,tag):
  if tag=='tool-tip':self.tooltip=None

def fetch_calendar(login,token=None):
 if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})',login):raise ValueError('Invalid GitHub username')
 headers={'User-Agent':'super-gurtej-world','Accept':'application/json'}
 if token:
  headers['Authorization']='Bearer '+token
  req=Request('https://api.github.com/graphql',data=json.dumps({'query':QUERY,'variables':{'login':login}}).encode(),headers=headers)
  with urlopen(req,timeout=30) as response:payload=json.load(response)
  if payload.get('errors'):raise RuntimeError('GitHub could not return contribution data')
  cal=payload['data']['user']['contributionsCollection']['contributionCalendar']
  days=[{'date':d['date'],'count':d['contributionCount'],'level':LEVELS[d['contributionLevel']]} for w in cal['weeks'] for d in w['contributionDays']]
 else:
  # Public fallback also allows a maintainer to rebuild locally without a secret.
  req=Request(f'https://github.com/users/{login}/contributions',headers={'User-Agent':'super-gurtej-world'})
  with urlopen(req,timeout=30) as response:html=response.read().decode()
  parser=CalendarParser();parser.feed(html)
  if not parser.days:raise RuntimeError('Public GitHub calendar was empty')
  days=[]
  for d in parser.days.values():
   if d['id'] not in parser.counts:raise RuntimeError('Contribution count missing from public calendar')
   days.append({'date':d['date'],'level':d['level'],'count':parser.counts[d['id']]})
  cal={'totalContributions':sum(d['count'] for d in days)}
 if not days:raise RuntimeError('GitHub calendar was empty')
 return {'login':login,'total':cal['totalContributions'],'days':sorted(days,key=lambda d:d['date'])}

def build_world(calendar):
 """Twelve Sunday-start weeks, including the current partial week; no fake activity."""
 days=sorted(calendar['days'],key=lambda d:d['date'])
 if not days:raise ValueError('Cannot build a world without calendar days')
 dates=[date.fromisoformat(d['date']) for d in days]
 if len(set(dates))!=len(dates):raise ValueError('Duplicate calendar days')
 if any(not isinstance(d['count'],int) or d['count']<0 for d in days):raise ValueError('Invalid contribution count')
 last=dates[-1];current=last-timedelta(days=(last.weekday()+1)%7)
 first=current-timedelta(weeks=11)
 weeks=[]
 for i in range(12):
  start=first+timedelta(weeks=i);end=min(start+timedelta(days=6),last)
  subset=[d for d in days if start<=date.fromisoformat(d['date'])<=end]
  weeks.append({'start':start.isoformat(),'end':end.isoformat(),'count':sum(d['count'] for d in subset),'activeDays':sum(d['count']>0 for d in subset),'partial':end<start+timedelta(days=6)})
 return {'version':1,'login':calendar['login'],'start':first.isoformat(),'end':last.isoformat(),'total':sum(w['count'] for w in weeks),'activeDays':sum(w['activeDays'] for w in weeks),'weeks':weeks}


def state_css(name,start,end):
 """Show one discrete readout during an exact interval of the looping replay."""
 frames=[]
 if start>0:frames.extend(['0%{opacity:0}',f'{start:.4f}%{{opacity:1}}'])
 else:frames.append('0%{opacity:1}')
 if end<100:frames.append(f'{end:.4f}%{{opacity:0}}')
 frames.append('100%{opacity:'+('1' if end==100 else '0')+'}')
 return f'.{name}{{animation:{name} 26s steps(1,end) infinite}}@keyframes {name}{{'+''.join(frames)+'}'


def render(calendar):
 world=build_world(calendar);weeks=world['weeks'];floor=450
 b=pixel('WORLD 1-5 / ACTIVITY REPLAY',44,27,1.7)+text('GURTEJBIR SINGH / LAST 12 WEEKS',1156,40,13,'#fff5db','end')
 b+=pixel('THE KINGDOM YOU BUILT',44,68,3.5)
 b+=text('My GitHub activity becomes the level. Mario plays it back.',44,119,18,'#172c55')
 b+=rect(44,143,1112,76,'#132543')
 b+=text('COINS COLLECTED',64,168,12,'#9fc4f7')+text('ACTIVE DAYS',480,168,12,'#9fc4f7')+text('WEEKS CROSSED',877,168,12,'#9fc4f7')
 b+=pixel(str(world['activeDays']).zfill(2),480,183,2.7,'#fff5db',False)
 b+=sprite('cloud',168,248,2.3)+sprite('cloud',635,244,2)+sprite('cloud',961,272,1.8)
 b+=hill(13,floor,180,100)+hill(930,floor,200,122)
 b+=sprite('bush',700,floor-24,4)
 css=[];collect_times=[];path=['0%,2%{transform:translate(7px,418px)}'];previous_x=7;previous_y=floor
 for i,w in enumerate(weeks):
  x=44+i*86;surface=floor-w['activeDays']*12;center=x+43
  begin=2+i*7;collect=begin+4.6;land=begin+7
  collect_times.append(collect)
  b+=f'<g class="week" data-start="{w["start"]}" data-contributions="{w["count"]}" data-active-days="{w["activeDays"]}"><title>{w["start"]} to {w["end"]}: {w["count"]} contributions, {w["activeDays"]} active days</title>'
  b+=f'<g class="spotlight spot{i}" opacity="0">'+rect(x,230,86,276,'#fff5db','opacity=".13"')+'</g>'
  css.append(state_css('spot'+str(i),begin,land))
  # Exactly one visible masonry row for each active day; rest weeks stay flat.
  for row in range(w['activeDays']):
   y=surface+row*12
   b+=rect(x,y,86,12,'#c86b32')+f'<path d="M{x} {y+11}h86M{x} {y}v12M{x+43 if row%2==0 else x+21} {y}v12M{x+64} {y}v12" stroke="#713a25" stroke-width="2"/>'
  if w['activeDays']:b+=rect(x,surface,86,3,'#ffdc59')+rect(x,surface+3,86,2,'#713a25')
  if w['count']:
   b+=f'<g class="reward reward{i}">'+sprite('coin',center-12,surface-77,1.5)+text('+'+str(w['count']),center,surface-88,13,'#172c55','middle')+'</g>'
   css.append(f'.reward{i}{{animation:reward{i} 26s steps(1,end) infinite}}@keyframes reward{i}{{0%{{opacity:1}}{collect:.4f}%,100%{{opacity:0}}}}')
  b+='</g>'
  apex=min(previous_y,surface)-100
  path.extend([f'{begin+1.8:.4f}%{{transform:translate({previous_x+5}px,{apex}px)}}',f'{collect:.4f}%{{transform:translate({center-16}px,{surface-70}px)}}',f'{land:.4f}%{{transform:translate({center-16}px,{surface-32}px)}}'])
  previous_x=center-16;previous_y=surface
 # Final walk, flag descent and a quiet hold before replaying.
 path+=['92%,100%{transform:translate(1102px,418px)}']
 css.append('.runner{transform:translate(7px,418px);animation:route 26s linear infinite}@keyframes route{'+''.join(path)+'}')
 b+=castle(1134,400,.35)+rect(1116,279,4,171,'#fff5db')+rect(1112,270,12,11,'#58c830')
 b+='<g class="finish-flag"><path d="M1116 288h-43v30h43z" fill="#fff5db" stroke="#241510" stroke-width="2"/>'+sprite('star',1084,292,1.4)+'</g>'
 css.append('.finish-flag{animation:flag-down 26s linear infinite}@keyframes flag-down{0%,89%{transform:translateY(0)}94%,100%{transform:translateY(112px)}}')
 b+='<g class="finish-message" opacity="0">'+pixel('WORLD CLEAR!',471,264,3,'#ffdc59')+text(f"{world['total']} REAL CONTRIBUTIONS. ONE WORLD BUILT.",600,315,16,'#172c55','middle')+'</g>'
 css.append(state_css('finish-message',92,100))
 b+=ground(floor,56)
 b+=rect(0,506,1200,144,'#132543')
 for i,w in enumerate(weeks):
  x=44+i*86;label=date.fromisoformat(w['start']).strftime('%b %d').upper()+('*' if w['partial'] else '')
  b+=text(label,x+43,531,11,'#c8ddff','middle')+text(str(w['count'])+' COINS',x+43,551,11,'#ffdc59','middle')+text(str(w['activeDays'])+' DAYS',x+43,569,10,'#9fc4f7','middle')
 b+=text('1 COIN = 1 CONTRIBUTION     /     1 RAISED ROW = 1 ACTIVE DAY',600,605,16,'#fff5db','middle')
 b+=text(world['start']+' TO '+world['end']+'  /  UPDATED DAILY  /  * CURRENT WEEK',600,634,12,'#9fc4f7','middle')
 b+='<g class="runner">'+sprite('mario',0,0,2)+'</g>'
 cumulative=0
 for i in range(13):
  start=0 if i==0 else collect_times[i-1];end=collect_times[i] if i<12 else 100
  b+=f'<g class="readout readout{i}" opacity="'+('1' if i==0 else '0')+'">'+text(f'{cumulative:03} / {world["total"]:03}',64,204,25,'#ffdc59')+text(f'{i:02} / 12',877,204,25,'#fff5db')+'</g>'
  css.append(state_css('readout'+str(i),start,end))
  if i<12:cumulative+=weeks[i]['count']
 css.append('@media(prefers-reduced-motion:reduce){.readout{opacity:0!important}.readout0{opacity:1!important}.reward{opacity:1!important}.spotlight,.finish-message{opacity:0!important}.finish-flag{transform:none!important}}')
 description=f"A Mario replay of {world['login']}'s last twelve GitHub contribution weeks, {world['start']} to {world['end']}. {world['total']} contributions become exactly {world['total']} coins. {world['activeDays']} active days become brick rows. Mario jumps across the actual weekly terrain and collects each week's contribution bundle. "
 description+=' '.join(f"{w['start']} to {w['end']}: {w['count']} contributions, {w['activeDays']} active days." for w in weeks)
 return svg('The Kingdom You Built — GitHub Activity Replay',description,650,b,css=''.join(css))

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--user',default=os.environ.get('GITHUB_USER','Gurtejhundal'));parser.add_argument('--input',type=Path);parser.add_argument('--output',type=Path,default=ROOT/'assets'/'mario-contributions.svg');parser.add_argument('--save-data',type=Path);parser.add_argument('--world-output',type=Path,default=ROOT/'game'/'activity-level.js')
 args=parser.parse_args();data=json.loads(args.input.read_text()) if args.input else fetch_calendar(args.user,os.environ.get('GITHUB_TOKEN'))
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(render(data))
 args.world_output.parent.mkdir(parents=True,exist_ok=True)
 args.world_output.write_text('// Generated from real GitHub contribution activity; see scripts/generate_mario.py.\nwindow.MARIO_WORLD = '+json.dumps(build_world(data),separators=(',',':'))+';\n')
 if args.save_data:args.save_data.write_text(json.dumps(data,indent=2)+'\n')
 print(f"Rendered {len(data['days'])} days and {data['total']} contributions to {args.output}")

if __name__=='__main__':main()
