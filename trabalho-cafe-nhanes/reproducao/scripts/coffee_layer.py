"""Camada visual "café em movimento" da apresentação.
Gera CSS, gradientes e a marcação dos slides redesenhados (coador, xícaras, relógio do café,
cardápio, comanda e números de seção que se enchem de café). Usada por build_html.py."""
import math, re

COFFEE_CSS = r"""
/* =========================================================
   CAFÉ EM MOVIMENTO — líquidos, xícaras, vapor, grãos
   ========================================================= */
:root{--liq-top:#dd9a55;--liq-bot:#8f4e28;--liq-foam:#f6dcb4;--night-top:#a3b7ff;--night-bot:#4357b8;--amber-top:#f6c06e;--amber-bot:#c27f2a;--roast-top:#a8642f;--roast-bot:#5a2f15;--grey-top:#8b7a6b;--grey-bot:#5a4a3e;--tube-fill:rgba(255,235,212,.035);--tube-line:rgba(255,226,196,.24);--espresso:#2c180c;--paper:#f6ead8;--paper-ink:#2b1a10}
:root[data-theme="light"]{--liq-top:#b9692a;--liq-bot:#6e3714;--liq-foam:#efd2a8;--night-top:#6d86e0;--night-bot:#2f43a0;--amber-top:#d6952f;--amber-bot:#8a560c;--roast-top:#7a4320;--roast-bot:#3f1f0b;--grey-top:#b5a594;--grey-bot:#8c7b6a;--tube-fill:rgba(92,54,26,.04);--tube-line:rgba(92,54,26,.26);--paper:#fffaf1}
.lq-coffee{fill:url(#lg-coffee)} .lq-night{fill:url(#lg-night)} .lq-amber{fill:url(#lg-amber)} .lq-roast{fill:url(#lg-roast)} .lq-grey{fill:url(#lg-grey)}
.lq-wave{animation:waveX var(--wd,2.8s) linear infinite}
@keyframes waveX{to{transform:translateX(calc(-1px * var(--wl,48)))}}
.slide.active .lq-rise{animation:lqRise 1.7s var(--ease) both;animation-delay:calc(var(--i,0)*120ms + 380ms)}
@keyframes lqRise{from{transform:translateY(calc(1px * var(--dy,300)))}}
.foam{fill:none;stroke:var(--liq-foam);stroke-width:3;opacity:.8}
.tube{fill:var(--tube-fill);stroke:var(--tube-line);stroke-width:2}
.bub{fill:var(--liq-foam);opacity:0}
.slide.active .bub{animation:bubUp var(--bd,3.6s) ease-in infinite;animation-delay:var(--bdl,0s)}
@keyframes bubUp{0%{opacity:0;transform:translateY(0)}20%{opacity:.55}80%{opacity:.35}100%{opacity:0;transform:translateY(calc(-1px * var(--rise,60)))}}
.steam-s path{fill:none;stroke:var(--steam);stroke-width:5;stroke-linecap:round;opacity:0;animation:steamS 4.4s ease-in-out infinite}
.steam-s path:nth-child(2){animation-delay:1.45s} .steam-s path:nth-child(3){animation-delay:2.9s}
@keyframes steamS{0%{opacity:0;transform:translateY(14px)}30%{opacity:.6}75%{opacity:.2}100%{opacity:0;transform:translateY(-46px)}}
.drop{fill:var(--liq-top);opacity:0}
.slide.active .drop{animation:dripFall var(--dd,2.2s) cubic-bezier(.55,0,1,.6) infinite;animation-delay:var(--ddl,0s)}
@keyframes dripFall{0%{opacity:0;transform:translateY(0) scale(.5)}12%{opacity:1;transform:translateY(0) scale(1)}85%{opacity:1}100%{opacity:0;transform:translateY(calc(1px * var(--fall,120))) scale(.9)}}
.stream{fill:none;stroke:var(--liq-top);stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1}
.slide.active .stream{animation:pourIn var(--pd,2.6s) var(--ease-io) both var(--pdl,.2s)}
@keyframes pourIn{0%{stroke-dashoffset:1}45%{stroke-dashoffset:0}100%{stroke-dashoffset:-1}}
.stream.loop{stroke-dasharray:.08 .06;stroke-dashoffset:0}
.slide.active .stream.loop{animation:flowDash 1.1s linear infinite}
@keyframes flowDash{to{stroke-dashoffset:-.28}}

/* ambiente: vapor e marcas de xícara */
.amb-steam{position:absolute;bottom:-60px;width:180px;height:560px;opacity:0;animation:ambSteam 13s ease-in-out infinite;animation-delay:var(--del,0s)}
.amb-steam path{fill:none;stroke:var(--steam);stroke-width:16;stroke-linecap:round;filter:blur(7px)}
@keyframes ambSteam{0%{opacity:0;transform:translateY(90px) scaleX(.9)}30%{opacity:.32}70%{opacity:.16}100%{opacity:0;transform:translateY(-300px) scaleX(1.18)}}
.ring-stain{position:absolute;width:var(--rs,240px);height:var(--rs,240px);opacity:.075;animation:spin 140s linear infinite}
.ring-stain circle{fill:none;stroke:var(--accent);stroke-width:3.4;stroke-dasharray:150 12 38 7 26 5 60 9}
.ring-stain circle+circle{stroke-width:1.2;stroke-dasharray:none;opacity:.6}
@keyframes spin{to{transform:rotate(360deg)}}

/* rodapé: xícara de progresso */
.sfoot::before{display:none}
.sf-cup{width:34px;height:30px;flex:none;overflow:visible}
.sf-out{fill:none;stroke:var(--accent);stroke-width:1.8;stroke-linejoin:round;stroke-linecap:round}
.sf-liq{fill:url(#lg-coffee)}
.slide.active .sf-liq{animation:lqRise 1.4s var(--ease) both .55s}

/* donut = xícara vista de cima */
.donut-wrap.cup .donut-center b{color:#fcefdf;text-shadow:0 4px 18px rgba(0,0,0,.45)}
.donut-wrap.cup .donut-center span{color:#ecd3b2}
.swirl{transform-box:fill-box;transform-origin:center;animation:spin 46s linear infinite}
.rim{fill:none;stroke:var(--cup-hi);stroke-width:1.3;opacity:.55}

/* divisores: número que se enche de café */
.div-svg{position:absolute;right:30px;top:50%;width:1000px;height:780px;transform:translateY(-50%);overflow:visible;pointer-events:none}
.dn-o{fill:none;stroke:var(--accent-line);stroke-width:2.2}
.dn-t{font-family:var(--font-display);font-weight:700;font-size:640px;letter-spacing:-.05em}

/* barras de líquido e pictogramas */
.mc{transform-box:fill-box;transform-origin:center}
.slide.active .mc{animation:pop .42s var(--ease) both;animation-delay:calc(var(--i)*1.1ms + 240ms)}
.mc-o{fill:none;stroke:var(--tube-line);stroke-width:1.5;stroke-linejoin:round}
.mc-l{transform-box:fill-box;transform-origin:50% 100%;transform:scaleY(0);fill:var(--mcf,var(--liq-top));transition:transform .55s var(--ease);transition-delay:calc(var(--i)*1.3ms)}
.waffle.mA .mc-l[data-a="1"]{transform:scaleY(1);--mcf:var(--liq-top)}
.waffle.mB .mc-l[data-b="1"]{transform:scaleY(1);--mcf:var(--night-top)}
.waffle.mC .mc-l[data-c="1"]{transform:scaleY(1);--mcf:var(--amber-top)}
.waffle.mA .mc-o,.waffle.mB .mc-o,.waffle.mC .mc-o{stroke:var(--tube-line)}
.bean-g{transform-box:fill-box;transform-origin:center}
.slide.active .bean-g{animation:pop .5s var(--ease) both;animation-delay:calc(var(--i)*2.2ms + 480ms)}
.bean-b{fill:var(--liq-top);opacity:.8}
.bean-c{fill:none;stroke:var(--espresso);stroke-width:1.5;stroke-linecap:round;opacity:.7}

/* barras horizontais = café escorrendo */
.hb-t i{opacity:1 !important;background:linear-gradient(90deg,var(--hb-bot,var(--liq-bot)),var(--hb-top,var(--liq-top)));position:relative;overflow:hidden}
.hb-t i::after{content:"";position:absolute;inset:0;background:linear-gradient(115deg,transparent 38%,rgba(255,244,228,.2) 50%,transparent 62%) 0 0/64px 100% repeat-x;animation:flow 1.7s linear infinite}
@keyframes flow{to{background-position:64px 0}}
.hbars[data-kind="conc"]{--hb-top:var(--amber-top);--hb-bot:var(--amber-bot)}
.hbars[data-kind="sleep"]{--hb-top:var(--night-top);--hb-bot:var(--night-bot)}
.hb:not(.top) .hb-t i{filter:saturate(.75) brightness(.86)}

/* coador (população) */
.strain-grid{display:grid;grid-template-columns:560px 1fr;gap:56px;align-items:center;margin-top:20px;flex:1;min-height:0}
.coador{width:100%;height:100%;max-height:720px;overflow:visible}
.cone{fill:var(--tube-fill);stroke:var(--tube-line);stroke-width:3}
.cone-rib{stroke:var(--tube-line);stroke-width:1.5;opacity:.6}
.grounds{fill:url(#lg-roast)}
.cd-num{fill:#fcefdf;font:600 64px var(--font-display);text-anchor:middle}
.cd-lab{fill:#ecd3b2;font:600 17px var(--font-body);letter-spacing:.12em;text-transform:uppercase;text-anchor:middle}
.strain{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px}
.strain li{display:grid;grid-template-columns:44px 1fr auto;column-gap:18px;align-items:baseline;padding:10px 0 12px;border-bottom:1px dashed var(--line-2)}
.strain li:last-child{border-bottom:0}
.st-n{font:600 19px var(--font-mono);color:var(--accent);opacity:.7}
.st-t{font-size:23px;color:var(--muted);line-height:1.35}
.st-v{font:600 42px/1 var(--font-display);color:var(--text)}
.strain li.last .st-v{color:var(--accent);font-size:56px}
.st-bar{grid-column:2/-1;height:12px;border-radius:99px;background:var(--card-2);margin-top:12px;overflow:hidden}
.st-bar i{display:block;height:100%;width:var(--w);border-radius:99px;background:linear-gradient(90deg,var(--liq-bot),var(--liq-top));transform-origin:left;position:relative}
.slide.active .st-bar i{animation:growX 1.1s var(--ease) both;animation-delay:calc(var(--i)*160ms + 600ms)}
.strain-notes{display:flex;flex-direction:column;gap:10px;margin-top:16px}
.sn{display:flex;gap:14px;align-items:flex-start;font-size:20px;line-height:1.42;color:var(--muted)}
.sn .ic{color:var(--accent);font-size:26px;margin-top:2px}
.sn b{color:var(--text)}

/* xícaras grandes (horário, condicional) */
.cups-svg{width:100%;height:100%;overflow:visible;display:block}
.cupb{fill:var(--tube-fill);stroke:var(--tube-line);stroke-width:3}
.cuph{fill:none;stroke:var(--tube-line);stroke-width:7;stroke-linecap:round}
.cups-saucer{fill:var(--card-2);stroke:var(--tube-line);stroke-width:2}
.cup-glow{opacity:.5}
.cv{fill:var(--text);font:600 92px/1 var(--font-display)}
.cv.sm{font-size:64px}
.cp{fill:var(--muted);font:600 30px var(--font-mono)}
.cp.sm{font-size:24px}
.cl{fill:var(--text);font:650 32px var(--font-body)}
.cl.sm{font-size:22px}
.cs{fill:var(--dim);font:500 18px var(--font-mono);letter-spacing:.04em}
.lvl-line{stroke:var(--text);stroke-width:2.5;stroke-dasharray:10 10;opacity:.6}
.lvl-lab{fill:var(--text);font:italic 500 26px var(--font-display)}
.cic{fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.cond-cups{display:grid;grid-template-columns:.78fr 1.22fr;gap:40px;margin-top:22px;flex:1;min-height:0}
.cond-col{display:flex;flex-direction:column;min-height:0}
.cond-col h3{margin:0;font:600 34px/1.15 var(--font-display);display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.cond-col .chart{margin-top:8px}
.cond-math{font:500 19px var(--font-mono);color:var(--muted);margin-top:10px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
.cond-math b{color:var(--text)}
.cond-sep{width:1px;background:linear-gradient(transparent,var(--line-2),transparent)}

/* relógio do café */
.clock-grid{display:grid;grid-template-columns:780px 1fr;gap:56px;align-items:center;margin-top:10px;flex:1;min-height:0}
.clock{width:100%;height:100%;max-height:800px;overflow:visible}
.ck-face{fill:var(--tube-fill);stroke:var(--tube-line);stroke-width:2}
.ck-tick{stroke:var(--tube-line);stroke-width:2}
.ck-num{fill:var(--dim);font:500 21px var(--font-mono);text-anchor:middle;dominant-baseline:middle}
.ck-bar{stroke-width:20;stroke-linecap:round;fill:none;stroke-dasharray:1;stroke-dashoffset:0}
.ck-bar.m{stroke:var(--liq-top)} .ck-bar.t{stroke:var(--roast-top)} .ck-bar.n{stroke:var(--night-top)}
.slide.active .ck-bar{animation:draw .7s var(--ease) both;animation-delay:calc(var(--h)*85ms + 500ms)}
.ck-win{fill:none;stroke:var(--sleep);stroke-width:26;opacity:.28}
.ck-sleep{fill:none;stroke:var(--night-bot);stroke-width:26;opacity:.55}
.ck-arc-lab{fill:var(--sleep);font:650 18px var(--font-body);letter-spacing:.06em}
.ck-hand{stroke:var(--text);stroke-width:4;stroke-linecap:round;transform-origin:380px 380px;transform:rotate(var(--rot))}
.slide.active .ck-hand{animation:handSweep 3.2s var(--ease-io) both .4s}
@keyframes handSweep{from{transform:rotate(0deg)}to{transform:rotate(var(--rot))}}
.ck-center{fill:url(#g-surface)}
.ck-c-num{fill:#fcefdf;font:600 54px var(--font-display);text-anchor:middle}
.ck-c-lab{fill:#ecd3b2;font:600 15px var(--font-body);letter-spacing:.14em;text-transform:uppercase;text-anchor:middle}
.clock-stats{display:flex;flex-direction:column}
.cks{display:grid;grid-template-columns:auto 1fr;gap:6px 26px;align-items:baseline;padding:22px 0;border-bottom:1px solid var(--line)}
.cks:last-child{border-bottom:0}
.cks b{font:600 76px/1 var(--font-display);color:var(--accent)}
.cks.sleep b{color:var(--sleep)}
.cks span{font-size:22px;line-height:1.45;color:var(--muted)}
.cks span b{font:inherit;color:var(--text);font-weight:650}
.ck-legend{display:flex;gap:22px;font-size:18px;color:var(--muted);margin-top:8px;flex-wrap:wrap}
.ck-legend i{display:inline-block;width:14px;height:14px;border-radius:50%;margin-right:8px;vertical-align:-1px}

/* cardápio de resultados */
.menu-board{position:relative;margin-top:30px;padding:40px 54px 34px;border-radius:30px;background:radial-gradient(120% 140% at 0% 0%,var(--accent-soft),transparent 60%),var(--card);border:1px solid var(--accent-line);box-shadow:var(--shadow)}
.menu-board::before{content:"";position:absolute;inset:12px;border-radius:22px;border:1px dashed var(--accent-line);pointer-events:none}
.mb-head{display:flex;align-items:baseline;justify-content:space-between;gap:20px;padding-bottom:16px;margin-bottom:10px;border-bottom:2px solid var(--accent-line)}
.mb-head span{font:italic 500 40px var(--font-display);color:var(--accent)}
.mb-head small{font:600 15px var(--font-body);letter-spacing:.16em;text-transform:uppercase;color:var(--dim)}
.mb-list{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;column-gap:64px}
.mb-list li{display:grid;grid-template-columns:40px auto 1fr auto;align-items:baseline;gap:14px;padding:20px 0 18px;border-bottom:1px solid var(--line)}
.mb-list li:nth-last-child(-n+2){border-bottom:0}
.mb-ic{color:var(--accent);font-size:28px;align-self:center}
.mb-ic.sleep{color:var(--sleep)} .mb-ic.conc{color:var(--conc)}
.mb-t{font-size:23px;line-height:1.35;color:var(--text);max-width:440px}
.mb-t small{display:block;font-size:18px;color:var(--muted);margin-top:4px}
.mb-dots{border-bottom:3px dotted var(--line-2);transform:translateY(-6px);min-width:24px}
.mb-v{font:600 56px/1 var(--font-display);color:var(--accent);white-space:nowrap}
.mb-v.sleep{color:var(--sleep)} .mb-v.conc{color:var(--conc)}
.mb-cup{position:absolute;right:46px;top:-74px;width:120px;height:120px;overflow:visible}

/* comanda (limites) */
.comanda-wrap{display:grid;grid-template-columns:1fr .9fr;gap:60px;align-items:center;margin-top:24px;flex:1;min-height:0}
.comanda{position:relative;background:var(--paper);color:var(--paper-ink);padding:46px 52px 40px;transform:rotate(-1.6deg);box-shadow:0 40px 70px -30px rgba(0,0,0,.65);font-family:var(--font-mono);
  -webkit-mask:conic-gradient(from -45deg at bottom,#0000,#000 1deg 89deg,#0000 90deg) 50%/26px 100%,conic-gradient(from 135deg at top,#0000,#000 1deg 89deg,#0000 90deg) 50%/26px 100%;
  -webkit-mask-composite:source-in;mask:conic-gradient(from -45deg at bottom,#0000,#000 1deg 89deg,#0000 90deg) 50%/26px 100% intersect,conic-gradient(from 135deg at top,#0000,#000 1deg 89deg,#0000 90deg) 50%/26px 100%}
.slide.active .comanda{animation:ticketIn 1.1s var(--ease) both .3s}
@keyframes ticketIn{from{opacity:0;transform:translateY(-120px) rotate(-6deg)}}
.cm-h{display:flex;justify-content:space-between;align-items:baseline;border-bottom:2px dashed rgba(43,26,16,.35);padding-bottom:16px;margin-bottom:8px}
.cm-h b{font:700 30px var(--font-display);letter-spacing:.02em}
.cm-h span{font-size:16px;letter-spacing:.1em;text-transform:uppercase;opacity:.65}
.cm-item{display:grid;grid-template-columns:40px 1fr;gap:14px;padding:16px 0;border-bottom:1px dotted rgba(43,26,16,.3)}
.cm-item:last-of-type{border-bottom:0}
.cm-q{font-weight:700;font-size:20px}
.cm-item b{display:block;font:700 21px var(--font-body);margin-bottom:4px}
.cm-item p{margin:0;font:500 18px/1.45 var(--font-body);opacity:.8}
.cm-total{display:flex;justify-content:space-between;align-items:baseline;border-top:2px dashed rgba(43,26,16,.35);padding-top:16px;margin-top:6px;font-size:18px;text-transform:uppercase;letter-spacing:.08em}
.cm-total b{font:700 26px var(--font-display);text-transform:none;letter-spacing:0}
.cm-stain{position:absolute;right:-26px;bottom:-30px;width:190px;height:190px;opacity:.28;pointer-events:none}
.cm-stain circle{fill:none;stroke:#8f4e28;stroke-width:5;stroke-dasharray:190 14 46 9 30 8}
.cm-side p{font:500 30px/1.45 var(--font-display);margin:0;color:var(--text)}
.cm-side p em{color:var(--accent)}
.cm-side .sn{margin-top:26px}
"""

GRADIENTS = (
    '<linearGradient id="lg-coffee" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--liq-top)"/><stop offset="1" style="stop-color:var(--liq-bot)"/></linearGradient>'
    '<linearGradient id="lg-night" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--night-top)"/><stop offset="1" style="stop-color:var(--night-bot)"/></linearGradient>'
    '<linearGradient id="lg-amber" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--amber-top)"/><stop offset="1" style="stop-color:var(--amber-bot)"/></linearGradient>'
    '<linearGradient id="lg-roast" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--roast-top)"/><stop offset="1" style="stop-color:var(--roast-bot)"/></linearGradient>'
    '<linearGradient id="lg-grey" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--grey-top)"/><stop offset="1" style="stop-color:var(--grey-bot)"/></linearGradient>'
    '<radialGradient id="g-surface" cx=".5" cy=".45" r=".6"><stop offset="0" stop-color="#7d4c2b"/><stop offset=".7" stop-color="#4a2a17"/><stop offset="1" stop-color="#2c180c"/></radialGradient>'
)

AMBIENT = (
    '<svg class="amb-steam" style="left:8%;--del:-2s" viewBox="0 0 120 400" aria-hidden="true"><path d="M60 400C20 330 100 290 60 220C20 150 100 110 60 40"/></svg>'
    '<svg class="amb-steam" style="left:47%;--del:-7s" viewBox="0 0 120 400" aria-hidden="true"><path d="M60 400C100 330 20 290 60 220C100 150 20 110 60 40"/></svg>'
    '<svg class="amb-steam" style="left:82%;--del:-11s" viewBox="0 0 120 400" aria-hidden="true"><path d="M60 400C20 330 100 290 60 220C20 150 100 110 60 40"/></svg>'
    '<svg class="ring-stain" style="right:4%;top:6%;--rs:300px" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="40"/><circle cx="50" cy="50" r="36"/></svg>'
    '<svg class="ring-stain" style="left:2%;bottom:5%;--rs:220px;animation-direction:reverse" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="40"/><circle cx="50" cy="50" r="35.5"/></svg>'
)

_uid = [0]
def uid(p='c'):
    _uid[0] += 1
    return f'{p}{_uid[0]}'

def wave_d(x0, y, width, amp, wl, depth):
    """Superfície ondulada (período wl) de x0 até x0+width+wl, fechada até y+depth."""
    n = int(math.ceil((width + wl) / (wl / 2))) + 2
    d = f'M{x0:.1f},{y:.1f} q{wl / 4:.2f},{-amp:.2f} {wl / 2:.2f},0' + f' t{wl / 2:.2f},0' * (n - 1)
    return d + f' V{y + depth:.1f} H{x0:.1f} Z'

def wave_line(x0, y, width, amp, wl):
    n = int(math.ceil((width + wl) / (wl / 2))) + 2
    return f'M{x0:.1f},{y:.1f} q{wl / 4:.2f},{-amp:.2f} {wl / 2:.2f},0' + f' t{wl / 2:.2f},0' * (n - 1)

def liquid(clip_d, x, y_top, width, bottom, kind='coffee', i=0, amp=6, wl=60, dur=2.8, bubbles=0):
    """Líquido com onda dentro de um contorno (clip_d). y_top = superfície; bottom = fundo do recipiente."""
    cid = uid('lq')
    dy = bottom - y_top + amp * 2 + 4
    bub = ''
    for k in range(bubbles):
        bx = x + width * (0.25 + 0.5 * ((k * 0.37) % 1))
        bub += (f'<circle class="bub" cx="{bx:.1f}" cy="{bottom - 10:.1f}" r="{3 + (k % 3)}" '
                f'style="--bd:{3.2 + k * 0.7:.1f}s;--bdl:{k * 0.9:.1f}s;--rise:{max(20, (bottom - y_top) * .8):.0f}"/>')
    return (f'<clipPath id="{cid}"><path d="{clip_d}"/></clipPath>'
            f'<g clip-path="url(#{cid})"><g class="lq-rise" style="--dy:{dy:.0f};--i:{i}">'
            f'<path class="lq-wave lq-{kind}" style="--wl:{wl};--wd:{dur}s" d="{wave_d(x - wl, y_top, width, amp, wl, bottom - y_top + amp + 30)}"/>'
            f'<path class="lq-wave foam" style="--wl:{wl};--wd:{dur}s" d="{wave_line(x - wl, y_top, width, amp, wl)}"/>'
            f'{bub}</g></g>')

def cup_path(cx, top, w, h):
    """Xícara de vidro em vista lateral: boca larga, fundo arredondado."""
    x0, x1 = cx - w / 2, cx + w / 2
    b = top + h
    r = h * 0.16
    return (f'M{x0:.1f},{top:.1f} H{x1:.1f} L{x1 - w * 0.07:.1f},{b - r:.1f} '
            f'Q{x1 - w * 0.09:.1f},{b:.1f} {x1 - w * 0.2:.1f},{b:.1f} H{x0 + w * 0.2:.1f} '
            f'Q{x0 + w * 0.09:.1f},{b:.1f} {x0 + w * 0.07:.1f},{b - r:.1f} Z')

def cup(cx, top, w, h, level, kind='coffee', i=0, steam=False, saucer=True, glow=None):
    d = cup_path(cx, top, w, h)
    inner = cup_path(cx, top + 4, w - 10, h - 8)
    x0, x1, b = cx - w / 2, cx + w / 2, top + h
    hx = x1 - w * 0.03
    handle = f'M{hx:.1f},{top + h * 0.22:.1f} C{hx + w * 0.3:.1f},{top + h * 0.18:.1f} {hx + w * 0.28:.1f},{top + h * 0.72:.1f} {hx - w * 0.06:.1f},{top + h * 0.7:.1f}'
    y_lvl = (top + 4) + (h - 8) * (1 - level)
    s = ''
    if glow:
        s += f'<ellipse class="cup-glow" cx="{cx:.1f}" cy="{top + h * .55:.1f}" rx="{w * .9:.1f}" ry="{h * .75:.1f}" fill="url(#{glow})"/>'
    if saucer:
        s += f'<ellipse class="cups-saucer" cx="{cx:.1f}" cy="{b + 10:.1f}" rx="{w * 0.62:.1f}" ry="{max(9, w * 0.07):.1f}"/>'
    s += f'<path class="cuph" d="{handle}"/>'
    s += f'<path class="cupb" d="{d}"/>'
    if level > 0:
        s += liquid(inner, x0 + 5, y_lvl, w - 10, b - 4, kind, i, amp=max(3, w * 0.022), wl=max(40, w * 0.36), bubbles=2 if level > .25 else 0)
    if steam and level > 0:
        sx = cx
        s += (f'<g class="steam-s" transform="translate({sx - 36:.1f} {top - 92:.1f})">'
              '<path d="M14 82C2 62 26 50 14 30C4 14 18 4 12 -6"/><path d="M38 80C26 60 50 48 38 28C28 12 42 2 36 -8"/>'
              '<path d="M62 82C50 62 74 50 62 30C52 14 66 4 60 -6"/></g>')
    s += f'<path d="M{x0 + 6:.1f},{top + 3:.1f} H{x1 - 6:.1f}" class="rim-line" style="stroke:var(--liq-foam);stroke-width:2;opacity:.25"/>'
    return s, y_lvl


def divider_svg(num):
    cid = uid('dv')
    y_base, top_fill = 640, 330
    lq = (f'<g clip-path="url(#{cid})"><g class="lq-rise" style="--dy:{780 - top_fill:.0f};--i:0">'
          f'<path class="lq-wave lq-coffee" style="--wl:120;--wd:3.4s;opacity:.92" d="{wave_d(-120, top_fill, 1000, 12, 120, 780 - top_fill)}"/>'
          f'<path class="lq-wave foam" style="--wl:120;--wd:3.4s" d="{wave_line(-120, top_fill, 1000, 12, 120)}"/>'
          + ''.join(f'<circle class="bub" cx="{x}" cy="600" r="{r}" style="--bd:{bd}s;--bdl:{bdl}s;--rise:220"/>'
                    for x, r, bd, bdl in [(520, 7, 3.4, 0), (700, 5, 4.1, 1.2), (820, 6, 3.7, 2.1), (610, 4, 4.6, .6), (900, 5, 3.9, 1.7)])
          + '</g></g>')
    return (f'<svg class="div-svg" viewBox="0 0 1000 780" aria-hidden="true">'
            f'<defs><clipPath id="{cid}"><text class="dn-t" x="980" y="{y_base}" text-anchor="end">{num}</text></clipPath></defs>'
            f'<path class="stream" pathLength="1" d="M720,-200 C722,-40 716,120 720,{top_fill + 30}" style="stroke-width:16;--pd:2.8s;--pdl:.15s"/>'
            f'{lq}<text class="dn-t dn-o" x="980" y="{y_base}" text-anchor="end">{num}</text></svg>')


def footer_cup_js():
    return ''


# ------------------------------------------------------------------ slides redesenhados
def slide_populacao(V):
    nf, R, N = V['nf'], V['R'], V['N']
    fl = R['fluxo']
    labs = ['Participantes do NHANES 2021–2023', 'Com 18 a 29 anos', 'Responderam aos itens de sono e concentração do PHQ-9',
            'Têm horas de sono calculáveis', 'Completaram 2 recordatórios alimentares válidos']
    rows = ''.join(
        f'<li class="rv-r{" last" if k == len(fl) - 1 else ""}" style="--d:{2 + k};--i:{k}"><span class="st-n">0{k + 1}</span><span class="st-t">{labs[k]}</span>'
        f'<b class="st-v">{nf(f["n"], 0)}</b><span class="st-bar"><i style="--w:{max(f["n"] / fl[0]["n"] * 100, 1.6):.2f}%"></i></span></li>'
        for k, f in enumerate(fl))
    # coador
    cone = 'M60,150 H500 L322,452 H238 Z'
    cup_s, ylv = cup(280, 548, 250, 168, 0.72, 'coffee', 0, steam=False)
    drops = ''.join(f'<path class="drop" d="M280,{462} c-6,10 -9,16 -9,21 a9,9 0 0 0 18,0 c0,-5 -3,-11 -9,-21z" style="--dd:{1.8 + k * .35:.2f}s;--ddl:{k * .62:.2f}s;--fall:{ylv - 470:.0f}"/>' for k in range(3))
    svg = (f'<svg class="coador" viewBox="0 0 560 760" aria-label="Ilustração: os critérios de seleção funcionam como um coador; da base completa restam {N} participantes">'
           f'<path class="stream loop" pathLength="1" d="M300,0 C302,40 296,80 300,140" style="stroke-width:12"/>'
           f'<path class="cone" d="{cone}"/>'
           f'<clipPath id="cone-clip"><path d="{cone}"/></clipPath>'
           f'<g clip-path="url(#cone-clip)"><rect class="grounds" x="40" y="150" width="480" height="150" opacity=".85"/>'
           f'<g class="lq-rise" style="--dy:160;--i:1"><path class="lq-wave lq-coffee" style="--wl:70;--wd:3s;opacity:.55" d="{wave_d(-70, 290, 600, 5, 70, 200)}"/></g></g>'
           + ''.join(f'<line class="cone-rib" x1="{80 + k * 70}" y1="160" x2="{256 + k * 12}" y2="440"/>' for k in range(6))
           + f'<path d="M30,150 H530" style="stroke:var(--tube-line);stroke-width:6;stroke-linecap:round"/>'
           f'<path d="M250,452 h60 v18 h-60z" style="fill:var(--tube-line)"/>'
           f'{drops}{cup_s}'
           f'<text class="cd-num" x="268" y="{ylv + 70:.0f}">{N}</text><text class="cd-lab" x="268" y="{ylv + 96:.0f}">na amostra</text>'
           f'</svg>')
    return f'''<section class="slide" id="populacao" data-title="População e amostra" data-section="Metodologia" aria-label="População e amostra">
  <div class="kicker rv"><span class="kn">05</span>População e amostra</div>
  <h2 class="title rv-blur" style="--d:1">{nf(fl[0]['n'], 0)} participantes, <em>{N} coados</em></h2>
  <div class="strain-grid">
    <div class="rv-s" style="--d:2;height:100%;min-height:0">{svg}</div>
    <div>
      <ol class="strain">{rows}</ol>
      <div class="strain-notes">
        <div class="sn rv" style="--d:8"><svg class="ic"><use href="#i-users"/></svg><span><b>População-alvo:</b> adultos de 18 a 29 anos dos EUA, faixa que concentra os universitários. Os números <b>não se transferem automaticamente</b> para a Fatec.</span></div>
        <div class="sn rv" style="--d:9"><svg class="ic"><use href="#i-coffee"/></svg><span>Exigimos <b>dois dias</b> de registro alimentar: dois dias aproximam o <b>hábito</b>, não só o que a pessoa tomou num dia.</span></div>
      </div>
    </div>
  </div>
  <aside class="notes"><p>Como um coador: da base completa do NHANES ago./2021–ago./2023 ({nf(fl[0]['n'], 0)} participantes), passam pelos filtros os que têm 18 a 29 anos ({nf(fl[1]['n'], 0)}), responderam aos itens 3 e 7 do PHQ-9 ({nf(fl[2]['n'], 0)}), têm horas de sono calculáveis ({nf(fl[3]['n'], 0)}) e completaram os dois recordatórios alimentares de 24 h com qualidade ({nf(fl[4]['n'], 0)}). A maior perda é o 2º recordatório, feito por telefone dias depois.</p><p>População-alvo: adultos de 18 a 29 anos da população civil dos EUA. Os resultados não se aplicam diretamente aos estudantes da Fatec. Não há valores ausentes nas variáveis analisadas.</p></aside>
</section>'''


def slide_horario(V):
    nf, pc, R = V['nf'], V['pc'], V['R']
    F = R['freq']; PR = R['prob']; H = R['horario']
    per = {r['cat']: r for r in F['periodo']}
    spec = [('Manhã', '5h00–11h59', 'sunrise', 'g-glow-sun'), ('Tarde', '12h00–17h59', 'sun', 'g-glow-sun'), ('Noite', '18h00–4h59', 'moon', 'g-glow-night')]
    W, cw, ch = 1660, 300, 330
    parts = ['<defs><radialGradient id="g-glow-sun"><stop offset="0" style="stop-color:var(--accent);stop-opacity:.35"/><stop offset="1" style="stop-color:var(--accent);stop-opacity:0"/></radialGradient>'
             '<radialGradient id="g-glow-night"><stop offset="0" style="stop-color:var(--sleep);stop-opacity:.35"/><stop offset="1" style="stop-color:var(--sleep);stop-opacity:0"/></radialGradient></defs>']
    icons = {'sunrise': '<path d="M12 2v8M4.93 10.93l1.41 1.41M2 18h2M20 18h2M19.07 10.93l-1.41 1.41M22 22H2M8 6l4-4 4 4M16 18a4 4 0 0 0-8 0"/>',
             'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>',
             'moon': '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>'}
    for k, (lab, faixa, ic, glow) in enumerate(spec):
        cx = W / 6 + k * W / 3
        r = per[lab]
        cup_s, _ = cup(cx - 20, 120, cw, ch, r['pct'], 'coffee', k, steam=(k < 2), glow=glow)
        col = 'var(--sleep)' if ic == 'moon' else 'var(--accent)'
        parts.append(f'<g>{cup_s}</g>')
        parts.append(f'<svg x="{cx - 20 - 22:.0f}" y="8" width="44" height="44" viewBox="0 0 24 24" class="cic" style="stroke:{col}">{icons[ic]}</svg>')
        parts.append(f'<text class="cl" x="{cx - 20:.0f}" y="560" text-anchor="middle">{lab}<tspan class="cs" dx="14">{faixa}</tspan></text>')
        parts.append(f'<text class="cv" x="{cx - 70:.0f}" y="650" text-anchor="end">{r["n"]}</text>')
        parts.append(f'<text class="cp" x="{cx - 50:.0f}" y="650">{pc(r["pct"])}</text>')
    svg = f'<svg class="cups-svg" viewBox="0 0 {W} 680" role="img" aria-label="Três xícaras: manhã {pc(per["Manhã"]["pct"])}, tarde {pc(per["Tarde"]["pct"])}, noite {pc(per["Noite"]["pct"])}">{"".join(parts)}</svg>'
    return f'''<section class="slide" id="horario" data-title="Horário de maior consumo" data-section="Os dados" aria-label="Horário de maior consumo">
  <div class="kicker rv"><span class="kn">10.4</span>Período de maior consumo · Gráfico 3</div>
  <h2 class="title rv-blur" style="--d:1">A manhã <em>enche a xícara</em></h2>
  <div class="rv-s" style="--d:2;flex:1;min-height:0;margin-top:26px">{svg}</div>
  <p class="chart-cap rv" style="--d:5;margin-top:8px">Gráfico 3 – O nível de cada xícara é a parcela dos {PR['n_A']} participantes que tomaram café cujo maior volume foi naquele período.</p>
  <aside class="notes"><p>Período de maior consumo entre os {PR['n_A']} que tomaram café: manhã {per['Manhã']['n']} ({pc(per['Manhã']['pct'])}), tarde {per['Tarde']['n']} ({pc(per['Tarde']['pct'])}) e noite {per['Noite']['n']} ({pc(per['Noite']['pct'])}). O nível do café em cada xícara é proporcional a esse percentual.</p><p>O horário vem do próprio registro: cada bebida tem a hora em que o consumo começou. Considerando as {H['itens']} bebidas, {pc(H['por_periodo_itens']['Manhã'] / H['itens'])} começaram de manhã.</p></aside>
</section>'''


def _pol(cx, cy, r, h):
    a = h / 24 * 2 * math.pi - math.pi / 2
    return cx + r * math.cos(a), cy + r * math.sin(a)

def _arc(cx, cy, r, h0, h1):
    x0, y0 = _pol(cx, cy, r, h0)
    x1, y1 = _pol(cx, cy, r, h1)
    span = (h1 - h0) % 24
    large = 1 if span > 12 else 0
    return f'M{x0:.1f},{y0:.1f} A{r},{r} 0 {large} 1 {x1:.1f},{y1:.1f}'

def slide_cafe_sono(V):
    nf, pc, R = V['nf'], V['pc'], V['R']
    H = R['horario']; IV = R['intervalo']; HS = R['horarios_sono']
    cx = cy = 380
    hrs = H['por_hora_itens']; mx = max(hrs)
    bed, wake = HS['dormir_mediana'] % 24, HS['acordar_mediana']
    win0 = (HS['dormir_mediana'] - 8.8) % 24
    def hm(x):
        x = x % 24; hh = int(x); mm = int(round((x - hh) * 60))
        if mm == 60: hh, mm = (hh + 1) % 24, 0
        return f'{hh}h{mm:02d}' if mm else f'{hh}h'
    p = [f'<circle class="ck-face" cx="{cx}" cy="{cy}" r="336"/>']
    p.append(f'<path class="ck-sleep" d="{_arc(cx, cy, 336, bed, wake)}"/>')
    p.append(f'<path class="ck-win" d="{_arc(cx, cy, 336, win0, bed)}"/>')
    for h in range(24):
        x0, y0 = _pol(cx, cy, 300, h); x1, y1 = _pol(cx, cy, 316 if h % 3 else 324, h)
        p.append(f'<line class="ck-tick" x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}"/>')
        if h % 3 == 0:
            tx, ty = _pol(cx, cy, 276, h)
            p.append(f'<text class="ck-num" x="{tx:.1f}" y="{ty:.1f}">{h}h</text>')
    for h, c in enumerate(hrs):
        if c == 0:
            continue
        r0, r1 = 118, 118 + c / mx * 136
        x0, y0 = _pol(cx, cy, r0, h + .5); x1, y1 = _pol(cx, cy, r1, h + .5)
        cls = 'm' if 5 <= h < 12 else 't' if 12 <= h < 18 else 'n'
        p.append(f'<path class="ck-bar {cls}" pathLength="1" style="--h:{h}" d="M{x0:.1f},{y0:.1f} L{x1:.1f},{y1:.1f}"><title>{h}h: {c} bebidas</title></path>')
    # rótulos dos arcos
    lx, ly = _pol(cx, cy, 372, (win0 + ((bed - win0) % 24) / 2))
    p.append(f'<text class="ck-arc-lab" x="{lx:.1f}" y="{ly:.1f}" text-anchor="end">janela de 8,8 h</text>')
    sx, sy = _pol(cx, cy, 366, (bed + ((wake - bed) % 24) / 2) % 24)
    p.append(f'<text class="ck-arc-lab" x="{sx:.1f}" y="{sy:.1f}" text-anchor="start" style="fill:var(--muted)">sono habitual</text>')
    # centro: xícara vista de cima
    p.append(f'<circle cx="{cx}" cy="{cy}" r="104" style="fill:none;stroke:var(--cup-hi);stroke-width:10;opacity:.75"/>')
    p.append(f'<circle class="ck-center" cx="{cx}" cy="{cy}" r="96"/>')
    p.append(f'<g class="swirl" style="opacity:.35"><path d="M{cx},{cy + 40} C{cx - 70},{cy - 4} {cx - 28},{cy - 62} {cx},{cy - 26} C{cx + 28},{cy - 62} {cx + 70},{cy - 4} {cx},{cy + 40}Z" fill="#f2dcc0"/></g>')
    p.append(f'<text class="ck-c-num" x="{cx}" y="{cy + 8}">{H["itens"]}</text><text class="ck-c-lab" x="{cx}" y="{cy + 36}">bebidas</text>')
    rot = (bed / 24) * 360
    hx, hy = _pol(cx, cy, 330, 0)
    p.append(f'<line class="ck-hand" x1="{cx}" y1="{cy - 106}" x2="{hx:.1f}" y2="{hy + 20:.1f}" style="--rot:{rot:.1f}deg"/>')
    mx_, my_ = _pol(cx, cy, 360, bed)
    p.append(f'<svg x="{mx_ - 16:.1f}" y="{my_ - 16:.1f}" width="32" height="32" viewBox="0 0 24 24" class="cic" style="stroke:var(--sleep)"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>')
    wx, wy = _pol(cx, cy, 360, wake)
    p.append(f'<svg x="{wx - 16:.1f}" y="{wy - 16:.1f}" width="32" height="32" viewBox="0 0 24 24" class="cic" style="stroke:var(--accent)"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>')
    svg = f'<svg class="clock" viewBox="-20 -20 800 800" role="img" aria-label="Relógio de 24 horas com o número de bebidas de café por hora, a janela de 8,8 horas antes de dormir e o sono habitual">{"".join(p)}</svg>'
    hr_med = H['mediana_horario_itens']
    return f'''<section class="slide" id="cafe-sono" data-title="Café e hora de dormir" data-section="Os dados" data-mood="night" aria-label="Horário do café e hora de dormir">
  <div class="kicker rv"><span class="kn">10.5</span>O relógio do café · Gráfico 4</div>
  <h2 class="title rv-blur" style="--d:1">Café às {hm(hr_med)}, <em>cama às {hm(bed)}</em></h2>
  <div class="clock-grid">
    <div class="rv-s" style="--d:2;height:100%;min-height:0">{svg}</div>
    <div class="clock-stats">
      <div class="cks rv-r" style="--d:3"><b>{hm(hr_med)}</b><span>mediana do horário das {H['itens']} bebidas; <b>{pc(H['ate_12h_itens_pct'], 0)}</b> antes do meio-dia</span></div>
      <div class="cks sleep rv-r" style="--d:4"><b>{hm(bed)}</b><span>hora habitual de dormir em dias úteis (mediana); a janela de 8,8 h começa às <b>{hm(win0)}</b></span></div>
      <div class="cks rv-r" style="--d:5"><b>{nf(IV['mediana_pessoa'], 0)} h</b><span>entre o último café do dia e a hora de dormir (mediana)</span></div>
      <div class="cks sleep rv-r" style="--d:6"><b>{pc(IV['pessoas_menor_88'] / IV['pessoas'])}</b><span>dos que tomam café entraram na janela de 8,8 h ({IV['pessoas_menor_88']} pessoas; {IV['pessoas_menor_6']} a menos de 6 h)</span></div>
      <div class="ck-legend rv" style="--d:7"><span><i style="background:var(--liq-top)"></i>manhã</span><span><i style="background:var(--roast-top)"></i>tarde</span><span><i style="background:var(--night-top)"></i>noite</span><span><i style="background:var(--sleep);opacity:.45"></i>janela de 8,8 h</span></div>
    </div>
  </div>
  <aside class="notes"><p><b>Novo, possível só com dados reais:</b> cada bebida do recordatório tem hora de início, e o questionário de sono traz a hora habitual de dormir. No relógio, cada raio é uma hora do dia e o comprimento é o número de bebidas de café ({H['itens']} no total). O pico vai das 8h às 11h; depois das 18h foram só {H['por_periodo_itens']['Noite']} bebidas.</p><p>A mediana da hora de dormir em dias úteis é {hm(bed)} (metade entre {hm(HS['dormir_q1'])} e {hm(HS['dormir_q3'])}); a de acordar, {hm(wake)}. A janela de 8,8 h antes de dormir (Gardiner et al., 2023) começa às {hm(win0)}. A mediana do menor intervalo entre o último café e a hora de dormir é de {nf(IV['mediana_pessoa'], 0)} horas; {IV['pessoas_menor_88']} dos {IV['pessoas']} que tomaram café ({pc(IV['pessoas_menor_88'] / IV['pessoas'])}) o fizeram dentro da janela, e {IV['pessoas_menor_6']} a menos de 6 h.</p></aside>
</section>'''


def slide_condicional(V):
    nf, pc, R = V['nf'], V['pc'], V['R']
    PR = R['prob']; AC, BC = PR['A_C'], PR['B_C']; GPS = R['grupos_probsono']
    # coluna A: duas xícaras
    pa = [AC['p_e2_dado_e1'], AC['p_e2_dado_nao_e1']]
    na = [AC['a'] + AC['b'], AC['c'] + AC['d']]
    W1, H1 = 640, 560
    left = []
    tops = []
    for k, (lev, lab) in enumerate(zip(pa, ['tomou café', 'não tomou'])):
        cx = 170 + k * 300
        s, ylv = cup(cx - 14, 120, 220, 290, lev, 'amber', k, steam=(k == 0))
        tops.append(ylv)
        left.append(s)
        left.append(f'<text class="cv sm" x="{cx - 14}" y="482" text-anchor="middle">{pc(lev)}</text>')
        left.append(f'<text class="cl sm" x="{cx - 14}" y="520" text-anchor="middle">{lab}</text><text class="cs" x="{cx - 14}" y="546" text-anchor="middle">n = {na[k]}</text>')
    yl = sum(tops) / 2
    left.append(f'<line class="lvl-line" x1="30" x2="610" y1="{yl:.1f}" y2="{yl:.1f}"/><text class="lvl-lab" x="320" y="{yl - 16:.1f}" text-anchor="middle">mesmo nível</text>')
    svgL = f'<svg class="cups-svg" viewBox="0 0 {W1} {H1}" role="img" aria-label="Dificuldade de concentração: {pc(pa[0])} entre quem tomou café e {pc(pa[1])} entre quem não tomou">{"".join(left)}</svg>'
    # coluna B: quatro xícaras
    W2 = 980
    right = []
    labs = ['nenhum dia', 'vários dias', 'mais da metade', 'quase todos']
    for k, g in enumerate(GPS):
        cx = 120 + k * 246
        s, _ = cup(cx - 12, 150, 176, 260, g['conc_prej'], 'amber', k + 2, steam=False)
        right.append(s)
        right.append(f'<text class="cv sm" x="{cx - 12}" y="482" text-anchor="middle">{pc(g["conc_prej"])}</text>')
        right.append(f'<text class="cl sm" x="{cx - 12}" y="520" text-anchor="middle">{labs[k]}</text><text class="cs" x="{cx - 12}" y="546" text-anchor="middle">n = {g["n"]}</text>')
        right.append(f'<svg x="{cx - 28:.0f}" y="{86 - k * 8}" width="32" height="32" viewBox="0 0 24 24" class="cic" style="stroke:var(--sleep);opacity:{.35 + k * .2:.2f}"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>')
    svgR = f'<svg class="cups-svg" viewBox="0 0 {W2} {H1}" role="img" aria-label="Dificuldade de concentração por frequência de problemas de sono: {", ".join(pc(g["conc_prej"]) for g in GPS)}">{"".join(right)}</svg>'
    ratio = BC['p_e2_dado_e1'] / BC['p_e2_dado_nao_e1']
    return f'''<section class="slide" id="condicional" data-title="Probabilidade condicional" data-section="Análise estatística" aria-label="Probabilidade condicional">
  <div class="kicker rv"><span class="kn">15.1</span>Probabilidade condicional · Gráfico 7</div>
  <h2 class="title rv-blur" style="--d:1">O que muda a chance de <em>perder a concentração?</em></h2>
  <div class="cond-cups">
    <div class="cond-col rv-l" style="--d:2">
      <h3>Saber que tomou café <span class="verdict no"><svg class="ic"><use href="#i-ban"/></svg>não muda</span></h3>
      <div class="chart">{svgL}</div>
      <div class="cond-math"><span>P(C | A) = {AC['a']}/{na[0]} · P(C | Ā) = {AC['c']}/{na[1]}</span><b>χ² = {nf(AC['chi2'], 3)} · p = {nf(AC['p'], 2)}</b></div>
    </div>
    <div class="cond-col rv-r" style="--d:3">
      <h3>Saber a frequência de problemas de sono <span class="verdict yes"><svg class="ic"><use href="#i-check"/></svg>{nf(ratio, 2)}× mais chance</span></h3>
      <div class="chart">{svgR}</div>
      <div class="cond-math"><span>P(C | B) = {BC['a']}/{BC['a'] + BC['b']} = {pc(BC['p_e2_dado_e1'])} · P(C | B̄) = {BC['c']}/{BC['c'] + BC['d']} = {pc(BC['p_e2_dado_nao_e1'])}</span><b>χ² = {nf(BC['chi2'], 1)} · p &lt; 0,001</b></div>
    </div>
  </div>
  <p class="foot-note rv" style="--d:5"><svg class="ic"><use href="#i-info"/></svg>O nível de cada xícara é a chance de ter dificuldade de concentração (evento C). P(A ∩ C) = {nf(AC['p_e1_e_e2'], 4)} ≈ P(A) × P(C) = {nf(PR['P_A'] * PR['P_C'], 4)}: café e concentração se comportam como eventos independentes.</p>
  <aside class="notes"><p><b>Novo, possível só com dados reais:</b> probabilidade condicional. O nível do café em cada xícara é a proporção com dificuldade de concentração (evento C) no grupo. Café × concentração: P(C | A) = {AC['a']}/{na[0]} = {pc(pa[0])} e P(C | Ā) = {AC['c']}/{na[1]} = {pc(pa[1])}, praticamente o mesmo nível; P(A ∩ C) = {nf(AC['p_e1_e_e2'], 4)} ≈ P(A)·P(C) = {nf(PR['P_A'] * PR['P_C'], 4)} → independentes (χ² = {nf(AC['chi2'], 3)}; p = {nf(AC['p'], 3)}).</p><p>Sono × concentração: P(C | B) = {pc(BC['p_e2_dado_e1'])} contra P(C | B̄) = {pc(BC['p_e2_dado_nao_e1'])}, razão de {nf(ratio, 2)} (χ² = {nf(BC['chi2'], 2)}; p &lt; 0,001). Por nível de problema de sono, as xícaras vão enchendo: {", ".join(pc(g["conc_prej"]) for g in GPS)}.</p></aside>
</section>'''


def slide_analise(V):
    nf, pc, R = V['nf'], V['pc'], V['R']
    PR = R['prob']; FX = R['por_faixa']; IV = R['intervalo']; P = R['pearson']; BC = PR['B_C']
    man = next(r for r in R['freq']['periodo'] if r['cat'] == 'Manhã')
    items = [
        ('i-coffee', '', 'Tomaram café em ao menos 1 de 2 dias', f'só {pc(PR["P_A2"])} nos dois dias', pc(PR['P_A']), ''),
        ('i-sunrise', '', 'Concentram o café de manhã', 'mediana das bebidas às 9h30', pc(man['pct']), ''),
        ('i-users', '', 'Consumo entre 18–21 e 26–29 anos', 'quanto mais velho, mais café', f'{pc(FX["18 a 21"]["tomou_cafe"], 0)} → {pc(FX["26 a 29"]["tomou_cafe"], 0)}', ''),
        ('i-hourglass', 'sleep', 'Tomaram café na janela de 8,8 h', 'antes da hora habitual de dormir', pc(IV['pessoas_menor_88'] / IV['pessoas']), 'sleep'),
        ('i-target', 'conc', 'Café × dificuldade de concentração', f'correlação nula (p = {nf(P["xic_conc"]["p"], 2)})', f'r = {nf(P["xic_conc"]["r"], 3)}', 'conc'),
        ('i-moon', 'sleep', 'Chance de perder a concentração com problemas de sono', f'{pc(BC["p_e2_dado_e1"])} contra {pc(BC["p_e2_dado_nao_e1"])}', f'{nf(BC["p_e2_dado_e1"] / BC["p_e2_dado_nao_e1"], 1)}×', 'sleep'),
    ]
    lis = ''.join(
        f'<li class="rv" style="--d:{3 + k}"><span class="mb-ic {cls}"><svg class="ic"><use href="#{ic}"/></svg></span>'
        f'<span class="mb-t">{t}<small>{sub}</small></span><span class="mb-dots"></span><b class="mb-v {vcls}">{v}</b></li>'
        for k, (ic, cls, t, sub, v, vcls) in enumerate(items))
    cup_s, _ = cup(60, 46, 84, 70, .78, 'coffee', 0, steam=True, saucer=True)
    return f'''<section class="slide" id="analise" data-title="Análise dos resultados" data-section="Conclusões" aria-label="Análise dos resultados">
  <div class="kicker rv"><span class="kn">17</span>Análise dos resultados</div>
  <h2 class="title rv-blur" style="--d:1">O que os dados <em>mostram</em></h2>
  <div class="menu-board rv-s" style="--d:2">
    <svg class="mb-cup" viewBox="0 0 120 140" aria-hidden="true">{cup_s}</svg>
    <div class="mb-head"><span>Cardápio de resultados</span><small>NHANES 2021–2023 · {R['n']} jovens de 18 a 29 anos</small></div>
    <ul class="mb-list">{lis}</ul>
  </div>
  <div class="banner rv" style="--d:9"><svg class="ic"><use href="#i-bulb"/></svg><p>O que acompanha a concentração é <b>a qualidade do sono</b>, não a quantidade de café.</p></div>
  <aside class="notes"><p>Síntese, em formato de cardápio: o café é hábito de {pc(PR['P_A'])} dos jovens ({pc(PR['P_A2'])} nos dois dias), cresce com a idade ({pc(FX['18 a 21']['tomou_cafe'])} → {pc(FX['26 a 29']['tomou_cafe'])}) e é matinal ({pc(man['pct'])} concentram o consumo de manhã). {IV['pessoas_menor_88']} dos {IV['pessoas']} que tomaram café ({pc(IV['pessoas_menor_88'] / IV['pessoas'])}) entraram na janela de 8,8 h antes de dormir.</p><p>A quantidade de café não se associa à concentração (r = {nf(P['xic_conc']['r'], 3)}); os problemas de sono, sim ({pc(BC['p_e2_dado_e1'])} contra {pc(BC['p_e2_dado_nao_e1'])}). Coerente com a literatura: o benefício da cafeína aparece em doses agudas e após privação de sono (Irwin et al., 2020) e, em consumidores habituais, é em boa parte reversão da abstinência (James; Rogers, 2005).</p></aside>
</section>'''


def slide_limitacoes(V):
    R = V['R']
    items = [('1×', 'Concentração autorrelatada', 'O item do PHQ-9 mede a frequência de uma dificuldade, não nota nem desempenho.'),
             ('1×', 'Dois dias de registro', 'Aproximam o hábito de consumo, mas não o medem exatamente.'),
             ('1×', 'Desenho transversal', 'Tudo foi medido no mesmo período: não dá para saber o que veio antes.'),
             ('1×', 'Jovens dos EUA', 'No Brasil o café é mais difundido: 78,1% o tomam num dia comum (POF 2017–2018).')]
    its = ''.join(f'<div class="cm-item"><span class="cm-q">{q}</span><div><b>{t}</b><p>{d}</p></div></div>' for q, t, d in items)
    return f'''<section class="slide" id="limitacoes" data-title="Limites do estudo" data-section="Conclusões" aria-label="Limites do estudo">
  <div class="kicker rv"><span class="kn">17</span>Cautela na interpretação</div>
  <h2 class="title rv-blur" style="--d:1">Os limites <em>deste estudo</em></h2>
  <div class="comanda-wrap">
    <div class="comanda">
      <div class="cm-h"><b>Comanda nº {R['n']}</b><span>Limites do estudo</span></div>
      {its}
      <div class="cm-total"><span>Vale para</span><b>{R['n']} jovens dos EUA</b></div>
      <svg class="cm-stain" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="40"/></svg>
    </div>
    <div class="cm-side">
      <p class="rv-r" style="--d:3">Os números valem para esses {R['n']} jovens. Para decidir na Fatec, é preciso uma <em>coleta própria</em>, com o mesmo método.</p>
      <div class="sn rv-r" style="--d:4"><svg class="ic"><use href="#i-info"/></svg><span>Sono e concentração vêm do mesmo questionário de saúde mental: parte da relação entre eles reflete o <b>humor</b>.</span></div>
      <div class="sn rv-r" style="--d:5"><svg class="ic"><use href="#i-sigma"/></svg><span>Os p-valores ignoram o desenho por conglomerados; resultados no limite de 5% foram tratados <b>com cautela</b>.</span></div>
    </div>
  </div>
  <aside class="notes"><p>Limites: (1) concentração medida pelo item 7 do PHQ-9, autorrelatada, sem notas ou tempo de estudo; (2) sono e concentração vêm do mesmo questionário de saúde mental, então parte da correlação reflete o humor; (3) dois recordatórios aproximam o hábito, e o horário de dormir usado é o habitual; (4) desenho transversal; (5) população norte-americana; (6) análise sem pesos amostrais — a comparação ponderada mudou pouco os percentuais, mas os p-valores ignoram o desenho por conglomerados.</p></aside>
</section>'''


OVERRIDES = {'populacao': slide_populacao, 'horario': slide_horario, 'cafe-sono': slide_cafe_sono,
             'condicional': slide_condicional, 'analise': slide_analise, 'limitacoes': slide_limitacoes}


def apply(html_slides, V):
    for sid, fn in OVERRIDES.items():
        pat = re.compile(r'<section class="slide[^"]*" id="' + re.escape(sid) + r'".*?</section>', re.S)
        assert pat.search(html_slides), sid
        new = fn(V)
        html_slides = pat.sub(lambda m: new, html_slides, count=1)
    # divisores: número que se enche de café
    html_slides, n = re.subn(r'<div class="div-num" aria-hidden="true"><span class="rv-s" style="--d:0">(\d\d)</span></div>',
                             lambda m: divider_svg(m.group(1)), html_slides)
    assert n == 4, n
    # donuts como xícara vista de cima
    html_slides = html_slides.replace('<div class="donut-wrap rv-s" style="--d:2">', '<div class="donut-wrap cup rv-s" style="--d:2">')
    return html_slides
