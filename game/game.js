(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const canvas = $('game'), ctx = canvas.getContext('2d'), stage = $('stage');
  ctx.imageSmoothingEnabled = false;
  const { palette, sprites } = window.MARIO_ART;
  const { Game, FLOOR } = window.MarioEngine;
  canvas.width = window.matchMedia('(max-width:600px)').matches ? 480 : 960;
  const game = new Game(window.MARIO_WORLD, canvas.width), keys = { left: false, right: false, jump: false };
  let previousState = '', sound = false, audio;
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
    castle(game.width - 176);
    const flagX = game.flagX + 36;
    rect(flagX, 180, 4, FLOOR - 180, '#fff5db');rect(flagX - 5, 170, 14, 12, '#58c830');
    rect(flagX - 35, 188, 35, 27, '#fff5db');image('star', flagX - 28, 191, 21, 21);
    for (const s of game.solids) {
      if (s.x + s.w < camera || s.x > camera + canvas.width) continue;
      // Every raised row corresponds to one active day, exactly as in the SVG.
      if (s.kind === 'week') {
        rect(s.x, s.y, s.w, FLOOR - s.y, '#c86b32');
        for (let row = 0; row < s.rows; row++) {
          const y = s.y + row * 12;
          rect(s.x, y + 10, s.w, 2, '#713a25');
          for (let x = s.x + (row % 2 ? 24 : 0); x < s.x + s.w; x += 48) rect(x, y, 2, 12, '#713a25');
        }
        if (s.rows) rect(s.x, s.y, s.w, 3, '#ffdc59');
        ctx.textAlign = 'center';ctx.font = 'bold 13px monospace';
        ctx.fillStyle = '#fff5db';ctx.fillText('WEEK ' + String(s.index + 1).padStart(2, '0'), s.x + s.w / 2, s.y - 108);
      }
      for (let x = s.x; x < s.x + s.w; x += 32) brick(x, FLOOR);
    }
    // Date labels sit on a dedicated strip rather than disappearing into the floor.
    for (const s of game.solids) if (s.kind === 'week') {
      rect(s.x, 448, s.w, 32, '#132543');
      const w = game.world.weeks[s.index];ctx.textAlign = 'center';ctx.font = 'bold 10px monospace';ctx.fillStyle = '#c8ddff';
      ctx.fillText(w.start, s.x + s.w / 2, 460);ctx.fillStyle = '#ffdc59';
      ctx.fillText(w.count + ' COINS / ' + w.activeDays + ' DAYS', s.x + s.w / 2, 474);
    }
    for (const item of game.pickups) {
      if (item.alive) {
        image('coin', item.x, item.y, item.w, item.h);
        ctx.textAlign = 'center';ctx.font = 'bold 14px monospace';ctx.fillStyle = '#172c55';ctx.fillText('+' + item.value, item.x + 12, item.y - 10);
      } else {
        ctx.textAlign = 'center';ctx.font = 'bold 12px monospace';ctx.fillStyle = '#172c55';ctx.fillText('BANKED ' + item.value, item.x + 12, item.y + 14);
      }
    }
    const p = game.player;
    const bounce = p.grounded && Math.abs(p.vx) > 0.8 ? Math.floor(game.tickCount / 6) % 2 : 0;
    image('mario', p.x - 2, p.y - bounce, 32, 32, p.facing < 0);
    ctx.restore();
    $('coins').textContent = game.coins + ' / ' + game.world.total;
    $('active-days').textContent = game.world.activeDays;
    $('progress').textContent = game.visited.size + ' / 12';
    const week = game.world.weeks[game.weekIndex];
    $('week-detail').textContent = week.start + ' TO ' + week.end + ' · ' + week.count + ' CONTRIBUTIONS · ' + week.activeDays + ' ACTIVE DAYS';
    $('pause').disabled = !['playing', 'paused'].includes(game.state);
    $('pause').textContent = game.state === 'paused' ? 'RESUME' : 'PAUSE';
    if (previousState !== game.state) {
      previousState = game.state;
      const remaining = game.pickups.filter(v => v.alive).length;
      const details = {
        ready: ['YOUR WORK BUILT THIS', 'PLAY MY LAST 12 WEEKS', `${game.world.total} contributions became ${game.world.total} coins. Collect every weekly bundle, then reach the flag.`, '▶ START GAME'],
        paused: ['TAKE YOUR TIME', 'GAME PAUSED', 'Your collected contributions are safe.', '▶ RESUME'],
        review: ['SOMETHING LEFT TO EXPLORE', `${remaining} BUNDLE${remaining === 1 ? '' : 'S'} LEFT`, 'Move left to find the remaining weekly contributions, then return to the flag.', '◀ KEEP EXPLORING'],
        won: ['EVERY CONTRIBUTION COUNTS', 'WORLD COMPLETE!', `${game.coins} real contributions collected. You explored the kingdom your work built.`, '▶ PLAY AGAIN'],
      };
      $('overlay').hidden = game.state === 'playing';
      if (details[game.state]) {
        const d = details[game.state];
        $('overlay-label').textContent = d[0];$('overlay-title').textContent = d[1];$('overlay-copy').textContent = d[2];$('start').textContent = d[3];
        $('status').textContent = d[1] + ' ' + d[2];
        if (game.state !== 'ready') $('start').focus({ preventScroll: true });
      } else $('status').textContent = 'Game started. Collect each weekly contribution bundle and reach the flag.';
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
    else if (game.state === 'review') game.continueExploring();
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
