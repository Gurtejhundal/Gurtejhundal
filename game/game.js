(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const canvas = $('game'), ctx = canvas.getContext('2d'), stage = $('stage');
  ctx.imageSmoothingEnabled = false;
  const { palette, sprites } = window.MARIO_ART;
  const { Game, FLOOR } = window.MarioEngine;
  let best = 0;
  try { best = Number(localStorage.getItem('super-gurtej-best')) || 0; } catch (_) { /* Storage is optional. */ }
  canvas.width = window.matchMedia('(max-width:600px)').matches ? 480 : 960;
  const game = new Game(best, canvas.width), keys = { left: false, right: false, jump: false };
  let previousState = '', sound = false, audio, savedBest = best;
  const images = {};
  for (const [name, rows] of Object.entries(sprites)) {
    const image = document.createElement('canvas'); image.width = Math.max(...rows.map(v => v.length)); image.height = rows.length;
    const c = image.getContext('2d');
    rows.forEach((row, y) => [...row].forEach((p, x) => { if (p !== '.') { c.fillStyle = palette[p]; c.fillRect(x, y, 1, 1); } }));
    images[name] = image;
  }
  function rect(x, y, w, h, color) { ctx.fillStyle = color; ctx.fillRect(Math.round(x), Math.round(y), w, h); }
  function image(name, x, y, w, h, flip = false) {
    ctx.save();ctx.translate(Math.round(x), Math.round(y));
    if (flip) { ctx.translate(w, 0); ctx.scale(-1, 1); }
    ctx.drawImage(images[name], 0, 0, w, h);ctx.restore();
  }
  function brick(x, y, w = 32, h = 32, dark = false) {
    rect(x, y, w, h, dark ? '#a94822' : '#c86b32');
    rect(x, y, w, 2, '#fff5db');rect(x, y + 15, w, 2, '#241510');
    rect(x, y, 2, 16, '#241510');rect(x + 16, y + 17, 2, 15, '#241510');
    rect(x, y + 30, w, 2, '#241510');
  }
  function pipe(x, y, w, h) {
    rect(x + 5, y + 17, w - 10, h - 17, '#241510');
    rect(x + 8, y + 20, w - 16, h - 20, '#16852b');
    rect(x + 11, y + 20, 9, h - 20, '#baf95b');rect(x + 24, y + 20, 5, h - 20, '#58c830');
    rect(x, y, w, 22, '#241510');rect(x + 3, y + 3, w - 6, 15, '#58c830');rect(x + 7, y + 4, w - 14, 3, '#baf95b');
  }
  function castle(x) {
    for (let row = 0; row < 4; row++) for (let col = 0; col < 5; col++) brick(x + col * 32, FLOOR - 128 + row * 32);
    for (let row = 0; row < 2; row++) for (let col = 1; col < 4; col++) brick(x + col * 32, FLOOR - 192 + row * 32);
    for (let i = 0; i < 5; i++) rect(x + i * 32, FLOOR - 140, 20, 16, '#c86b32');
    for (let i = 1; i < 4; i++) rect(x + i * 32, FLOOR - 204, 20, 16, '#c86b32');
    rect(x + 64, FLOOR - 54, 32, 54, '#241510');rect(x + 43, FLOOR - 170, 12, 20, '#241510');rect(x + 106, FLOOR - 170, 12, 20, '#241510');
  }
  function render() {
    rect(0, 0, 960, 480, '#5c94fc');
    const camera = game.camera;
    ctx.imageSmoothingEnabled = false;
    for (let i = -1; i < 9; i++) {
      const x = i * 290 - (camera * 0.25 % 290);
      image('cloud', x + 40, 52 + (i % 3) * 23, 96, 44);
      ctx.fillStyle = i % 2 ? '#58c830' : '#85d94a';
      ctx.beginPath();ctx.moveTo(x, FLOOR);ctx.lineTo(x + 60, FLOOR - 128);ctx.lineTo(x + 125, FLOOR - 128);ctx.lineTo(x + 190, FLOOR);ctx.closePath();ctx.fill();
      rect(x + 88, FLOOR - 106, 4, 10, '#241510');rect(x + 103, FLOOR - 106, 4, 10, '#241510');
      image('bush', x + 210, FLOOR - 24, 104, 24);
    }
    ctx.save();ctx.translate(-Math.round(camera), 0);
    castle(3712);
    rect(3648, 180, 4, FLOOR - 180, '#fff5db');rect(3643, 170, 14, 12, '#58c830');
    rect(3613, 188, 35, 27, '#fff5db');image('star', 3620, 191, 21, 21);
    for (const s of game.solids) {
      if (s.x + s.w < camera || s.x > camera + 960) continue;
      if (s.kind === 'ground') { brick(s.x, s.y);brick(s.x, s.y + 32); }
      else if (s.kind === 'pipe') pipe(s.x, s.y, s.w, s.h);
      else if (s.kind === 'question') {
        rect(s.x, s.y, 32, 32, '#241510');rect(s.x + 2, s.y + 2, 28, 28, s.used ? '#9b6138' : '#ef8c27');rect(s.x + 4, s.y + 4, 24, 2, '#ffdc59');
        if (!s.used) { ctx.font = 'bold 25px monospace';ctx.fillStyle = '#fff5db';ctx.fillText('?', s.x + 8, s.y + 25); }
      } else {
        for (let y = s.y; y < s.y + s.h; y += 32) brick(s.x, y, 32, 32, s.kind === 'step');
      }
    }
    for (const item of game.pickups) if (item.alive) image(item.kind, item.x, item.y, item.w, item.h);
    for (const e of game.enemies) if (e.alive) image('goomba', e.x, e.y, e.w, e.h, Math.floor(game.tickCount / 9) % 2 === 0);
    for (const v of game.particles) image('coin', v.x, v.y, 20, 28);
    const p = game.player;
    if (!p.invincible || Math.floor(p.invincible / 5) % 2 === 0 || game.state !== 'playing') {
      const bounce = p.grounded && Math.abs(p.vx) > 0.8 ? Math.floor(game.tickCount / 6) % 2 : 0;
      image('mario', p.x - 2, p.y - bounce - (p.shield ? 8 : 0), 32, p.shield ? 40 : 32, p.facing < 0);
    }
    ctx.restore();
    $('score').textContent = String(game.score).padStart(6, '0');
    $('coins').textContent = '× ' + String(game.coins).padStart(2, '0');
    $('lives').textContent = '× ' + game.lives;$('time').textContent = Math.ceil(game.time);
    $('best').textContent = 'BEST ' + String(game.best).padStart(6, '0');
    $('power').textContent = p.shield ? 'SUPER MARIO' : 'SMALL MARIO';
    $('pause').disabled = !['playing', 'paused'].includes(game.state);
    $('pause').textContent = game.state === 'paused' ? 'RESUME' : 'PAUSE';
    if (previousState !== game.state) {
      previousState = game.state;
      const details = {
        ready: ['WORLD 1-1', 'LET’S-A GO!', 'A whole Mushroom Kingdom ahead of you.', '▶ START GAME'],
        paused: ['TAKE A BREATHER', 'GAME PAUSED', 'Your adventure will be right here.', '▶ RESUME'],
        over: ['TRY ANOTHER ROUTE', 'GAME OVER', `You collected ${game.coins} coins and scored ${game.score}.`, '↻ TRY AGAIN'],
        won: ['WORLD 1-1 CLEAR', 'COURSE CLEAR!', `You made it! ${game.score} points. The next build awaits.`, '▶ PLAY AGAIN'],
      };
      $('overlay').hidden = game.state === 'playing';
      if (details[game.state]) {
        const d = details[game.state];
        $('overlay-label').textContent = d[0];$('overlay-title').textContent = d[1];$('overlay-copy').textContent = d[2];$('start').textContent = d[3];
        $('status').textContent = d[1] + ' ' + d[2];
        if (game.state !== 'ready') $('start').focus({ preventScroll: true });
      } else $('status').textContent = 'Game started. Collect coins and reach the flag.';
    }
    if (game.best > savedBest) {
      savedBest = game.best;
      try { localStorage.setItem('super-gurtej-best', String(savedBest)); } catch (_) { /* Storage is optional. */ }
    }
  }
  function beep(event) {
    if (!sound || !audio) return;
    const notes = { jump: [330, 520], coin: [880, 1320], stomp: [160, 90], hurt: [180, 70], power: [440, 880], win: [660, 1320] };
    const [a, b] = notes[event] || [330, 440], at = audio.currentTime;
    const osc = audio.createOscillator(), volume = audio.createGain();
    osc.type = 'square';osc.frequency.setValueAtTime(a, at);osc.frequency.exponentialRampToValueAtTime(b, at + 0.1);
    volume.gain.setValueAtTime(0.035, at);volume.gain.exponentialRampToValueAtTime(0.001, at + 0.16);
    osc.connect(volume);volume.connect(audio.destination);osc.start(at);osc.stop(at + 0.17);
  }
  function clearInput() { keys.left = keys.right = keys.jump = false; }
  function play() {
    clearInput();
    if (game.state === 'paused') game.pause();
    else { if (game.state !== 'ready') game.reset();game.start(); }
    if (audio) audio.resume().catch(() => {});
    stage.focus({ preventScroll: true });render();
  }
  $('start').addEventListener('click', play);
  $('restart').addEventListener('click', () => { game.reset();play(); });
  $('pause').addEventListener('click', () => { clearInput();game.pause();if (game.state === 'playing') stage.focus({ preventScroll: true });render(); });
  $('sound').addEventListener('click', () => {
    sound = !sound;
    if (sound) {
      try { audio = audio || new (window.AudioContext || window.webkitAudioContext)();audio.resume().catch(() => {}); }
      catch (_) { sound = false; }
    }
    $('sound').textContent = sound ? 'SOUND ON' : 'SOUND OFF';$('sound').setAttribute('aria-pressed', String(sound));
  });
  const bindings = { ArrowLeft: 'left', KeyA: 'left', ArrowRight: 'right', KeyD: 'right', Space: 'jump', ArrowUp: 'jump', KeyW: 'jump' };
  stage.addEventListener('keydown', event => {
    if (event.target !== stage && !['KeyP', 'KeyR'].includes(event.code)) return;
    if (bindings[event.code]) { event.preventDefault();keys[bindings[event.code]] = true; }
    if (event.repeat) return;
    if (event.code === 'KeyP') { event.preventDefault();clearInput();game.pause();if (game.state === 'playing') stage.focus({ preventScroll: true });render(); }
    if (event.code === 'KeyR') { event.preventDefault();game.reset();play(); }
  });
  window.addEventListener('keyup', event => { if (bindings[event.code]) keys[bindings[event.code]] = false; });
  for (const button of document.querySelectorAll('[data-control]')) {
    const control = button.dataset.control;
    button.addEventListener('pointerdown', event => {
      event.preventDefault();button.setPointerCapture(event.pointerId);keys[control] = true;
    });
    for (const type of ['pointerup', 'pointercancel', 'lostpointercapture']) button.addEventListener(type, () => { keys[control] = false; });
  }
  function autoPause() { clearInput();if (game.state === 'playing') { game.pause();render(); } }
  window.addEventListener('blur', autoPause);
  window.addEventListener('resize', () => {
    canvas.width = window.matchMedia('(max-width:600px)').matches ? 480 : 960;
    game.viewportWidth = canvas.width;
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) autoPause(); });
  let last = 0, accumulator = 0;
  function frame(now) {
    accumulator += Math.min((now - (last || now)) / 1000, 0.1);last = now;
    while (accumulator >= 1 / 60) {
      game.update(keys);if (game.state === 'playing' || game.events.includes('win')) for (const event of game.events) beep(event);
      game.events = [];accumulator -= 1 / 60;
    }
    render();requestAnimationFrame(frame);
  }
  render();requestAnimationFrame(frame);
})();
