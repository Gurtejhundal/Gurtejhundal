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
from art import block, ground, pixel, pipe, rect, sprite, svg, text

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

def render(calendar):
 days=calendar['days'];start=date.fromisoformat(days[0]['date']);start-=timedelta(days=(start.weekday()+1)%7)
 columns=max((date.fromisoformat(d['date'])-start).days//7 for d in days)+1
 step=min(20,1080/columns);size=step-4;colors=['#416dba','#c7ad64','#efb231','#ffd34e','#fff3b0']
 b=pixel('WORLD 1-5',44,27,2)+pixel('MARIO CONTRIBUTION RUN',44,65,3)
 b+=text(f"{calendar['total']:,} CONTRIBUTIONS  /  {sum(d['count']>0 for d in days)} ACTIVE DAYS",1150,43,16,'#fff5db','end')
 b+=text('Every block is a day. Every contribution powers the adventure.',44,117,16,'#172c55')
 months=set()
 for d in days:
  day=date.fromisoformat(d['date']);delta=(day-start).days;col=delta//7;row=delta%7;x=44+col*step;y=155+row*20
  if day.day<=7 and day.month not in months:
   b+=text(day.strftime('%b').upper(),x,144,11,'#172c55');months.add(day.month)
  label=f"{d['date']}: {d['count']} contributions"
  b+=f'<g><title>{label}</title>'+rect(round(x,2),y,size,size,colors[d['level']])
  if d['level']:
   b+=rect(round(x+2,2),y+2,size-4,2,'#fff5db')+rect(round(x+size-2,2),y+2,2,size-2,'#a94822')
  b+='</g>'
 b+=text('LESS',44,315,10,'#172c55')
 for i,c in enumerate(colors):b+=rect(78+i*15,306,11,11,c)
 b+=text('MORE',159,315,10,'#172c55')
 b+=sprite('goomba',300,362,2.7)+block(545,352,40,False)+pipe(830,326,64,66)
 for i,(x,y) in enumerate([(322,300),(554,300),(851,265)]):
  b+=f'<g class="collect c{i}">'+sprite('coin',x,y,2)+'</g>'
 b+=rect(1139,151,5,241,'#fff5db')+rect(1135,143,13,11,'#58c830')+'<path d="M1144 163h-43v30h43z" fill="#fff5db" stroke="#241510" stroke-width="2"/>'
 b+=sprite('star',1112,167,1.4)
 b+='<g class="runner">'+sprite('mario',0,344,3)+'</g>'
 b+=ground(392,58)
 b+=text(f"{days[0]['date']} — {days[-1]['date']}  /  AUTO-SAVES DAILY",600,432,13,'#fff5db','middle')
 css='''.runner{animation:run 18s linear infinite;transform:translateX(44px)}
@keyframes run{0%,3%{transform:translate(44px,0)}20%{transform:translate(235px,0)}26%{transform:translate(315px,-95px)}32%{transform:translate(395px,0)}42%{transform:translate(490px,0)}48%{transform:translate(550px,-95px)}54%{transform:translate(620px,0)}66%{transform:translate(756px,0)}74%{transform:translate(837px,-150px)}82%{transform:translate(930px,0)}95%,100%{transform:translate(1080px,0)}}
.collect{animation-duration:18s;animation-iteration-count:infinite;animation-timing-function:steps(1,end)}.c0{animation-name:collect0}.c1{animation-name:collect1}.c2{animation-name:collect2}
@keyframes collect0{0%,24%{opacity:1}25%,100%{opacity:0}}@keyframes collect1{0%,46%{opacity:1}47%,100%{opacity:0}}@keyframes collect2{0%,72%{opacity:1}73%,100%{opacity:0}}'''
 return svg('Mario Contribution Run',f"Mario jumps over a Goomba, brick and green pipe beneath {calendar['login']}'s real GitHub contribution calendar. {calendar['total']} contributions. The animation restarts at the flagpole.",450,b,css=css)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--user',default=os.environ.get('GITHUB_USER','Gurtejhundal'));parser.add_argument('--input',type=Path);parser.add_argument('--output',type=Path,default=ROOT/'assets'/'mario-contributions.svg');parser.add_argument('--save-data',type=Path)
 args=parser.parse_args();data=json.loads(args.input.read_text()) if args.input else fetch_calendar(args.user,os.environ.get('GITHUB_TOKEN'))
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(render(data))
 if args.save_data:args.save_data.write_text(json.dumps(data,indent=2)+'\n')
 print(f"Rendered {len(data['days'])} days and {data['total']} contributions to {args.output}")

if __name__=='__main__':main()
