const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { Game, FLOOR, WEEK_WIDTH, LEAD } = require('../game/engine.js');
function world(counts = [3,8,0,21,1,0,13,7,0,2,4,9]) {
  const weeks = counts.map((count, i) => ({ start:`2026-08-${String(i+1).padStart(2,'0')}`, end:'2026-11-06', count, activeDays:Math.min(7,count) }));
  return {weeks,total:counts.reduce((a,b)=>a+b,0),activeDays:weeks.reduce((a,b)=>a+b.activeDays,0)};
}
function active(data = world(), width = 960) { const g = new Game(data,width);g.start();return g; }
function frames(g, n, input = {}) { for (let i=0;i<n;i++) g.update(input); }
test('weekly active days determine exact physical terrain and contribution bundles', () => {
  const data=world(),g=active(data);
  data.weeks.forEach((w,i)=>{
    const ground=g.solids.find(s=>s.index===i);assert.equal(ground.y,FLOOR-w.activeDays*12);assert.equal(ground.rows,w.activeDays);
    assert.equal(g.pickups.find(v=>v.index===i)?.value || 0,w.count);
  });
  assert.equal(g.pickups.reduce((n,v)=>n+v.value,0),data.total);
});
test('a collected bundle banks its exact contribution value exactly once', () => {
  const g=active();const c=g.pickups[1];g.player.x=c.x;g.player.y=c.y;g.player.grounded=false;
  g.update();assert.equal(g.coins,c.value);assert.equal(c.alive,false);frames(g,3);assert.equal(g.coins,c.value);
});
test('rest weeks are flat, accessible ground with no invented rewards', () => {
  const g=active(world(Array(12).fill(0)));assert.equal(g.pickups.length,0);
  assert.ok(g.solids.every(s=>s.y===FLOOR));
  frames(g,80,{right:true});assert.ok(g.player.x>300);assert.equal(g.coins,0);assert.equal(g.player.y+g.player.h,FLOOR);
});
test('a normal jump can clear the maximum seven-day terrace', () => {
  const g=active(world(Array(12).fill(7)));g.player.x=200;
  frames(g,24,{right:true,jump:true});assert.ok(g.player.x>LEAD);assert.ok(g.player.y+g.player.h<FLOOR-84);
  frames(g,40);assert.equal(g.player.y+g.player.h,FLOOR-84);
});
test('pause freezes the replay; restart restores all real bundles', () => {
  const g=active();const c=g.pickups[0];g.player.x=c.x;g.player.y=c.y;g.update();g.pause();const x=g.player.x;
  frames(g,50,{right:true});assert.equal(g.player.x,x);assert.equal(g.coins,3);
  g.reset();assert.equal(g.coins,0);assert.ok(g.pickups.every(v=>v.alive));assert.equal(g.state,'ready');
});
test('the flag cannot claim completion while contributions are missing; revisiting is possible', () => {
  const g=active();g.player.x=g.flagX;g.update();assert.equal(g.state,'review');
  g.continueExploring();g.update();assert.equal(g.state,'playing');
  frames(g,50,{left:true});assert.ok(g.player.x<g.flagX-100);assert.equal(g.finishArmed,true);
});
test('completion banks the source total with no invented time or flag bonuses', () => {
  const g=active();for(const c of g.pickups){g.player.x=c.x;g.player.y=c.y;g.player.vy=0;g.update();}
  assert.equal(g.coins,g.world.total);g.player.x=g.flagX;g.update();assert.equal(g.state,'won');
  frames(g,60);assert.equal(g.coins,g.world.total);
});
test('an empty activity world completes honestly with zero coins', () => {
  const g=active(world(Array(12).fill(0)));g.player.x=g.flagX;g.update();assert.equal(g.state,'won');assert.equal(g.coins,0);
});
test('mobile camera can reach the final contribution week and castle', () => {
  const g=active(world(),480);g.player.x=g.flagX-10;g.update();assert.ok(g.player.x-g.camera<480);
});
test('invalid or fabricated source totals are rejected', () => {
  assert.throws(()=>new Game({...world(),total:999}),/total/);
  const bad=world();bad.weeks[0].activeDays=8;assert.throws(()=>new Game(bad),/Invalid/);
});
test('committed activity level is a valid input and supplies the exact coin budget', () => {
  const source=fs.readFileSync(require.resolve('../game/activity-level.js'),'utf8');
  const data=JSON.parse(source.split('window.MARIO_WORLD = ')[1].trim().replace(/;$/,''));
  const g=new Game(data);assert.equal(g.pickups.reduce((a,b)=>a+b.value,0),data.total);
});
test('ordinary movement and jumps collect the entire real world and reach the flag', () => {
  const source=fs.readFileSync(require.resolve('../game/activity-level.js'),'utf8');
  const data=JSON.parse(source.split('window.MARIO_WORLD = ')[1].trim().replace(/;$/,''));
  const g=active(data);let hold=0;
  for(let frame=0;frame<6000&&g.state==='playing';frame++){
    const p=g.player,target=g.pickups.find(c=>c.alive),tx=target?target.x:g.flagX+8,dx=tx-p.x;
    const direction=Math.abs(dx)>3?Math.sign(dx):0;
    const rise=g.solids.find(s=>s.y<p.y+p.h-2&&(direction>0?s.x>=p.x+p.w&&s.x-p.x-p.w<60:s.x+s.w<=p.x&&p.x-s.x-s.w<60));
    if(p.grounded&&hold===0&&(rise||target&&Math.abs(dx)<70))hold=30;
    g.update({right:direction>0,left:direction<0,jump:hold>0});if(hold)hold--;
  }
  assert.equal(g.state,'won');assert.equal(g.coins,data.total);assert.ok(g.pickups.every(c=>!c.alive));
});
