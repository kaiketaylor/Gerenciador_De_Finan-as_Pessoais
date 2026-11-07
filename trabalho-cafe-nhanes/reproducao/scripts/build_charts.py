"""Gráficos do relatório (PNG, 200 dpi) a partir de out/base_analitica.csv e out/results.json."""
import json, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter, MaxNLocator

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'out')
FIG = os.path.join(OUT, 'graficos')
os.makedirs(FIG, exist_ok=True)
R = json.load(open(os.path.join(OUT, 'results.json'), encoding='utf-8'))
b = pd.read_csv(os.path.join(OUT, 'base_analitica.csv'))
N = R['n']

COFFEE, SLEEP, AMBER = '#9a5426', '#3a62c4', '#b97a10'
NONE = '#c9bfb5'
INK, MUTED, GRID = '#2b2118', '#6b5b4e', '#e8e0d8'
plt.rcParams.update({
    'font.family': 'Liberation Sans', 'font.size': 10, 'text.color': INK, 'axes.labelcolor': INK,
    'axes.edgecolor': GRID, 'axes.linewidth': 1, 'xtick.color': MUTED, 'ytick.color': MUTED,
    'xtick.labelsize': 9.5, 'ytick.labelsize': 9.5, 'axes.titlesize': 11, 'axes.titleweight': 'bold',
    'axes.titlelocation': 'left', 'axes.titlepad': 10, 'figure.dpi': 100, 'savefig.dpi': 200,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.spines.left': False,
    'axes.grid': True, 'axes.grid.axis': 'y', 'grid.color': GRID, 'grid.linewidth': 0.8,
    'axes.axisbelow': True, 'legend.frameon': False, 'legend.fontsize': 9.5,
})


from decimal import Decimal, ROUND_HALF_UP
def br(v, d=1):
    q = Decimal(abs(float(v))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    txt = f'{q:,.{d}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return ('−' if float(v) < 0 and q != 0 else '') + txt


pct_fmt = FuncFormatter(lambda v, _: br(v, 0) + '%')
dec_fmt = FuncFormatter(lambda v, _: br(v, 0) if float(v).is_integer() else br(v, 1))


def save(fig, name):
    fig.savefig(os.path.join(FIG, name), bbox_inches='tight', facecolor='white')
    plt.close(fig)


def bars(ax, labels, values, color, total=None, fmt_top=None, width=0.55, rotate=0):
    x = np.arange(len(values))
    colors = color if isinstance(color, list) else [color] * len(values)
    ax.bar(x, values, width=width, color=colors, zorder=2)
    top = max(values)
    for i, v in enumerate(values):
        txt = fmt_top(v) if fmt_top else (f'{v}\n{br(v / total * 100)}%' if total else str(v))
        ax.text(i, v + top * 0.025, txt, ha='center', va='bottom', fontsize=9, color=INK)
    ax.set_xticks(x, labels, rotation=rotate)
    ax.set_ylim(0, top * 1.28)
    ax.yaxis.set_major_locator(MaxNLocator(5, integer=True))
    ax.yaxis.set_major_formatter(dec_fmt)
    ax.tick_params(axis='x', length=0)


fq = R['freq']

# 1 — perfil
fig, axs = plt.subplots(1, 3, figsize=(10, 3.4), gridspec_kw={'width_ratios': [2, 3, 4]})
for ax, key, title in [(axs[0], 'genero', 'Gênero'), (axs[1], 'faixa_etaria', 'Faixa etária (anos)'),
                       (axs[2], 'situacao', 'Situação na semana anterior')]:
    rows = fq[key]
    labels = [r['cat'].replace('Procurando trabalho', 'Procurando\ntrabalho').replace('Outra situação', 'Outra\nsituação') for r in rows]
    bars(ax, labels, [r['n'] for r in rows], COFFEE, total=N, width=0.55)
    ax.set_title(title)
axs[0].set_ylabel('Participantes')
fig.tight_layout(w_pad=2.5)
save(fig, 'g01_perfil.png')

# 2 — consumo de café nos dois dias + por faixa etária
fig, axs = plt.subplots(1, 2, figsize=(10, 3.5), gridspec_kw={'width_ratios': [3, 2.4]})
rows = fq['consumo']
bars(axs[0], ['Nenhum dos\ndois dias', 'Um dos\ndois dias', 'Os dois\ndias'], [r['n'] for r in rows],
     [NONE, COFFEE, COFFEE], total=N)
axs[0].set_title('Dias com café no recordatório')
axs[0].set_ylabel('Participantes')
fx = R['por_faixa']
vals = [fx[k]['tomou_cafe'] * 100 for k in ['18 a 21', '22 a 25', '26 a 29']]
bars(axs[1], ['18 a 21', '22 a 25', '26 a 29'], vals, COFFEE,
     fmt_top=lambda v: br(v) + '%')
axs[1].set_ylim(0, 70)
axs[1].yaxis.set_major_formatter(pct_fmt)
axs[1].set_title('Tomaram café, por faixa etária')
for k, key in enumerate(['18 a 21', '22 a 25', '26 a 29']):
    axs[1].text(k, -9.5, f"n = {fx[key]['n']}", ha='center', fontsize=8.5, color=MUTED)
fig.tight_layout(w_pad=3)
save(fig, 'g02_consumo.png')

# 3 — xícaras por dia
fig, ax = plt.subplots(figsize=(8.2, 3.6))
rows = fq['faixa_xicaras']
bars(ax, ['0', 'Até 1', 'Mais de 1\na 2', 'Mais de 2\na 3', 'Mais de 3'], [r['n'] for r in rows],
     [NONE] + [COFFEE] * 4, total=N, width=0.55)
ax.set_ylabel('Participantes')
ax.set_xlabel('Xícaras de 240 mL por dia (média dos dois dias)', color=MUTED, labelpad=8)
save(fig, 'g03_xicaras.png')

# 4 — horário do café
hr = R['horario']['por_hora_itens']
cols = [COFFEE if 5 <= h < 12 else AMBER if 12 <= h < 18 else SLEEP for h in range(24)]
fig, ax = plt.subplots(figsize=(10, 3.6))
ax.bar(range(24), hr, width=0.72, color=cols, zorder=2)
ax.set_xticks(range(0, 24, 2), [f'{h}h' for h in range(0, 24, 2)])
ax.set_xlim(-0.7, 23.7)
ax.set_ylabel('Bebidas de café registradas')
ax.yaxis.set_major_locator(MaxNLocator(5, integer=True))
ax.tick_params(axis='x', length=0)
pi = R['horario']['por_periodo_itens']
tot = sum(pi.values())
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=COFFEE, label=f'Manhã (5h–11h59): {br(pi["Manhã"] / tot * 100)}%'),
                   Patch(color=AMBER, label=f'Tarde (12h–17h59): {br(pi["Tarde"] / tot * 100)}%'),
                   Patch(color=SLEEP, label=f'Noite (18h–4h59): {br(pi["Noite"] / tot * 100)}%')],
          loc='upper right')
ax.set_ylim(0, max(hr) * 1.18)
save(fig, 'g04_horario.png')

# 5 — horas de sono
rows = fq['sono_util']
fig, ax = plt.subplots(figsize=(8.2, 3.6))
bars(ax, [r['cat'] for r in rows], [r['n'] for r in rows], [AMBER, AMBER, SLEEP, SLEEP, SLEEP], total=N)
ax.set_ylabel('Participantes')
ax.set_xlabel('Horas habituais de sono em dias úteis', color=MUTED, labelpad=8)
ax.legend(handles=[Patch(color=AMBER, label=f'Abaixo de 7 h: {br(R["prob"]["P_sono_insuf"] * 100)}%'),
                   Patch(color=SLEEP, label='7 h ou mais')], loc='upper left')
save(fig, 'g05_sono_horas.png')

# 6 — PHQ-9 itens 3 e 7
lev = ['Nenhum dia', 'Vários dias', 'Mais da metade\ndos dias', 'Quase todos\nos dias']
ps = [r['n'] for r in fq['prob_sono']]
dc = [r['n'] for r in fq['dif_conc']]
x = np.arange(4)
fig, ax = plt.subplots(figsize=(9, 3.7))
w = 0.34
ax.bar(x - w / 2 - 0.01, ps, width=w, color=SLEEP, label='Problemas de sono (item 3)', zorder=2)
ax.bar(x + w / 2 + 0.01, dc, width=w, color=AMBER, label='Dificuldade de concentração (item 7)', zorder=2)
for i in range(4):
    ax.text(x[i] - w / 2 - 0.01, ps[i] + 5, f'{br(ps[i] / N * 100)}%', ha='center', fontsize=8.5)
    ax.text(x[i] + w / 2 + 0.01, dc[i] + 5, f'{br(dc[i] / N * 100)}%', ha='center', fontsize=8.5)
ax.set_xticks(x, lev)
ax.tick_params(axis='x', length=0)
ax.set_ylabel('Participantes')
ax.set_ylim(0, max(ps + dc) * 1.22)
ax.legend(loc='upper right')
save(fig, 'g06_phq9.png')

# 7 — boxplots
fig, axs = plt.subplots(4, 1, figsize=(9, 5.2))
specs = [('Xícaras/dia (só quem tomou café)', b.loc[b['Tomou café (Sim/Não)'] == 'Sim', 'Xícaras/dia (240 mL)'], COFFEE, None),
         ('Cafeína total (mg/dia)', b['Cafeína total (mg/dia)'], COFFEE, None),
         ('Sono em dias úteis (h)', b['Sono em dias úteis (h)'], SLEEP, None),
         ('Idade (anos)', b['Idade (anos)'], '#7a6a5c', None)]
for ax, (lab, ser, colr, _) in zip(axs, specs):
    bp = ax.boxplot(ser, orientation='horizontal', widths=0.5, patch_artist=True, showmeans=True,
                    meanprops=dict(marker='D', markerfacecolor='white', markeredgecolor=INK, markersize=6),
                    medianprops=dict(color=INK, linewidth=2), whiskerprops=dict(color=MUTED),
                    capprops=dict(color=MUTED), flierprops=dict(marker='o', markersize=3.5, markerfacecolor=colr,
                                                                 markeredgecolor='white', alpha=.75))
    bp['boxes'][0].set(facecolor=colr + '33', edgecolor=colr, linewidth=1.4)
    ax.set_yticks([])
    ax.set_title(lab, fontsize=10)
    ax.grid(axis='x', color=GRID)
    ax.grid(axis='y', visible=False)
    ax.xaxis.set_major_formatter(dec_fmt)
fig.tight_layout(h_pad=1.2)
save(fig, 'g07_boxplots.png')

# 8 — dispersão xícaras × dificuldade de concentração
rng = np.random.default_rng(7)
X = b['Xícaras/dia (240 mL)'].to_numpy()
Yc = b['Dificuldade de concentração (0–3)'].to_numpy()
Ys = b['Sono em dias úteis (h)'].to_numpy()
pc = R['pearson']['xic_conc']
fig, ax = plt.subplots(figsize=(9, 4))
jx = X + np.where(X == 0, rng.uniform(-0.12, 0.12, len(X)), 0)
jy = Yc + rng.uniform(-0.22, 0.22, len(Yc))
ax.scatter(jx, jy, s=16, color=COFFEE, alpha=.55, edgecolors='white', linewidths=.5, zorder=2)
xx = np.linspace(0, 8, 50)
ax.plot(xx, pc['a'] + pc['b'] * xx, color=INK, lw=2, zorder=3)
ax.text(5.2, 2.55, f"Ŷ = {br(pc['a'], 3)} − {br(abs(pc['b']), 3)}·X\nr = {br(pc['r'], 3)} · R² = {br(pc['r2'] * 100, 2)}%",
        fontsize=9.5, color=INK, bbox=dict(boxstyle='round,pad=.4', fc='white', ec=GRID))
ax.set_yticks([0, 1, 2, 3], ['0 · nenhum dia', '1 · vários dias', '2 · mais da metade', '3 · quase todos'])
ax.set_xlabel('Xícaras de 240 mL por dia', color=MUTED)
ax.set_xlim(-0.3, 8.3)
ax.set_ylim(-0.45, 3.45)
ax.grid(axis='x', color=GRID)
ax.xaxis.set_major_formatter(dec_fmt)
save(fig, 'g08_disp_conc.png')

# 9 — dispersão xícaras × horas de sono
ps_ = R['pearson']['xic_sono']
fig, ax = plt.subplots(figsize=(9, 4))
ax.scatter(jx, Ys + rng.uniform(-0.12, 0.12, len(Ys)), s=16, color=SLEEP, alpha=.5, edgecolors='white', linewidths=.5, zorder=2)
ax.plot(xx, ps_['a'] + ps_['b'] * xx, color=INK, lw=2, zorder=3)
ax.axhline(7, color=AMBER, lw=1.2, ls=(0, (4, 3)), zorder=1)
ax.text(8.2, 6.45, 'mínimo recomendado: 7 h', color=AMBER, ha='right', fontsize=8.5)
ax.text(5.2, 12.3, f"Ŷ = {br(ps_['a'], 3)} − {br(abs(ps_['b']), 3)}·X\nr = {br(ps_['r'], 3)} · R² = {br(ps_['r2'] * 100, 2)}%",
        fontsize=9.5, color=INK, bbox=dict(boxstyle='round,pad=.4', fc='white', ec=GRID))
ax.set_xlabel('Xícaras de 240 mL por dia', color=MUTED)
ax.set_ylabel('Horas de sono em dias úteis')
ax.set_xlim(-0.3, 8.3)
ax.grid(axis='x', color=GRID)
ax.xaxis.set_major_formatter(dec_fmt)
ax.yaxis.set_major_formatter(dec_fmt)
save(fig, 'g09_disp_sono.png')

# 10 — probabilidade condicional
pr = R['prob']
fig, axs = plt.subplots(1, 2, figsize=(10, 3.7), gridspec_kw={'width_ratios': [2, 4]})
v1 = [pr['A_C']['p_e2_dado_e1'] * 100, pr['A_C']['p_e2_dado_nao_e1'] * 100]
bars(axs[0], ['Tomou café', 'Não tomou'], v1, [COFFEE, NONE], fmt_top=lambda v: br(v) + '%')
axs[0].set_title('Segundo o consumo de café')
gps = R['grupos_probsono']
v2 = [g['conc_prej'] * 100 for g in gps]
labs2 = ['Nenhum dia', 'Vários dias', 'Mais da metade', 'Quase todos']
bars(axs[1], [f"{l}\nn = {g['n']}" for l, g in zip(labs2, gps)], v2, SLEEP, fmt_top=lambda v: br(v) + '%')
axs[1].set_title('Segundo a frequência de problemas de sono')
axs[0].set_xticks([0, 1], [f"Tomou café\nn = {pr['A_C']['a'] + pr['A_C']['b']}", f"Não tomou\nn = {pr['A_C']['c'] + pr['A_C']['d']}"])
for ax in axs:
    ax.set_ylim(0, 92)
    ax.yaxis.set_major_formatter(pct_fmt)
axs[0].set_ylabel('Com dificuldade de concentração')
fig.tight_layout(w_pad=3)
save(fig, 'g10_condicional.png')

# 11 — binomial
pk = [v * 100 for v in R['binomial']['pk']]
fig, ax = plt.subplots(figsize=(8.2, 3.5))
bars(ax, [f'k = {k}' for k in range(6)], pk, [COFFEE] * 6, fmt_top=lambda v: br(v, 2) + '%')
ax.set_ylim(0, 45)
ax.yaxis.set_major_formatter(pct_fmt)
ax.set_ylabel('P(X = k)')
ax.set_xlabel(f"Número de jovens que tomaram café entre 5 sorteados (p = {br(R['binomial']['p'], 3)})", color=MUTED, labelpad=8)
save(fig, 'g11_binomial.png')

# 12 — fontes de cafeína
fc = R['fontes_cafeina']
labs = list(fc.keys())[::-1]
vals = [fc[k] * 100 for k in labs]
fig, ax = plt.subplots(figsize=(8.2, 3.1))
ax.barh(labs, vals, height=0.52, color=[NONE if 'Outros' in l else (COFFEE if l == 'Café' else '#7a6a5c') for l in labs], zorder=2)
for i, v in enumerate(vals):
    ax.text(v + 1, i, br(v) + '%', va='center', fontsize=9)
ax.set_xlim(0, 72)
ax.grid(axis='y', visible=False)
ax.grid(axis='x', color=GRID)
ax.xaxis.set_major_formatter(pct_fmt)
ax.tick_params(axis='y', length=0)
ax.set_xlabel('Participação na cafeína total ingerida nos dois dias', color=MUTED)
save(fig, 'g12_fontes_cafeina.png')
print('ok', sorted(os.listdir(FIG)))
