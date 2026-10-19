/* DrumFill2 site: theme toggle, reveal-on-scroll, tabs, copy buttons and the toy drum machine.
   Every sound is synthesised here with Web Audio; no samples are loaded. */
(function () {
  "use strict";
  var root = document.documentElement;
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- theme ---------- */
  function storedTheme() { try { return localStorage.getItem("df-theme"); } catch (e) { return null; } }
  function storeTheme(t) { try { localStorage.setItem("df-theme", t); } catch (e) { /* private mode */ } }
  var t0 = storedTheme();
  if (t0 === "light" || t0 === "dark") root.setAttribute("data-theme", t0);
  document.querySelectorAll(".theme-btn").forEach(function (b) {
    b.addEventListener("click", function () {
      var dark = root.getAttribute("data-theme")
        ? root.getAttribute("data-theme") === "dark"
        : !window.matchMedia("(prefers-color-scheme: light)").matches;
      var next = dark ? "light" : "dark";
      root.setAttribute("data-theme", next);
      storeTheme(next);
      b.setAttribute("aria-label", next === "dark" ? "Switch to light theme" : "Switch to dark theme");
    });
  });

  /* ---------- reveal on scroll ---------- */
  var revealEls = document.querySelectorAll(".reveal");
  if (reduceMotion || !("IntersectionObserver" in window)) {
    revealEls.forEach(function (el) { el.classList.add("in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    revealEls.forEach(function (el) { io.observe(el); });
  }

  /* ---------- tabs (workflows) ---------- */
  document.querySelectorAll("[role=tablist]").forEach(function (list) {
    var tabs = Array.prototype.slice.call(list.querySelectorAll("[role=tab]"));
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { select(t, false); });
      t.addEventListener("keydown", function (e) {
        var k = e.key, n = null;
        if (k === "ArrowRight") n = tabs[(i + 1) % tabs.length];
        if (k === "ArrowLeft") n = tabs[(i - 1 + tabs.length) % tabs.length];
        if (k === "Home") n = tabs[0];
        if (k === "End") n = tabs[tabs.length - 1];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
  });

  /* ---------- copy buttons ---------- */
  document.querySelectorAll("[data-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var text = document.getElementById(b.getAttribute("data-copy")).textContent.trim();
      var done = function () { var o = b.textContent; b.textContent = "Copied"; setTimeout(function () { b.textContent = o; }, 1400); };
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, function () {});
    });
  });

  /* ---------- floating notes in the hero (decorative) ---------- */
  var notes = document.querySelector(".notes");
  if (notes && !reduceMotion) {
    var glyphs = ["♩", "♪", "♫", "♬"];
    for (var i = 0; i < 14; i++) {
      var s = document.createElement("span");
      s.textContent = glyphs[i % glyphs.length];
      s.style.left = (Math.random() * 100) + "%";
      s.style.animationDelay = (Math.random() * 9) + "s";
      s.style.animationDuration = (7 + Math.random() * 6) + "s";
      s.style.fontSize = (14 + Math.random() * 18) + "px";
      notes.appendChild(s);
    }
  }

  /* ---------- tilt the praise quotes a little ---------- */
  document.querySelectorAll(".quote").forEach(function (q, i) {
    q.style.setProperty("--r", ((i * 37) % 5 - 2) * 0.6 + "deg");
  });

  /* ================= toy drum machine ================= */
  var machine = document.getElementById("toy");
  if (!machine) return;

  var ctx = null, master = null, noiseBuf = null;
  function audio() {
    if (!ctx) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      ctx = new AC();
      master = ctx.createDynamicsCompressor();
      master.threshold.value = -10; master.ratio.value = 6;
      var out = ctx.createGain(); out.gain.value = 0.8;
      master.connect(out); out.connect(ctx.destination);
      noiseBuf = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate);
      var d = noiseBuf.getChannelData(0);
      for (var i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    }
    if (ctx.state === "suspended") ctx.resume();
    return ctx;
  }
  function env(g, t, a, peak, decay) {
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(peak, t + a);
    g.gain.exponentialRampToValueAtTime(0.0001, t + a + decay);
  }
  function noise(t, dur, type, freq, q, peak, decay) {
    var src = ctx.createBufferSource(); src.buffer = noiseBuf;
    var f = ctx.createBiquadFilter(); f.type = type; f.frequency.value = freq; f.Q.value = q;
    var g = ctx.createGain(); env(g, t, 0.001, peak, decay);
    src.connect(f); f.connect(g); g.connect(master);
    src.start(t, Math.random() * 0.5, dur);
  }
  function tone(t, f0, f1, sweep, peak, decay, type) {
    var o = ctx.createOscillator(); o.type = type || "sine";
    o.frequency.setValueAtTime(f0, t); o.frequency.exponentialRampToValueAtTime(f1, t + sweep);
    var g = ctx.createGain(); env(g, t, 0.002, peak, decay);
    o.connect(g); g.connect(master); o.start(t); o.stop(t + decay + 0.05);
  }
  var voices = {
    kick: function (t, v) { tone(t, 150, 48, 0.12, 1.0 * v, 0.42); noise(t, 0.02, "highpass", 2500, 0.7, 0.25 * v, 0.015); },
    snare: function (t, v) { tone(t, 330, 180, 0.05, 0.35 * v, 0.12, "triangle"); noise(t, 0.3, "bandpass", 1900, 0.8, 0.7 * v, 0.17); },
    ghost: function (t, v) { noise(t, 0.1, "bandpass", 2000, 0.9, 0.16 * v, 0.06); },
    hat: function (t, v) { noise(t, 0.06, "highpass", 7500, 0.8, 0.28 * v, 0.04); },
    open: function (t, v) { noise(t, 0.5, "highpass", 6800, 0.6, 0.26 * v, 0.32); },
    crash: function (t, v) { noise(t, 2, "highpass", 4200, 0.5, 0.45 * v, 1.4); noise(t, 1.5, "bandpass", 9000, 0.6, 0.2 * v, 1.0); },
    tomHi: function (t, v) { tone(t, 260, 170, 0.18, 0.75 * v, 0.3); },
    tomMid: function (t, v) { tone(t, 190, 125, 0.2, 0.8 * v, 0.34); },
    tomLo: function (t, v) { tone(t, 135, 85, 0.24, 0.9 * v, 0.42); }
  };
  function hit(name, t, v) { if (voices[name]) voices[name](t, v == null ? 1 : v); }

  // 16 steps per bar. Each entry: step -> [[voice, velocity], ...]
  function pat(spec) {
    var bar = []; for (var i = 0; i < 16; i++) bar.push([]);
    Object.keys(spec).forEach(function (v) { spec[v].forEach(function (s) { bar[s[0]].push([v, s[1]]); }); });
    return bar;
  }
  var E = function (steps, vel) { return steps.map(function (s) { return [s, vel]; }); };
  var P = {
    intro: pat({ hat: E([0, 4, 8, 12], 0.8), kick: E([0], 0.9), snare: E([12], 0.5) }),
    verse: pat({ hat: E([0, 2, 4, 6, 8, 10, 12, 14], 0.7), kick: E([0, 7, 8], 0.95), snare: E([4, 12], 1), ghost: E([10, 15], 0.6) }),
    chorus: pat({ hat: E([0, 2, 4, 6, 8, 10, 12], 0.85), open: E([14], 0.8), kick: E([0, 3, 8, 10], 1), snare: E([4, 12], 1.1) }),
    bridge: pat({ hat: E([0, 4, 8, 12], 0.6), kick: E([0, 10], 0.9), snare: E([8], 1), tomLo: E([14], 0.6) }),
    smallFill: pat({ snare: E([12, 13, 14], 0.9), tomHi: E([15], 0.9) }),
    bigFill: pat({ snare: E([0, 2, 4, 5], 0.9), tomHi: E([6, 7, 8], 0.95), tomMid: E([9, 10, 11], 1), tomLo: E([12, 13, 14, 15], 1), kick: E([0, 8], 0.8) }),
    ending: pat({ crash: E([0], 1), kick: E([0], 1.1) })
  };
  var SONG = [
    { id: "intro", label: "Intro", bars: 1, color: "#8B93A1", pat: "intro" },
    { id: "a", label: "A", bars: 4, color: "#5AA7EE", pat: "verse" },
    { id: "chorus", label: "Chorus", bars: 4, color: "#F2A33A", pat: "chorus", crash: true },
    { id: "bridge", label: "Bridge", bars: 2, color: "#B28BE8", pat: "bridge", crash: true },
    { id: "chorus2", label: "Chorus", bars: 4, color: "#F2A33A", pat: "chorus", crash: true },
    { id: "outro", label: "Outro", bars: 1, color: "#8B93A1", pat: "ending", ending: true }
  ];

  var el = {
    section: machine.querySelector("[data-lcd=section]"),
    bar: machine.querySelector("[data-lcd=bar]"),
    bpm: machine.querySelector("[data-lcd=bpm]"),
    msg: machine.querySelector("[data-lcd=msg]"),
    leds: machine.querySelectorAll(".led"),
    strip: machine.querySelector(".song-strip"),
    play: machine.querySelector("[data-act=play]"),
    next: machine.querySelector("[data-act=next]"),
    mode: machine.querySelector("[data-act=mode]"),
    live: document.getElementById("toy-live")
  };
  var bpm = 104;
  var state = {
    playing: false, follow: "chart", sec: 0, bar: 0, step: 0, nextTime: 0,
    fill: null, wantNext: false, ending: false, timer: null, stopAt: 0
  };

  // strip
  SONG.forEach(function (s, i) {
    var b = document.createElement("button");
    b.type = "button";
    b.style.setProperty("--c", s.color);
    b.setAttribute("aria-label", "Jump to " + s.label + " (" + s.bars + (s.bars > 1 ? " bars)" : " bar)"));
    b.innerHTML = '<div class="bar"><i></i></div><span>' + s.label + "</span>";
    b.style.flexGrow = Math.max(1, s.bars);
    onPress(b, function () { jump(i); });
    el.strip.appendChild(b);
  });
  var stripBtns = el.strip.querySelectorAll("button");

  function say(text) { el.msg.textContent = text; }
  function announce(text) { if (el.live) el.live.textContent = text; }
  function setStage(color) { root.style.setProperty("--stage", color); }
  function render() {
    var s = SONG[state.sec];
    el.section.textContent = s.label.toUpperCase();
    var overrun = state.bar + 1 > s.bars;
    el.bar.textContent = "BAR " + (state.bar + 1) + (overrun ? " of " : "/") + s.bars;
    stripBtns.forEach(function (b, i) {
      b.classList.toggle("on", i === state.sec);
      var fillPct = i < state.sec ? 100 : i === state.sec ? Math.min(100, ((state.bar + state.step / 16) / SONG[i].bars) * 100) : 0;
      b.querySelector("i").style.width = (state.playing ? fillPct : 0) + "%";
    });
    var lastBar = state.bar + 1 >= s.bars;
    el.next.classList.toggle("armed", state.playing && lastBar && state.follow === "me" && !s.ending);
    el.next.textContent = state.sec < SONG.length - 1 ? "NEXT ▸ " + SONG[state.sec + 1].label.toUpperCase() : "NEXT";
    setStage(state.playing ? s.color : "#F2A33A");
  }
  function setLed(beat) {
    el.leds.forEach(function (l, i) { l.classList.toggle("on", i === beat); });
  }

  // scheduler: 25 ms timer, 100 ms look-ahead
  var stepDur = function () { return 60 / bpm / 4; };
  function tick() {
    while (state.nextTime < ctx.currentTime + 0.1) {
      scheduleStep(state.nextTime);
      advance();
      if (!state.playing) return;
    }
  }
  function scheduleStep(t) {
    var s = SONG[state.sec];
    var step = state.step;
    var events = P[s.pat][step];
    if (state.fill && step >= state.fill.from) events = P[state.fill.pat][step];
    if (step === 0 && state.bar === 0 && s.crash) hit("crash", t, 0.9);
    events.forEach(function (e) { hit(e[0], t, e[1]); });
    if (step % 4 === 0) {
      var beat = step / 4, barNow = state.bar, secNow = state.sec;
      var delay = Math.max(0, (t - ctx.currentTime) * 1000);
      setTimeout(function () {
        if (!state.playing) return;
        setLed(beat);
        if (beat === 0) { state.viewBar = barNow; }
        render();
      }, delay);
    }
  }
  function advance() {
    state.nextTime += stepDur();
    state.step++;
    if (state.step < 16) return;
    state.step = 0;
    state.fill = null;
    var s = SONG[state.sec];
    if (s.ending) { stop("The end. Take a bow."); return; }
    state.bar++;
    var done = state.bar >= s.bars;
    if (state.wantNext || (state.follow === "chart" && done)) {
      state.wantNext = false;
      state.sec = Math.min(state.sec + 1, SONG.length - 1);
      state.bar = 0;
      var ns = SONG[state.sec];
      say(ns.ending ? "Ending…" : (state.follow === "me" ? "Follow me: tap NEXT when ready" : "Follow chart: hands off"));
      announce("Now playing " + ns.label);
    } else if (done && state.follow === "me") {
      say("waiting for NEXT…");
    }
    // auto fill in the last bar of a section (Follow chart), like the app's end fills
    var cur = SONG[state.sec];
    if (state.follow === "chart" && !cur.ending && state.bar === cur.bars - 1 && cur.bars > 1 && !state.fill) {
      state.fill = { pat: "smallFill", from: 12 };
    }
  }
  function start() {
    if (!audio()) { say("No Web Audio in this browser"); return; }
    if (state.playing) return;
    state.playing = true; state.bar = 0; state.step = 0; state.fill = null; state.wantNext = false;
    if (SONG[state.sec].ending) state.sec = 0;
    state.nextTime = ctx.currentTime + 0.06;
    el.play.textContent = "■ STOP";
    el.play.classList.add("red"); el.play.classList.remove("orange");
    say(state.follow === "me" ? "Follow me: sections wait for NEXT" : "Follow chart: hands off");
    announce("Playing " + SONG[state.sec].label);
    render();
    state.timer = setInterval(tick, 25);
    tick();
  }
  function stop(msg) {
    state.playing = false;
    clearInterval(state.timer);
    el.play.textContent = "▶ PLAY";
    el.play.classList.remove("red"); el.play.classList.add("orange");
    setLed(-1);
    say(msg || "Stopped. Tap a section to start there.");
    announce("Stopped");
    if (SONG[state.sec].ending) state.sec = 0;
    state.bar = 0; state.step = 0;
    render();
  }
  function fill(big) {
    if (!state.playing) {
      // stopped: just play the fill once so the pad still makes noise
      if (!audio()) return;
      var t = ctx.currentTime + 0.02, p = P[big ? "bigFill" : "smallFill"];
      for (var i = big ? 0 : 12; i < 16; i++) p[i].forEach(function (e) { hit(e[0], t + (i - (big ? 0 : 12)) * stepDur(), e[1]); });
      return;
    }
    if (big) {
      // a whole bar: starts on the next bar line
      state.pendingBig = true;
      state.fill = state.step === 0 ? { pat: "bigFill", from: 0 } : { pat: "bigFill", from: Math.max(state.step + 1, 4) };
      say("BIG FILL → lands on the next downbeat");
    } else {
      // same tick position inside the fill so it lands on the next downbeat
      var from = Math.max(12, state.step + 1);
      if (from > 15) { say("Too late for this bar: next bar"); from = 12; }
      state.fill = { pat: "smallFill", from: from };
      say("FILL → lands on the next downbeat");
    }
  }
  function next() {
    if (!state.playing) { jump(Math.min(state.sec + 1, SONG.length - 2)); return; }
    if (SONG[state.sec].ending) return;
    state.wantNext = true;
    if (!state.fill) state.fill = { pat: "smallFill", from: Math.max(12, state.step + 1) };
    say("NEXT → " + SONG[state.sec + 1].label + " on the bar line");
  }
  function end() {
    if (!state.playing) return;
    state.sec = SONG.length - 2; state.wantNext = true;
    state.fill = { pat: "bigFill", from: Math.max(4, state.step + 1) };
    say("END → ending on the next bar line");
  }
  function jump(i) {
    if (state.playing) {
      state.sec = Math.max(0, i - 1); state.bar = 0;
      if (i === 0) { state.sec = 0; } else { state.wantNext = true; }
      say("Jump queued to the next bar line");
    } else {
      state.sec = i; state.bar = 0;
      say("Start point: " + SONG[i].label + ". Tap PLAY.");
      render();
    }
  }
  function toggleMode() {
    state.follow = state.follow === "chart" ? "me" : "chart";
    el.mode.textContent = state.follow === "chart" ? "FOLLOW CHART" : "FOLLOW ME";
    el.mode.setAttribute("aria-pressed", state.follow === "me" ? "true" : "false");
    say(state.follow === "me" ? "Follow me: sections wait for NEXT" : "Follow chart: plays the whole form");
  }
  function flash(btn) { btn.classList.add("hit"); setTimeout(function () { btn.classList.remove("hit"); }, 120); }

  // fire on touch-down like the app; keyboard (click with detail 0) still works
  function onPress(btn, fn) {
    btn.addEventListener("pointerdown", function (e) { if (e.button > 0) return; e.preventDefault(); flash(btn); fn(); });
    btn.addEventListener("click", function (e) { if (e.detail === 0) { flash(btn); fn(); } });
  }
  onPress(el.play, function () { if (state.playing) stop(); else start(); });
  onPress(el.next, next);
  onPress(el.mode, toggleMode);
  onPress(machine.querySelector("[data-act=end]"), end);
  onPress(machine.querySelector("[data-act=fill]"), function () { fill(false); });
  onPress(machine.querySelector("[data-act=big]"), function () { fill(true); });
  onPress(machine.querySelector("[data-act=tempo-down]"), function () { bpm = Math.max(60, bpm - 4); el.bpm.textContent = bpm; });
  onPress(machine.querySelector("[data-act=tempo-up]"), function () { bpm = Math.min(180, bpm + 4); el.bpm.textContent = bpm; });
  machine.querySelectorAll("[data-hit]").forEach(function (b) {
    onPress(b, function () { if (audio()) hit(b.getAttribute("data-hit"), ctx.currentTime + 0.005, 1); });
  });
  document.addEventListener("visibilitychange", function () { if (document.hidden && state.playing) stop(); });
  render();
  say("Tap PLAY (sound on). Then FILL, NEXT, END.");
})();
