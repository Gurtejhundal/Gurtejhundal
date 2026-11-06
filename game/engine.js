/* Shared deterministic game simulation: browser rendering is in game.js. */
(function (root) {
  'use strict';
  const FLOOR = 416, WIDTH = 3904;
  function intersects(a, b) {
    return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
  }
  class Game {
    constructor(best = 0, viewportWidth = 960) { this.best = best; this.viewportWidth = viewportWidth; this.reset(); }
    reset() {
      this.state = 'ready'; this.lives = 3; this.score = 0; this.coins = 0;
      this.time = 300; this.tickCount = 0; this.camera = 0; this.events = [];
      this.makeLevel(); this.spawn(); this.player.invincible = 0;
    }
    makeLevel() {
      const gaps = [[1056, 1152], [2400, 2496]];
      this.solids = [];
      for (let x = 0; x < WIDTH; x += 32) {
        if (!gaps.some(([a, b]) => x >= a && x < b)) this.solids.push({ x, y: FLOOR, w: 32, h: 64, kind: 'ground' });
      }
      for (const [x, h] of [[608, 64], [1408, 96], [2112, 64], [3072, 96]]) {
        this.solids.push({ x, y: FLOOR - h, w: 64, h, kind: 'pipe' });
      }
      for (const [x, y, kind] of [
        [256, 304, 'brick'], [288, 304, 'question'], [320, 304, 'brick'],
        [800, 288, 'question'], [832, 288, 'brick'], [864, 288, 'question'],
        [1216, 288, 'brick'], [1248, 288, 'question'],
        [1696, 304, 'brick'], [1728, 304, 'question'], [1760, 304, 'brick'],
        [2592, 288, 'question'], [2624, 288, 'brick'], [2656, 288, 'question'],
      ]) this.solids.push({ x, y, w: 32, h: 32, kind, used: false });
      for (let i = 0; i < 5; i++) this.solids.push({ x: 3328 + i * 32, y: FLOOR - (i + 1) * 32, w: 32, h: (i + 1) * 32, kind: 'step' });
      this.enemies = [448, 928, 1312, 1856, 2240, 2784, 2944].map(x => ({ x, y: FLOOR - 28, w: 30, h: 28, vx: -0.85, vy: 0, alive: true }));
      this.pickups = [352, 480, 720, 960, 1024, 1184, 1568, 1824, 1984, 2320, 2528, 2752, 2880, 3200].map(x => ({ x, y: 340, w: 20, h: 28, kind: 'coin', alive: true }));
      this.particles = [];
    }
    spawn() {
      this.player = { x: 72, y: FLOOR - 32, w: 28, h: 32, vx: 0, vy: 0, grounded: true, facing: 1, shield: false, invincible: 100 };
      this.jumpBuffer = 0; this.coyote = 0; this.jumpHeld = false; this.camera = 0;
    }
    start() { if (this.state === 'ready') this.state = 'playing'; }
    pause() { if (this.state === 'playing') this.state = 'paused'; else if (this.state === 'paused') this.state = 'playing'; }
    addScore(n) { this.score += n; this.best = Math.max(this.best, this.score); }
    collectCoin() { this.coins++; this.addScore(100); this.events.push('coin'); }
    damage() {
      const p = this.player;
      if (p.invincible > 0) return;
      if (p.shield) { p.shield = false; p.invincible = 120; this.events.push('hurt'); return; }
      this.loseLife();
    }
    loseLife() {
      this.lives--; this.events.push('hurt');
      if (this.lives <= 0) { this.state = 'over'; return; }
      this.makeLevel(); this.spawn();
    }
    update(input = {}) {
      if (this.state !== 'playing') return;
      this.events = []; this.tickCount++;
      this.time = Math.max(0, this.time - 1 / 60);
      if (this.time <= 0) { this.state = 'over'; return; }
      let p = this.player;
      if (p.invincible > 0) p.invincible--;
      if (input.jump && !this.jumpHeld) this.jumpBuffer = 7;
      this.jumpHeld = !!input.jump;
      if (p.grounded) this.coyote = 5; else this.coyote--;
      if (this.jumpBuffer > 0 && this.coyote > 0) {
        p.vy = -11.8; p.grounded = false; this.coyote = 0; this.jumpBuffer = 0; this.events.push('jump');
      }
      this.jumpBuffer--;
      if (!input.jump && p.vy < -5) p.vy = -5;
      const direction = Number(!!input.right) - Number(!!input.left);
      p.vx = direction ? Math.max(-4, Math.min(4, p.vx + direction * 0.5)) : p.vx * 0.75;
      if (direction) p.facing = direction;
      p.x = Math.max(0, Math.min(WIDTH - p.w, p.x + p.vx));
      for (const s of this.solids) if (intersects(p, s)) {
        if (p.vx > 0) p.x = s.x - p.w; else if (p.vx < 0) p.x = s.x + s.w;
        p.vx = 0;
      }
      const previousBottom = p.y + p.h;
      p.vy = Math.min(13, p.vy + 0.55); p.y += p.vy; p.grounded = false;
      for (const s of this.solids) if (intersects(p, s)) {
        if (p.vy >= 0) { p.y = s.y - p.h; p.grounded = true; }
        else {
          p.y = s.y + s.h;
          if (s.kind === 'question' && !s.used) {
            s.used = true; this.collectCoin();
            this.particles.push({ x: s.x + 6, y: s.y - 20, life: 35 });
            if (!this.pickups.some(v => v.kind === 'mushroom')) this.pickups.push({ x: s.x, y: s.y - 32, w: 28, h: 28, kind: 'mushroom', alive: true });
          }
        }
        p.vy = 0;
      }
      if (p.y > 520) { this.loseLife(); return; }
      for (const e of this.enemies) {
        if (!e.alive) continue;
        e.x += e.vx;
        for (const s of this.solids) if (s.kind !== 'ground' && intersects(e, s)) {
          e.x = e.vx > 0 ? s.x - e.w : s.x + s.w; e.vx *= -1;
        }
        // Turn around at platform edges so Goombas patrol rather than float over pits.
        const ahead = e.vx < 0 ? e.x - 2 : e.x + e.w + 2;
        if (!this.solids.some(s => s.kind === 'ground' && ahead >= s.x && ahead < s.x + s.w)) e.vx *= -1;
        if (intersects(p, e)) {
          if (previousBottom <= e.y + 10 && p.vy >= 0) {
            e.alive = false; p.vy = -7; this.addScore(200); this.events.push('stomp');
          } else {
            const lives = this.lives; this.damage();
            if (this.lives !== lives || this.state !== 'playing') return;
          }
        }
      }
      for (const item of this.pickups) if (item.alive && intersects(p, item)) {
        item.alive = false;
        if (item.kind === 'mushroom') { p.shield = true; this.addScore(1000); this.events.push('power'); }
        else this.collectCoin();
      }
      this.particles = this.particles.filter(v => --v.life > 0);
      for (const v of this.particles) v.y -= 1.7;
      this.camera = Math.max(0, Math.min(WIDTH - this.viewportWidth, p.x - this.viewportWidth * 0.3125));
      if (p.x >= 3616) { this.state = 'won'; this.addScore(Math.ceil(this.time) * 10); this.events.push('win'); }
    }
  }
  const api = { Game, intersects, FLOOR, WIDTH };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.MarioEngine = api;
})(typeof window === 'undefined' ? globalThis : window);
