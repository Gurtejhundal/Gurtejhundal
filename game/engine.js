/* The level is built entirely from the same twelve real weeks as the README replay. */
(function (root) {
  'use strict';
  const FLOOR = 416, WEEK_WIDTH = 192, LEAD = 256;
  function intersects(a, b) {
    return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
  }
  class Game {
    constructor(world, viewportWidth = 960) {
      if (!world || !Array.isArray(world.weeks) || world.weeks.length !== 12) throw new Error('Twelve real activity weeks are required.');
      if (world.weeks.some(w => !Number.isInteger(w.count) || w.count < 0 || !Number.isInteger(w.activeDays) || w.activeDays < 0 || w.activeDays > 7 || (w.count === 0) !== (w.activeDays === 0))) throw new Error('Invalid weekly activity.');
      if (world.weeks.reduce((n, w) => n + w.count, 0) !== world.total) throw new Error('Contribution total must match the weeks.');
      this.world = world;this.viewportWidth = viewportWidth;this.width = LEAD + WEEK_WIDTH * 12 + 352;this.flagX = this.width - 240;this.reset();
    }
    reset() {
      this.state = 'ready';this.coins = 0;this.tickCount = 0;this.camera = 0;this.events = [];
      this.player = { x: 72, y: FLOOR - 32, w: 28, h: 32, vx: 0, vy: 0, grounded: true, facing: 1 };
      this.jumpBuffer = 0;this.coyote = 0;this.jumpHeld = false;this.finishArmed = true;
      this.visited = new Set();this.solids = [{ x: 0, y: FLOOR, w: LEAD, h: 64, kind: 'ground' }];this.pickups = [];
      this.world.weeks.forEach((w, index) => {
        const x = LEAD + index * WEEK_WIDTH, y = FLOOR - w.activeDays * 12;
        this.solids.push({ x, y, w: WEEK_WIDTH, h: 480 - y, kind: 'week', index, rows: w.activeDays });
        if (w.count) this.pickups.push({ x: x + WEEK_WIDTH / 2 - 12, y: y - 72, w: 24, h: 28, value: w.count, index, alive: true });
      });
      this.solids.push({ x: LEAD + WEEK_WIDTH * 12, y: FLOOR, w: 352, h: 64, kind: 'ground' });
    }
    get weekIndex() { return Math.max(0, Math.min(11, Math.floor((this.player.x - LEAD) / WEEK_WIDTH))); }
    start() { if (this.state === 'ready') this.state = 'playing'; }
    pause() { if (this.state === 'playing') this.state = 'paused';else if (this.state === 'paused') this.state = 'playing'; }
    continueExploring() { if (this.state === 'review') this.state = 'playing'; }
    update(input = {}) {
      if (this.state !== 'playing') return;
      this.events = [];this.tickCount++;
      const p = this.player;
      if (input.jump && !this.jumpHeld) this.jumpBuffer = 7;
      this.jumpHeld = !!input.jump;
      if (p.grounded) this.coyote = 5;else this.coyote--;
      if (this.jumpBuffer > 0 && this.coyote > 0) {
        p.vy = -11.8;p.grounded = false;this.coyote = 0;this.jumpBuffer = 0;this.events.push('jump');
      }
      this.jumpBuffer--;
      if (!input.jump && p.vy < -5) p.vy = -5;
      const direction = Number(!!input.right) - Number(!!input.left);
      p.vx = direction ? Math.max(-4, Math.min(4, p.vx + direction * 0.5)) : p.vx * 0.75;
      if (direction) p.facing = direction;
      p.x = Math.max(0, Math.min(this.width - p.w, p.x + p.vx));
      for (const s of this.solids) if (intersects(p, s)) {
        if (p.vx > 0) p.x = s.x - p.w;else if (p.vx < 0) p.x = s.x + s.w;
        p.vx = 0;
      }
      p.vy = Math.min(13, p.vy + 0.55);p.y += p.vy;p.grounded = false;
      for (const s of this.solids) if (intersects(p, s)) {
        if (p.vy >= 0) { p.y = s.y - p.h;p.grounded = true; }else p.y = s.y + s.h;
        p.vy = 0;
      }
      for (const item of this.pickups) if (item.alive && intersects(p, item)) {
        item.alive = false;this.coins += item.value;this.events.push('coin');
      }
      this.world.weeks.forEach((_, i) => { if (p.x + p.w / 2 >= LEAD + i * WEEK_WIDTH + WEEK_WIDTH / 2) this.visited.add(i); });
      this.camera = Math.max(0, Math.min(this.width - this.viewportWidth, p.x - this.viewportWidth * 0.3125));
      if (p.x < this.flagX - 100) this.finishArmed = true;
      if (p.x >= this.flagX && this.finishArmed) {
        this.finishArmed = false;
        this.state = this.coins === this.world.total ? 'won' : 'review';
        if (this.state === 'won') this.events.push('win');
      }
    }
  }
  const api = { Game, intersects, FLOOR, WEEK_WIDTH, LEAD };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;else root.MarioEngine = api;
})(typeof window === 'undefined' ? globalThis : window);
