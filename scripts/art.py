"""Shared, original pixel drawings for the profile and browser game (no dependencies)."""
from html import escape

PALETTE = {'.':'none','k':'#241510','r':'#ed3024','R':'#a91018','s':'#ffc49a','h':'#814125','b':'#2266d5','B':'#123b91','y':'#ffdc59','w':'#fff5db','g':'#58c830','G':'#16852b','o':'#ef8c27','t':'#c86b32','c':'#8bcee9'}
SPRITES = {
'mario': [
'.....rrrrrr.....','....rrrrrrrrr...','....hhhssks.....','...hshsssksss...','...hshhsssksss..','...hhsssskkkk...','.....sssssss....','....rrbrrbr.....','...rrrbrrbrrr...','..rrrrbbbbrrrr..','..ssrbybbybrss..','..sssbbbbbbsss..','....bbbbbbbb....','....bbb..bbb....','...hhh....hhh...','..hhhh....hhhh..'],
'goomba': [
'......tttt......','....tttttttt....','...tttttttttt...','..tttttttttttt..','.ttkkttttkktttt.','.ttwkkttkkwtttt.','tttwwkttkwwttttt','tttttttttttttttt','.ttttkkkktttttt.','..ttsssssstttt..','....ssssssss....','...kksssssskk...','..kkkksssskkkk..','.kkkkk....kkkkk.'],
'mushroom': [
'.....rrrrrr.....','...rrrrrrrrrr...','..rrwwwrrwwrrr..','.rrwwwwrrwwwrrr.','.rrwwwwrrrrrrrr.','rrrwwwrrrrrrwwrr','rrrrrrrrrrrwwwwr','rwwrrrrrrrrwwwwr','rwwwrrrrrrrrwwrr','.rrrrrrrrrrrrrr.','..kkssssssskkk..','...ssksksksss...','...ssksksksss...','...ssssssssss...','....ssssssss....','.....kkkkkk.....'],
'flower': [
'.....rrrrrr.....','...rryyyyyyrr...','..ryywwwwwwyyr..','.rywwwwwwwwwwyr.','.rywkkkkkkwwwwr.','.rywkwkkwkwywyr.','..rykkkkkkyyyr..','...rryyyyyyrr...','.....rrrrrr.....','.......GG.......','..gg...GG...gg..','..gGg..GG..gGg..','...gGg.GG.gGg...','....gGgGGgGg....','.....gGGGGg.....','.......GG.......'],
'star': [
'.......yy.......','.......yy.......','......yyyy......','......yyyy......','yyyyyyyyyyyyyyyy','.yyyyyyyyyyyyyy.','..yyyyyyyyyyyy..','...yykyykyyyy...','...yykyykyyyy...','...yykyykyyyy...','...yyyyyyyyyy...','...yyyyyyyyyy...','..yyyyy..yyyyy..','..yyyy....yyyy..','.yyy........yyy.','................'],
'coin': [
'.....yyyyyy.....','...yyooooooyy...','..yoyyyyyyyoyy..','..yoyywwyyyoyy..','.yoyyywwyyyyoyy.','.yoyyywwyyyyoyy.','.yoyyywwyyyyoyy.','.yoyyywwyyyyoyy.','.yoyyywwyyyyoyy.','.yoyyywwyyyyoyy.','.yoyyywwyyyyoyy.','.yoyyywwyyyyoyy.','..yoyyyyyyyoyy..','..yoyyyyyyyoyy..','...yyooooooyy...','.....yyyyyy.....'],
'cloud': [
'.......kkkkkk...........','.....kkwwwwwwkk.........','....kwwwwwwwwwwk........','..kkwwwwwwwwwwwwkk......','.kwwwwwwwwwwwwwwwwkk....','kwwwwwwwwwwwwwwwwwwwk...','kwwwwwwwkwwwkwwwwwwwwk..','kwwwwwwwkwwwkwwwwwwwwk..','.kwwwwwwwwwwwwwwwwwwwk..','..kkwwwwwwwwwwwwwwwkk...','....kkkkkkkkkkkkkkk.....'],
'bush': [
'......ggg........ggg......','....ggGGGgg....ggGGGgg....','..ggGGGGGGGggggGGGGGGGgg..','.gGGGGGGGGGGGGGGGGGGGGGGg.','gGGGGGGGGGGGGGGGGGGGGGGGGg','gGGGGGGGGGGGGGGGGGGGGGGGGg'],
}
# 5-by-7 bitmap lettering keeps titles sharp and identical inside GitHub image embeds.
FONT = dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', [
'01110 10001 10001 11111 10001 10001 10001','11110 10001 10001 11110 10001 10001 11110','01111 10000 10000 10000 10000 10000 01111','11110 10001 10001 10001 10001 10001 11110','11111 10000 10000 11110 10000 10000 11111','11111 10000 10000 11110 10000 10000 10000','01111 10000 10000 10111 10001 10001 01111','10001 10001 10001 11111 10001 10001 10001','11111 00100 00100 00100 00100 00100 11111','00111 00010 00010 00010 10010 10010 01100','10001 10010 10100 11000 10100 10010 10001','10000 10000 10000 10000 10000 10000 11111','10001 11011 10101 10101 10001 10001 10001','10001 11001 10101 10011 10001 10001 10001','01110 10001 10001 10001 10001 10001 01110','11110 10001 10001 11110 10000 10000 10000','01110 10001 10001 10001 10101 10010 01101','11110 10001 10001 11110 10100 10010 10001','01111 10000 10000 01110 00001 00001 11110','11111 00100 00100 00100 00100 00100 00100','10001 10001 10001 10001 10001 10001 01110','10001 10001 10001 10001 10001 01010 00100','10001 10001 10001 10101 10101 10101 01010','10001 10001 01010 00100 01010 10001 10001','10001 10001 01010 00100 00100 00100 00100','11111 00001 00010 00100 01000 10000 11111',
'01110 10001 10011 10101 11001 10001 01110','00100 01100 00100 00100 00100 00100 01110','01110 10001 00001 00010 00100 01000 11111','11110 00001 00001 01110 00001 00001 11110','00010 00110 01010 10010 11111 00010 00010','11111 10000 10000 11110 00001 00001 11110','01110 10000 10000 11110 10001 10001 01110','11111 00001 00010 00100 01000 01000 01000','01110 10001 10001 01110 10001 10001 01110','01110 10001 10001 01111 00001 00001 01110']))
FONT.update({'?':'01110 10001 00001 00010 00100 00000 00100','-':'00000 00000 00000 11111 00000 00000 00000','.':'00000 00000 00000 00000 00000 01100 01100','/':'00001 00001 00010 00100 01000 10000 10000',':':'00000 01100 01100 00000 01100 01100 00000','!':'00100 00100 00100 00100 00100 00000 00100','+':'00000 00100 00100 11111 00100 00100 00000'})

def rect(x,y,w,h,fill,extra=''):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'

def pixel(text,x,y,size=4,color='#fff5db',shadow=True):
 paths=[]
 for i,char in enumerate(text.upper()):
  for row,bits in enumerate(FONT.get(char,'').split()):
   for col,bit in enumerate(bits):
    if bit=='1': paths.append(f'M{(i*6+col)*size} {row*size}h{size}v{size}h-{size}z')
 d=''.join(paths)
 return f'<g transform="translate({x} {y})" aria-label="{escape(text)}">'+(f'<path d="{d}" fill="#241510" transform="translate({size} {size})"/>' if shadow else '')+f'<path d="{d}" fill="{color}"/></g>'

def text(t,x,y,size=18,color='#fff5db',anchor='start'):
 return f'<text x="{x}" y="{y}" font-family="Courier New,monospace" font-weight="bold" font-size="{size}" fill="{color}" text-anchor="{anchor}">{escape(t)}</text>'

def sprite(name,x,y,scale=3,extra=''):
 rows=SPRITES[name]; paths={}
 for row,line in enumerate(rows):
  for col,c in enumerate(line):
   if c!='.': paths.setdefault(c,[]).append(f'M{col} {row}h1v1h-1z')
 return f'<g transform="translate({x} {y}) scale({scale})" {extra}>'+''.join(f'<path fill="{PALETTE[c]}" d="{"".join(p)}"/>' for c,p in paths.items())+'</g>'

def ground(y,h=64,dark=False):
 color='#1670aa' if dark else '#c86b32'
 return f'<g>{rect(0,y,1200,h,color)}{rect(0,y,1200,5,"#fff5db")}{rect(0,y+5,1200,5,"#241510")}'+''.join(f'<path d="M{x} {y+10}h40v28h-40zM{x-20} {y+38}h40v28h-40z" fill="none" stroke="#241510" stroke-width="3"/>' for x in range(0,1240,40))+'</g>'

def pipe(x,y,w=80,h=100):
 return f'<g stroke="#241510" stroke-width="4">{rect(x+7,y+20,w-14,h-20,"#16852b")}{rect(x+14,y+24,12,h-24,"#a2ed4d")}{rect(x+28,y+24,6,h-24,"#58c830")}{rect(x+w-20,y+24,6,h-24,"#075b24")}{rect(x,y,w,25,"#58c830")}{rect(x+8,y+4,w-16,5,"#baf95b")}</g>'

def block(x,y,size=48,question=True):
 s=f'<g>{rect(x,y,size,size,"#241510")}{rect(x+3,y+3,size-6,size-6,"#ef8c27")}{rect(x+5,y+5,size-10,3,"#ffdc59")}'
 if question: s+=pixel('?',x+size*.27,y+size*.16,size/12,'#fff5db',True)
 else: s+=f'<path d="M{x+3} {y+size/2}h{size-6}M{x+size/2} {y+3}v{size/2-3}M{x+size/4} {y+size/2}v{size/2-3}M{x+size*.75} {y+size/2}v{size/2-3}" stroke="#241510" stroke-width="3"/>'
 return s+'</g>'

def hill(x,y,w=180,h=130):
 return f'<g><path d="M{x} {y}v-{h//3}l{w//3} -{h*2//3}h{w//3}l{w//3} {h*2//3}v{h//3}z" fill="#58c830" stroke="#241510" stroke-width="3"/>{rect(x+w*.45,y-h*.65,5,12,"#241510")}{rect(x+w*.55,y-h*.65,5,12,"#241510")}</g>'

def castle(x,y,s=1):
 out=f'<g transform="translate({x} {y}) scale({s})">'
 for bx,by,bw,bh in [(0,42,160,102),(35,0,90,144)]:
  out+=rect(bx,by,bw,bh,'#c86b32','stroke="#241510" stroke-width="3"')
  for ry in range(by+14,by+bh,16):
   out+=f'<path d="M{bx} {ry}h{bw}" stroke="#814125" stroke-width="2"/>'
   for rx in range(bx+((ry//16)%2)*16,bx+bw,32): out+=rect(rx,ry-14,2,14,'#814125')
 for bx,by,bw in [(0,30,160),(35,-12,90)]:
  for rx in range(bx,bx+bw,18):out+=rect(rx,by,12,16,'#c86b32','stroke="#241510" stroke-width="2"')
 out+=f'<path d="M65 144v-35q15-22 30 0v35z" fill="#241510"/>'+rect(51,23,10,16,'#241510')+rect(99,23,10,16,'#241510')
 return out+'</g>'

def svg(title,desc,height,body,bg='#5c94fc',css=''):
 return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc" shape-rendering="crispEdges">
<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>
<style>.bob{{animation:bob 1.6s steps(3,end) infinite}}.twinkle{{animation:twinkle 1.2s steps(2,end) infinite}}@keyframes bob{{50%{{transform:translateY(-8px)}}}}@keyframes twinkle{{50%{{opacity:.35}}}}{css}@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
{rect(0,0,1200,height,bg)}{body}</svg>'''
