"""Atualiza a apresentação HTML com os dados reais (NHANES 2021–2023).
Mantém o design, a navegação e os componentes do arquivo original; troca conteúdo, dados e gráficos."""
import json, os, re, html, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coffee_layer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
SRC = os.path.join(ROOT, 'modelo', 'apresentacao_original.html')
DST = os.path.join(ROOT, 'out', 'apresentacao-cafe.html')
R = json.load(open(os.path.join(ROOT, 'out', 'results.json'), encoding='utf-8'))
orig = open(SRC, encoding='utf-8').read()

from decimal import Decimal, ROUND_HALF_UP
def nf(v, d=1):
    q = Decimal(abs(v)).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    s = f'{q:,.{d}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return ('−' if v < 0 and q != 0 else '') + s
pc = lambda v, d=1: nf(v * 100, d) + '%'
N = R['n']; F = R['freq']; D = R['desc']; P = R['pearson']; PR = R['prob']; H = R['horario']; IV = R['intervalo']
fr = lambda k, c: next(r for r in F[k] if r['cat'] == c)
xc, xs, sc, xh = P['xic_conc'], P['xic_probsono'], P['probsono_conc'], P['xic_sono']
AC, BC, AB = PR['A_C'], PR['B_C'], PR['A_B']
BI = R['binomial']; pB = BI['p']; qB = 1 - pB
dxc = D['xicaras_consumidores']; dx = D['xicaras']
FX = R['por_faixa']; GEN = R['por_genero']; CD = R['concordancia_dias']; GD = R['grupos_dias']; GPS = R['grupos_probsono']
manha, tarde, noite = fr('periodo', 'Manhã'), fr('periodo', 'Tarde'), fr('periodo', 'Noite')
hr_med = H['mediana_horario_itens']; hr_txt = f"{int(hr_med)}h{int(round((hr_med % 1) * 60)):02d}"

# ------------------------------------------------------------------ peças do original
head = orig[:orig.index('<!-- ======================= 1 · CAPA')]
logo_f = re.search(r'<img class="logo-fatec"[^>]+>', orig).group(0)
logo_c = re.search(r'<img class="logo-cps"[^>]+>', orig).group(0)
tail = orig[orig.index('<nav id="controls"'):orig.index('<script>')]
head = head.replace(
    '<meta name="description" content="Apresentação do projeto Consumo de café e produtividade acadêmica: análise estatística de 500 registros sobre café, concentração e qualidade do sono.">',
    '<meta name="description" content="Consumo de café e produtividade acadêmica: análise estatística de 496 adultos de 18 a 29 anos com microdados reais do NHANES 2021–2023 (CDC/EUA) sobre café, sono e concentração.">')
assert '496 adultos' in head

EXTRA_CSS = r"""
/* ===== acréscimos: dados reais (NHANES 2021–2023) ===== */
:root{--tarde:#3fbf9f}
:root[data-theme="light"]{--tarde:#0f8a6e}
.rmeter.tall .rm-val{font-size:19px;padding:4px 10px}
.rmeter.tall .rm-val em{font-size:13px;margin-right:6px}
.rm-mk.al-r .rm-val{transform:translateX(calc(-100% + 18px))}
.rm-mk.al-l .rm-val{transform:translateX(-18px)}
.hbars[data-kind="conc"] .hb{grid-template-columns:180px 1fr 170px}
.funnel-card{display:flex;flex-direction:column;justify-content:center}
.funnel{display:flex;flex-direction:column;gap:16px;margin-top:6px}
.fn-row{display:grid;grid-template-columns:1fr 150px;gap:6px 18px;align-items:center}
.fn-l{grid-column:1/-1;font-size:20px;color:var(--muted);line-height:1.3}
.fn-t{height:30px;border-radius:10px;background:var(--card-2);overflow:hidden}
.fn-t i{display:block;height:100%;width:var(--w);border-radius:10px;background:var(--accent);opacity:.45;transform-origin:left}
.fn-row.last .fn-t i{opacity:1}
.fn-v{font:650 28px var(--font-mono);text-align:right}
.fn-row.last .fn-v{color:var(--accent)}
.slide.active .fn-t i{animation:growX 1s var(--ease) both;animation-delay:calc(var(--i)*140ms + 520ms)}
.fn-cap{font-size:19px;color:var(--dim);margin:6px 0 0;line-height:1.45}
.samp.ok{border-style:solid;border-color:var(--pos)}
.samp.ok::after{content:"✓";color:var(--pos);font-style:normal;opacity:.5}
.samp.ok .samp-ic{background:var(--pos-soft);color:var(--pos)}
.samp-st.ok{color:var(--pos)}
.samp p{margin:0;font-size:20px;line-height:1.4;color:var(--muted)}
.reg-note.ok .ic{color:var(--pos)}
.tbl.vars.dense td{padding:8px 18px;font-size:21px}
.tbl.stats.dense td{padding:15px 18px}
.pill.neu{background:var(--card-2);color:var(--muted)}
.pill.sleep-s{background:var(--sleep-soft);color:var(--sleep)}
.rmeter.tall{margin-top:112px}
.rm-mk.lv1 .rm-val{bottom:96px}
.rm-mk.lv1 .rm-pin::after{content:"";position:absolute;left:50%;bottom:28px;width:2px;height:48px;margin-left:-1px;background:var(--mk);opacity:.55}
.rm-mk.pos{--mk:var(--pos)}
.r-big.neu{color:var(--muted)}
.ev-c .ev-res{color:var(--conc)}
.ev-c.on{border-color:var(--conc);background:linear-gradient(100deg,var(--conc-soft),var(--card))}
.waffle.mC .wd[data-c="1"]{fill:var(--conc)}
.waffle-card.isC .wf-head b{color:var(--conc)}
.waffle-card.isC .wf-legend .on{background:var(--conc)}
.bar.gr{fill:var(--dim);opacity:.45}
.bar.cf{fill:var(--accent);opacity:1}
.bar.am{fill:var(--tarde);opacity:1}
.bar.sn{fill:var(--sleep);opacity:1}
.seg.models button{width:auto;padding:0 20px;font-size:19px;font-family:var(--font-body)}
.sim-top-2{display:flex;gap:28px;align-items:flex-end;flex-wrap:wrap}
.kgrid{display:grid;grid-template-columns:1fr;gap:16px}
.kg{padding:20px 26px;border-radius:22px;background:var(--card);border:1px solid var(--line)}
.kg b{display:block;font:600 60px/1 var(--font-display);color:var(--accent)}
.kg.sleep b{color:var(--sleep)}
.kg span{display:block;margin-top:8px;font-size:20px;color:var(--muted);line-height:1.4}
.kg span b{display:inline;font:inherit;color:var(--text);font-weight:650}
.cond-grid{display:grid;grid-template-columns:.8fr 1.2fr;gap:30px;margin-top:30px;flex:1;min-height:0}
.cond-foot{display:flex;justify-content:space-between;gap:16px;align-items:center;margin-top:10px;font:500 19px var(--font-mono);color:var(--muted)}
.cond-foot b{color:var(--text)}
.verdict{display:inline-flex;align-items:center;gap:8px;padding:8px 16px;border-radius:999px;font-size:18px;font-weight:700;white-space:nowrap}
.verdict.no{background:var(--card-2);color:var(--muted)}
.verdict.yes{background:var(--sleep-soft);color:var(--sleep)}
.refs.dense{gap:9px}
.refs.dense li{padding:13px 22px 13px 74px;font-size:18px;line-height:1.45}
.refs.dense li::before{top:11px;left:22px;font-size:19px}
"""
head = head.replace('</style>', EXTRA_CSS + coffee_layer.COFFEE_CSS + '</style>', 1)
head = head.replace('<div class="grain"></div>', coffee_layer.AMBIENT + '<div class="grain"></div>', 1)
assert 'amb-steam' in head

ICON_EXTRA = ('<symbol id="i-hourglass" viewBox="0 0 24 24"><path d="M5 22h14M5 2h14M17 22v-4.17a2 2 0 0 0-.59-1.42L12 12l-4.41 4.41A2 2 0 0 0 7 17.83V22M7 2v4.17a2 2 0 0 0 .59 1.42L12 12l4.41-4.41A2 2 0 0 0 17 6.17V2"/></symbol>'
              '<symbol id="i-database" viewBox="0 0 24 24"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/></symbol>'
              '<symbol id="i-git" viewBox="0 0 24 24"><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="12" r="3"/><path d="M6 9v6M8.6 7.5 15.4 10.5"/></symbol>')
head = head.replace('</defs>', ICON_EXTRA + coffee_layer.GRADIENTS + '</defs>', 1)

E = html.escape
V = dict(N=N)

# ------------------------------------------------------------------ slides
S = []
add = S.append

add(f'''<!-- ======================= 1 · CAPA ======================= -->
<section class="slide cover" id="capa" data-title="Capa" data-section="Abertura" data-chrome="off" aria-label="Capa">
  <div class="cover-logos rv" style="--d:0">
    {logo_f}
    <span class="logo-sep" aria-hidden="true"></span>
    {logo_c}
  </div>
  <div class="cover-grid">
    <div>
      <div class="eyebrow rv" style="--d:1"><span class="dot"></span>Estatística Aplicada · Análise e Desenvolvimento de Sistemas</div>
      <h1 class="cover-title rv-blur" style="--d:2">Consumo de café<em>e produtividade acadêmica</em></h1>
      <p class="cover-sub rv" style="--d:4">Café, sono e concentração em {N} adultos de 18 a 29 anos, com microdados reais do NHANES 2021–2023, pesquisa nacional de saúde dos Estados Unidos.</p>
      <div class="authors rv" style="--d:5">
        <span class="author">Bruna Lais Amorin</span><span class="author">Kaike Taylor Antonio Santos</span><span class="author">Lucas Gustavo Mendes</span><span class="author">Rafael Gervazoni Bezerra</span>
      </div>
      <div class="cover-meta rv" style="--d:6"><svg class="ic"><use href="#i-pin"/></svg>Presidente Prudente – SP<span class="sep">•</span>2026</div>
    </div>
    <div class="cover-art rv-s" style="--d:3">
      CUP_SVG
      <div class="bf-wrap rv" style="--d:7;left:-10px;top:70px"><div class="badge-float"><strong>{N}</strong><span>jovens · dados reais</span></div></div>
      <div class="bf-wrap rv" style="--d:8;right:-24px;top:330px"><div class="badge-float" style="animation-delay:-1.8s"><strong>{pc(PR['P_A'])}</strong><span>tomaram café (2 dias de registro)</span></div></div>
      <div class="bf-wrap rv" style="--d:9;left:10px;bottom:60px"><div class="badge-float" style="animation-delay:-3.4s"><strong>r = {nf(xc['r'], 3)}</strong><span>café × concentração</span></div></div>
    </div>
  </div>
  <aside class="notes"><p>Abertura: projeto <b>“Consumo de café e produtividade acadêmica”</b> — Fatec Presidente Prudente, 2026, Estatística Aplicada (ADS). Integrantes: Bruna Lais Amorin, Kaike Taylor Antonio Santos, Lucas Gustavo Mendes e Rafael Gervazoni Bezerra.</p><p>Os dados são reais: microdados públicos do NHANES (National Health and Nutrition Examination Survey), ciclo agosto/2021–agosto/2023, do CDC dos EUA. Analisamos todos os {N} participantes de 18 a 29 anos com dados completos de café, sono e concentração.</p></aside>
</section>''')

cup_svg = re.search(r'<div class="cup-wrap" id="cup-src">.*?</svg>\s*</div>', orig, flags=re.S).group(0)
S[-1] = S[-1].replace('CUP_SVG', cup_svg)

add('''<!-- ======================= 2 · ROTEIRO ======================= -->
<section class="slide" id="roteiro" data-title="Roteiro" data-section="Abertura" aria-label="Roteiro">
  <div class="kicker rv"><span class="kn">00</span>Roteiro da apresentação</div>
  <h2 class="title rv-blur" style="--d:1">O caminho <em>da análise</em></h2>
  <div class="journey">
    <div class="jline" aria-hidden="true"><i></i></div>
    <button type="button" class="jstep rv" style="--d:3" data-goto="tema"><span class="jdot"></span><span class="jcard"><span class="jn">01</span><span class="jt">Contexto</span><span class="js">Título, tema, problema de pesquisa e objetivos</span><span class="jsec">Seções 1–4</span></span></button>
    <button type="button" class="jstep rv" style="--d:4" data-goto="d-metodologia"><span class="jdot"></span><span class="jcard"><span class="jn">02</span><span class="jt">Metodologia</span><span class="js">De onde vêm os dados, como a amostra foi formada e o que foi medido</span><span class="jsec">Seções 5–9</span></span></button>
    <button type="button" class="jstep rv" style="--d:5" data-goto="d-dados"><span class="jdot"></span><span class="jcard"><span class="jn">03</span><span class="jt">Os dados</span><span class="js">Café, horário, sono e concentração em tabelas e gráficos</span><span class="jsec">Seções 10–11</span></span></button>
    <button type="button" class="jstep rv" style="--d:6" data-goto="d-estatistica"><span class="jdot"></span><span class="jcard"><span class="jn">04</span><span class="jt">Estatística</span><span class="js">Medidas, correlação, regressão, probabilidade e binomial</span><span class="jsec">Seções 12–16</span></span></button>
    <button type="button" class="jstep rv" style="--d:7" data-goto="d-conclusoes"><span class="jdot"></span><span class="jcard"><span class="jn">05</span><span class="jt">Conclusões</span><span class="js">Análise, limites, conclusão, decisão e referências</span><span class="jsec">Seções 17–21</span></span></button>
  </div>
  <p class="hint rv" style="--d:9"><svg class="ic"><use href="#i-info"/></svg>Clique em uma etapa para ir direto a ela · ← → navegam · M abre o sumário · N mostra as notas</p>
  <aside class="notes"><p>A apresentação segue a estrutura do relatório: contexto (seções 1 a 4), metodologia (5 a 9), dados descritivos (10 e 11), análise estatística (12 a 16) e conclusões (17 a 21).</p></aside>
</section>''')

add(f'''<!-- ======================= 3 · TEMA ======================= -->
<section class="slide" id="tema" data-title="Título e tema" data-section="Contexto" aria-label="Título e tema">
  <div class="kicker rv"><span class="kn">01–02</span>Título do projeto · Tema escolhido</div>
  <h2 class="title rv-blur" style="--d:1">Café, concentração <em>e sono</em></h2>
  <div class="content" style="grid-template-columns:.95fr 1.05fr">
    <div class="card project-card rv-l" style="--d:2">
      <div class="pc-label"><svg class="ic"><use href="#i-book"/></svg>Título do projeto</div>
      <p class="pc-title">Consumo de Café e Produtividade Acadêmica: <em>café, sono e concentração em {N} adultos de 18 a 29 anos, com dados reais do NHANES 2021–2023.</em></p>
      <div class="pc-foot">As <b>mesmas pessoas</b> informaram o café que tomaram, com horário, quanto dormem e com que frequência têm dificuldade de concentração.</div>
    </div>
    <div class="stack">
      <div class="feature rv-r" style="--d:3"><div class="icon-badge"><svg class="ic"><use href="#i-zap"/></svg></div><div><h3>Cafeína</h3><p>Bloqueia a adenosina e reduz a sonolência. O ganho de atenção é maior em quem dormiu pouco.</p></div></div>
      <div class="feature rv-r" style="--d:4"><div class="icon-badge"><svg class="ic"><use href="#i-clock"/></svg></div><div><h3>Horário importa</h3><p>Café tomado a menos de <b>8,8 h</b> da hora de dormir reduz o sono (Gardiner et al., 2023).</p></div></div>
      <div class="feature rv-r" style="--d:5"><div class="icon-badge sleep"><svg class="ic"><use href="#i-pin"/></svg></div><div><h3>No Brasil</h3><p>O café é o alimento mais frequente: <b>78,1%</b> dos brasileiros o tomam em um dia comum (POF 2017–2018).</p></div></div>
    </div>
  </div>
  <aside class="notes"><p><b>Título:</b> Consumo de Café e Produtividade Acadêmica: café, sono e concentração em {N} adultos de 18 a 29 anos, com dados reais do NHANES 2021–2023.</p><p><b>Tema:</b> a cafeína bloqueia a adenosina, que produz sonolência; por isso ajuda a manter o alerta, sobretudo após pouco sono (Irwin et al., 2020). O mesmo mecanismo prejudica o sono quando o café é tomado perto de deitar: a metanálise de Gardiner et al. (2023) indica pelo menos 8,8 horas de antecedência. No Brasil, o café foi o alimento consumido com maior frequência na POF 2017–2018: 78,1% das pessoas com 10 anos ou mais, com média de 163,2 g por dia.</p></aside>
</section>''')

add(f'''<!-- ======================= 4 · PROBLEMA ======================= -->
<section class="slide" id="problema" data-title="Problema de pesquisa" data-section="Contexto" aria-label="Problema de pesquisa">
  <div class="kicker rv"><span class="kn">03</span>Problema de pesquisa</div>
  <div class="content" style="grid-template-columns:1.22fr .78fr;align-items:center;margin-top:20px">
    <div>
      <blockquote class="big-q rv-blur" style="--d:1">Entre adultos de 18 a 29 anos, a quantidade de café consumida por dia está associada à <mark class="m-conc">dificuldade de concentração</mark> e à <mark class="m-sleep">qualidade do sono</mark>?</blockquote>
      <div class="subqs">
        <div class="subq rv" style="--d:3"><svg class="ic"><use href="#i-help"/></svg>Quanto, com que frequência e a que horas?</div>
        <div class="subq rv" style="--d:4"><svg class="ic"><use href="#i-help"/></svg>Se não for o café, o que acompanha a concentração?</div>
      </div>
      <div class="callout rv" style="--d:5;margin-top:30px"><svg class="ic"><use href="#i-sigma"/></svg><p>Hipóteses testadas a 5%: <b>H₀: ρ = 0</b> (sem correlação) contra <b>H₁: ρ ≠ 0</b>. Como a amostra é probabilística, agora é possível testá-las — o que ainda <b>não prova causa</b>.</p></div>
    </div>
    <div class="card diagram-card rv-s" style="--d:3">
      <svg viewBox="0 0 640 560" aria-label="Diagrama: xícaras por dia relacionadas a concentração e qualidade do sono">
        <path class="dg-link" d="M236 280C306 280 292 120 362 120"/>
        <path class="dg-link" d="M236 280C306 280 292 440 362 440"/>
        <rect class="dg-node x" x="6" y="214" width="230" height="132" rx="26"/>
        <svg x="30" y="234" width="46" height="46" class="dg-ic" style="color:var(--accent)"><use href="#i-coffee"/></svg>
        <text class="dg-t" x="30" y="318">Xícaras/dia</text>
        <rect class="dg-node c" x="362" y="54" width="272" height="132" rx="26"/>
        <svg x="386" y="74" width="46" height="46" class="dg-ic" style="color:var(--conc)"><use href="#i-target"/></svg>
        <text class="dg-t" x="386" y="158">Concentração</text>
        <rect class="dg-node s" x="362" y="374" width="272" height="132" rx="26"/>
        <svg x="386" y="394" width="46" height="46" class="dg-ic" style="color:var(--sleep)"><use href="#i-moon"/></svg>
        <text class="dg-t" x="386" y="478">Qualidade do sono</text>
        <g class="dg-q"><circle cx="299" cy="200" r="26"/><text x="299" y="210" text-anchor="middle">?</text></g>
        <g class="dg-q"><circle cx="299" cy="360" r="26"/><text x="299" y="370" text-anchor="middle">?</text></g>
        <text class="dg-foot" x="320" y="548" text-anchor="middle">associação ≠ causalidade</text>
      </svg>
    </div>
  </div>
  <aside class="notes"><p><b>Problema:</b> entre adultos de 18 a 29 anos, a quantidade de café consumida por dia está associada à dificuldade de concentração e à qualidade do sono? Questões complementares: com que frequência, quanto e a que horas esses jovens tomam café; quantos dormem menos de 7 horas; e, se o café não acompanhar a concentração, que outra variável acompanha.</p><p><b>Hipóteses:</b> H₀: ρ = 0; H₁: ρ ≠ 0, nível de 5%, testadas com o teste t do coeficiente de Pearson e com qui-quadrado nas tabelas de contingência. Correlação não prova causa.</p></aside>
</section>''')

add(f'''<!-- ======================= 5 · OBJETIVOS ======================= -->
<section class="slide" id="objetivos" data-title="Objetivos" data-section="Contexto" aria-label="Objetivos do estudo">
  <div class="kicker rv"><span class="kn">04</span>Objetivo do estudo</div>
  <h2 class="title rv-blur" style="--d:1">O que buscamos <em>responder</em></h2>
  <div class="fill">
  <div class="goal rv" style="--d:2"><span class="goal-tag">Objetivo geral</span><p>Analisar, com dados reais, a relação entre a quantidade de café e a dificuldade de concentração e o sono de <b>{N} adultos de 18 a 29 anos</b> (NHANES 2021–2023).</p></div>
  <div class="obj-label rv" style="--d:3">Objetivos específicos</div>
  <div class="obj-grid">
    <div class="obj rv" style="--d:3"><span class="obj-l">a</span><svg class="ic"><use href="#i-users"/></svg><p>Descrever o perfil da amostra</p></div>
    <div class="obj rv" style="--d:4"><span class="obj-l">b</span><svg class="ic"><use href="#i-coffee"/></svg><p>Medir frequência, quantidade e horário do café</p></div>
    <div class="obj rv" style="--d:5"><span class="obj-l">c</span><svg class="ic"><use href="#i-moon"/></svg><p>Descrever sono, problemas de sono e concentração</p></div>
    <div class="obj rv" style="--d:6"><span class="obj-l">d</span><svg class="ic"><use href="#i-sigma"/></svg><p>Calcular medidas de posição e dispersão</p></div>
    <div class="obj rv" style="--d:7"><span class="obj-l">e</span><svg class="ic"><use href="#i-scatter"/></svg><p>Estimar e testar correlações de Pearson</p></div>
    <div class="obj rv" style="--d:8"><span class="obj-l">f</span><svg class="ic"><use href="#i-spline"/></svg><p>Ajustar retas de regressão linear simples</p></div>
    <div class="obj rv" style="--d:9"><span class="obj-l">g</span><svg class="ic"><use href="#i-dice"/></svg><p>Calcular probabilidades simples, condicionais e binomial</p></div>
    <div class="obj rv" style="--d:10"><span class="obj-l">h</span><svg class="ic"><use href="#i-flag"/></svg><p>Propor decisões sustentadas pelos dados</p></div>
  </div>
  </div>
  <aside class="notes"><p>Objetivo geral: analisar, com dados reais, a relação entre a quantidade de café e a dificuldade de concentração e o sono de {N} adultos de 18 a 29 anos.</p><p>Específicos: (a) perfil da amostra; (b) frequência, quantidade e horário do café; (c) sono, problemas de sono e concentração; (d) medidas de posição e dispersão; (e) correlações de Pearson com teste de significância; (f) regressão linear simples; (g) probabilidades simples e condicionais e binomial; (h) decisões sustentadas pelos dados.</p></aside>
</section>''')

add('''<!-- ======================= 6 · DIVISOR METODOLOGIA ======================= -->
<section class="slide divider" id="d-metodologia" data-title="Parte 2 — Metodologia" data-section="Metodologia" data-chrome="off" aria-label="Parte 2: Metodologia">
  <div class="div-num" aria-hidden="true"><span class="rv-s" style="--d:0">02</span></div>
  <div class="div-body">
    <div class="kicker rv" style="--d:1">Parte 2 · Seções 5 a 9</div>
    <h2 class="div-title rv-blur" style="--d:2">Metodologia</h2>
    <p class="div-desc rv" style="--d:3">De onde vêm os dados, como a amostra foi formada e como cada variável foi medida.</p>
    <ul class="div-list">
      <li class="rv" style="--d:4">População e amostra</li><li class="rv" style="--d:5">Tipo de amostragem</li><li class="rv" style="--d:6">Variáveis e classificação</li><li class="rv" style="--d:7">Coleta e organização dos dados</li>
    </ul>
  </div>
</section>''')

fl = R['fluxo']
fl_rows = ''.join(
    f'<div class="fn-row{" last" if k == len(fl) - 1 else ""}" style="--i:{k}"><span class="fn-l">{E(lab)}</span><span class="fn-t"><i style="--w:{max(f["n"] / fl[0]["n"] * 100, 1.2):.2f}%"></i></span><span class="fn-v">{nf(f["n"], 0)}</span></div>'
    for k, (f, lab) in enumerate(zip(fl, ['Participantes do NHANES 2021–2023', 'Com 18 a 29 anos', 'Responderam aos itens de sono e concentração do PHQ-9', 'Têm horas de sono calculáveis', 'Completaram 2 recordatórios alimentares válidos'])))
add(f'''<!-- ======================= 7 · POPULAÇÃO ======================= -->
<section class="slide" id="populacao" data-title="População e amostra" data-section="Metodologia" aria-label="População e amostra">
  <div class="kicker rv"><span class="kn">05</span>População e amostra</div>
  <h2 class="title rv-blur" style="--d:1">{N} jovens reais, <em>nenhum dado ausente</em></h2>
  <div class="content" style="grid-template-columns:1fr 1fr">
    <div class="col-gap" style="justify-content:center">
      <div class="stats3">
        <div class="stat rv" style="--d:2"><b data-count="{N}">{N}</b><span>participantes analisados</span></div>
        <div class="stat rv" style="--d:3"><b>{nf(fl[0]['n'], 0)}</b><span>pessoas no NHANES 2021–2023</span></div>
        <div class="stat rv" style="--d:4"><b>0</b><span>valores ausentes nas variáveis</span></div>
      </div>
      <div class="callout rv" style="--d:5"><svg class="ic"><use href="#i-users"/></svg><p><b>População-alvo:</b> adultos de 18 a 29 anos dos EUA — a faixa que concentra os universitários. Os números descrevem esse grupo e <b>não se transferem automaticamente</b> para estudantes da Fatec.</p></div>
      <div class="callout rv" style="--d:6"><svg class="ic"><use href="#i-info"/></svg><p>Exigimos <b>dois dias</b> de registro alimentar: um dia mostra o que a pessoa comeu naquele dia; dois dias aproximam o <b>hábito</b>.</p></div>
    </div>
    <div class="card funnel-card rv-s" style="--d:3;padding:30px 34px">
      <div class="card-head"><h3><svg class="ic c-accent"><use href="#i-database"/></svg>Da base completa à amostra</h3></div>
      <div class="funnel">{fl_rows}</div>
      <p class="fn-cap">A maior perda está no 2º recordatório, feito por telefone dias depois do primeiro.</p>
    </div>
  </div>
  <aside class="notes"><p>Fonte: NHANES ago./2021–ago./2023, {nf(fl[0]['n'], 0)} participantes. Filtros: 18 a 29 anos ({nf(fl[1]['n'], 0)}); respostas válidas aos itens 3 e 7 do PHQ-9 ({nf(fl[2]['n'], 0)}); horas de sono calculáveis ({nf(fl[3]['n'], 0)}); dois recordatórios alimentares de 24 h classificados como confiáveis ({nf(fl[4]['n'], 0)}).</p><p>A população-alvo são adultos de 18 a 29 anos da população civil dos EUA. Os resultados descrevem esse grupo e não podem ser aplicados diretamente aos estudantes da Fatec.</p></aside>
</section>''')

add(f'''<!-- ======================= 8 · AMOSTRAGEM ======================= -->
<section class="slide" id="amostragem" data-title="Tipo de amostragem" data-section="Metodologia" aria-label="Tipo de amostragem">
  <div class="kicker rv"><span class="kn">06</span>Tipo de amostragem utilizada</div>
  <h2 class="title rv-blur" style="--d:1">Como as pessoas <em>foram sorteadas</em></h2>
  <p class="lead rv" style="--d:2">O NHANES sorteia em <b>quatro estágios</b>: condados → quarteirões → domicílios → pessoas, dentro de estratos. Sobre essa amostra, <b>não fizemos novo sorteio</b>: entraram todos os elegíveis.</p>
  <div class="fill">
  <div class="samp-grid">
    <div class="samp ok rv" style="--d:3"><div class="samp-ic"><svg class="ic"><use href="#i-layers"/></svg></div><h3>Estratificada</h3><p>15 estratos no ciclo 2021–2023</p><span class="samp-st ok"><svg class="ic"><use href="#i-check"/></svg>usada no NHANES</span></div>
    <div class="samp ok rv" style="--d:4"><div class="samp-ic"><svg class="ic"><use href="#i-building"/></svg></div><h3>Por conglomerados</h3><p>30 unidades primárias, sorteio em 4 estágios</p><span class="samp-st ok"><svg class="ic"><use href="#i-check"/></svg>usada no NHANES</span></div>
    <div class="samp rv" style="--d:5"><div class="samp-ic"><svg class="ic"><use href="#i-shuffle"/></svg></div><h3>Aleatória simples</h3><p>não houve sorteio único da população</p><span class="samp-st"><svg class="ic"><use href="#i-x"/></svg>não se aplica</span></div>
    <div class="samp rv" style="--d:6"><div class="samp-ic"><svg class="ic"><use href="#i-usercheck"/></svg></div><h3>Por conveniência</h3><p>ninguém foi escolhido por facilidade de acesso</p><span class="samp-st"><svg class="ic"><use href="#i-x"/></svg>não se aplica</span></div>
  </div>
  <div class="reg-card rv" style="--d:7">
    <div class="reg-label"><svg class="ic"><use href="#i-check"/></svg>Procedimento registrado no relatório</div>
    <p>“Amostra probabilística complexa do NHANES; analisados todos os {N} participantes elegíveis, sem novo sorteio.”</p>
    <span class="reg-note ok"><svg class="ic"><use href="#i-check-circle"/></svg>Com os pesos amostrais, o consumo de café passa de {pc(PR['P_A'])} para {pc(R['ponderado']['tomou_cafe'])}: a ponderação quase não muda os resultados.</span>
  </div>
  </div>
  <aside class="notes"><p>O NHANES usa amostragem probabilística complexa, estratificada e por conglomerados em quatro estágios: unidades primárias (condados ou grupos de condados) sorteadas dentro de estratos; segmentos (quarteirões); domicílios; e pessoas. O ciclo 2021–2023 tem 15 estratos e 30 unidades primárias mascaradas, com sobreamostragem por faixa etária.</p><p>Neste trabalho não houve novo sorteio: foram incluídos todos os participantes que atendiam aos critérios — uma subamostra por critérios de elegibilidade. As tabelas não usam pesos; com o peso de dois dias de dieta (WTDR2D), café passa de {pc(PR['P_A'])} para {pc(R['ponderado']['tomou_cafe'])}, sono abaixo de 7 h de {pc(PR['P_sono_insuf'])} para {pc(R['ponderado']['sono_insuf'])} e dificuldade de concentração de {pc(PR['P_C'])} para {pc(R['ponderado']['conc_prej'])}.</p></aside>
</section>''')

add('''<!-- ======================= 9 · VARIÁVEIS ======================= -->
<section class="slide" id="variaveis" data-title="Variáveis e classificação" data-section="Metodologia" aria-label="Variáveis e classificação">
  <div class="kicker rv"><span class="kn">07</span>Variáveis analisadas e classificação</div>
  <h2 class="title rv-blur" style="--d:1">Onze variáveis, <em>seis classificações</em></h2>
  <div class="card tbl-card rv" style="--d:2">
    <table class="tbl vars dense">
      <thead><tr><th>Variável</th><th>Classificação</th><th>Como foi medida</th></tr></thead>
      <tbody>
        <tr><td>ID e SEQN</td><td><span class="tag t-id">Identificador</span></td><td>Número do participante no NHANES; permite conferir cada linha.</td></tr>
        <tr><td>Gênero</td><td><span class="tag t-nom">Qualitativa nominal</span></td><td>Masculino ou feminino, na entrevista domiciliar.</td></tr>
        <tr><td>Idade</td><td><span class="tag t-quant">Quantitativa discreta</span></td><td>Anos completos, de 18 a 29.</td></tr>
        <tr><td>Situação na semana anterior</td><td><span class="tag t-nom">Qualitativa nominal</span></td><td>Trabalhando, estudando, procurando trabalho ou outra.</td></tr>
        <tr><td>Dias com café (0, 1 ou 2)</td><td><span class="tag t-ord">Qualitativa ordinal</span></td><td>Em quantos dos dois dias registrados houve café.</td></tr>
        <tr><td>Xícaras por dia</td><td><span class="tag t-quant">Quantitativa contínua</span></td><td>Volume médio de café dos dois dias ÷ 240 mL.</td></tr>
        <tr><td>Período de maior consumo</td><td><span class="tag t-nom">Qualitativa nominal</span></td><td>Manhã, tarde ou noite, pelo horário de cada bebida.</td></tr>
        <tr><td>Cafeína total (mg/dia)</td><td><span class="tag t-quant">Quantitativa contínua</span></td><td>Todas as fontes: café, refrigerante, chá, energético.</td></tr>
        <tr><td>Horas de sono</td><td><span class="tag t-quant">Quantitativa contínua</span></td><td>Calculadas dos horários habituais de dormir e acordar.</td></tr>
        <tr><td>Problemas de sono (0–3)</td><td><span class="tag t-ord">Escala ordinal*</span></td><td>PHQ-9, item 3: frequência nas últimas 2 semanas.</td></tr>
        <tr><td>Dificuldade de concentração (0–3)</td><td><span class="tag t-ord">Escala ordinal*</span></td><td>PHQ-9, item 7: mesma escala de frequência.</td></tr>
      </tbody>
    </table>
    <p class="tfoot">* 0 = nenhum dia · 1 = vários dias · 2 = mais da metade dos dias · 3 = quase todos os dias. Tratadas como números na correlação e na regressão, com conferência pelo coeficiente de Spearman.</p>
  </div>
  <aside class="notes"><p>A concentração vem do item 7 do PHQ-9: “Nas últimas duas semanas, com que frequência você se sentiu incomodado por dificuldade de se concentrar nas coisas, como ler o jornal ou assistir à televisão?”. O item 3 pergunta sobre dificuldade para pegar no sono, permanecer dormindo ou dormir demais. Os itens medem a frequência de uma dificuldade: valores maiores indicam pior concentração ou pior sono.</p><p>As escalas de 0 a 3 foram tratadas como numéricas nos cálculos de média, correlação e regressão; os resultados foram conferidos com o coeficiente de Spearman, próprio para dados ordinais.</p></aside>
</section>''')

g_f, g_m = fr('genero', 'Feminino'), fr('genero', 'Masculino')
add(f'''<!-- ======================= 10 · COLETA ======================= -->
<section class="slide" id="coleta" data-title="Coleta e organização" data-section="Metodologia" aria-label="Coleta e organização dos dados">
  <div class="kicker rv"><span class="kn">08–09</span>Processo de coleta · Organização dos dados</div>
  <h2 class="title rv-blur" style="--d:1">Dos arquivos do CDC <em>à análise</em></h2>
  <div class="content" style="grid-template-columns:1fr 1fr">
    <div class="col-gap">
      <div class="file-card rv-l" style="--d:2"><div class="file-ic"><svg class="ic"><use href="#i-database"/></svg></div><div><b>NHANES ago./2021–ago./2023 · 9 arquivos .xpt</b><span>Microdados públicos do CDC/NCHS, baixados em 07/11/2026</span></div></div>
      <ol class="pipeline">
        <li class="rv-l" style="--d:3"><span class="pn">1</span><div><b>Junção</b><span>Demografia, ocupação, sono, PHQ-9 e dieta unidos pelo número do participante.</span></div></li>
        <li class="rv-l" style="--d:4"><span class="pn">2</span><div><b>Seleção</b><span>18–29 anos, PHQ-9, sono e 2 recordatórios válidos: {N} pessoas.</span></div></li>
        <li class="rv-l" style="--d:5"><span class="pn">3</span><div><b>Café identificado</b><span>Códigos USDA 921xxxxx (coado, espresso, solúvel, latte, gelado); volume ÷ 240 mL.</span></div></li>
        <li class="rv-l" style="--d:6"><span class="pn">4</span><div><b>Horário</b><span>Hora de cada bebida comparada com a hora habitual de dormir.</span></div></li>
      </ol>
    </div>
    <div class="col-gap">
      <div class="card rv-r" style="--d:3">
        <div class="cc-title"><svg class="ic"><use href="#i-check-circle"/></svg>Conferência inicial</div>
        <div class="cc-row"><span>Registros</span><b>{N}</b></div>
        <div class="cc-row"><span>Valores ausentes</span><b>0</b></div>
        <div class="cc-split"><div class="cc-split-h"><span>Gênero</span><span><b>{g_f['n']}</b> feminino · <b>{g_m['n']}</b> masculino</span></div><div class="splitbar"><i class="sb-a" style="--w:{g_f['pct'] * 100:.1f}%"></i><i class="sb-b" style="--w:{g_m['pct'] * 100:.1f}%"></i></div></div>
        <div class="cc-split"><div class="cc-split-h"><span>Tomou café em ao menos 1 dia</span><span><b>{PR['n_A']}</b> sim · <b>{N - PR['n_A']}</b> não</span></div><div class="splitbar"><i class="sb-a" style="--w:{PR['P_A'] * 100:.1f}%"></i><i class="sb-c" style="--w:{(1 - PR['P_A']) * 100:.1f}%"></i></div></div>
      </div>
      <div class="callout rv-r" style="--d:5"><svg class="ic"><use href="#i-info"/></svg><p>Como o NHANES coletou: <b>entrevista domiciliar</b> (sono, ocupação), <b>PHQ-9 respondido no computador</b>, sem entrevistador, e <b>dois recordatórios de 24 h</b> por telefone, pelo método de múltiplas passagens do USDA.</p></div>
    </div>
  </div>
  <aside class="notes"><p><b>Coleta (NHANES):</b> entrevista domiciliar por computador (gênero, idade, ocupação e horários habituais de sono, adaptados do Munich ChronoType Questionnaire); PHQ-9 respondido em computador com áudio, sem entrevistador; dois recordatórios alimentares de 24 h por telefone (Automated Multiple-Pass Method do USDA), com horário, ocasião e quantidade de cada item, codificados pela base FNDDS 2021–2023, que fornece gramas e cafeína.</p><p><b>Tratamento:</b> 9 arquivos .xpt lidos em Python e unidos pelo SEQN; filtros de idade e completude; café = códigos 92100000–92189999 ({H['itens']} bebidas de {H['consumidores']} pessoas, {H['descafeinado_itens']} descafeinadas); xícaras = volume médio dos dois dias ÷ 240 mL. Nenhum valor foi alterado ou imputado. A planilha separa os dados brutos das variáveis derivadas, que são fórmulas.</p></aside>
</section>''')

add('''<!-- ======================= 11 · DIVISOR DADOS ======================= -->
<section class="slide divider" id="d-dados" data-title="Parte 3 — Os dados" data-section="Os dados" data-chrome="off" aria-label="Parte 3: Os dados">
  <div class="div-num" aria-hidden="true"><span class="rv-s" style="--d:0">03</span></div>
  <div class="div-body">
    <div class="kicker rv" style="--d:1">Parte 3 · Seções 10 e 11</div>
    <h2 class="div-title rv-blur" style="--d:2">Os dados</h2>
    <p class="div-desc rv" style="--d:3">O que os {N} jovens relataram sobre café, horário, sono e concentração.</p>
    <ul class="div-list">
      <li class="rv" style="--d:4">Gênero</li><li class="rv" style="--d:5">Café nos dois dias</li><li class="rv" style="--d:6">Xícaras por dia</li><li class="rv" style="--d:7">Horário do café</li><li class="rv" style="--d:8">Café × hora de dormir</li><li class="rv" style="--d:9">Problemas de sono</li><li class="rv" style="--d:10">Sono e concentração</li>
    </ul>
  </div>
</section>'''.replace('{N}', str(N)))

add(f'''<!-- ======================= 12 · GÊNERO ======================= -->
<section class="slide" id="genero" data-title="Gênero" data-section="Os dados" aria-label="Participantes por gênero">
  <div class="kicker rv"><span class="kn">10.1</span>Gênero · Gráfico 1</div>
  <h2 class="title rv-blur" style="--d:1">Participantes <em>por gênero</em></h2>
  <div class="content" style="grid-template-columns:.92fr 1.08fr;align-items:center">
    <div class="donut-wrap rv-s" style="--d:2">
      <div class="donut" id="donut-gen"></div>
      <div class="donut-center"><b data-count="{N}">{N}</b><span>participantes</span></div>
    </div>
    <div class="col-gap">
      <div class="legend-big">
        <div class="lb rv-r" style="--d:3"><i class="sw sw-a"></i><div><span class="lbn">Feminino</span><b><span data-count="{g_f['n']}">{g_f['n']}</span> <small>· <span data-count="{g_f['pct'] * 100:.1f}" data-dec="1" data-suf="%">{pc(g_f['pct'])}</span></small></b></div></div>
        <div class="lb rv-r" style="--d:4"><i class="sw sw-b"></i><div><span class="lbn">Masculino</span><b><span data-count="{g_m['n']}">{g_m['n']}</span> <small>· <span data-count="{g_m['pct'] * 100:.1f}" data-dec="1" data-suf="%">{pc(g_m['pct'])}</span></small></b></div></div>
      </div>
      <div class="card rv-r" style="--d:5;padding:22px 28px">
        <table class="tbl compact">
          <thead><tr><th>Categoria</th><th class="num">Frequência</th><th class="num">Percentual</th></tr></thead>
          <tbody>
            <tr><td>Feminino</td><td class="num">{g_f['n']}</td><td class="num">{pc(g_f['pct'])}</td></tr>
            <tr><td>Masculino</td><td class="num">{g_m['n']}</td><td class="num">{pc(g_m['pct'])}</td></tr>
            <tr class="total"><td>Total</td><td class="num">{N}</td><td class="num">100,0%</td></tr>
          </tbody>
        </table>
      </div>
      <p class="insight rv-r" style="--d:6"><svg class="ic"><use href="#i-info"/></svg><span>Elas tomam mais café: <b>{pc(GEN['Feminino']['tomou_cafe'])}</b> das mulheres e <b>{pc(GEN['Masculino']['tomou_cafe'])}</b> dos homens tomaram café em ao menos um dos dois dias.</span></p>
    </div>
  </div>
  <aside class="notes"><p>Tabela / Gráfico 1 — Gênero: {g_f['n']} mulheres ({pc(g_f['pct'])}) e {g_m['n']} homens ({pc(g_m['pct'])}). Idade média de {nf(D['idade']['media'], 1)} anos; a faixa de 18 a 21 anos é a maior ({pc(fr('faixa_etaria', '18 a 21')['pct'])}). Na semana anterior, {pc(fr('situacao', 'Trabalhando')['pct'])} trabalhavam e {pc(fr('situacao', 'Estudando')['pct'])} não trabalhavam porque estudavam.</p><p>As mulheres tomaram mais café ({pc(GEN['Feminino']['tomou_cafe'])} contra {pc(GEN['Masculino']['tomou_cafe'])}) e também relataram mais problemas de sono ({pc(GEN['Feminino']['sono_prej'])} contra {pc(GEN['Masculino']['sono_prej'])}).</p></aside>
</section>''')

c0, c1, c2 = fr('consumo', 'Nenhum dos dois dias'), fr('consumo', 'Um dos dois dias'), fr('consumo', 'Os dois dias')
add(f'''<!-- ======================= 13 · CONSUMO ======================= -->
<section class="slide" id="consumo" data-title="Café nos dois dias" data-section="Os dados" aria-label="Consumo de café nos dois dias de registro">
  <div class="kicker rv"><span class="kn">10.2</span>Consumo de café nos dois dias de registro</div>
  <h2 class="title rv-blur" style="--d:1">Café: <em>hábito de poucos</em></h2>
  <div class="content" style="grid-template-columns:.92fr 1.08fr;align-items:center">
    <div class="donut-wrap rv-s" style="--d:2">
      <div class="donut" id="ring-daily"></div>
      <div class="donut-center"><b data-count="{PR['P_A'] * 100:.1f}" data-dec="1" data-suf="%">{pc(PR['P_A'])}</b><span>tomaram café em ao menos 1 dia</span></div>
    </div>
    <div class="col-gap">
      <div class="card rv-r" style="--d:3;padding:22px 28px">
        <table class="tbl compact">
          <thead><tr><th>Dias com café</th><th class="num">Frequência</th><th class="num">Percentual</th></tr></thead>
          <tbody>
            <tr><td>Nenhum dos dois dias</td><td class="num">{c0['n']}</td><td class="num">{pc(c0['pct'])}</td></tr>
            <tr><td>Um dos dois dias</td><td class="num">{c1['n']}</td><td class="num">{pc(c1['pct'])}</td></tr>
            <tr class="hl"><td>Os dois dias</td><td class="num">{c2['n']}</td><td class="num">{pc(c2['pct'])}</td></tr>
            <tr class="total"><td>Total</td><td class="num">{N}</td><td class="num">100,0%</td></tr>
          </tbody>
        </table>
      </div>
      <div class="kpi rv-r" style="--d:4"><span>Consumo regular</span><b><span data-count="{c2['n']}">{c2['n']}</span> de {N}</b><small>tomaram café nos dois dias registrados ({pc(c2['pct'])})</small></div>
      <p class="insight rv-r" style="--d:5"><span class="tag-comp">hábito</span><span>Dos {CD['d1']} que tomaram café no 1º dia, <b>{pc(CD['p_d2_dado_d1'])}</b> tomaram de novo no 2º; entre os que não tomaram, só <b>{pc(CD['p_d2_dado_nao_d1'])}</b>.</span></p>
    </div>
  </div>
  <aside class="notes"><p>Tabela — Consumo de café nos dois dias: nenhum {c0['n']} ({pc(c0['pct'])}); um dia {c1['n']} ({pc(c1['pct'])}); os dois dias {c2['n']} ({pc(c2['pct'])}). Ao todo, {PR['n_A']} participantes ({pc(PR['P_A'])}) tomaram café em ao menos um dos dias — é o evento A da probabilidade e o p da binomial.</p><p>Os dois dias funcionam como teste de hábito: {CD['d1_e_d2']} dos {CD['d1']} que tomaram no primeiro dia ({pc(CD['p_d2_dado_d1'])}) repetiram no segundo; entre os {N - CD['d1']} que não tomaram no primeiro, só {pc(CD['p_d2_dado_nao_d1'])} tomaram no segundo. O consumo cresce com a idade: {pc(FX['18 a 21']['tomou_cafe'])} (18–21), {pc(FX['22 a 25']['tomou_cafe'])} (22–25) e {pc(FX['26 a 29']['tomou_cafe'])} (26–29).</p></aside>
</section>''')

xf = F['faixa_xicaras']
xrows = ''.join(f'<tr{" class=\"hl\"" if k == 0 else ""}><td>{E(r["cat"])}</td><td class="num">{r["n"]}</td><td class="num">{pc(r["pct"])}</td></tr>' for k, r in enumerate(xf))
fc = R['fontes_cafeina']
add(f'''<!-- ======================= 14 · XÍCARAS ======================= -->
<section class="slide" id="xicaras" data-title="Xícaras por dia" data-section="Os dados" aria-label="Quantidade de xícaras por dia">
  <div class="kicker rv"><span class="kn">10.3</span>Xícaras de café por dia · Gráfico 2</div>
  <h2 class="title rv-blur" style="--d:1">Quantas xícaras <em>por dia?</em></h2>
  <div class="content" style="grid-template-columns:1.38fr .62fr">
    <div class="card chart-card rv" style="--d:2">
      <div class="chart" id="bar-cups"></div>
      <div class="chart-cap">Gráfico 2 – Xícaras de 240 mL por dia, média dos dois dias de registro (frequência e percentual sobre {N} participantes).</div>
    </div>
    <div class="col-gap">
      <div class="card rv-r" style="--d:3;padding:20px 24px">
        <table class="tbl compact">
          <thead><tr><th>Xícaras/dia</th><th class="num">Freq.</th><th class="num">%</th></tr></thead>
          <tbody>
            {xrows}
            <tr class="total"><td>Total</td><td class="num">{N}</td><td class="num">100,0%</td></tr>
          </tbody>
        </table>
      </div>
      <div class="kpi rv-r" style="--d:4"><span>Entre quem toma café</span><b>{nf(dxc['media'], 2)} xícara</b><small>≈ {nf(dxc['media'] * 240, 0)} mL por dia · o café dá {pc(fc['Café'], 0)} da cafeína ingerida</small></div>
    </div>
  </div>
  <aside class="notes"><p>Tabela / Gráfico 2 — Xícaras por dia (média dos dois dias, xícara de 240 mL): 0 → {xf[0]['n']} ({pc(xf[0]['pct'])}); até 1 → {xf[1]['n']} ({pc(xf[1]['pct'])}); mais de 1 a 2 → {xf[2]['n']} ({pc(xf[2]['pct'])}); mais de 2 a 3 → {xf[3]['n']} ({pc(xf[3]['pct'])}); mais de 3 → {xf[4]['n']} ({pc(xf[4]['pct'])}).</p><p>Entre os {PR['n_A']} que tomaram café, a média é {nf(dxc['media'], 2)} xícara (≈ {nf(dxc['media'] * 240, 0)} mL) e metade fica entre {nf(dxc['q1'], 2)} e {nf(dxc['q3'], 2)} xícara. O café responde por {pc(fc['Café'])} da cafeína; refrigerantes {pc(fc['Refrigerantes'])}, chás {pc(fc['Chás'])}, energéticos {pc(fc['Energéticos'])}.</p></aside>
</section>''')

hmax = manha['n']
add(f'''<!-- ======================= 15 · HORÁRIO ======================= -->
<section class="slide" id="horario" data-title="Horário de maior consumo" data-section="Os dados" aria-label="Horário de maior consumo">
  <div class="kicker rv"><span class="kn">10.4</span>Período de maior consumo · Gráfico 3</div>
  <h2 class="title rv-blur" style="--d:1">A manhã <em>concentra o café</em></h2>
  <div class="tod-grid">
    <div class="tod lead1 rv" style="--d:2;--h:100%"><div class="tod-top"><svg class="ic"><use href="#i-sunrise"/></svg>Manhã<span class="tod-rank">5h–11h59</span></div><div class="tod-bar"><i></i></div><div class="tod-num"><b data-count="{manha['n']}">{manha['n']}</b><span data-count="{manha['pct'] * 100:.1f}" data-dec="1" data-suf="%">{pc(manha['pct'])}</span></div></div>
    <div class="tod rv" style="--d:3;--h:{tarde['n'] / hmax * 100:.1f}%"><div class="tod-top"><svg class="ic"><use href="#i-sun"/></svg>Tarde<span class="tod-rank">12h–17h59</span></div><div class="tod-bar"><i></i></div><div class="tod-num"><b data-count="{tarde['n']}">{tarde['n']}</b><span data-count="{tarde['pct'] * 100:.1f}" data-dec="1" data-suf="%">{pc(tarde['pct'])}</span></div></div>
    <div class="tod night rv" style="--d:4;--h:{max(noite['n'] / hmax * 100, 2):.1f}%"><div class="tod-top"><svg class="ic"><use href="#i-moon"/></svg>Noite<span class="tod-rank">18h–4h59</span></div><div class="tod-bar"><i></i></div><div class="tod-num"><b data-count="{noite['n']}">{noite['n']}</b><span data-count="{noite['pct'] * 100:.1f}" data-dec="1" data-suf="%">{pc(noite['pct'])}</span></div></div>
  </div>
  <p class="chart-cap rv" style="--d:5;margin-top:16px">Gráfico 3 – Período com o maior volume de café, entre os {PR['n_A']} participantes que tomaram café em ao menos um dos dois dias.</p>
  <aside class="notes"><p>Tabela / Gráfico 3 — Período de maior consumo (n = {PR['n_A']}): manhã {manha['n']} ({pc(manha['pct'])}), tarde {tarde['n']} ({pc(tarde['pct'])}) e noite {noite['n']} ({pc(noite['pct'])}).</p><p>O horário vem do próprio registro: cada bebida tem a hora em que o consumo começou. Considerando as {H['itens']} bebidas, {pc(H['por_periodo_itens']['Manhã'] / H['itens'])} começaram de manhã e a mediana do horário foi {hr_txt}.</p></aside>
</section>''')

add(f'''<!-- ======================= 16 · CAFÉ × HORA DE DORMIR (NOVO) ======================= -->
<section class="slide" id="cafe-sono" data-title="Café e hora de dormir" data-section="Os dados" data-mood="night" aria-label="Horário do café e hora de dormir">
  <div class="kicker rv"><span class="kn">10.5</span>Horário de cada xícara · Gráfico 4</div>
  <h2 class="title rv-blur" style="--d:1">Café às 9h, <em>sono às 23h</em></h2>
  <div class="content" style="grid-template-columns:1.32fr .68fr">
    <div class="card chart-card rv" style="--d:2">
      <div class="card-head"><h3>Bebidas de café por hora do dia</h3><span class="tag-comp">novo</span></div>
      <div class="chart" id="bar-hour"></div>
      <div class="chart-cap">Gráfico 4 – Hora de início de cada uma das {H['itens']} bebidas de café registradas nos dois recordatórios.</div>
    </div>
    <div class="kgrid">
      <div class="kg rv-r" style="--d:3"><b>{hr_txt}</b><span>mediana do horário das bebidas; <b>{pc(H['ate_12h_itens_pct'], 0)}</b> antes do meio-dia</span></div>
      <div class="kg sleep rv-r" style="--d:4"><b>{nf(IV['mediana_pessoa'], 0)} h</b><span>mediana entre o último café do dia e a <b>hora habitual de dormir</b></span></div>
      <div class="kg rv-r" style="--d:5"><b>{pc(IV['pessoas_menor_88'] / IV['pessoas'])}</b><span>dos que tomam café o fizeram a menos de <b>8,8 h</b> de dormir ({IV['pessoas_menor_88']} pessoas; {IV['pessoas_menor_6']} a menos de 6 h)</span></div>
    </div>
  </div>
  <aside class="notes"><p><b>Novo cálculo, possível só com dados reais:</b> o recordatório informa a hora de cada bebida e o questionário de sono informa a hora habitual de dormir (de dia útil ou de fim de semana, conforme o dia do registro).</p><p>O pico de consumo vai das 8h às 11h; após as 18h foram só {H['por_periodo_itens']['Noite']} bebidas. A mediana do menor intervalo entre o último café e a hora de dormir foi de {nf(IV['mediana_pessoa'], 0)} horas. Mesmo assim, {IV['pessoas_menor_88']} dos {IV['pessoas']} que tomaram café ({pc(IV['pessoas_menor_88'] / IV['pessoas'])}) o fizeram a menos de 8,8 h do sono — limite da metanálise de Gardiner et al. (2023) — e {IV['pessoas_menor_6']} a menos de 6 h. Isso ajuda a explicar por que o café quase não aparece associado ao sono: para a maioria, a cafeína chega cedo.</p></aside>
</section>''')

sp_yes = fr('sono_prej', 'Sim'); sp_no = fr('sono_prej', 'Não')
add(f'''<!-- ======================= 17 · PROBLEMAS DE SONO ======================= -->
<section class="slide" id="sono" data-title="Problemas de sono" data-section="Os dados" data-mood="night" aria-label="Problemas de sono">
  <div class="kicker rv"><span class="kn">10.6</span>Problemas de sono (PHQ-9, item 3) · Gráfico 5</div>
  <h2 class="title rv-blur" style="--d:1">Dormir mal <em>é comum</em></h2>
  <div class="content" style="grid-template-columns:1fr 1fr">
    <div class="card col-gap rv-l" style="--d:2;justify-content:space-between">
      <div class="duo">
        <div class="duo-item"><span class="duo-l">Nenhum dia</span><b data-count="{sp_no['n']}">{sp_no['n']}</b><small data-count="{sp_no['pct'] * 100:.1f}" data-dec="1" data-suf="%">{pc(sp_no['pct'])}</small></div>
        <div class="duo-item sleep"><span class="duo-l">Vários dias ou mais</span><b data-count="{sp_yes['n']}">{sp_yes['n']}</b><small data-count="{sp_yes['pct'] * 100:.1f}" data-dec="1" data-suf="%">{pc(sp_yes['pct'])}</small></div>
      </div>
      <div class="stackbar"><i class="sbk-a" style="--w:{sp_no['pct'] * 100:.1f}%">Não · {pc(sp_no['pct'])}</i><i class="sbk-b" style="--w:{sp_yes['pct'] * 100:.1f}%">Sim · {pc(sp_yes['pct'])}</i></div>
      <p class="muted-p"><b>Mais da metade</b> teve dificuldade para dormir, acordou à noite ou dormiu demais nas últimas duas semanas; <b>{pc(fr('prob_sono', 'Quase todos os dias')['pct'])}</b> quase todos os dias. É o evento B.</p>
      <div class="chart-cap" style="margin:0">Gráfico 5 – Participantes com problemas de sono em vários dias ou mais (PHQ-9, item 3).</div>
    </div>
    <div class="card chart-card rv-r" style="--d:3">
      <div class="card-head"><h3>Problemas de sono por dias com café</h3><span class="tag-comp">cruzamento</span></div>
      <div class="chart" id="bar-imp"></div>
      <p class="chart-note">Proporções quase iguais: o café não separa quem dorme mal de quem dorme bem (χ² = {nf(AB['chi2'], 2)}; p = {nf(AB['p'], 2)}).</p>
    </div>
  </div>
  <aside class="notes"><p>Gráfico 5 — Problemas de sono nas últimas duas semanas: nenhum dia {fr('prob_sono', 'Nenhum dia')['n']} ({pc(fr('prob_sono', 'Nenhum dia')['pct'])}); vários dias {fr('prob_sono', 'Vários dias')['n']} ({pc(fr('prob_sono', 'Vários dias')['pct'])}); mais da metade {fr('prob_sono', 'Mais da metade dos dias')['n']} ({pc(fr('prob_sono', 'Mais da metade dos dias')['pct'])}); quase todos {fr('prob_sono', 'Quase todos os dias')['n']} ({pc(fr('prob_sono', 'Quase todos os dias')['pct'])}).</p><p>Cruzamento: relatam problemas de sono {pc(GD[0]['sono_prej'])} de quem não tomou café, {pc(GD[1]['sono_prej'])} de quem tomou em um dia e {pc(GD[2]['sono_prej'])} de quem tomou nos dois. Teste qui-quadrado (tomou café × problemas de sono): χ² = {nf(AB['chi2'], 2)}; p = {nf(AB['p'], 2)}.</p></aside>
</section>''')

su = F['sono_util']; dcf = F['dif_conc']
add(f'''<!-- ======================= 18 · SONO E CONCENTRAÇÃO ======================= -->
<section class="slide" id="faixas" data-title="Sono e concentração" data-section="Os dados" aria-label="Horas de sono e dificuldade de concentração">
  <div class="kicker rv"><span class="kn">10.7</span>Horas de sono · Dificuldade de concentração</div>
  <h2 class="title rv-blur" style="--d:1">Quanto dormem <em>e como se concentram</em></h2>
  <div class="content" style="grid-template-columns:1fr 1fr">
    <div class="card rv-l" style="--d:2">
      <div class="card-head"><h3><svg class="ic c-sleep"><use href="#i-moon"/></svg>Horas de sono em dias úteis</h3><span class="pill sleep">{pc(PR['P_sono_insuf'])} abaixo de 7 h</span></div>
      <div class="hbars" data-kind="sleep" data-v="{','.join(str(r['n']) for r in su)}" data-labels="menos de 6 h|6 a 6,5 h|7 a 7,5 h|8 a 8,5 h|9 h ou mais"></div>
      <p class="band-insight">Média de <b>{nf(D['sono_util']['media'], 2)} h</b>; no fim de semana sobe para {nf(D['sono_fds']['media'], 2)} h, e <b>{pc(R['sono_fds_vs_util']['pct_mais_1h'])}</b> dormem 1 h a mais nas folgas.</p>
    </div>
    <div class="card rv-r" style="--d:3">
      <div class="card-head"><h3><svg class="ic c-conc"><use href="#i-target"/></svg>Dificuldade de concentração</h3><span class="pill conc">{pc(PR['P_C'])} em vários dias ou mais</span></div>
      <div class="hbars" data-kind="conc" data-v="{','.join(str(r['n']) for r in dcf)}" data-labels="nenhum dia|vários dias|mais da metade|quase todos"></div>
      <p class="band-insight">Mediana <b>0</b>: a maioria não teve o problema; <b>{pc((fr('dif_conc', 'Mais da metade dos dias')['n'] + fr('dif_conc', 'Quase todos os dias')['n']) / N)}</b> tiveram em mais da metade dos dias. É o evento C.</p>
    </div>
  </div>
  <p class="foot-note rv" style="--d:5"><svg class="ic"><use href="#i-info"/></svg>Sono calculado pelo NCHS a partir dos horários habituais de dormir e acordar; concentração pelo item 7 do PHQ-9 (últimas duas semanas).</p>
  <aside class="notes"><p>Horas de sono em dias úteis: menos de 6 h {su[0]['n']} ({pc(su[0]['pct'])}); 6 a 6,5 h {su[1]['n']} ({pc(su[1]['pct'])}); 7 a 7,5 h {su[2]['n']} ({pc(su[2]['pct'])}); 8 a 8,5 h {su[3]['n']} ({pc(su[3]['pct'])}); 9 h ou mais {su[4]['n']} ({pc(su[4]['pct'])}). {PR['n_sono_insuf']} participantes ({pc(PR['P_sono_insuf'])}) dormem menos de 7 h, o mínimo recomendado para adultos (Watson et al., 2015). Diferença média fim de semana × dias úteis: {nf(R['sono_fds_vs_util']['media_dif'], 2)} h (t pareado, p &lt; 0,001).</p><p>Dificuldade de concentração: nenhum dia {dcf[0]['n']} ({pc(dcf[0]['pct'])}); vários dias {dcf[1]['n']} ({pc(dcf[1]['pct'])}); mais da metade {dcf[2]['n']} ({pc(dcf[2]['pct'])}); quase todos {dcf[3]['n']} ({pc(dcf[3]['pct'])}).</p></aside>
</section>''')

add('''<!-- ======================= 19 · DIVISOR ESTATÍSTICA ======================= -->
<section class="slide divider" id="d-estatistica" data-title="Parte 4 — Análise estatística" data-section="Análise estatística" data-chrome="off" aria-label="Parte 4: Análise estatística">
  <div class="div-num" aria-hidden="true"><span class="rv-s" style="--d:0">04</span></div>
  <div class="div-body">
    <div class="kicker rv" style="--d:1">Parte 4 · Seções 12 a 16</div>
    <h2 class="div-title rv-blur" style="--d:2">Análise <em>estatística</em></h2>
    <p class="div-desc rv" style="--d:3">Medidas, correlação, regressão e probabilidade aplicadas aos dados reais — agora com testes de hipótese.</p>
    <ul class="div-list">
      <li class="rv" style="--d:4">Medidas de posição e dispersão</li><li class="rv" style="--d:5">Correlação de Pearson</li><li class="rv" style="--d:6">Regressão linear simples</li><li class="rv" style="--d:7">Probabilidade simples e condicional</li><li class="rv" style="--d:8">Distribuição binomial</li>
    </ul>
  </div>
</section>''')

def srow(dot, lab, d, k=2, mode_k=None):
    mk = k if mode_k is None else mode_k
    return (f'<tr><td><span class="vdot {dot}"></span>{lab}</td><td class="num">{nf(d["media"], k)}</td><td class="num">{nf(d["mediana"], k)}</td>'
            f'<td class="num">{nf(d["moda"], mk)}</td><td class="num">{nf(d["amplitude"], k)}</td><td class="num">{nf(d["dp"], k)}</td>'
            f'<td class="num">{nf(d["q1"], k)}</td><td class="num">{nf(d["q3"], k)}</td></tr>')
add(f'''<!-- ======================= 20 · MEDIDAS ======================= -->
<section class="slide" id="medidas" data-title="Medidas estatísticas" data-section="Análise estatística" aria-label="Medidas de posição e dispersão">
  <div class="kicker rv"><span class="kn">12</span>Cálculos estatísticos</div>
  <h2 class="title rv-blur" style="--d:1">Medidas de posição <em>e dispersão</em></h2>
  <div class="fill">
  <div class="gloss">
    <div class="gl rv" style="--d:2"><b>Média</b><span>o valor médio</span></div>
    <div class="gl rv" style="--d:2.4"><b>Mediana</b><span>divide os dados ordenados em duas metades</span></div>
    <div class="gl rv" style="--d:2.8"><b>Moda</b><span>o valor mais frequente</span></div>
    <div class="gl rv" style="--d:3.2"><b>Amplitude</b><span>maior valor − menor valor</span></div>
    <div class="gl rv" style="--d:3.6"><b>Desvio padrão</b><span>o quanto os valores se afastam da média</span></div>
    <div class="gl rv" style="--d:4"><b>Quartis</b><span>Q1 = 25% e Q3 = 75% dos dados</span></div>
  </div>
  <div class="card tbl-card rv" style="--d:4">
    <table class="tbl stats dense">
      <thead><tr><th>Variável</th><th>Média</th><th>Mediana</th><th>Moda</th><th>Amplitude</th><th>Desvio padrão*</th><th>Q1</th><th>Q3</th></tr></thead>
      <tbody>
        {srow('v-cups', 'Xícaras/dia — todos', dx)}
        {srow('v-cups', f'Xícaras/dia — quem toma (n = {dxc["n"]})', dxc)}
        {srow('v-conc', 'Cafeína total (mg/dia)', D['cafeina'], 1)}
        {srow('v-sleep', 'Sono em dias úteis (h)', D['sono_util'])}
        {srow('v-conc', 'Dificuldade de concentração (0–3)', D['dif_conc'])}
        {srow('v-age', 'Idade (anos)', D['idade'])}
      </tbody>
    </table>
    <p class="tfoot">* Desvio padrão amostral (n − 1). Quartis pelo método inclusivo (função QUARTIL do Excel). Todas as medidas estão na aba Medidas da planilha.</p>
  </div>
  </div>
  <aside class="notes"><p>Medidas calculadas sobre os {N} participantes (e sobre os {dxc['n']} que tomaram café, na segunda linha). Xícaras/dia, todos: média {nf(dx['media'], 3)}, mediana 0, moda 0, DP {nf(dx['dp'], 3)}; quem toma: média {nf(dxc['media'], 2)}, mediana {nf(dxc['mediana'], 2)}. Cafeína: média {nf(D['cafeina']['media'], 1)} mg, mediana {nf(D['cafeina']['mediana'], 1)} mg. Sono: média {nf(D['sono_util']['media'], 2)} h, mediana e moda 8 h. Idade: média {nf(D['idade']['media'], 2)} anos.</p><p>Desvio padrão amostral (n − 1); quartis pelo método inclusivo.</p></aside>
</section>''')

def bp(kind, d, dom, ticks, k=2):
    return (f'data-kind="{kind}" data-min="{d["minimo"]}" data-q1="{d["q1"]}" data-med="{d["mediana"]}" data-q3="{d["q3"]}" '
            f'data-max="{d["maximo"]}" data-mean="{d["media"]:.4f}" data-dom="{dom}" data-ticks="{ticks}"')
dca, dsu, did = D['cafeina'], D['sono_util'], D['idade']
add(f'''<!-- ======================= 21 · INTERPRETAÇÃO ======================= -->
<section class="slide" id="interpretacao" data-title="Interpretação das medidas" data-section="Análise estatística" aria-label="Interpretação das medidas">
  <div class="kicker rv"><span class="kn">12</span>Interpretação das medidas</div>
  <h2 class="title rv-blur" style="--d:1">O que as medidas <em>revelam</em></h2>
  <div class="bp-grid">
    <div class="card bp-card rv" style="--d:2">
      <div class="bp-head"><span class="vdot v-cups"></span><h3>Xícaras/dia · quem toma café</h3><span class="bp-vals">mín {nf(dxc['minimo'], 2)} · Q1 {nf(dxc['q1'], 2)} · Md {nf(dxc['mediana'], 2)} · Q3 {nf(dxc['q3'], 2)} · máx {nf(dxc['maximo'], 0)}</span></div>
      <div class="boxplot" {bp('cups', dxc, '0,8', '0,2,4,6,8')}></div>
      <p>Metade bebe entre <b>{nf(dxc['q1'] * 240, 0)} e {nf(dxc['q3'] * 240, 0)} mL</b> por dia. O máximo de 8 xícaras é um caso isolado.</p>
    </div>
    <div class="card bp-card rv" style="--d:3">
      <div class="bp-head"><span class="vdot v-conc"></span><h3>Cafeína total (mg/dia)</h3><span class="bp-vals">mín 0 · Q1 {nf(dca['q1'], 1)} · Md {nf(dca['mediana'], 1)} · Q3 {nf(dca['q3'], 1)} · máx {nf(dca['maximo'], 0)}</span></div>
      <div class="boxplot" {bp('conc', dca, '0,850', '0,200,400,600,800')}></div>
      <p>Média de <b>{nf(dca['media'], 1)} mg</b>, menos que uma xícara de café coado; só {R['cafeina_acima_400']} pessoas passam de 400 mg.</p>
    </div>
    <div class="card bp-card rv" style="--d:4">
      <div class="bp-head"><span class="vdot v-sleep"></span><h3>Sono em dias úteis (h)</h3><span class="bp-vals">mín {nf(dsu['minimo'], 0)} · Q1 {nf(dsu['q1'], 0)} · Md {nf(dsu['mediana'], 0)} · Q3 {nf(dsu['q3'], 0)} · máx {nf(dsu['maximo'], 0)}</span></div>
      <div class="boxplot" {bp('sleep', dsu, '0,14', '0,2,4,6,8,10,12,14')}></div>
      <p>Metade dorme entre <b>7 e 9 h</b>; os extremos (2 e 14) são os códigos-limite do NHANES.</p>
    </div>
    <div class="card bp-card rv" style="--d:5">
      <div class="bp-head"><span class="vdot v-age"></span><h3>Idade (anos)</h3><span class="bp-vals">mín 18 · Q1 {nf(did['q1'], 0)} · Md {nf(did['mediana'], 0)} · Q3 {nf(did['q3'], 2)} · máx 29</span></div>
      <div class="boxplot" {bp('age', did, '17,30', '18,20,22,24,26,28,30')}></div>
      <p>Idade média de <b>{nf(did['media'], 1)} anos</b>; quanto mais velho, mais café (r = {nf(P['idade_xic']['r'], 3)}).</p>
    </div>
  </div>
  <div class="bp-legend rv" style="--d:6">
    <span><svg viewBox="0 0 34 20"><rect x="2" y="3" width="30" height="14" rx="4" fill="var(--crema)" fill-opacity=".2" stroke="var(--crema)" stroke-width="2"/></svg>Q1 a Q3 (50% centrais)</span>
    <span><svg viewBox="0 0 34 20"><line x1="17" y1="1" x2="17" y2="19" stroke="var(--text)" stroke-width="4" stroke-linecap="round"/></svg>mediana</span>
    <span><svg viewBox="0 0 34 20"><path d="M17 3l7 7-7 7-7-7z" fill="var(--text)"/></svg>média</span>
    <span><svg viewBox="0 0 34 20"><line x1="2" y1="10" x2="32" y2="10" stroke="var(--muted)" stroke-width="2"/><line x1="2" y1="4" x2="2" y2="16" stroke="var(--muted)" stroke-width="2"/><line x1="32" y1="4" x2="32" y2="16" stroke="var(--muted)" stroke-width="2"/></svg>mínimo a máximo</span>
  </div>
  <aside class="notes"><p>Café entre quem toma: média {nf(dxc['media'], 2)} e mediana {nf(dxc['mediana'], 2)} xícara; metade entre {nf(dxc['q1'] * 240, 0)} e {nf(dxc['q3'] * 240, 0)} mL por dia. A distribuição tem cauda à direita (máximo de 8 xícaras, quem relatou 2,9 litros de café coado num dia).</p><p>Cafeína: média {nf(dca['media'], 1)} mg/dia, mediana {nf(dca['mediana'], 1)} mg; {R['cafeina_acima_400']} pessoas ({pc(R['cafeina_acima_400'] / N)}) acima de 400 mg/dia (limite da FDA). Sono: metade entre 7 e 9 h. Idade: média {nf(did['media'], 2)} anos; correlação idade × xícaras r = {nf(P['idade_xic']['r'], 3)}.</p></aside>
</section>''')

add(f'''<!-- ======================= 22 · FÓRMULAS ======================= -->
<section class="slide" id="formulas" data-title="Fórmulas" data-section="Análise estatística" aria-label="Fórmulas utilizadas">
  <div class="kicker rv"><span class="kn">12.1</span>Fórmulas utilizadas</div>
  <h2 class="title rv-blur" style="--d:1">Como cada medida <em>é calculada</em></h2>
  <div class="f-grid">
    <div class="fcard rv" style="--d:2"><span class="f-name">Média</span><div class="math"><span class="ov">x</span> <span class="up">=</span> <span class="frac"><span>Σx</span><span>n</span></span></div><p>Soma de todos os valores dividida pelo número de observações.</p></div>
    <div class="fcard rv" style="--d:3"><span class="f-name">Mediana</span><div class="math">Md <span class="up">=</span> <span class="frac"><span>x<sub>248º</sub> + x<sub>249º</sub></span><span class="up">2</span></span></div><p>Valor central dos dados ordenados. Como n = {N} é par, é a média entre o 248º e o 249º valores.</p></div>
    <div class="fcard rv" style="--d:4"><span class="f-name">Moda</span><div class="math">Mo <span class="up">=</span> <span class="tx">valor de maior frequência</span></div><p>O valor que aparece mais vezes na base.</p></div>
    <div class="fcard rv" style="--d:5"><span class="f-name">Amplitude</span><div class="math">A <span class="up">=</span> <span>x<sub>máx</sub></span> <span class="up">−</span> <span>x<sub>mín</sub></span></div><p>Diferença entre o maior e o menor valor observado.</p></div>
    <div class="fcard rv" style="--d:6"><span class="f-name">Variância e desvio padrão</span><div class="math">s² <span class="up">=</span> <span class="frac"><span>Σ(x − <span class="ov">x</span>)²</span><span>n − 1</span></span><span class="up" style="margin-left:.5em">·</span> s <span class="up">=</span> <span class="sqrt"><span>s²</span></span></div><p>Versões amostrais, com n − 1 no denominador.</p></div>
    <div class="fcard rv" style="--d:7"><span class="f-name">Quartis</span><div class="math">Q1 <span class="tx">→ 25%</span> <span class="up">·</span> Q3 <span class="tx">→ 75%</span></div><p>Q1 deixa 25% dos dados abaixo e Q3, 75%; entre eles está a metade central.</p></div>
  </div>
  <aside class="notes"><p>Média x̄ = Σx ÷ n. Mediana: com n = {N} (par), média entre o 248º e o 249º valores ordenados. Moda: valor mais frequente. Amplitude: máximo − mínimo. Variância amostral s² = Σ(x − x̄)² ÷ (n − 1); desvio padrão s = √s². Quartis pelo método inclusivo.</p></aside>
</section>''')

add(f'''<!-- ======================= 23 · EXEMPLO ======================= -->
<section class="slide" id="exemplo" data-title="Exemplo: xícaras por dia" data-section="Análise estatística" aria-label="Exemplo completo com xícaras por dia">
  <div class="kicker rv"><span class="kn">12.1.1</span>Exemplo completo: xícaras de café por dia</div>
  <h2 class="title rv-blur" style="--d:1">Passo a passo <em>com os {N} registros</em></h2>
  <div class="steps-grid">
    <div class="step rv" style="--d:2"><span class="sl"><i>1</i>Média</span><div class="eq"><span class="ov">x</span> = Σx ÷ n<br>= {nf(dx['soma'], 3)} ÷ {N}</div><div class="res">{nf(dx['media'], 4)} <small>xícara por dia</small></div></div>
    <div class="frag"><div class="step"><span class="sl"><i>2</i>Mediana</span><div class="eq">248º e 249º valores ordenados = 0<br>({dx['moda_freq']} pessoas não tomaram café)</div><div class="res">Md = 0</div></div></div>
    <div class="frag"><div class="step"><span class="sl"><i>3</i>Moda</span><div class="eq">O valor 0 aparece {dx['moda_freq']} vezes,<br>a maior frequência da base</div><div class="res">Mo = 0</div></div></div>
    <div class="frag"><div class="step"><span class="sl"><i>4</i>Amplitude</span><div class="eq">A = maior − menor<br>= {nf(dx['maximo'], 0)} − 0</div><div class="res">A = {nf(dx['amplitude'], 0)} <small>xícaras</small></div></div></div>
    <div class="frag"><div class="step"><span class="sl"><i>5</i>Desvio padrão</span><div class="eq">Σ(x − <span class="ov">x</span>)² = {nf(dx['sq_desvios'], 3)}<br>s² = {nf(dx['sq_desvios'], 3)} ÷ {N - 1} = {nf(dx['variancia'], 4)}<br>s = √{nf(dx['variancia'], 4)}</div><div class="res">s = {nf(dx['dp'], 4)}</div></div></div>
    <div class="frag"><div class="step"><span class="sl"><i>6</i>Quartis</span><div class="eq">25% dos registros até 0 xícara<br>75% dos registros até {nf(dx['q3'], 3)} xícara</div><div class="res">Q1 = 0 · Q3 = {nf(dx['q3'], 2)}</div></div></div>
  </div>
  <aside class="notes"><p><b>Média:</b> Σx = {nf(dx['soma'], 3)}; x̄ = {nf(dx['soma'], 3)} ÷ {N} = {nf(dx['media'], 4)} xícara por dia. <b>Mediana:</b> o 248º e o 249º valores ordenados são 0, porque {dx['moda_freq']} participantes não tomaram café; Md = 0. <b>Moda:</b> 0. <b>Amplitude:</b> {nf(dx['maximo'], 0)} − 0 = {nf(dx['amplitude'], 0)}. <b>Desvio padrão:</b> Σ(x − x̄)² = {nf(dx['sq_desvios'], 3)}; s² = {nf(dx['variancia'], 4)}; s = {nf(dx['dp'], 4)}. <b>Quartis:</b> Q1 = 0 e Q3 = {nf(dx['q3'], 3)}.</p><p>Média e mediana contam histórias diferentes: a média sugere consumo espalhado; a mediana zero mostra que a maioria não tomou café. Entre quem toma, a média é {nf(dxc['media'], 2)} xícara. Avance para revelar cada passo (5 cliques).</p></aside>
</section>''')

add(f'''<!-- ======================= 24 · CORRELAÇÃO ======================= -->
<section class="slide" id="correlacao" data-title="Correlação" data-section="Análise estatística" data-mood="focus" aria-label="Correlação entre café e concentração">
  <div class="kicker rv"><span class="kn">13</span>Correlação e interpretação · Gráfico 6</div>
  <h2 class="title rv-blur" style="--d:1">Café × concentração: <em>há relação?</em></h2>
  <div class="content" style="grid-template-columns:1.18fr .82fr">
    <div class="card chart-card rv-l" style="--d:2">
      <div class="chart" id="scatter"></div>
      <div class="chart-cap">Gráfico 6 – Xícaras por dia × dificuldade de concentração (0 a 3), com a reta ajustada. Pontos deslocados levemente para evitar sobreposição.</div>
    </div>
    <div class="col-gap">
      <div class="card r-card rv-r" style="--d:3">
        <span class="r-label">Coeficiente de correlação de Pearson</span>
        <div class="r-big neu">r = <span data-count="{xc['r']:.3f}" data-dec="3" data-delay="600">{nf(xc['r'], 3)}</span></div>
        <span class="pill neu"><svg class="ic"><use href="#i-ban"/></svg>nula · p = {nf(xc['p'], 2)}</span>
        <div class="rmeter" data-r="{xc['r']:.4f}" data-cls="conc"></div>
      </div>
      <p class="body-p rv-r" style="--d:4">A quantidade de café <b>não acompanha</b> a dificuldade de concentração. Intervalo de 95%: de {nf(xc['ci_lo'], 2)} a +{nf(xc['ci_hi'], 2)}; Spearman: {nf(xc['spearman'], 3)}. Não se rejeita H₀.</p>
      <div class="factors rv-r" style="--d:5"><span class="f-title">O que pode pesar mais que o café</span><span class="chip">problemas de sono</span><span class="chip">humor</span><span class="chip">idade</span><span class="chip">trabalho</span><span class="chip">tolerância à cafeína</span></div>
    </div>
  </div>
  <aside class="notes"><p>Variáveis: X = xícaras por dia (média de dois dias) e Y = dificuldade de concentração (PHQ-9, item 7, de 0 a 3). r = {nf(xc['r'], 4)}; t = {nf(xc['t'], 3)} com {N - 2} graus de liberdade; p = {nf(xc['p'], 3)}; IC 95% de {nf(xc['ci_lo'], 3)} a {nf(xc['ci_hi'], 3)}; Spearman = {nf(xc['spearman'], 3)}.</p><p>Interpretação: associação nula. Em todos os níveis de dificuldade há quem não tome café e quem tome duas ou três xícaras. Retirando os 5 maiores consumidores (mais de 4 xícaras), r = {nf(R['robustez']['xic_conc_r'], 3)}; só entre os {R['robustez']['consumidores_n']} que tomaram café, r = {nf(R['robustez']['consumidores_xic_conc_r'], 3)}.</p></aside>
</section>''')

add(f'''<!-- ======================= 25 · PEARSON ======================= -->
<section class="slide" id="pearson" data-title="Cálculo de Pearson" data-section="Análise estatística" data-mood="focus" aria-label="Cálculo da correlação de Pearson">
  <div class="kicker rv"><span class="kn">13.1</span>Correlação de Pearson: xícaras e concentração</div>
  <h2 class="title rv-blur" style="--d:1">Calculando <em>o r de Pearson</em></h2>
  <div class="content" style="grid-template-columns:.98fr 1.02fr;gap:34px;margin-top:34px">
    <div class="col-gap">
      <div class="card formula-hero rv" style="--d:2">
        <div class="math">r <span class="up">=</span> <span class="frac"><span>n·ΣXY − (ΣX)(ΣY)</span><span><span class="sqrt"><span>[n·ΣX² − (ΣX)²]·[n·ΣY² − (ΣY)²]</span></span></span></span></div>
        <div class="xy-def"><span><b>X</b>xícaras de café por dia</span><span><b>Y</b>dificuldade de concentração (0–3)</span></div>
      </div>
      <div class="sums rv" style="--d:3">
        <div class="sum"><span>n</span><b>{N}</b></div><div class="sum"><span>ΣX</span><b>{nf(xc['Sx'], 3)}</b></div><div class="sum"><span>ΣY</span><b>{nf(xc['Sy'], 0)}</b></div>
        <div class="sum"><span>ΣX²</span><b>{nf(xc['Sxx'], 3)}</b></div><div class="sum"><span>ΣY²</span><b>{nf(xc['Syy'], 0)}</b></div><div class="sum"><span>ΣXY</span><b>{nf(xc['Sxy'], 3)}</b></div>
      </div>
      <p class="sum-cap rv" style="--d:4">Somatórios da aba Correlação e regressão, com os {N} registros.</p>
    </div>
    <div class="col-gap calc-list">
      <div class="frag"><div class="calc"><span class="cl">Numerador</span><div class="ce">{N} × {nf(xc['Sxy'], 3)} − ({nf(xc['Sx'], 3)} × {xc['Sy']:.0f})<br>= {nf(N * xc['Sxy'], 2)} − {nf(xc['Sx'] * xc['Sy'], 2)}</div><b class="cr">{nf(xc['num'], 2)}</b></div></div>
      <div class="frag"><div class="calc"><span class="cl">1º termo do denominador</span><div class="ce">{N} × {nf(xc['Sxx'], 3)} − {nf(xc['Sx'], 3)}²<br>= {nf(N * xc['Sxx'], 2)} − {nf(xc['Sx'] ** 2, 2)}</div><b class="cr">{nf(xc['t1'], 2)}</b></div></div>
      <div class="frag"><div class="calc"><span class="cl">2º termo do denominador</span><div class="ce">{N} × {xc['Syy']:.0f} − {xc['Sy']:.0f}²<br>= {nf(N * xc['Syy'], 0)} − {nf(xc['Sy'] ** 2, 0)}</div><b class="cr">{nf(xc['t2'], 0)}</b></div></div>
      <div class="frag"><div class="calc"><span class="cl">Denominador</span><div class="ce">√({nf(xc['t1'], 2)} × {nf(xc['t2'], 0)})</div><b class="cr">≈ {nf(xc['den'], 2)}</b></div></div>
      <div class="frag"><div class="calc result"><span class="cl">Resultado</span><div class="ce">{nf(xc['num'], 2)} ÷ {nf(xc['den'], 2)}<br>t = {nf(xc['t'], 3)} · p = {nf(xc['p'], 3)}</div><b class="cr">r ≈ {nf(xc['r'], 3)}<small>nula · não significativa</small></b></div></div>
    </div>
  </div>
  <aside class="notes"><p>Fórmula: r = [n·ΣXY − (ΣX)(ΣY)] ÷ √{{[n·ΣX² − (ΣX)²]·[n·ΣY² − (ΣY)²]}}. Valores: n = {N}; ΣX = {nf(xc['Sx'], 3)}; ΣY = {nf(xc['Sy'], 0)}; ΣX² = {nf(xc['Sxx'], 3)}; ΣY² = {nf(xc['Syy'], 0)}; ΣXY = {nf(xc['Sxy'], 3)}.</p><p>Numerador = {nf(xc['num'], 2)}; 1º termo = {nf(xc['t1'], 2)}; 2º termo = {nf(xc['t2'], 0)}; denominador = {nf(xc['den'], 2)}; r = {nf(xc['r'], 4)}. Teste: t = r√(n − 2) ÷ √(1 − r²) = {nf(xc['t'], 3)}; p = {nf(xc['p'], 3)}. Avance para revelar cada etapa (5 cliques).</p></aside>
</section>''')

add(f'''<!-- ======================= 26 · CAFÉ × SONO ======================= -->
<section class="slide" id="sono-corr" data-title="Café × sono" data-section="Análise estatística" data-mood="night" aria-label="Correlações com o sono">
  <div class="kicker rv"><span class="kn">13.2</span>Correlação entre xícaras e problemas de sono</div>
  <h2 class="title rv-blur" style="--d:1">O que acompanha <em>a concentração?</em></h2>
  <div class="content" style="grid-template-columns:1.05fr .95fr;gap:30px;margin-top:34px">
    <div class="col-gap calc-list">
      <div class="sums five rv" style="--d:2">
        <div class="sum"><span>ΣX</span><b>{nf(xs['Sx'], 3)}</b></div><div class="sum"><span>ΣY</span><b>{nf(xs['Sy'], 0)}</b></div><div class="sum"><span>ΣX²</span><b>{nf(xs['Sxx'], 3)}</b></div><div class="sum"><span>ΣY²</span><b>{nf(xs['Syy'], 0)}</b></div><div class="sum"><span>ΣXY</span><b>{nf(xs['Sxy'], 3)}</b></div>
      </div>
      <p class="sum-cap rv" style="--d:3">Mesma fórmula, agora com <b>Y = problemas de sono (0–3)</b>.</p>
      <div class="frag"><div class="calc"><span class="cl">Numerador</span><div class="ce">{N} × {nf(xs['Sxy'], 3)} − ({nf(xs['Sx'], 3)} × {xs['Sy']:.0f})<br>= {nf(N * xs['Sxy'], 2)} − {nf(xs['Sx'] * xs['Sy'], 2)}</div><b class="cr">{nf(xs['num'], 2)}</b></div></div>
      <div class="frag"><div class="calc"><span class="cl">Denominador</span><div class="ce">√{{{nf(xs['t1'], 2)} × [{N} × {xs['Syy']:.0f} − {xs['Sy']:.0f}²]}}<br>= √({nf(xs['t1'], 2)} × {nf(xs['t2'], 0)})</div><b class="cr">≈ {nf(xs['den'], 2)}</b></div></div>
      <div class="frag"><div class="calc result sleep"><span class="cl">Resultado</span><div class="ce">{nf(xs['num'], 2)} ÷ {nf(xs['den'], 2)}<br>p = {nf(xs['p'], 3)} · explica {pc(xs['r2'])}</div><b class="cr">r ≈ {nf(xs['r'], 3)}<small>desprezível</small></b></div></div>
    </div>
    <div class="col-gap">
      <div class="card rv-r" style="--d:3;padding:24px 34px 20px">
        <div class="card-head"><h3>Três correlações lado a lado</h3></div>
        <div class="rmeter tall" data-r="{xc['r']:.4f},{xs['r']:.4f},{sc['r']:.4f}" data-cls="conc,sleep,pos" data-labels="café × concentração|café × sono|sono × concentração" data-lv="1,0,0" data-al="c,r,l"></div>
      </div>
      <div class="card chart-card rv-r" style="--d:4;flex:1;min-height:0;padding:24px 30px 18px">
        <div class="card-head"><h3>Médias por consumo de café</h3><span class="tag-comp">escala 0–3</span></div>
        <div class="chart" id="line-means"></div>
      </div>
    </div>
  </div>
  <aside class="notes"><p>Com Y = problemas de sono: ΣX = {nf(xs['Sx'], 3)}; ΣY = {nf(xs['Sy'], 0)}; ΣX² = {nf(xs['Sxx'], 3)}; ΣY² = {nf(xs['Syy'], 0)}; ΣXY = {nf(xs['Sxy'], 3)}. Numerador = {nf(xs['num'], 2)}; denominador = {nf(xs['den'], 2)}; r = {nf(xs['r'], 4)} (p = {nf(xs['p'], 3)}). Negativa e desprezível: explica {pc(xs['r2'])} da variação; com o efeito do desenho amostral, não deve ser tratada como achado firme. Uma leitura possível é causalidade reversa: quem dorme mal pode evitar café. Com as horas de sono, r = {nf(xh['r'], 3)} (p = {nf(xh['p'], 2)}).</p><p>O contraste: problemas de sono × dificuldade de concentração tem r = {nf(sc['r'], 3)} (IC 95% {nf(sc['ci_lo'], 3)} a {nf(sc['ci_hi'], 3)}; p &lt; 0,001), a única correlação moderada da base. As duas perguntas vêm do PHQ-9, então parte da associação reflete o humor.</p></aside>
</section>''')

add(f'''<!-- ======================= 27 · REGRESSÃO ======================= -->
<section class="slide" id="regressao" data-title="Regressão linear" data-section="Análise estatística" data-mood="focus" aria-label="Regressão linear simples">
  <div class="kicker rv"><span class="kn">14</span>Regressão linear simples e interpretação</div>
  <h2 class="title rv-blur" style="--d:1">Estimando a concentração <em>pelo café</em></h2>
  <div class="eq-hero rv-s" style="--d:2"><span class="eqh-y">Ŷ</span><span class="eqh-op">=</span><span class="eqh-a">{nf(xc['a'], 4)}</span><span class="eqh-op">−</span><span class="eqh-b">{nf(abs(xc['b']), 4)}</span><span class="eqh-op">·</span><span class="eqh-x">X</span></div>
  <div class="eq-legend rv" style="--d:3"><span><b class="c-conc">Ŷ</b>dificuldade de concentração estimada (0–3)</span><span><b>X</b>xícaras de café por dia</span></div>
  <div class="reg-grid">
    <div class="card coef rv" style="--d:4"><span class="coef-l">Coeficiente angular · b</span><b class="coef-v c-accent" data-count="{xc['b']:.4f}" data-dec="4">{nf(xc['b'], 4)}</b><p>Uma xícara a mais muda a estimativa em <b>−0,01 ponto</b>. IC 95%: {nf(xc['b_lo'], 3)} a +{nf(xc['b_hi'], 3)}, que inclui o zero.</p></div>
    <div class="card coef rv" style="--d:5"><span class="coef-l">Intercepto · a</span><b class="coef-v" data-count="{xc['a']:.4f}" data-dec="4">{nf(xc['a'], 4)}</b><p>Dificuldade estimada para quem <b>não toma café</b> (X = 0).</p></div>
    <div class="card coef r2 rv" style="--d:6"><div class="ring-sm"><div class="donut" id="ring-r2"></div><span class="rc">≈0%</span></div><div><span class="coef-l">Determinação · R²</span><b class="coef-v" style="font-size:48px">{nf(xc['r2'], 4)}</b><p>O café explica <b>{pc(xc['r2'], 2)}</b> da variação da concentração: a reta é praticamente horizontal.</p></div></div>
  </div>
  <div class="callout mt rv" style="--d:7"><svg class="ic"><use href="#i-moon"/></svg><p><b>Modelo complementar:</b> trocando X por problemas de sono, Ŷ = {nf(sc['a'], 4)} + {nf(sc['b'], 4)}·X e <b>R² = {pc(sc['r2'])}</b> — cada nível a mais de problema de sono soma 0,36 ponto à dificuldade de concentração.</p></div>
  <aside class="notes"><p>Modelo 1: Y = dificuldade de concentração; X = xícaras por dia. Ŷ = {nf(xc['a'], 4)} − {nf(abs(xc['b']), 4)}·X. b = {nf(xc['b'], 4)} (erro padrão {nf(xc['se_b'], 3)}; IC 95% {nf(xc['b_lo'], 3)} a {nf(xc['b_hi'], 3)}); R² = {nf(xc['r2'], 5)}. Para X = 2, Ŷ = {nf(xc['a'] + 2 * xc['b'], 3)}; para X = 0, {nf(xc['a'], 3)}.</p><p>Modelo 2: X = problemas de sono (0–3). Ŷ = {nf(sc['a'], 4)} + {nf(sc['b'], 4)}·X; R² = {pc(sc['r2'])}; IC 95% de b: {nf(sc['b_lo'], 3)} a {nf(sc['b_hi'], 3)}. Os dois modelos tratam a escala ordinal como numérica e não controlam outras variáveis: descrevem a tendência média, não provam efeito.</p></aside>
</section>''')

add(f'''<!-- ======================= 28 · SIMULADOR ======================= -->
<section class="slide" id="simulador" data-title="Cálculo e simulação" data-section="Análise estatística" data-mood="focus" aria-label="Cálculo da regressão e simulador">
  <div class="kicker rv"><span class="kn">14.1</span>Cálculo da regressão linear simples</div>
  <h2 class="title rv-blur" style="--d:1">Café ou sono: <em>qual reta inclina?</em></h2>
  <div class="content" style="grid-template-columns:.84fr 1.16fr;gap:34px;margin-top:34px">
    <div class="col-gap calc-list" style="justify-content:center">
      <div class="calc rv-l" style="--d:2"><span class="cl">Modelo 1 · inclinação</span><div class="ce">b = {nf(xc['num'], 2)} ÷ {nf(xc['t1'], 2)}</div><b class="cr">{nf(xc['b'], 4)}</b></div>
      <div class="calc rv-l" style="--d:3"><span class="cl">Modelo 1 · intercepto</span><div class="ce">a = {nf(xc['ybar'], 4)} − ({nf(xc['b'], 4)} × {nf(xc['xbar'], 4)})</div><b class="cr">{nf(xc['a'], 4)}</b></div>
      <div class="calc rv-l" style="--d:4"><span class="cl">Modelo 2 · inclinação</span><div class="ce">b = {nf(sc['num'], 0)} ÷ {nf(sc['t1'], 0)}</div><b class="cr">{nf(sc['b'], 4)}</b></div>
      <div class="calc rv-l" style="--d:5"><span class="cl">Modelo 2 · intercepto</span><div class="ce">a = {nf(sc['ybar'], 4)} − ({nf(sc['b'], 4)} × {nf(sc['xbar'], 4)})</div><b class="cr">{nf(sc['a'], 4)}</b></div>
      <div class="calc result rv-l" style="--d:6"><span class="cl">Determinação</span><div class="ce">R² modelo 1 = {pc(xc['r2'], 2)}<br>R² modelo 2 = r² = {nf(sc['r'], 4)}²</div><b class="cr">{pc(sc['r2'])}</b></div>
    </div>
    <div class="card sim-card rv-r" style="--d:3">
      <div class="sim-top">
        <div class="sim-top-2">
          <div><span class="sim-l">Modelo</span>
            <div class="seg models" role="group" aria-label="Modelo de regressão" id="sim-models">
              <button type="button" data-m="0" class="on">X = xícaras/dia</button><button type="button" data-m="1">X = problemas de sono</button>
            </div>
          </div>
          <div><span class="sim-l" id="sim-xl">Xícaras por dia (X)</span>
            <div class="seg" role="group" aria-label="Valor de X" id="sim-xs"></div>
          </div>
        </div>
        <div class="sim-res"><b id="sim-y">0,61</b><span>dificuldade estimada (Ŷ)</span></div>
      </div>
      <div class="sim-eq" id="sim-eq"></div>
      <div class="chart" id="sim-chart"></div>
      <p class="sim-note" id="sim-note" aria-live="polite"></p>
    </div>
  </div>
  <aside class="notes"><p>Modelo 1 (café): b = [nΣXY − ΣXΣY] ÷ [nΣX² − (ΣX)²] = {nf(xc['num'], 2)} ÷ {nf(xc['t1'], 2)} = {nf(xc['b'], 4)}; a = Ȳ − b·X̄ = {nf(xc['a'], 4)}. Modelo 2 (problemas de sono): b = {nf(sc['num'], 0)} ÷ {nf(sc['t1'], 0)} = {nf(sc['b'], 4)}; a = {nf(sc['a'], 4)}; R² = {pc(sc['r2'])}.</p><p>Use os botões para trocar de modelo e escolher X. Os círculos vazados são as médias observadas em cada grupo. No modelo do café a reta é plana; no do sono ela sobe de {nf(sc['a'], 2)} para {nf(sc['a'] + 3 * sc['b'], 2)}, perto das médias observadas ({nf(GPS[0]['conc'], 2)} e {nf(GPS[3]['conc'], 2)}).</p></aside>
</section>''')

add(f'''<!-- ======================= 29 · PROBABILIDADE ======================= -->
<section class="slide" id="probabilidade" data-title="Probabilidade simples" data-section="Análise estatística" aria-label="Probabilidade simples">
  <div class="kicker rv"><span class="kn">15</span>Probabilidade simples</div>
  <h2 class="title rv-blur" style="--d:1">Sorteando <em>um participante</em></h2>
  <div class="content" style="grid-template-columns:.92fr 1.08fr">
    <div class="col-gap" style="justify-content:center">
      <div class="card formula-mini rv" style="--d:2"><div class="math">P <span class="up">=</span> <span class="frac"><span class="tx" style="font-size:.62em;color:var(--text)">casos favoráveis</span><span class="tx" style="font-size:.62em;color:var(--text)">total de casos</span></span></div></div>
      <button type="button" class="ev ev-a on rv" style="--d:3" data-ev="0"><span class="ev-tag">Evento A</span><span class="ev-t">Tomou café em ao menos 1 dia</span><span class="ev-calc">P(A) = {PR['n_A']} ÷ {N} = {nf(PR['P_A'], 4)}</span><span class="ev-res">{pc(PR['P_A'])}</span></button>
      <div class="frag"><button type="button" class="ev ev-b" data-ev="1"><span class="ev-tag">Evento B</span><span class="ev-t">Problemas de sono em vários dias ou mais</span><span class="ev-calc">P(B) = {PR['n_B']} ÷ {N} = {nf(PR['P_B'], 4)}</span><span class="ev-res">{pc(PR['P_B'])}</span></button></div>
      <div class="frag"><button type="button" class="ev ev-c" data-ev="2"><span class="ev-tag">Evento C</span><span class="ev-t">Dificuldade de concentração em vários dias ou mais</span><span class="ev-calc">P(C) = {PR['n_C']} ÷ {N} = {nf(PR['P_C'], 4)}</span><span class="ev-res">{pc(PR['P_C'])}</span></button></div>
    </div>
    <div class="card waffle-card rv-s" style="--d:3" id="wf-card">
      <div class="wf-head"><span id="wf-label">Evento A · tomou café</span><b id="wf-count">{PR['n_A']} / {N}</b></div>
      <div class="waffle" id="w-prob"></div>
      <div class="wf-legend"><span><i class="on"></i>casos favoráveis</span><span><i class="off"></i>demais participantes</span><span style="margin-left:auto">1 xícara = 1 participante</span></div>
    </div>
  </div>
  <aside class="notes"><p>Probabilidade = casos favoráveis ÷ total, sorteando um dos {N} participantes com a mesma chance. A: tomou café em ao menos um dos dois dias, {PR['n_A']}/{N} = {nf(PR['P_A'], 4)}. B: problemas de sono em vários dias ou mais, {PR['n_B']}/{N} = {nf(PR['P_B'], 4)}. C: dificuldade de concentração em vários dias ou mais, {PR['n_C']}/{N} = {nf(PR['P_C'], 4)}. Outros: dorme menos de 7 h, {PR['n_sono_insuf']}/{N} = {nf(PR['P_sono_insuf'], 4)}; cafeína acima de 400 mg/dia, {R['cafeina_acima_400']}/{N}.</p><p>Avance (ou clique nos eventos B e C) para trocar o gráfico.</p></aside>
</section>''')

add(f'''<!-- ======================= 30 · CONDICIONAL (NOVO) ======================= -->
<section class="slide" id="condicional" data-title="Probabilidade condicional" data-section="Análise estatística" aria-label="Probabilidade condicional">
  <div class="kicker rv"><span class="kn">15.1</span>Probabilidade condicional · Gráfico 7</div>
  <h2 class="title rv-blur" style="--d:1">O que muda a chance de <em>perder a concentração?</em></h2>
  <div class="cond-grid">
    <div class="card chart-card rv-l" style="--d:2">
      <div class="card-head"><h3>Saber que tomou café</h3><span class="verdict no"><svg class="ic"><use href="#i-ban"/></svg>não muda</span></div>
      <div class="chart" id="bar-cond-a"></div>
      <div class="cond-foot"><span>P(C | A) = {AC['a']}/{AC['a'] + AC['b']} · P(C | Ā) = {AC['c']}/{AC['c'] + AC['d']}</span><b>χ² = {nf(AC['chi2'], 3)} · p = {nf(AC['p'], 2)}</b></div>
    </div>
    <div class="card chart-card rv-r" style="--d:3">
      <div class="card-head"><h3>Saber a frequência de problemas de sono</h3><span class="verdict yes"><svg class="ic"><use href="#i-check"/></svg>{nf(BC['p_e2_dado_e1'] / BC['p_e2_dado_nao_e1'], 2)}× mais chance</span></div>
      <div class="chart" id="bar-cond-b"></div>
      <div class="cond-foot"><span>P(C | B) = {BC['a']}/{BC['a'] + BC['b']} = {pc(BC['p_e2_dado_e1'])} · P(C | B̄) = {BC['c']}/{BC['c'] + BC['d']} = {pc(BC['p_e2_dado_nao_e1'])}</span><b>χ² = {nf(BC['chi2'], 1)} · p &lt; 0,001</b></div>
    </div>
  </div>
  <p class="foot-note rv" style="--d:5"><svg class="ic"><use href="#i-info"/></svg>P(A ∩ C) = {nf(AC['p_e1_e_e2'], 4)} ≈ P(A) × P(C) = {nf(PR['P_A'] * PR['P_C'], 4)}: café e dificuldade de concentração se comportam como eventos independentes.</p>
  <aside class="notes"><p><b>Novo, possível só com dados reais:</b> probabilidade condicional. Café × concentração: P(C | A) = {AC['a']}/{AC['a'] + AC['b']} = {pc(AC['p_e2_dado_e1'])} e P(C | Ā) = {AC['c']}/{AC['c'] + AC['d']} = {pc(AC['p_e2_dado_nao_e1'])}; P(A ∩ C) = {nf(AC['p_e1_e_e2'], 4)} ≈ P(A)·P(C) = {nf(PR['P_A'] * PR['P_C'], 4)} → independentes (χ² = {nf(AC['chi2'], 3)}; p = {nf(AC['p'], 3)}).</p><p>Sono × concentração: P(C | B) = {BC['a']}/{BC['a'] + BC['b']} = {pc(BC['p_e2_dado_e1'])} e P(C | B̄) = {BC['c']}/{BC['c'] + BC['d']} = {pc(BC['p_e2_dado_nao_e1'])}, razão de {nf(BC['p_e2_dado_e1'] / BC['p_e2_dado_nao_e1'], 2)} (χ² = {nf(BC['chi2'], 2)}; p &lt; 0,001). Por nível de problema de sono: {', '.join(pc(g['conc_prej']) for g in GPS)} — um gradiente contínuo.</p></aside>
</section>''')

pk = BI['pk']
add(f'''<!-- ======================= 31 · BINOMIAL ======================= -->
<section class="slide" id="binomial" data-title="Distribuição binomial" data-section="Análise estatística" aria-label="Distribuição binomial">
  <div class="kicker rv"><span class="kn">16</span>Distribuição binomial</div>
  <h2 class="title rv-blur" style="--d:1">Cinco jovens: <em>quantos tomaram café?</em></h2>
  <div class="params rv" style="--d:2"><span class="chip strong">Sucesso = tomou café</span><span class="chip">p = {PR['n_A']} ÷ {N} = {nf(pB, 4)}</span><span class="chip">q = 1 − p = {nf(qB, 4)}</span><span class="chip">n = 5 sorteios independentes</span><span class="chip">X = nº que tomou café</span></div>
  <div class="content" style="grid-template-columns:.95fr 1.05fr;gap:34px;margin-top:28px">
    <div class="col-gap calc-list">
      <div class="card formula-mini rv" style="--d:3;padding:22px 30px"><div class="math">P(X = k) <span class="up">=</span> C(n,k) <span class="up">·</span> <span>p<sup>k</sup></span> <span class="up">·</span> <span>q<sup>n−k</sup></span></div><div class="math sm">C(n,k) <span class="up">=</span> <span class="frac"><span>n!</span><span>k!(n − k)!</span></span></div></div>
      <div class="calc rv" style="--d:4"><span class="cl">Exatamente 2</span><div class="ce">C(5,2) × {nf(pB, 4)}² × {nf(qB, 4)}³<br>= 10 × {nf(pB ** 2, 4)} × {nf(qB ** 3, 4)}</div><b class="cr">{pc(pk[2], 2)}</b></div>
      <div class="calc rv" style="--d:5"><span class="cl">Nenhum</span><div class="ce">C(5,0) × {nf(pB, 4)}⁰ × {nf(qB, 4)}⁵<br>= 1 × 1 × {nf(pk[0], 4)}</div><b class="cr">{pc(pk[0], 2)}</b></div>
      <div class="calc result rv" style="--d:6"><span class="cl">Pelo menos 1</span><div class="ce">P(X ≥ 1) = 1 − P(X = 0)<br>= 1 − {nf(pk[0], 4)} = {nf(1 - pk[0], 4)}</div><b class="cr">{pc(1 - pk[0], 2)}</b></div>
    </div>
    <div class="card chart-card rv-r" style="--d:3;padding:26px 30px 20px">
      <div class="card-head"><h3>P(X = k) para n = 5 e p = {nf(pB, 4)}</h3></div>
      <div class="chart" id="bar-binom"></div>
      <p class="chart-note">O mais provável é X = 2 (média n·p = {nf(5 * pB, 2)}). A independência vale para sorteios numa população grande, não para um grupo de amigos.</p>
    </div>
  </div>
  <aside class="notes"><p>Sucesso = tomou café em ao menos um dos dois dias. p = {PR['n_A']}/{N} = {nf(pB, 4)}; q = {nf(qB, 4)}; X ~ Binomial(5; {nf(pB, 4)}). P(X = 2) = 10 × {nf(pB, 4)}² × {nf(qB, 4)}³ = {pc(pk[2], 2)}. P(X = 0) = {nf(qB, 4)}⁵ = {pc(pk[0], 2)}. P(X ≥ 1) = 1 − P(X = 0) = {pc(1 - pk[0], 2)} (evento complementar).</p><p>Distribuição completa: {', '.join(f'P({k}) = {pc(v, 2)}' for k, v in enumerate(pk))}. Valor esperado: n·p = {nf(5 * pB, 2)}. Em cerca de 9 de cada 100 grupos de cinco jovens, ninguém teria tomado café.</p></aside>
</section>''')

add('''<!-- ======================= 32 · DIVISOR CONCLUSÕES ======================= -->
<section class="slide divider" id="d-conclusoes" data-title="Parte 5 — Conclusões" data-section="Conclusões" data-chrome="off" aria-label="Parte 5: Conclusões">
  <div class="div-num" aria-hidden="true"><span class="rv-s" style="--d:0">05</span></div>
  <div class="div-body">
    <div class="kicker rv" style="--d:1">Parte 5 · Seções 17 a 21</div>
    <h2 class="div-title rv-blur" style="--d:2">Conclusões</h2>
    <p class="div-desc rv" style="--d:3">O que os dados reais mostram, até onde eles vão e qual decisão eles sustentam.</p>
    <ul class="div-list">
      <li class="rv" style="--d:4">Análise dos resultados</li><li class="rv" style="--d:5">Limites do estudo</li><li class="rv" style="--d:6">Conclusão</li><li class="rv" style="--d:7">Tomada de decisão</li><li class="rv" style="--d:8">Referências</li>
    </ul>
  </div>
</section>''')

add(f'''<!-- ======================= 33 · ANÁLISE ======================= -->
<section class="slide" id="analise" data-title="Análise dos resultados" data-section="Conclusões" aria-label="Análise dos resultados">
  <div class="kicker rv"><span class="kn">17</span>Análise dos resultados</div>
  <h2 class="title rv-blur" style="--d:1">O que os dados <em>mostram</em></h2>
  <div class="fill">
  <div class="ins-grid">
    <div class="ins rv" style="--d:2"><b class="ins-n" data-count="{PR['P_A'] * 100:.1f}" data-dec="1" data-suf="%">{pc(PR['P_A'])}</b><p>tomaram café em ao menos um de dois dias; só <b>{pc(PR['P_A2'])}</b> nos dois.</p></div>
    <div class="ins rv" style="--d:3"><b class="ins-n">{pc(FX['18 a 21']['tomou_cafe'], 0)} → {pc(FX['26 a 29']['tomou_cafe'], 0)}</b><p>O consumo <b>dobra</b> entre os 18–21 e os 26–29 anos.</p></div>
    <div class="ins sleep rv" style="--d:4"><b class="ins-n">{pc(IV['pessoas_menor_88'] / IV['pessoas'])}</b><p>de quem toma café o fez a <b>menos de 8,8 h</b> de dormir; a maioria toma até as 12h.</p></div>
    <div class="ins conc rv" style="--d:5"><b class="ins-n">r = {nf(xc['r'], 3)}</b><p>Café × dificuldade de concentração: <b>nula</b> (p = {nf(xc['p'], 2)}; R² = {pc(xc['r2'], 2)}).</p></div>
    <div class="ins sleep rv" style="--d:6"><b class="ins-n">{nf(BC['p_e2_dado_e1'] / BC['p_e2_dado_nao_e1'], 1)}× <small>mais chance</small></b><p>de dificuldade de concentração com <b>problemas de sono</b>: {pc(BC['p_e2_dado_e1'])} contra {pc(BC['p_e2_dado_nao_e1'])}.</p></div>
    <div class="ins rv" style="--d:7"><b class="ins-n">{pc(PR['P_sono_insuf'])}</b><p>dormem menos de 7 h em dias úteis; <b>{pc(R['sono_fds_vs_util']['pct_mais_1h'])}</b> compensam no fim de semana.</p></div>
  </div>
  <div class="banner rv" style="--d:8"><svg class="ic"><use href="#i-bulb"/></svg><p>O que acompanha a concentração é <b>a qualidade do sono</b>, não a quantidade de café.</p></div>
  </div>
  <aside class="notes"><p>Síntese: o café é hábito de {pc(PR['P_A'])} dos jovens ({pc(PR['P_A2'])} nos dois dias), cresce com a idade ({pc(FX['18 a 21']['tomou_cafe'])} → {pc(FX['26 a 29']['tomou_cafe'])}) e é matinal ({pc(manha['pct'])} concentram o consumo de manhã). Média de {nf(dxc['media'], 2)} xícara entre quem toma; só {pc(R['cafeina_acima_400'] / N)} passam de 400 mg de cafeína.</p><p>A quantidade de café não se associa à concentração (r = {nf(xc['r'], 3)}; P(C|A) = P(C|Ā) ≈ 42%). Os problemas de sono, sim (r = {nf(sc['r'], 3)}; {pc(BC['p_e2_dado_e1'])} contra {pc(BC['p_e2_dado_nao_e1'])}). Coerente com a literatura: o benefício da cafeína aparece em doses agudas e após privação de sono (Irwin et al., 2020) e, em consumidores habituais, é em boa parte reversão da abstinência (James; Rogers, 2005).</p></aside>
</section>''')

add('''<!-- ======================= 34 · LIMITES ======================= -->
<section class="slide" id="limitacoes" data-title="Limites do estudo" data-section="Conclusões" aria-label="Limites do estudo">
  <div class="kicker rv"><span class="kn">17</span>Cautela na interpretação</div>
  <h2 class="title rv-blur" style="--d:1">Os limites <em>deste estudo</em></h2>
  <div class="fill">
  <div class="lim-grid">
    <div class="lim rv" style="--d:2"><div class="lim-ic"><svg class="ic"><use href="#i-target"/></svg></div><h3>Concentração autorrelatada</h3><p>O item do PHQ-9 mede a frequência de uma dificuldade, não nota nem desempenho.</p></div>
    <div class="lim rv" style="--d:3"><div class="lim-ic"><svg class="ic"><use href="#i-clock"/></svg></div><h3>Dois dias de registro</h3><p>Aproximam o hábito de consumo, mas não o medem exatamente.</p></div>
    <div class="lim rv" style="--d:4"><div class="lim-ic"><svg class="ic"><use href="#i-search"/></svg></div><h3>Desenho transversal</h3><p>Tudo foi medido no mesmo período: não dá para saber o que veio antes.</p></div>
    <div class="lim rv" style="--d:5"><div class="lim-ic"><svg class="ic"><use href="#i-pin"/></svg></div><h3>Jovens dos EUA</h3><p>No Brasil o café é mais difundido: 78,1% o tomam num dia comum (POF).</p></div>
  </div>
  <div class="banner rv" style="--d:6"><svg class="ic"><use href="#i-target"/></svg><p>Os números valem para esses 496 jovens. Para decidir na Fatec, é preciso uma <b>coleta própria</b> com o mesmo método.</p></div>
  </div>
  <aside class="notes"><p>Limites: (1) concentração medida pelo item 7 do PHQ-9, autorrelatada, sem notas ou tempo de estudo; (2) sono e concentração vêm do mesmo questionário de saúde mental, então parte da correlação reflete o humor; (3) dois recordatórios aproximam o hábito, e o horário de dormir usado é o habitual; (4) desenho transversal; (5) população norte-americana; (6) análise sem pesos amostrais — a comparação ponderada mudou pouco os percentuais, mas os p-valores ignoram o desenho por conglomerados.</p></aside>
</section>''')

add(f'''<!-- ======================= 35 · CONCLUSÃO ======================= -->
<section class="slide" id="conclusao" data-title="Conclusão" data-section="Conclusões" aria-label="Conclusão">
  <div class="kicker rv"><span class="kn">18</span>Conclusão</div>
  <h2 class="title rv-blur" style="--d:1">Café não, <em>sono sim</em></h2>
  <div class="content" style="grid-template-columns:1fr 1fr;gap:34px;margin-top:34px">
    <div class="card rv-l" style="--d:2">
      <div class="card-head"><h3>Com os {N} jovens analisados</h3></div>
      <ul class="checks">
        <li><svg class="ic"><use href="#i-check"/></svg><span>O café é hábito de <b>{pc(PR['P_A'])}</b>, moderado e <b>matinal</b> ({pc(manha['pct'], 0)} pela manhã).</span></li>
        <li><svg class="ic"><use href="#i-check"/></svg><span>Café × concentração: <b>sem associação</b> (r = {nf(xc['r'], 3)}; p = {nf(xc['p'], 2)}).</span></li>
        <li><svg class="ic"><use href="#i-check"/></svg><span>Café × horas de sono: <b>sem associação</b> (r = {nf(xh['r'], 3)}; p = {nf(xh['p'], 2)}).</span></li>
        <li><svg class="ic"><use href="#i-check"/></svg><span>Problemas de sono × concentração: <b class="c-pos">moderada e positiva</b> (r = {nf(sc['r'], 3)}).</span></li>
      </ul>
    </div>
    <div class="col-gap">
      <div class="yn rv-r" style="--d:3">
        <div class="yn-i yes"><svg class="ic"><use href="#i-check-circle"/></svg><span class="yn-h">Os dados mostram</span><p>A dificuldade de concentração <b>cresce com os problemas de sono</b>: de {pc(GPS[0]['conc_prej'])} a {pc(GPS[3]['conc_prej'])}.</p></div>
        <div class="yn-i no"><svg class="ic"><use href="#i-ban"/></svg><span class="yn-h">Os dados não permitem</span><p>Afirmar <b>causa</b> nem aplicar os números à Fatec sem nova coleta.</p></div>
      </div>
      <div class="card rv-r" style="--d:4;padding:24px 30px">
        <div class="card-head"><h3>Para uma conclusão mais forte</h3></div>
        <div class="chips"><span class="chip">PSQI (qualidade do sono)</span><span class="chip">notas do semestre</span><span class="chip">café com horário</span><span class="chip">amostra por curso e turno</span></div>
      </div>
    </div>
  </div>
  <blockquote class="quote-banner rv" style="--d:6">Os dados reais derrubaram a hipótese inicial e mudaram a pergunta: de <em>“quanto café?”</em> para <em>“como está o sono?”</em></blockquote>
  <aside class="notes"><p>Resposta ao problema: entre os {N} adultos de 18 a 29 anos, a quantidade de café por dia não está associada à dificuldade de concentração (r = {nf(xc['r'], 3)}; p = {nf(xc['p'], 2)}) nem à duração do sono (r = {nf(xh['r'], 3)}; p = {nf(xh['p'], 2)}), e tem associação negativa desprezível com os problemas de sono (r = {nf(xs['r'], 3)}). As hipóteses nulas não foram rejeitadas para concentração e horas de sono.</p><p>O resultado mais consistente não envolve o café: a dificuldade de concentração atinge {pc(GPS[0]['conc_prej'])} de quem não relata problemas de sono e {pc(GPS[3]['conc_prej'])} de quem os tem quase todos os dias.</p></aside>
</section>''')

add(f'''<!-- ======================= 36 · DECISÃO ======================= -->
<section class="slide" id="decisao" data-title="Tomada de decisão" data-section="Conclusões" aria-label="Tomada de decisão">
  <div class="kicker rv"><span class="kn">19</span>Tomada de decisão</div>
  <h2 class="title rv-blur" style="--d:1">Recomendação: <em>cuidar do sono, não da xícara</em></h2>
  <div class="content" style="grid-template-columns:1fr 1fr;gap:34px;margin-top:34px">
    <div class="card dec rv-l" style="--d:2">
      <div class="dec-head"><div class="icon-badge"><svg class="ic"><use href="#i-user"/></svg></div><h3>Para os estudantes</h3></div>
      <ul class="dec-list">
        <li><svg class="ic"><use href="#i-moon"/></svg><span>Horários de sono regulares na semana — {pc(R['sono_fds_vs_util']['pct_mais_1h'], 0)} compensam no fim de semana.</span></li>
        <li><svg class="ic"><use href="#i-sunrise"/></svg><span>Café, se houver, <b>pela manhã</b>.</span></li>
        <li><svg class="ic"><use href="#i-hourglass"/></svg><span>Nada de café nas <b>8,8 h</b> antes de dormir: quem deita às 23h para às 14h.</span></li>
        <li><svg class="ic"><use href="#i-activity"/></svg><span>Problemas de sono em mais da metade dos dias: <b>procurar orientação</b>.</span></li>
      </ul>
    </div>
    <div class="card dec rv-r" style="--d:3">
      <div class="dec-head"><div class="icon-badge alt"><svg class="ic"><use href="#i-building"/></svg></div><h3>Para a Fatec e o grupo</h3></div>
      <p class="dec-p">Repetir o estudo com <b>estudantes da Fatec</b>, com o mesmo método:</p>
      <div class="chips"><span class="chip">café de 2 dias, com horário</span><span class="chip">PSQI</span><span class="chip">notas (com autorização)</span><span class="chip">amostra por curso e turno</span></div>
      <p class="dec-p" style="margin-top:18px">Tamanho mínimo: <b>n = 385</b> (margem de 5 pontos, 95% de confiança); com 1.000 alunos matriculados, <b>278</b>.</p>
    </div>
  </div>
  <div class="banner rv" style="--d:5"><svg class="ic"><use href="#i-flag"/></svg><p><b>Nem aumentar, nem cortar o café:</b> os dados não sustentam nenhuma das duas orientações. A prioridade é o sono, e do café só importa o horário.</p></div>
  <aside class="notes"><p>Decisão: não recomendar aumento nem redução do café como estratégia de produtividade acadêmica. Priorizar o sono e controlar apenas o horário da cafeína: café pela manhã e nada nas 8,8 horas anteriores ao horário de dormir (Gardiner et al., 2023).</p><p>Para a Fatec: repetir o estudo com estudantes, registrando o café de dois dias com horário, o PSQI e, com autorização, as notas, em amostra aleatória estratificada por curso e turno. Tamanho: n₀ = 1,96² × 0,5 × 0,5 ÷ 0,05² = 384,2 → 385; com correção para população finita de 1.000 alunos, 278. Rever a decisão se o estudo local encontrar r acima de 0,3 entre café e concentração ou consumo noturno muito acima dos {pc(noite['pct'])} observados.</p></aside>
</section>''')

add(f'''<!-- ======================= 37 · REFERÊNCIAS ======================= -->
<section class="slide" id="referencias" data-title="Referências" data-section="Conclusões" aria-label="Referências e anexos">
  <div class="kicker rv"><span class="kn">20–21</span>Referências · Anexos</div>
  <h2 class="title rv-blur" style="--d:1">Referências</h2>
  <div class="content" style="grid-template-columns:1.45fr .55fr;gap:30px;margin-top:30px">
    <ol class="refs dense">
      <li class="rv" style="--d:2">CENTERS FOR DISEASE CONTROL AND PREVENTION (CDC/NCHS). <b>National Health and Nutrition Examination Survey: August 2021–August 2023.</b> 2024. Disponível em: <a href="https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?Cycle=2021-2023" target="_blank" rel="noopener">wwwn.cdc.gov/nchs/nhanes</a>. Acesso em: 7 nov. 2026.</li>
      <li class="rv" style="--d:2.5">GARDINER, C. et al. <b>The effect of caffeine on subsequent sleep: a systematic review and meta-analysis.</b> Sleep Medicine Reviews, v. 69, 101764, 2023.</li>
      <li class="rv" style="--d:3">IRWIN, C. et al. <b>Effects of acute caffeine consumption following sleep loss on cognitive, physical, occupational and driving performance.</b> Neuroscience &amp; Biobehavioral Reviews, v. 108, p. 877–888, 2020.</li>
      <li class="rv" style="--d:3.5">JAMES, J. E.; ROGERS, P. J. <b>Effects of caffeine on performance and mood: withdrawal reversal is the most plausible explanation.</b> Psychopharmacology, v. 182, p. 1–8, 2005.</li>
      <li class="rv" style="--d:4">KROENKE, K.; SPITZER, R. L.; WILLIAMS, J. B. W. <b>The PHQ-9: validity of a brief depression severity measure.</b> Journal of General Internal Medicine, v. 16, p. 606–613, 2001.</li>
      <li class="rv" style="--d:4.5">IBGE. <b>Pesquisa de orçamentos familiares 2017–2018: análise do consumo alimentar pessoal no Brasil.</b> Rio de Janeiro: IBGE, 2020.</li>
      <li class="rv" style="--d:5">WATSON, N. F. et al. <b>Recommended amount of sleep for a healthy adult.</b> Sleep, v. 38, n. 6, p. 843–844, 2015.</li>
      <li class="rv" style="--d:5.5">GARCIA, M. <b>Projeto estatístico aplicado: da coleta à tomada de decisão.</b> Material da disciplina de Estatística Aplicada, Fatec Presidente Prudente, 2026.</li>
    </ol>
    <div class="card rv-r" style="--d:4;padding:26px 30px">
      <div class="card-head"><h3>Anexos</h3></div>
      <div class="ax"><b>A</b><p>Planilha com dados brutos do NHANES, base derivada por fórmulas e todos os cálculos.</p></div>
      <div class="ax"><b>B</b><p>Relatório completo, com tabelas, gráficos e demonstrações.</p></div>
      <div class="ax"><b>C</b><p>Scripts em Python que reproduzem todos os números a partir dos arquivos oficiais.</p></div>
      <div class="ax"><b>D</b><p>Microdados: 9 arquivos .xpt do ciclo 2021–2023 (DEMO, OCQ, SLQ, DPQ, DR1/DR2).</p></div>
    </div>
  </div>
  <aside class="notes"><p>Referências completas na seção 20 do relatório, que também inclui Terry et al. (2024) sobre o plano do NHANES 2021–2023, Moshfegh et al. (2008) sobre o método de recordatório, Roenneberg et al. (2003) sobre as perguntas de sono, a FDA sobre o limite de 400 mg/dia e a base FNDDS 2021–2023 do USDA.</p><p>Anexos: A — planilha Base_Real_Cafe_NHANES_496.xlsx; B — relatório; C — scripts; D — arquivos do NHANES.</p></aside>
</section>''')

add(f'''<!-- ======================= 38 · FIM ======================= -->
<section class="slide finale" id="fim" data-title="Encerramento" data-section="Encerramento" data-chrome="off" aria-label="Encerramento">
  <div class="fin-grid">
    <div>
      <div class="eyebrow rv"><span class="dot"></span>Consumo de café e produtividade acadêmica</div>
      <h2 class="fin-title rv-blur" style="--d:1">Obrigado<em>!</em></h2>
      <p class="fin-sub rv" style="--d:2">Perguntas, dúvidas e comentários são bem-vindos.</p>
      <div class="authors rv" style="--d:3"><span class="author">Bruna Lais Amorin</span><span class="author">Kaike Taylor Antonio Santos</span><span class="author">Lucas Gustavo Mendes</span><span class="author">Rafael Gervazoni Bezerra</span></div>
      <div class="cover-logos rv" style="--d:4" id="fin-logos"></div>
    </div>
    <div class="cover-art rv-s" style="--d:2"><div class="cup-wrap" id="cup-dst"></div></div>
  </div>
  <aside class="notes"><p>Encerramento. Dados de apoio: {N} jovens de 18 a 29 anos (NHANES 2021–2023); {pc(PR['P_A'])} tomaram café; {pc(manha['pct'])} de manhã; café × concentração r = {nf(xc['r'], 3)}; problemas de sono × concentração r = {nf(sc['r'], 3)}; {pc(BC['p_e2_dado_e1'])} contra {pc(BC['p_e2_dado_nao_e1'])} de dificuldade de concentração com e sem problemas de sono.</p></aside>
</section>''')

slides_html = '\n\n'.join(S)
slides_html = coffee_layer.apply(slides_html, dict(nf=nf, pc=pc, R=R, N=N))

# ------------------------------------------------------------------ script
js = open(os.path.join(HERE, 'pres_script.js'), encoding='utf-8').read()
cls_stats = []
import pandas as pd
b = pd.read_csv(os.path.join(ROOT, 'out', 'base_analitica.csv'))
repl = {
    '__RAW__': R['raw_html'], '__N__': str(N),
    '__A1__': f"{xc['a']:.6f}", '__B1__': f"{xc['b']:.6f}", '__A2__': f"{sc['a']:.6f}", '__B2__': f"{sc['b']:.6f}",
    '__NF__': str(g_f['n']), '__NM__': str(g_m['n']), '__PA__': f"{PR['P_A'] * 100:.2f}", '__R2_1__': f"{xc['r2'] * 100:.4f}",
    '__CUPS__': json.dumps([r['n'] for r in xf]), '__HOURS__': json.dumps(H['por_hora_itens']),
    '__NA__': str(PR['n_A']), '__NB__': str(PR['n_B']), '__NC__': str(PR['n_C']), '__P__': f"{pB:.6f}",
    '__PBIN1__': pc(1 - pk[0], 2),
}
for k, v in repl.items():
    assert k in js, k
    js = js.replace(k, v)

out = head + slides_html + '\n\n</div>\n</div>\n\n' + tail + '<script>\n' + js + '\n</script>\n</body>\n</html>\n'
with open(DST, 'w', encoding='utf-8') as f:
    f.write(out)
print('saved', DST, len(out), 'slides:', out.count('<section class="slide'))
