const { test } = require('node:test');
const assert = require('node:assert/strict');
const { Game, FLOOR } = require('../game/engine.js');
function active() { const g = new Game();g.start();g.player.invincible = 0;return g; }
function frames(g, n, input = {}) { for (let i = 0; i < n; i++) g.update(input); }
test('movement, floor collision and camera scrolling', () => {
  const g = active();frames(g, 50, { right: true });
  assert.ok(g.player.x > 200);assert.equal(g.player.y + g.player.h, FLOOR);
  g.player.x = 1500;g.update();assert.ok(g.camera > 0);
});
test('jump clears a pipe and lands on its top without tunnelling', () => {
  const g = active();g.player.x = 550;
  frames(g, 22, { right: true, jump: true });assert.ok(g.player.y + g.player.h < 352);
  frames(g, 30);assert.equal(g.player.y + g.player.h, 352);assert.equal(g.player.grounded, true);
});
test('hitting a question block yields a coin and mushroom once', () => {
  const g = active();g.player.x = 290;
  frames(g, 18, { jump: true });
  assert.equal(g.coins, 1);assert.equal(g.solids.find(s => s.x === 288 && s.kind === 'question').used, true);
  assert.equal(g.pickups.filter(s => s.kind === 'mushroom').length, 1);
  frames(g, 30);frames(g, 18, { jump: true });assert.equal(g.coins, 1);
});
test('descending onto a Goomba stomps it and bounces', () => {
  const g = active();const e = g.enemies[0];g.player.x = e.x;g.player.y = e.y - 33;g.player.vy = 4;g.player.grounded = false;
  g.update();assert.equal(e.alive, false);assert.ok(g.player.vy < 0);assert.equal(g.score, 200);
});
test('side collision loses a life; mushroom absorbs one hit', () => {
  const g = active();g.player.shield = true;g.player.x = g.enemies[0].x;g.update();
  assert.equal(g.lives, 3);assert.equal(g.player.shield, false);
  g.player.invincible = 0;g.player.x = g.enemies[0].x;g.update();assert.equal(g.lives, 2);
});
test('falling in a pit respawns and the third fall ends the game', () => {
  const g = active();
  for (let i = 0; i < 3; i++) { g.player.x = 1080;g.player.y = 540;g.update(); }
  assert.equal(g.lives, 0);assert.equal(g.state, 'over');
});
test('pause freezes physics and timer; restart resets the level', () => {
  const g = active();g.pause();const t = g.time;const x = g.player.x;
  frames(g, 60, { right: true });assert.equal(g.time, t);assert.equal(g.player.x, x);
  g.pause();g.update({ right: true });assert.ok(g.player.x > x);
  g.reset();assert.equal(g.lives, 3);assert.equal(g.coins, 0);assert.equal(g.state, 'ready');
});
test('flag awards time bonus once and preserves best score', () => {
  const g = active();g.player.x = 3630;g.update();const score = g.score;
  assert.equal(g.state, 'won');assert.ok(score > 0);frames(g, 60);assert.equal(g.score, score);
  g.reset();assert.equal(g.best, score);assert.equal(g.score, 0);
});
test('timer expiration ends the run', () => {
  const g = active();g.time = 0.001;g.update();assert.equal(g.state, 'over');
});
test('complete the full handmade level with ordinary movement and jump inputs', () => {
  const g = new Game();g.start();
  const jumps = new Map([[17,26],[58,26],[109,39],[151,30],[236,34],[278,25],[321,30],[353,32],[498,29],[534,39],[582,37],[624,25],[668,30],[715,28],[773,37],[839,32],[872,35]]);
  let hold = 0;
  for (let frame = 0; frame < 1800 && g.state === 'playing'; frame++) {
    if (jumps.has(frame)) hold = jumps.get(frame);
    g.update({right:true,jump:hold > 0});if (hold) hold--;
  }
  assert.equal(g.state, 'won');assert.equal(g.lives, 3);
});
test('mobile camera follows the player all the way to the castle', () => {
  const g = new Game(0, 480);g.start();g.player.x = 3600;g.update();
  assert.ok(g.camera > 3000);assert.ok(g.player.x - g.camera < 480);
});
