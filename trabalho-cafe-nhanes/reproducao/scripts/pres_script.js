(() => {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const root = document.documentElement;
  const reduce = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
  const nf = (v, d = 0) => v.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d }).replace('-', '−');
  const sign = (v, d) => (v > 0 ? '+' : '') + nf(v, d);

  try { const t = localStorage.getItem('cafe-theme'); if (t === 'light' || t === 'dark') root.dataset.theme = t; } catch (e) {}

  const stage = $('#stage');
  const slides = $$('.slide', stage);
  const N = slides.length;
  let cur = -1;
  const hooks = {};
  const comps = [];
  const reg = (el, c) => { c.slide = el.closest('.slide'); comps.push(c); return c; };

  /* ---------- fit 1920×1080 stage to the window ---------- */
  const fit = () => stage.style.setProperty('--s', Math.min(innerWidth / 1920, innerHeight / 1080));
  addEventListener('resize', fit); fit();

  /* ---------- tween ---------- */
  const easeOut = t => 1 - Math.pow(1 - t, 3);
  const easeIO = t => (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  function tween({ dur = 1200, delay = 0, ease = easeOut, update, done }) {
    let start = null, raf = 0, dead = false;
    if (reduce) { update(1); if (done) done(); return { cancel() {} }; }
    update(0);
    const step = ts => {
      if (dead) return;
      if (start === null) start = ts + delay;
      const t = Math.min(1, Math.max(0, (ts - start) / dur));
      update(ease(t));
      if (t < 1) raf = requestAnimationFrame(step); else if (done) done();
    };
    raf = requestAnimationFrame(step);
    return { cancel() { dead = true; cancelAnimationFrame(raf); } };
  }

  /* ---------- dados reais: NHANES 2021–2023, 18 a 29 anos (n = __N__) ----------
     cada registro: xícaras/dia (240 mL, média de 2 dias), dificuldade de concentração (0–3),
     problemas de sono (0–3), horas de sono em dias úteis, dias com café (0–2) */
  const RAW = '__RAW__';
  const DATA = RAW.split(';').map(r => r.split(',').map(Number));
  const NS = DATA.length;
  const A1 = __A1__, B1 = __B1__;   // modelo 1: concentração ~ xícaras
  const A2 = __A2__, B2 = __B2__;   // modelo 2: concentração ~ problemas de sono
  const mean = (arr, i) => arr.length ? arr.reduce((s, d) => s + d[i], 0) / arr.length : NaN;
  const share = (arr, f) => arr.length ? arr.filter(f).length / arr.length * 100 : NaN;
  const GX = [0, 1, 2, 3, 4, 5].map(k => DATA.filter(d => Math.min(5, Math.floor(d[0] + .5)) === k));
  const GB = [0, 1, 2, 3].map(k => DATA.filter(d => d[2] === k));
  const clsOf = x => (x === 0 ? 0 : x <= 1 ? 1 : x <= 2 ? 2 : 3);
  const GC = [0, 1, 2, 3].map(k => DATA.filter(d => clsOf(d[0]) === k));
  const GD = [0, 1, 2].map(k => DATA.filter(d => d[4] === k));
  const IMP = GD.map(g => share(g, d => d[2] >= 1));
  const DRINK = DATA.filter(d => d[4] > 0), NODRINK = DATA.filter(d => d[4] === 0);
  const CA = [share(DRINK, d => d[1] >= 1), share(NODRINK, d => d[1] >= 1)];
  const CB = GB.map(g => share(g, d => d[1] >= 1));

  /* ---------- helpers ---------- */
  function topRound(x, y, w, h, r) {
    if (h <= 0.5) return `M${x},${y}h${w}`;
    r = Math.min(r, h, w / 2);
    return `M${x},${y + h}V${y + r}Q${x},${y} ${x + r},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y + h}Z`;
  }
  function wavePath(x0, y, width, amp, wl) {
    const n = Math.ceil((width + wl) / (wl / 2)) + 2;
    let d = `M${x0.toFixed(1)},${y.toFixed(1)} q${(wl / 4).toFixed(2)},${(-amp).toFixed(2)} ${(wl / 2).toFixed(2)},0`;
    for (let k = 1; k < n; k++) d += ` t${(wl / 2).toFixed(2)},0`;
    return d;
  }
  let LQ = 0;
  function liquidSVG(clipD, x, yTop, width, bottom, kind = 'coffee', i = 0, o = {}) {
    const id = 'jlq' + (++LQ), amp = o.amp ?? Math.max(2.5, Math.min(6, width * .05)), wl = o.wl ?? Math.max(36, width * .8), dur = o.dur ?? 2.8;
    const line = wavePath(x - wl, yTop, width, amp, wl);
    const body = line + ` V${(bottom + amp + 30).toFixed(1)} H${(x - wl).toFixed(1)} Z`;
    const dy = bottom - yTop + amp * 2 + 4;
    const nb = o.bubbles ?? (bottom - yTop > 70 ? 2 : 0);
    let bub = '';
    for (let k = 0; k < nb; k++) bub += `<circle class="bub" cx="${(x + width * (.3 + .4 * k)).toFixed(1)}" cy="${(bottom - 8).toFixed(1)}" r="${2.5 + k}" style="--bd:${(3 + k * .8).toFixed(1)}s;--bdl:${(k * 1.1).toFixed(1)}s;--rise:${Math.max(20, (bottom - yTop) * .8).toFixed(0)}"/>`;
    return `<clipPath id="${id}"><path d="${clipD}"/></clipPath><g clip-path="url(#${id})"><g class="lq-rise" style="--dy:${dy.toFixed(0)};--i:${i}"><path class="lq-wave lq-${kind}" style="--wl:${wl.toFixed(1)};--wd:${dur}s" d="${body}"/><path class="lq-wave foam" style="--wl:${wl.toFixed(1)};--wd:${dur}s" d="${line}"/>${bub}</g></g>`;
  }
  const rrect = (x, y, w, h, r) => `M${x + r},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y + h - r}Q${x + w},${y + h} ${x + w - r},${y + h}H${x + r}Q${x},${y + h} ${x},${y + h - r}V${y + r}Q${x},${y} ${x + r},${y}Z`;
  const miniCup = (x, y, w, h) => `M${x.toFixed(1)},${y.toFixed(1)}H${(x + w).toFixed(1)}L${(x + w * .9).toFixed(1)},${(y + h * .8).toFixed(1)}Q${(x + w * .88).toFixed(1)},${(y + h).toFixed(1)} ${(x + w * .72).toFixed(1)},${(y + h).toFixed(1)}H${(x + w * .28).toFixed(1)}Q${(x + w * .12).toFixed(1)},${(y + h).toFixed(1)} ${(x + w * .1).toFixed(1)},${(y + h * .8).toFixed(1)}Z`;
  const miniHandle = (x, y, w, h) => `M${(x + w * .95).toFixed(1)},${(y + h * .18).toFixed(1)}c${(w * .38).toFixed(1)},0 ${(w * .38).toFixed(1)},${(h * .52).toFixed(1)} ${(-w * .05).toFixed(1)},${(h * .54).toFixed(1)}`;

  function mulberry32(a) { return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

  /* ---------- counters ---------- */
  $$('[data-count]').forEach(el => {
    const to = parseFloat(el.dataset.count), dec = +(el.dataset.dec || 0), pre = el.dataset.pre || '', suf = el.dataset.suf || '';
    const delay = +(el.dataset.delay || 380);
    const set = v => { el.textContent = pre + nf(v, dec) + suf; };
    let tw;
    reg(el, { enter() { if (tw) tw.cancel(); tw = tween({ dur: 1500, delay, update: t => set(to * t) }); }, final() { if (tw) tw.cancel(); set(to); } });
  });

  /* ---------- donut / ring ---------- */
  const ARC = 'M50,8a42,42 0 1,1 0,84a42,42 0 1,1 0,-84';
  function donut(el, segs, opt = {}) {
    if (!el) return;
    const total = opt.total || segs.reduce((a, s) => a + s.v, 0);
    const sw = opt.sw || 11, gap = segs.length > 1 ? (opt.gap ?? .7) : 0;
    let acc = 0;
    const parts = segs.map(s => { const p = s.v / total * 100, o = { p, start: acc, cls: s.cls }; acc += p; return o; });
    const cupTop = el.closest('.donut-wrap.cup') ? `<circle class="rim" cx="50" cy="50" r="48.6"/><circle cx="50" cy="50" r="${(42 - sw / 2 - .8).toFixed(1)}" fill="url(#g-surface)"/><g class="swirl" style="opacity:.2"><circle cx="50" cy="50" r="23" fill="none" stroke="#f2dcc0" stroke-width="1.2" stroke-dasharray="14 6 4 6"/><path d="M50,74 C36,66 34,56 44,55 C47,55 49.3,57 50,59 C50.7,57 53,55 56,55 C66,56 64,66 50,74Z" fill="#f2dcc0"/></g>` : '';
    el.innerHTML = `<svg viewBox="0 0 100 100" aria-hidden="true">${cupTop}<path class="dn-track" d="${ARC}" pathLength="100" style="stroke-width:${sw}"/>` +
      parts.map(s => `<path class="dn-seg ${s.cls}" d="${ARC}" pathLength="100" style="stroke-width:${sw}"/>`).join('') + '</svg>';
    const paths = $$('.dn-seg', el);
    const render = t => paths.forEach((p, i) => {
      const s = parts[i], len = Math.max(0, s.p * t - gap);
      p.style.strokeDasharray = `${len} ${100 - len}`;
      p.style.strokeDashoffset = `${-(s.start * t + gap / 2)}`;
      p.style.opacity = len < .3 ? 0 : 1;
    });
    let tw;
    reg(el, { enter() { if (tw) tw.cancel(); tw = tween({ dur: 1700, delay: opt.delay ?? 450, ease: easeIO, update: render }); }, final() { if (tw) tw.cancel(); render(1); } });
    render(1);
  }
  donut($('#donut-gen'), [{ v: __NF__, cls: 's-a' }, { v: __NM__, cls: 's-b' }]);
  donut($('#ring-daily'), [{ v: __PA__, cls: 's-a round' }], { total: 100 });
  donut($('#ring-r2'), [{ v: Math.max(__R2_1__, .8), cls: 's-conc round' }], { total: 100, sw: 12, delay: 900 });

  /* ---------- vertical bar charts ---------- */
  function vbars(el, o) {
    if (!el) return;
    const W = o.w, H = o.h, m = Object.assign({ t: 70, r: 10, b: 84, l: 70 }, o.m || {});
    const iw = W - m.l - m.r, ih = H - m.t - m.b, n = o.values.length, band = iw / n;
    const bw = Math.min(band * (o.bw || .62), o.maxBw || 150);
    const y = v => m.t + ih - v / o.max * ih;
    let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${o.aria}">`;
    (o.ticks || []).forEach(t => { s += `<line class="g-line" x1="${m.l}" x2="${W - m.r}" y1="${y(t)}" y2="${y(t)}"/><text class="g-tick" x="${m.l - 14}" y="${y(t) + 6}" text-anchor="end">${o.tickFmt ? o.tickFmt(t) : t}</text>`; });
    o.values.forEach((v, i) => {
      const x = m.l + band * i + (band - bw) / 2, yy = y(v), h = m.t + ih - yy, cls = o.cls ? o.cls[i] : '';
      const kind = o.kinds ? o.kinds[i] : 'coffee', rr = Math.min(o.rad ?? 16, bw / 3);
      s += `<path class="tube" d="${rrect(x, m.t, bw, ih, rr)}"/>`;
      if (v > 0) s += liquidSVG(rrect(x + 3, m.t + 3, bw - 6, ih - 6, Math.max(2, rr - 3)), x + 3, Math.min(yy, m.t + ih - 4), bw - 6, m.t + ih - 3, kind, i);
      if (o.cupAxis) {
        const cw = 13, cg = 5, tot = 5 * cw + 4 * cg, sx = x + bw / 2 - tot / 2;
        for (let c = 0; c < 5; c++) {
          const cx0 = sx + c * (cw + cg), cy0 = m.t + ih + 14;
          s += `<path d="${miniCup(cx0, cy0, cw, 12)}" class="${c < i ? 'lq-coffee' : ''}" style="${c < i ? '' : 'fill:none;'}stroke:var(--tube-line);stroke-width:1.4"/><path d="${miniHandle(cx0, cy0, cw, 12)}" style="fill:none;stroke:var(--tube-line);stroke-width:1.4"/>`;
        }
      }
      if (o.top) s += `<text class="bar-val" style="--i:${i}" x="${x + bw / 2}" y="${yy - (o.sub ? 40 : 14)}" text-anchor="middle">${o.top[i]}</text>`;
      if (o.sub) s += `<text class="bar-sub" style="--i:${i}" x="${x + bw / 2}" y="${yy - 13}" text-anchor="middle">${o.sub[i]}</text>`;
      if (o.labels[i] !== '') s += `<text class="${o.lblCls || 'bar-lbl'}" x="${x + bw / 2}" y="${m.t + ih + (o.cupAxis ? 60 : 38)}" text-anchor="middle">${o.labels[i]}</text>`;
      if (o.lbl2) s += `<text class="bar-lbl2" x="${x + bw / 2}" y="${m.t + ih + 64}" text-anchor="middle">${o.lbl2[i]}</text>`;
    });
    s += `<line class="g-axis" x1="${m.l}" x2="${W - m.r}" y1="${m.t + ih}" y2="${m.t + ih}"/>`;
    if (o.extra) s += o.extra({ xc: i => m.l + band * i + band / 2, bw, y, m, ih, W, H });
    el.innerHTML = s + '</svg>';
  }
  const pctS = v => nf(v, 1) + '%';
  const cupsF = __CUPS__;
  vbars($('#bar-cups'), {
    w: 1080, h: 600, max: 350, ticks: [0, 100, 200, 300], aria: 'Gráfico de barras: xícaras de café por dia',
    values: cupsF, labels: ['0', 'até 1', '1 a 2', '2 a 3', 'mais de 3'], top: cupsF.map(String), sub: cupsF.map(v => pctS(v / NS * 100)),
    cls: ['', 'hi', 'hi', 'hi', 'hi'], kinds: ['grey', 'coffee', 'coffee', 'coffee', 'coffee'], m: { b: 96 }, bw: .58,
    extra: g => `<text class="ax-title" x="${(g.W + 70) / 2}" y="${g.H - 10}" text-anchor="middle">xícaras de 240 mL por dia (média dos 2 dias)</text>`
  });
  vbars($('#bar-imp'), {
    w: 760, h: 470, max: 100, ticks: [0, 25, 50, 75, 100], tickFmt: t => t + '%', aria: 'Percentual com problemas de sono por dias com café',
    values: IMP, labels: ['nenhum dia', '1 dia', '2 dias'], top: IMP.map(pctS), lbl2: GD.map(g => 'n=' + g.length),
    cls: IMP.map(() => 'sl hi'), kinds: ['night', 'night', 'night'], m: { t: 46, l: 76, b: 90 }, bw: .5
  });
  const HOURS = __HOURS__;
  vbars($('#bar-hour'), {
    w: 1100, h: 520, max: 60, ticks: [0, 20, 40, 60], aria: 'Bebidas de café por hora do dia',
    values: HOURS, labels: HOURS.map((_, h) => (h % 3 === 0 ? h + 'h' : '')), lblCls: 'g-tick',
    cls: HOURS.map((_, h) => (h >= 5 && h < 12 ? 'cf' : h >= 12 && h < 18 ? 'am' : 'sn')),
    m: { t: 40, l: 64, b: 70, r: 6 }, bw: .74, rad: 6,
    extra: g => {
      const lg = [['manhã', 'var(--accent)'], ['tarde', 'var(--tarde)'], ['noite', 'var(--sleep)']];
      return lg.map((l, i) => `<g transform="translate(${g.W - 420 + i * 140} 12)"><rect width="18" height="18" rx="5" style="fill:${l[1]}"/><text class="ax-title" x="28" y="16">${l[0]}</text></g>`).join('') +
        `<text class="ax-title" x="${(g.W + 64) / 2}" y="${g.H - 8}" text-anchor="middle">hora em que a bebida começou</text>`;
    }
  });
  vbars($('#bar-cond-a'), {
    w: 640, h: 470, max: 100, ticks: [0, 25, 50, 75, 100], tickFmt: t => t + '%', aria: 'Dificuldade de concentração segundo o consumo de café',
    values: CA, labels: ['tomou café', 'não tomou'], top: CA.map(pctS), lbl2: ['n=' + DRINK.length, 'n=' + NODRINK.length],
    cls: ['cf', 'gr'], m: { t: 50, l: 76, b: 90 }, bw: .5
  });
  vbars($('#bar-cond-b'), {
    w: 960, h: 470, max: 100, ticks: [0, 25, 50, 75, 100], tickFmt: t => t + '%', aria: 'Dificuldade de concentração segundo a frequência de problemas de sono',
    values: CB, labels: ['nenhum dia', 'vários dias', 'mais da metade', 'quase todos'], top: CB.map(pctS), lbl2: GB.map(g => 'n=' + g.length),
    cls: ['sn', 'sn', 'sn', 'sn'], m: { t: 50, l: 76, b: 90 }, bw: .52
  });
  const pBin = __P__;
  const bin = [0, 1, 2, 3, 4, 5].map(k => { const c = [1, 5, 10, 10, 5, 1][k]; return c * Math.pow(pBin, k) * Math.pow(1 - pBin, 5 - k) * 100; });
  vbars($('#bar-binom'), {
    w: 820, h: 470, max: 40, ticks: [0, 10, 20, 30, 40], tickFmt: t => t + '%', aria: 'Distribuição binomial n=5',
    values: bin, labels: ['k=0', 'k=1', 'k=2', 'k=3', 'k=4', 'k=5'],
    top: bin.map(v => nf(v, 2) + '%'), cls: ['', 'hi', 'hi', 'hi', 'hi', 'hi'], kinds: ['grey', 'coffee', 'coffee', 'coffee', 'coffee', 'coffee'], cupAxis: true, m: { t: 120, l: 76, b: 84 }, bw: .6,
    extra: g => {
      const x1 = g.xc(1) - g.bw / 2, x2 = g.xc(5) + g.bw / 2, yb = g.y(Math.max(...bin)) - 64;
      return `<g class="bracket"><path d="M${x1},${yb + 16}V${yb}H${x2}V${yb + 16}"/><text x="${(x1 + x2) / 2}" y="${yb - 16}" text-anchor="middle">P(X ≥ 1) = __PBIN1__</text></g>`;
    }
  });

  /* ---------- scatter (Gráfico 6) ---------- */
  (function scatter() {
    const el = $('#scatter'); if (!el) return;
    const W = 1000, H = 610, m = { t: 24, r: 24, b: 84, l: 80 }, iw = W - m.l - m.r, ih = H - m.t - m.b;
    const X = v => m.l + (v + .35) / 8.7 * iw, Y = v => m.t + ih - (v + .55) / 4.1 * ih;
    let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Dispersão entre xícaras por dia e dificuldade de concentração, com reta ajustada">`;
    for (let v = 0; v <= 3; v++) s += `<line class="g-line" x1="${m.l}" x2="${W - m.r}" y1="${Y(v)}" y2="${Y(v)}"/><text class="g-tick" x="${m.l - 14}" y="${Y(v) + 6}" text-anchor="end">${v}</text>`;
    for (let v = 0; v <= 8; v++) s += `<text class="g-tick" x="${X(v)}" y="${m.t + ih + 34}" text-anchor="middle">${v}</text>`;
    const rnd = mulberry32(11);
    const pts = DATA.map(d => [d[0] + (d[0] === 0 ? (rnd() - .5) * .34 : 0), d[1] + (rnd() - .5) * .46]).sort((a, b) => a[0] - b[0]);
    s += '<g>' + pts.map((p, i) => `<g transform="translate(${X(p[0]).toFixed(1)} ${Y(p[1]).toFixed(1)}) rotate(${(rnd() * 180 - 90).toFixed(0)})"><g class="bean-g" style="--i:${i}"><ellipse class="bean-b" rx="7.4" ry="5.1"/><path class="bean-c" d="M-5.6,.7C-2,-2.6 2,2.6 5.6,-.7"/></g></g>`).join('') + '</g>';
    s += `<path class="reg-line" pathLength="1" d="M${X(0)},${Y(A1)}L${X(8)},${Y(A1 + 8 * B1)}"/>`;
    const lx = X(4.6), ly = Y(3.05);
    s += `<g class="reg-lab"><rect x="${lx}" y="${ly - 34}" width="318" height="50" rx="12"/><line x1="${lx + 18}" x2="${lx + 56}" y1="${ly - 9}" y2="${ly - 9}" style="stroke:var(--text);stroke-width:5;stroke-linecap:round"/><text x="${lx + 70}" y="${ly - 2}">Ŷ = ${nf(A1, 3)} − ${nf(Math.abs(B1), 3)}X</text></g>`;
    s += `<text class="ax-title" x="${m.l + iw / 2}" y="${H - 12}" text-anchor="middle">xícaras de café por dia</text>`;
    s += `<text class="ax-title" transform="translate(22 ${m.t + ih / 2}) rotate(-90)" text-anchor="middle">dificuldade de concentração (0 a 3)</text>`;
    el.innerHTML = s + '</svg>';
  })();

  /* ---------- line chart: means by coffee class ---------- */
  (function lineMeans() {
    const el = $('#line-means'); if (!el) return;
    const W = 820, H = 330, m = { t: 20, r: 190, b: 64, l: 56 }, iw = W - m.l - m.r, ih = H - m.t - m.b;
    const X = k => m.l + k / 3 * iw, Y = v => m.t + ih - v / 1.2 * ih;
    const MCc = GC.map(g => mean(g, 1)), MBc = GC.map(g => mean(g, 2));
    const lab = ['0', 'até 1', '1 a 2', '> 2'];
    let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Médias de dificuldade de concentração e de problemas de sono por consumo de café">`;
    [0, .4, .8, 1.2].forEach(v => { s += `<line class="g-line" x1="${m.l}" x2="${m.l + iw}" y1="${Y(v)}" y2="${Y(v)}"/><text class="g-tick sm" x="${m.l - 12}" y="${Y(v) + 5}" text-anchor="end">${nf(v, 1)}</text>`; });
    for (let k = 0; k <= 3; k++) s += `<text class="g-tick sm" x="${X(k)}" y="${m.t + ih + 28}" text-anchor="middle">${lab[k]}</text><text class="bar-lbl2" x="${X(k)}" y="${m.t + ih + 50}" text-anchor="middle">n=${GC[k].length}</text>`;
    const path = arr => arr.map((v, k) => (k ? 'L' : 'M') + X(k).toFixed(1) + ',' + Y(v).toFixed(1)).join('');
    s += `<path class="ln conc" pathLength="1" d="${path(MCc)}"/><path class="ln sleep" pathLength="1" d="${path(MBc)}"/>`;
    MCc.forEach((v, k) => { s += `<circle class="ln-pt conc" style="--i:${k}" cx="${X(k)}" cy="${Y(v)}" r="8"/>`; });
    MBc.forEach((v, k) => { s += `<circle class="ln-pt sleep" style="--i:${k}" cx="${X(k)}" cy="${Y(v)}" r="8"/>`; });
    const yc = Y(MCc[3]), ys = Y(MBc[3]), sep = Math.abs(yc - ys) < 26 ? 15 : 0;
    s += `<text class="ln-lbl conc" x="${X(3) + 18}" y="${yc + 6 - (yc <= ys ? sep : -sep)}">concentração ${nf(MCc[3], 2)}</text>`;
    s += `<text class="ln-lbl sleep" x="${X(3) + 18}" y="${ys + 6 + (yc <= ys ? sep : -sep)}">sono ${nf(MBc[3], 2)}</text>`;
    s += `<text class="ln-lbl conc" x="${X(0) + 14}" y="${Y(MCc[0]) + 30}">${nf(MCc[0], 2)}</text>`;
    s += `<text class="ln-lbl sleep" x="${X(0) + 14}" y="${Y(MBc[0]) - 16}">${nf(MBc[0], 2)}</text>`;
    el.innerHTML = s + '</svg>';
  })();

  /* ---------- box plots ---------- */
  $$('.boxplot').forEach(el => {
    const d = el.dataset, v = k => parseFloat(d[k]);
    const [a, b] = d.dom.split(',').map(Number), ticks = d.ticks.split(',').map(Number);
    const W = 760, H = 112, m = { l: 20, r: 20 }, iw = W - m.l - m.r, X = t => m.l + (t - a) / (b - a) * iw, cy = 40, bh = 46;
    let s = `<svg viewBox="0 0 ${W} ${H}" class="bp ${d.kind}" aria-hidden="true">`;
    ticks.forEach(t => { s += `<line class="g-line" x1="${X(t)}" x2="${X(t)}" y1="6" y2="${cy + bh / 2 + 6}"/><text class="g-tick sm" x="${X(t)}" y="${H - 6}" text-anchor="middle">${nf(t)}</text>`; });
    s += `<g class="bp-wh"><line x1="${X(v('min'))}" x2="${X(v('max'))}" y1="${cy}" y2="${cy}"/><line x1="${X(v('min'))}" x2="${X(v('min'))}" y1="${cy - 14}" y2="${cy + 14}"/><line x1="${X(v('max'))}" x2="${X(v('max'))}" y1="${cy - 14}" y2="${cy + 14}"/></g>`;
    s += `<rect class="bp-box" x="${X(v('q1'))}" y="${cy - bh / 2}" width="${Math.max(2, X(v('q3')) - X(v('q1')))}" height="${bh}" rx="10"/>`;
    s += `<line class="bp-med" x1="${X(v('med'))}" x2="${X(v('med'))}" y1="${cy - bh / 2 - 5}" y2="${cy + bh / 2 + 5}"/>`;
    s += `<path class="bp-mean" d="M${X(v('mean'))},${cy - 12}l12,12l-12,12l-12,-12z"/>`;
    el.innerHTML = s + '</svg>';
  });

  /* ---------- horizontal band bars ---------- */
  $$('.hbars').forEach(el => {
    const v = el.dataset.v.split(',').map(Number), max = Math.max(...v), labs = (el.dataset.labels || '').split('|');
    el.innerHTML = v.map((x, i) => `<div class="hb${x === max ? ' top' : ''}" style="--i:${i};--w:${x / max * 100}%"><span class="hb-l">${labs[i] || ''}</span><span class="hb-t"><i></i></span><span class="hb-v"><b>${x}</b><small>${nf(x / NS * 100, 1)}%</small></span></div>`).join('');
  });

  /* ---------- r meter ---------- */
  $$('.rmeter').forEach(el => {
    const rs = el.dataset.r.split(',').map(Number), cls = (el.dataset.cls || 'conc').split(','), lab = (el.dataset.labels || '').split('|');
    const lv = (el.dataset.lv || '').split(',').map(Number), al = (el.dataset.al || '').split(',');
    el.innerHTML = `<div class="rm-track"></div>` +
      rs.map((r, i) => `<div class="rm-mk ${cls[i]}${lv[i] === 1 ? ' lv1' : ''}${al[i] === 'r' ? ' al-r' : al[i] === 'l' ? ' al-l' : ''}"><span class="rm-pin"></span><span class="rm-val">${lab[i] ? `<em>${lab[i]}</em>` : ''}<span class="rv-n">${sign(r, 3)}</span></span></div>`).join('') +
      `<div class="rm-ticks"><span>−1</span><span>−0,5</span><span>0</span><span>+0,5</span><span>+1</span></div>` +
      `<div class="rm-zones"><span>forte</span><span>moderada</span><span>fraca</span><span>fraca</span><span>moderada</span><span>forte</span></div>`;
    const mks = $$('.rm-mk', el);
    const render = t => mks.forEach((mk, i) => { const r = rs[i] * t; mk.style.left = ((r + 1) / 2 * 100) + '%'; mk.querySelector('.rv-n').textContent = sign(r, 3); });
    let tw;
    reg(el, { enter() { if (tw) tw.cancel(); tw = tween({ dur: 1600, delay: 700, ease: easeIO, update: render }); }, final() { if (tw) tw.cancel(); render(1); } });
    render(1);
  });

  /* ---------- waffle (1 ponto = 1 participante) ---------- */
  function waffle(el, total, a, b, c) {
    if (!el) return;
    const cols = 25, gap = 30, rows = Math.ceil(total / cols);
    let s = `<svg viewBox="0 0 ${cols * gap} ${rows * gap}" aria-hidden="true">`;
    for (let k = 0; k < total; k++) {
      const x = (k % cols) * gap + 4, y = Math.floor(k / cols) * gap + 6;
      s += `<g class="mc" style="--i:${k}"><path class="mc-l" style="--i:${k}" data-a="${k < a ? 1 : 0}" data-b="${k < b ? 1 : 0}" data-c="${k < c ? 1 : 0}" d="${miniCup(x + 1.6, y + 2.2, 15.8, 15.2)}"/><path class="mc-o" d="${miniCup(x, y, 19, 18)} ${miniHandle(x, y, 19, 18)}"/></g>`;
    }
    el.innerHTML = s + '</svg>';
  }
  const wp = $('#w-prob');
  const EV = [['Evento A · tomou café', __NA__], ['Evento B · problemas de sono', __NB__], ['Evento C · dificuldade de concentração', __NC__]];
  waffle(wp, NS, EV[0][1], EV[1][1], EV[2][1]);
  let probMode = 0, probReady = true, probTimer = 0;
  const wfCard = $('#wf-card');
  function applyProb() {
    if (!wp) return;
    ['mA', 'mB', 'mC'].forEach((c, i) => wp.classList.toggle(c, probReady && probMode === i));
    wfCard.classList.toggle('isB', probMode === 1);
    wfCard.classList.toggle('isC', probMode === 2);
    $('#wf-label').textContent = EV[probMode][0];
    $('#wf-count').textContent = `${EV[probMode][1]} / ${NS}`;
    $$('#probabilidade .ev').forEach(b => b.classList.toggle('on', +b.dataset.ev === probMode));
  }
  if (wp) reg(wp, {
    enter() { clearTimeout(probTimer); probReady = false; applyProb(); probTimer = setTimeout(() => { probReady = true; applyProb(); }, reduce ? 0 : 950); },
    final() { clearTimeout(probTimer); probReady = true; applyProb(); }
  });
  hooks.probabilidade = { step(n) { probMode = Math.min(n, 2); applyProb(); } };
  $$('#probabilidade .ev').forEach(b => b.addEventListener('click', e => {
    const s = b.closest('.slide'); setFrags(s, +b.dataset.ev); if (e.detail) b.blur();
  }));
  applyProb();

  /* ---------- regression simulator (dois modelos) ---------- */
  (function simulator() {
    const el = $('#sim-chart'); if (!el) return;
    const MODELS = [
      { a: A1, b: B1, xs: [0, 1, 2, 3, 4, 5], groups: GX, xl: 'Xícaras por dia (X)', axis: 'xícaras por dia · ○ média observada no grupo', unit: k => (k === 1 ? 'xícara' : 'xícaras') },
      { a: A2, b: B2, xs: [0, 1, 2, 3], groups: GB, xl: 'Problemas de sono (X)', axis: 'problemas de sono: 0 nenhum dia · 1 vários · 2 mais da metade · 3 quase todos · ○ média observada', unit: () => 'no nível' }
    ];
    const W = 900, H = 360, m = { t: 18, r: 26, b: 56, l: 64 }, iw = W - m.l - m.r, ih = H - m.t - m.b;
    const Y = v => m.t + ih - v / 2 * ih;
    const btnWrap = $('#sim-xs'), modelBtns = $$('#sim-models button');
    let mi = 0, curX = 0, tw, X, mk, gv, gh, lbl, btns = [];
    const build = (fast = false) => {
      const M = MODELS[mi], xmax = M.xs[M.xs.length - 1];
      X = v => m.l + (v + .3) / (xmax + .6) * iw;
      let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Reta de regressão com estimativa para o valor de X escolhido">`;
      [0, .5, 1, 1.5, 2].forEach(v => { s += `<line class="g-line" x1="${m.l}" x2="${W - m.r}" y1="${Y(v)}" y2="${Y(v)}"/><text class="g-tick sm" x="${m.l - 12}" y="${Y(v) + 5}" text-anchor="end">${nf(v, 1)}</text>`; });
      M.xs.forEach(k => { s += `<text class="g-tick sm" x="${X(k)}" y="${m.t + ih + 30}" text-anchor="middle">${k}</text>`; });
      s += `<path class="reg-line" pathLength="1" d="M${X(0)},${Y(M.a)}L${X(xmax)},${Y(M.a + xmax * M.b)}" style="stroke-width:4${fast ? ';animation-delay:.05s;animation-duration:.6s' : ''}"/>`;
      M.groups.forEach((g, k) => { if (g.length) s += `<circle class="sim-mean" cx="${X(k)}" cy="${Y(mean(g, 1))}" r="${g.length < 10 ? 6 : 9}"/>`; });
      s += `<line class="sim-guide" id="sg-v"/><line class="sim-guide" id="sg-h"/>`;
      s += `<g class="sim-mk" id="sim-mk"><circle class="halo" r="24"/><circle r="12"/></g><text class="sim-lbl" id="sim-lbl" text-anchor="middle"></text>`;
      s += `<text class="ax-title" x="${m.l + iw / 2}" y="${H - 6}" text-anchor="middle" style="font-size:17px">${M.axis}</text>`;
      el.innerHTML = s + '</svg>';
      mk = $('#sim-mk'); gv = $('#sg-v'); gh = $('#sg-h'); lbl = $('#sim-lbl');
      btnWrap.innerHTML = M.xs.map(k => `<button type="button" data-x="${k}">${k}</button>`).join('');
      btns = $$('button', btnWrap);
      btns.forEach(b => b.addEventListener('click', e => { setX(+b.dataset.x, true); if (e.detail) b.blur(); }));
      $('#sim-xl').textContent = M.xl;
      modelBtns.forEach(b => b.classList.toggle('on', +b.dataset.m === mi));
    };
    const draw = x => {
      const M = MODELS[mi], yv = M.a + M.b * x, px = X(x), py = Y(yv);
      mk.setAttribute('transform', `translate(${px} ${py})`);
      gv.setAttribute('x1', px); gv.setAttribute('x2', px); gv.setAttribute('y1', py); gv.setAttribute('y2', m.t + ih);
      gh.setAttribute('x1', m.l); gh.setAttribute('x2', px); gh.setAttribute('y1', py); gh.setAttribute('y2', py);
      lbl.setAttribute('x', px); lbl.setAttribute('y', py - 34); lbl.textContent = nf(yv, 2);
    };
    const setX = (x, animate) => {
      const M = MODELS[mi], from = curX; curX = x;
      btns.forEach(b => b.classList.toggle('on', +b.dataset.x === x));
      const yv = M.a + M.b * x, g = M.groups[x];
      $('#sim-y').textContent = nf(yv, 3);
      $('#sim-eq').innerHTML = `Ŷ = ${nf(M.a, 4)} ${M.b < 0 ? '−' : '+'} ${nf(Math.abs(M.b), 4)} × <b>${x}</b>`;
      $('#sim-note').innerHTML = `Média observada para X = ${x}: <b>${nf(mean(g, 1), 2)}</b> (${g.length} registros).` +
        (g.length < 10 ? ' <span class="w">Grupo pequeno: a média oscila muito.</span>' : '');
      if (tw) tw.cancel();
      if (!animate) { draw(x); return; }
      tw = tween({ dur: 700, ease: easeIO, update: t => draw(from + (x - from) * t) });
    };
    const setModel = (k, x0 = 0, fast = false) => { if (tw) tw.cancel(); mi = k; curX = x0; build(fast); setX(x0, false); };
    modelBtns.forEach(b => b.addEventListener('click', e => { setModel(+b.dataset.m, 0, true); setX(2, true); if (e.detail) b.blur(); }));
    let t0 = 0;
    reg(el, {
      enter() { clearTimeout(t0); setModel(0); t0 = setTimeout(() => setX(2, true), reduce ? 0 : 1100); },
      final() { clearTimeout(t0); setModel(0, 2); }
    });
    setModel(0, 2);
  })();

  /* ---------- clone cup + logos into the finale ---------- */
  const cupSrc = $('#cup-src svg'), cupDst = $('#cup-dst');
  if (cupSrc && cupDst) cupDst.appendChild(cupSrc.cloneNode(true));
  const logoSrc = $('#capa .cover-logos'), logoDst = $('#fin-logos');
  if (logoSrc && logoDst) logoDst.innerHTML = logoSrc.innerHTML;

  /* ---------- per-slide footer + table row stagger ---------- */
  slides.forEach((s, i) => {
    if (s.dataset.chrome === 'off') return;
    const f = document.createElement('footer');
    f.className = 'sfoot';
    const lvl = (i + 1) / N, ctop = 6 + 17.5 * (1 - lvl), cupD = 'M4 6h21l-2 15.6a4 4 0 0 1-4 3.4H10a4 4 0 0 1-4-3.4z';
    f.innerHTML = `<svg class="sf-cup" viewBox="0 0 34 30" aria-hidden="true"><defs><clipPath id="sfc${i}"><path d="${cupD}"/></clipPath></defs><g clip-path="url(#sfc${i})"><rect class="sf-liq" x="0" y="${ctop.toFixed(1)}" width="30" height="30" style="--dy:${(30 - ctop).toFixed(1)}"/></g><path class="sf-out" d="${cupD}"/><path class="sf-out" d="M25 9h2.4a3.4 3.4 0 0 1 0 6.8H24"/></svg><span>Consumo de café e produtividade acadêmica · dados reais NHANES 2021–2023</span><span class="sf-sec">${s.dataset.section}</span><span class="sf-step"></span><span class="sf-num">${String(i + 1).padStart(2, '0')} / ${N}</span>`;
    s.appendChild(f);
  });
  $$('.tbl tbody').forEach(tb => Array.from(tb.children).forEach((tr, i) => tr.style.setProperty('--r', i)));

  /* ---------- fragments + navigation ---------- */
  const frags = s => $$('.frag', s);
  const fragN = s => frags(s).filter(f => f.classList.contains('on')).length;
  function setFrags(s, n) {
    frags(s).forEach((f, i) => f.classList.toggle('on', i < n));
    const h = hooks[s.id]; if (h && h.step) h.step(n);
    updateUI();
  }
  function go(i, opt = {}) {
    i = Math.max(0, Math.min(N - 1, i));
    if (i === cur && !opt.force) return;
    const prev = cur, back = prev >= 0 && i < prev;
    slides.forEach((s, k) => {
      s.classList.toggle('active', k === i);
      s.classList.toggle('past', k < i);
      s.inert = k !== i;
      s.setAttribute('aria-hidden', k === i ? 'false' : 'true');
    });
    cur = i;
    const s = slides[i], fr = frags(s), n = back ? fr.length : 0;
    fr.forEach((f, k) => f.classList.toggle('on', k < n));
    comps.forEach(c => { if (c.slide === s) c.enter(); });
    const h = hooks[s.id]; if (h && h.step) h.step(n);
    updateUI();
    try { history.replaceState(null, '', '#/' + (i + 1)); } catch (e) {}
  }
  const next = () => { const s = slides[cur]; const n = fragN(s); if (n < frags(s).length) setFrags(s, n + 1); else go(cur + 1); };
  const prev = () => { const s = slides[cur]; const n = fragN(s); if (n > 0) setFrags(s, n - 1); else go(cur - 1); };

  /* ---------- menu, notes, help ---------- */
  const menu = $('#menu'), scrim = $('#scrim'), notes = $('#notes'), help = $('#help');
  const menuList = $('#menu-list');
  let lastSec = '';
  slides.forEach((s, i) => {
    if (s.dataset.section !== lastSec) { const li = document.createElement('li'); li.className = 'msec'; li.textContent = s.dataset.section; menuList.appendChild(li); lastSec = s.dataset.section; }
    const li = document.createElement('li'), b = document.createElement('button');
    b.type = 'button'; b.className = 'mi';
    b.innerHTML = `<span class="mn">${String(i + 1).padStart(2, '0')}</span><span>${s.dataset.title}</span>`;
    b.addEventListener('click', () => { closePanels(); go(i); });
    li.appendChild(b); menuList.appendChild(li);
  });
  const menuBtns = $$('.mi', menuList);
  function closePanels() { menu.classList.remove('open'); help.classList.remove('open'); scrim.classList.remove('on'); }
  function toggleMenu() { const o = !menu.classList.contains('open'); closePanels(); menu.classList.toggle('open', o); scrim.classList.toggle('on', o); if (o && menuBtns[cur]) menuBtns[cur].scrollIntoView({ block: 'center' }); }
  function toggleHelp() { const o = !help.classList.contains('open'); closePanels(); help.classList.toggle('open', o); scrim.classList.toggle('on', o); }
  function toggleNotes() { notes.classList.toggle('open'); $('#b-notes').classList.toggle('on', notes.classList.contains('open')); }
  function toggleTheme() { const t = root.dataset.theme === 'light' ? 'dark' : 'light'; root.dataset.theme = t; try { localStorage.setItem('cafe-theme', t); } catch (e) {} }
  function toggleFS() { try { if (!document.fullscreenElement) { const p = root.requestFullscreen && root.requestFullscreen(); if (p && p.catch) p.catch(() => {}); } else if (document.exitFullscreen) document.exitFullscreen(); } catch (e) {} }
  scrim.addEventListener('click', closePanels);
  help.addEventListener('click', e => { if (e.target === help) closePanels(); });
  $('#menu-x').addEventListener('click', closePanels);

  function updateUI() {
    const s = slides[cur]; if (!s) return;
    $('#progress i').style.setProperty('--p', ((cur + 1) / N * 100) + '%');
    $('#cnt').textContent = `${cur + 1} / ${N}`;
    stage.dataset.mood = s.dataset.mood || 'warm';
    menuBtns.forEach((b, k) => b.classList.toggle('cur', k === cur));
    const nt = s.querySelector('.notes');
    $('#notes-title').textContent = `Notas · ${cur + 1}. ${s.dataset.title}`;
    $('#notes-body').innerHTML = nt ? nt.innerHTML : '<p>Sem notas para este slide.</p>';
    const fr = frags(s).length, st = s.querySelector('.sf-step');
    if (st) st.textContent = fr ? `passo ${fragN(s) + 1}/${fr + 1}` : '';
  }

  /* ---------- input ---------- */
  const ctl = (id, fn) => $(id).addEventListener('click', e => { fn(); if (e.detail) e.currentTarget.blur(); });
  ctl('#b-prev', prev); ctl('#b-next', next); ctl('#b-menu', toggleMenu); ctl('#b-notes', toggleNotes);
  ctl('#b-theme', toggleTheme); ctl('#b-fs', toggleFS); ctl('#b-help', toggleHelp);
  $$('[data-goto]').forEach(b => b.addEventListener('click', e => { const i = slides.findIndex(s => s.id === b.dataset.goto); if (i >= 0) go(i); if (e.detail) b.blur(); }));

  addEventListener('keydown', e => {
    if (e.defaultPrevented || e.altKey || e.ctrlKey || e.metaKey) return;
    const t = e.target, tag = t && t.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || (t && t.isContentEditable)) return;
    const k = e.key;
    if ((k === ' ' || k === 'Enter') && (tag === 'BUTTON' || tag === 'A')) return;
    switch (k) {
      case 'ArrowRight': case 'ArrowDown': case 'PageDown': case 'Enter': e.preventDefault(); next(); break;
      case ' ': e.preventDefault(); e.shiftKey ? prev() : next(); break;
      case 'ArrowLeft': case 'ArrowUp': case 'PageUp': case 'Backspace': e.preventDefault(); prev(); break;
      case 'Home': e.preventDefault(); go(0); break;
      case 'End': e.preventDefault(); go(N - 1); break;
      case 'f': case 'F': toggleFS(); break;
      case 'm': case 'M': toggleMenu(); break;
      case 'n': case 'N': toggleNotes(); break;
      case 't': case 'T': toggleTheme(); break;
      case '?': case 'h': case 'H': toggleHelp(); break;
      case 'Escape': closePanels(); if (notes.classList.contains('open')) toggleNotes(); break;
    }
  });

  let tx = null, ty = 0;
  const vp = $('#viewport');
  vp.addEventListener('touchstart', e => { if (e.touches.length === 1) { tx = e.touches[0].clientX; ty = e.touches[0].clientY; } }, { passive: true });
  vp.addEventListener('touchend', e => {
    if (tx === null) return;
    const dx = e.changedTouches[0].clientX - tx, dy = e.changedTouches[0].clientY - ty; tx = null;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.3) (dx < 0 ? next : prev)();
  }, { passive: true });

  let idleT = 0;
  const wake = () => { document.body.classList.add('ui-on'); document.body.classList.remove('idle'); clearTimeout(idleT); idleT = setTimeout(() => { document.body.classList.remove('ui-on'); document.body.classList.add('idle'); }, 2800); };
  addEventListener('mousemove', wake, { passive: true });
  addEventListener('touchstart', wake, { passive: true });
  wake();

  addEventListener('hashchange', () => { const h = parseInt((location.hash.match(/^#\/(\d+)/) || [])[1], 10); if (h && h - 1 !== cur) go(h - 1); });
  addEventListener('beforeprint', () => comps.forEach(c => c.final()));
  addEventListener('afterprint', () => go(cur, { force: true }));

  const h0 = parseInt((location.hash.match(/^#\/(\d+)/) || [])[1], 10);
  go(h0 ? h0 - 1 : 0, { force: true });
})();
