#!/usr/bin/env python3
"""Rebuild the five profile scenes and the browser game's shared sprite data."""
import json
from pathlib import Path
from art import block, castle, ground, hill, PALETTE, pixel, pipe, rect, sprite, SPRITES, svg, text

ROOT=Path(__file__).resolve().parents[1]
def save(name,title,desc,h,body,bg='#5c94fc',css=''):
 (ROOT/'assets'/name).write_text(svg(title,desc,h,body,bg,css))

def hud(world,label='GURTEJ',right='LET\'S-A GO!'):
 return pixel(label,44,26,2)+pixel('WORLD '+world,540,26,2)+pixel(right,930,26,2)

def heading(world,title,subtitle,dark=False):
 return pixel('WORLD '+world,44,28,2,'#78d8ff' if dark else '#fff5db')+pixel(title,44,64,4)+text(subtitle,44,119,16,'#a7dfff' if dark else '#172c55')

def main():
 # The title-screen composition deliberately uses the game's own visual language.
 b=hud('1-1',right='PLAYER 01')
 b+=sprite('cloud',810,78,3)+sprite('cloud',1030,165,2)+sprite('cloud',74,83,2)
 b+=hill(620,574,230,160)+hill(980,574,240,220)+sprite('bush',36,544,5)
 b+=rect(48,122,705,267,'#241510')+rect(54,128,693,255,'#c86b32')+rect(62,136,677,239,'#a94822')
 for x in [66,725]:
  for y in [140,363]:b+=rect(x,y,6,6,'#241510')+rect(x,y,3,3,'#ffdc59')
 b+=pixel('SUPER',88,151,5,'#fff5db')+pixel('GURTEJ',84,206,14,'#ffdc59')+pixel('WORLD',91,318,5,'#fff5db')
 b+=text('GURTEJBIR SINGH',56,435,27,'#fff5db')+text('FULL-STACK ENGINEER  /  AI BUILDER',56,468,21,'#172c55')
 b+=text('Building useful software. One level at a time.',56,501,17,'#172c55')
 b+='<g class="twinkle">'+pixel('PRESS START',58,528,2)+'</g>'
 b+=block(820,256,56,False)+block(876,256,56)+block(932,256,56,False)
 b+='<g class="bob">'+sprite('mushroom',883,197,3.5)+'</g>'
 b+=sprite('mario',851,353,5)+text('HERE WE GO!',878,333,13,'#172c55','middle')
 b+=pipe(1037,452,102,122)+sprite('goomba',729,526,3.4)
 b+=ground(580,80)
 save('level-01-start.svg','Super Gurtej World — Gurtejbir Singh','A Super Mario Bros. inspired title screen with Mario jumping toward a question block, a Super Mushroom, Goomba, green pipe, smiling hills and brick ground. Gurtejbir Singh: full-stack engineer and AI builder.',660,b)
 # Four stage entrances: the actual linked project cards are in the Markdown below.
 b=heading('1-2','CHOOSE YOUR ADVENTURE','Four projects. Four worlds to explore.')
 b+=sprite('cloud',983,40,2)+hill(1010,484,180,120)+sprite('bush',470,454,5)
 projects=[('1','MEDIAFORGE','LOCAL-FIRST MEDIA TOOLS','NEXT.JS / TYPESCRIPT','mushroom'),('2','ROADMAP TRACER','YOUR LEARNING, MAPPED','REACT / FASTAPI','flower'),('3','GHOST ENGINEER','MULTI-AGENT CODE REVIEW','ARCHITECT / DEBUG / SECURITY','star'),('4','VIBEMAXING','AGENTS THAT BUILD WEBSITES','MOTION / QA / VERIFICATION','coin')]
 for i,(n,name,desc,stack,icon) in enumerate(projects):
  x=44+i*286
  b+=rect(x+5,164,258,244,'#241510')+rect(x,159,258,244,'#fff5db')
  b+=rect(x,159,258,33,'#a94822')+pixel('STAGE 0'+n,x+14,170,1.6,'#fff5db',False)
  b+=sprite(icon,x+99,209,3.6)
  b+=pixel(name,x+14,286,2 if len(name)<14 else 1.9,'#241510',False)
  b+=text(desc,x+14,326,12,'#814125')+text(stack,x+14,350,11,'#172c55')
  b+=block(x,370,33,False)+block(x+33,370,33,False)+block(x+192,370,33,False)+block(x+225,370,33,False)
  b+=pipe(x+86,416,80,68)
 b+=sprite('mario',57,436,3)+sprite('goomba',973,442,3)
 b+=ground(484,56)
 save('level-02-quests.svg','World 1-2 — Choose Your Adventure','Four Mushroom Kingdom stage entrances for MediaForge, Roadmap Tracer, Ghost Engineer and VibeMaxing, each with a familiar Mario power-up.',540,b)
 # Underground blue bricks, gold question blocks, real power-up sprites.
 b=heading('1-3','THE POWER-UP ROOM','The tools I collect. The products I build.',True)
 b+=sprite('coin',1085,48,3)
 for i,(label,detail,icon) in enumerate([('REACT','NEXT.JS','mushroom'),('PYTHON','FASTAPI / DJANGO','flower'),('TYPESCRIPT','VITE / TAILWIND','star'),('POSTGRES','SQLITE','coin')]):
  x=55+i*291
  for j in range(4):b+=block(x+j*56,253,56,j==1)
  b+='<g class="bob" style="animation-delay:'+str(i*.3)+'s">'+sprite(icon,x+85,166,4)+'</g>'
  b+=pixel(label,x+112-len(label)*7.5,329,2.5,'#fff5db',False)+text(detail,x+112,375,15,'#a7dfff','middle')
 b+=text('BONUS ITEMS  /  GIT  /  DOCKER  /  VERCEL  /  FIGMA  /  PRODUCT DESIGN',600,418,16,'#ffdc59','middle')
 b+=ground(444,56,True)
 save('level-03-inventory.svg','World 1-3 — The Power-up Room','An underground Mario bonus room with collectible mushrooms, Fire Flowers, Super Stars and coins above the engineering stack.',500,b,'#081d3f')
 b=heading('1-4','EVERY SHIP IS A LEVEL UP','Inspect. Build. Test. Refine. Ship. Repeat.')
 for i,label in enumerate(['INSPECT','BUILD','TEST','REFINE','SHIP']):
  x=92+i*225
  b+=block(x,182,48)+sprite('coin',x+9,139,2)
  b+=pixel(label,x+24-len(label)*6,251,2,'#172c55',False)
  b+=text('0'+str(i+1),x+24,291,14,'#172c55','middle')
 b+=sprite('mario',477,280,3)+sprite('goomba',890,286,3)+sprite('bush',22,298,5)+pipe(1110,267,70,61)+ground(328,52)
 save('level-04-loop.svg','World 1-4 — Every Ship is a Level Up','Mario crosses a five-block engineering course: Inspect, Build, Test, Refine and Ship.',380,b)
 b=hud('1-6',right='WORLD CLEAR!')+sprite('cloud',44,82,2)+sprite('cloud',990,68,2)
 b+=castle(70,150,1.05)
 b+=rect(303,95,5,206,'#fff5db')+rect(298,88,15,10,'#58c830')+'<path d="M308 106h68v42h-68z" fill="#fff5db" stroke="#241510" stroke-width="3"/>'+sprite('star',329,111,2)
 b+=pixel('THANK YOU, PLAYER!',428,112,4)+text('The next world is already loading.',430,176,20,'#172c55')
 b+=pixel('KEEP BUILDING. KEEP GOING.',431,212,2.4,'#ffdc59')+text('PORTFOLIO  /  REPOSITORIES  /  NEXT ADVENTURE',431,274,17,'#172c55')
 b+=sprite('mario',343,253,3)+ground(301,59)
 save('level-05-continue.svg','World Clear — Continue the Adventure','Mario reaches the castle and Star flag. Thank you, player. Keep building. Keep going.',360,b)
 (ROOT/'game'/'sprites.js').write_text('// Generated by scripts/build_profile.py; edit scripts/art.py.\nwindow.MARIO_ART = '+json.dumps({'palette':PALETTE,'sprites':SPRITES},separators=(',',':'))+';\n')

if __name__=='__main__':main()
