"""
Constrói a amostra analítica (NHANES ago/2021–ago/2023, adultos de 18 a 29 anos)
e calcula todas as estatísticas usadas na planilha, no relatório e na apresentação.

Entrada : arquivos .xpt oficiais do CDC/NCHS em ../raw
Saída   : ../out/base_analitica.csv, ../out/itens_cafe.csv, ../out/dados_brutos.csv,
          ../out/results.json
"""
import json, math, os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, '..', 'raw')
OUT = os.path.join(HERE, '..', 'out')
os.makedirs(OUT, exist_ok=True)

CUP_G = 240.0          # xícara-padrão USDA: 8 fl oz ≈ 240 g de bebida
GAP_LIMIT = 8.8        # h — Gardiner et al. (2023): café ≥ 8,8 h antes de dormir
AGE_MIN, AGE_MAX = 18, 29


def rd(name):
    df = pd.read_sas(os.path.join(RAW, name + '.xpt'), format='xport', encoding='latin-1')
    num = df.select_dtypes('number').columns
    # o formato XPORT grava o zero como 5,4e-79; normaliza para 0
    df[num] = df[num].mask(df[num].abs() < 1e-10, 0)
    return df


demo, ocq, slq, dpq = rd('DEMO_L'), rd('OCQ_L'), rd('SLQ_L'), rd('DPQ_L')
t1, t2, i1, i2 = rd('DR1TOT_L'), rd('DR2TOT_L'), rd('DR1IFF_L'), rd('DR2IFF_L')
fcd = rd('DRXFCD_L')
fcd['code'] = fcd['DRXFDCD'].astype(int)
DESC = dict(zip(fcd['code'], fcd['DRXFCLD']))

# ---------------------------------------------------------------- fluxo de seleção
d = (demo.merge(ocq, on='SEQN', how='left')
         .merge(slq, on='SEQN', how='left')
         .merge(dpq, on='SEQN', how='left')
         .merge(t1[['SEQN', 'DR1DRSTZ', 'DR1TCAFF', 'DR1DAY', 'DRDINT']], on='SEQN', how='left')
         .merge(t2[['SEQN', 'DR2DRSTZ', 'DR2TCAFF', 'DR2DAY', 'WTDR2D']], on='SEQN', how='left'))

flow = [{'etapa': 'Participantes do NHANES ago/2021–ago/2023 (arquivo DEMO_L)', 'n': int(len(d))}]
m = d['RIDAGEYR'].between(AGE_MIN, AGE_MAX)
flow.append({'etapa': f'Com {AGE_MIN} a {AGE_MAX} anos na entrevista', 'n': int(m.sum())})
m &= d['DPQ030'].isin([0, 1, 2, 3]) & d['DPQ070'].isin([0, 1, 2, 3])
flow.append({'etapa': 'Responderam aos itens de sono e de concentração do PHQ-9', 'n': int(m.sum())})
m &= d['SLD012'].notna() & d['SLD013'].notna()
flow.append({'etapa': 'Informaram horários de dormir e acordar (horas de sono calculáveis)', 'n': int(m.sum())})
m &= (d['DR1DRSTZ'] == 1) & (d['DR2DRSTZ'] == 1)
flow.append({'etapa': 'Completaram os dois recordatórios alimentares de 24 h com qualidade', 'n': int(m.sum())})
s = d[m].copy().sort_values('SEQN').reset_index(drop=True)
N = len(s)


# ---------------------------------------------------------------- itens de café (dias 1 e 2)
def coffee_items(df, p, day):
    df = df[df['SEQN'].isin(s['SEQN'])].copy()
    df['code'] = df[p + 'IFDCD'].astype(int)
    c = df[(df['code'] >= 92100000) & (df['code'] < 92190000)].copy()   # bebidas de café (FNDDS 921xxxxx)
    c['dia'] = day
    c['dow'] = c[p + 'DAY'].astype(int)
    c['seg'] = c[p + '_020'].astype(float)
    c['g'] = c[p + 'IGRMS'].astype(float)
    c['caf'] = c[p + 'ICAFF'].astype(float)
    c['ocasiao'] = c[p + '_030Z'].astype(int)
    return c[['SEQN', 'dia', 'dow', 'seg', 'code', 'g', 'caf', 'ocasiao']]


it = pd.concat([coffee_items(i1, 'DR1', 1), coffee_items(i2, 'DR2', 2)], ignore_index=True)
it['h'] = it['seg'] / 3600.0


def periodo(h):
    if 5 <= h < 12:
        return 'Manhã'
    if 12 <= h < 18:
        return 'Tarde'
    return 'Noite'


it['periodo'] = it['h'].apply(periodo)
it['h_ord'] = np.where(it['h'] < 5, it['h'] + 24, it['h'])   # 0h–4h59 = continuação da noite

PT_DESC = {
    'Coffee, brewed': 'Café coado',
    'Iced Coffee, brewed': 'Café coado gelado',
    'Coffee, espresso': 'Café espresso',
    'Coffee, instant, reconstituted': 'Café solúvel preparado',
    'Coffee, bottled/canned': 'Café pronto (garrafa/lata)',
    'Coffee, Latte, flavored': 'Café latte aromatizado',
    'Coffee, Cappuccino': 'Cappuccino',
    'Coffee, Latte': 'Café latte',
    'Coffee, macchiato, sweetened': 'Macchiato adoçado',
    'Coffee, bottled/canned, light': 'Café pronto light (garrafa/lata)',
    'Coffee, Iced Latte, with non-dairy milk, flavored': 'Latte gelado com bebida vegetal, aromatizado',
    'Coffee, brewed, decaffeinated': 'Café coado descafeinado',
    'Coffee, instant, decaffeinated, reconstituted': 'Café solúvel descafeinado',
    'Coffee, Cappuccino, with non-dairy milk': 'Cappuccino com bebida vegetal',
    'Coffee, Iced Latte, flavored': 'Latte gelado aromatizado',
    'Frozen coffee drink': 'Café batido com gelo',
    'Coffee, brewed, blend of regular and decaffeinated': 'Café coado, mistura comum e descafeinado',
    'Coffee, Latte, with non-dairy milk, flavored': 'Latte com bebida vegetal, aromatizado',
    'Frozen coffee drink, with whipped cream': 'Café batido com gelo e chantili',
    'Coffee, pre-lightened': 'Café com leite pronto',
    'Coffee, Iced Latte, with non-dairy milk': 'Latte gelado com bebida vegetal',
    'Iced Coffee, brewed, decaffeinated': 'Café coado gelado descafeinado',
    'Coffee, cafe con leche': 'Café com leite (café con leche)',
    'Frozen mocha coffee drink, with whipped cream': 'Mocha batido com gelo e chantili',
    'Coffee, Iced Latte': 'Latte gelado',
    'Coffee, decaffeinated, pre-sweetened with sugar': 'Café descafeinado adoçado',
    'Coffee, instant, pre-sweetened with sugar, reconstituted': 'Café solúvel adoçado',
}
OCASIAO = {1: 'Café da manhã', 2: 'Almoço', 3: 'Jantar', 4: 'Ceia', 5: 'Brunch', 6: 'Lanche',
           7: 'Bebida avulsa', 9: 'Consumo prolongado', 10: 'Café da manhã', 11: 'Almoço',
           12: 'Almoço', 13: 'Lanche', 14: 'Jantar', 15: 'Lanche', 16: 'Lanche', 17: 'Lanche',
           18: 'Lanche', 19: 'Bebida avulsa'}
DOW = {1: 'Domingo', 2: 'Segunda', 3: 'Terça', 4: 'Quarta', 5: 'Quinta', 6: 'Sexta', 7: 'Sábado'}

it['descricao_en'] = it['code'].map(DESC)
it['descricao_pt'] = it['descricao_en'].map(PT_DESC).fillna(it['descricao_en'])
it['descafeinado'] = it['descricao_en'].str.contains('decaffeinated', case=False) & \
    ~it['descricao_en'].str.contains('blend', case=False)


def hhmm(sec):
    sec = int(round(sec))
    return f'{sec // 3600:02d}:{(sec % 3600) // 60:02d}'


it['horario'] = it['seg'].apply(hhmm)

# ---------------------------------------------------------------- variáveis por participante
g = it.groupby(['SEQN', 'dia'])['g'].sum().unstack(fill_value=0).reindex(columns=[1, 2], fill_value=0)
s['g_d1'] = s['SEQN'].map(g[1]).fillna(0)
s['g_d2'] = s['SEQN'].map(g[2]).fillna(0)
cafc = it.groupby('SEQN')['caf'].sum()
s['caf_cafe'] = (s['SEQN'].map(cafc).fillna(0) / 2)
s['dias_cafe'] = (s['g_d1'] > 0).astype(int) + (s['g_d2'] > 0).astype(int)
s['xicaras'] = (s['g_d1'] + s['g_d2']) / 2 / CUP_G
s['cafeina'] = (s['DR1TCAFF'] + s['DR2TCAFF']) / 2

per = it.groupby(['SEQN', 'periodo'])['g'].sum().unstack(fill_value=0).reindex(columns=['Manhã', 'Tarde', 'Noite'], fill_value=0)
main = per.idxmax(axis=1)  # idxmax devolve o primeiro em caso de empate (ordem manhã→tarde→noite)
s['periodo_maior'] = s['SEQN'].map(main).fillna('Não consumiu')


def hours(x):
    if not isinstance(x, str) or ':' not in x:
        return np.nan
    h, mnt = x.split(':')
    return int(h) + int(mnt) / 60


s['dormir_util_h'] = s['SLQ300'].apply(hours)
s['acordar_util_h'] = s['SLQ310'].apply(hours)
s['dormir_fds_h'] = s['SLQ320'].apply(hours)

last = it.groupby(['SEQN', 'dia']).agg(ultimo=('h_ord', 'max'), dow=('dow', 'first')).reset_index()
last = last.merge(s[['SEQN', 'dormir_util_h', 'dormir_fds_h']], on='SEQN')
last['dormir'] = np.where(last['dow'].isin([6, 7]), last['dormir_fds_h'], last['dormir_util_h'])
last['dormir_adj'] = np.where(last['dormir'] < 12, last['dormir'] + 24, last['dormir'])
last['intervalo'] = last['dormir_adj'] - last['ultimo']
gap_min = last.groupby('SEQN')['intervalo'].min()
s['intervalo_min'] = s['SEQN'].map(gap_min)

# rótulos
s['genero'] = s['RIAGENDR'].map({1: 'Masculino', 2: 'Feminino'})
s['idade'] = s['RIDAGEYR'].astype(int)
s['faixa_etaria'] = pd.cut(s['idade'], [17, 21, 25, 29], labels=['18 a 21', '22 a 25', '26 a 29']).astype(str)


def situacao(r):
    if r['OCD150'] in (1, 2):
        return 'Trabalhando'
    if r['OCD150'] == 3:
        return 'Procurando trabalho'
    if r['OCD150'] == 4 and r['OCQ383'] == 2:
        return 'Estudando'
    return 'Outra situação'


s['situacao'] = s.apply(situacao, axis=1)
s['consumo_cat'] = s['dias_cafe'].map({0: 'Nenhum dos dois dias', 1: 'Um dos dois dias', 2: 'Os dois dias'})
s['tomou_cafe'] = np.where(s['dias_cafe'] > 0, 'Sim', 'Não')


def faixa_x(x):
    if x == 0:
        return '0'
    if x <= 1:
        return 'Até 1'
    if x <= 2:
        return 'Mais de 1 a 2'
    if x <= 3:
        return 'Mais de 2 a 3'
    return 'Mais de 3'


s['faixa_xicaras'] = s['xicaras'].apply(faixa_x)
s['sono_util'] = s['SLD012'].astype(float)
s['sono_fds'] = s['SLD013'].astype(float)
s['sono_insuf'] = np.where(s['sono_util'] < 7, 'Sim', 'Não')
LIK = {0: 'Nenhum dia', 1: 'Vários dias', 2: 'Mais da metade dos dias', 3: 'Quase todos os dias'}
s['prob_sono'] = s['DPQ030'].astype(int)
s['prob_sono_txt'] = s['prob_sono'].map(LIK)
s['dif_conc'] = s['DPQ070'].astype(int)
s['dif_conc_txt'] = s['dif_conc'].map(LIK)
s['sono_prej'] = np.where(s['prob_sono'] >= 1, 'Sim', 'Não')
s['conc_prej'] = np.where(s['dif_conc'] >= 1, 'Sim', 'Não')


def fmt_h(h):
    if pd.isna(h):
        return ''
    mins = int(round(h * 60)) % (24 * 60)
    return f'{mins // 60:02d}:{mins % 60:02d}'


s['dormir_util'] = s['dormir_util_h'].apply(fmt_h)
s['acordar_util'] = s['acordar_util_h'].apply(fmt_h)
s['ID'] = np.arange(1, N + 1)

base = pd.DataFrame({
    'ID': s['ID'],
    'SEQN (NHANES)': s['SEQN'].astype(int),
    'Gênero': s['genero'],
    'Idade (anos)': s['idade'],
    'Faixa etária': s['faixa_etaria'],
    'Situação na semana anterior': s['situacao'],
    'Café no dia 1 (mL)': s['g_d1'].round(1),
    'Café no dia 2 (mL)': s['g_d2'].round(1),
    'Dias com café (0–2)': s['dias_cafe'],
    'Consumo de café': s['consumo_cat'],
    'Tomou café (Sim/Não)': s['tomou_cafe'],
    'Xícaras/dia (240 mL)': s['xicaras'].round(4),
    'Faixa de xícaras/dia': s['faixa_xicaras'],
    'Período de maior consumo': s['periodo_maior'],
    'Menor intervalo café→dormir (h)': s['intervalo_min'].round(2),
    'Cafeína total (mg/dia)': s['cafeina'].round(1),
    'Cafeína do café (mg/dia)': s['caf_cafe'].round(1),
    'Hora de dormir (dias úteis)': s['dormir_util'],
    'Hora de acordar (dias úteis)': s['acordar_util'],
    'Sono em dias úteis (h)': s['sono_util'],
    'Sono no fim de semana (h)': s['sono_fds'],
    'Sono < 7 h em dias úteis': s['sono_insuf'],
    'Problemas de sono (0–3)': s['prob_sono'],
    'Problemas de sono (frequência)': s['prob_sono_txt'],
    'Sono prejudicado (Sim/Não)': s['sono_prej'],
    'Dificuldade de concentração (0–3)': s['dif_conc'],
    'Dificuldade de concentração (frequência)': s['dif_conc_txt'],
    'Concentração prejudicada (Sim/Não)': s['conc_prej'],
})
base.to_csv(os.path.join(OUT, 'base_analitica.csv'), index=False)

raw_cols = ['SEQN', 'RIAGENDR', 'RIDAGEYR', 'OCD150', 'OCQ383', 'SLQ300', 'SLQ310', 'SLD012',
            'SLQ320', 'SLQ330', 'SLD013', 'DPQ030', 'DPQ070', 'DR1DRSTZ', 'DR2DRSTZ', 'DR1DAY',
            'DR2DAY', 'DR1TCAFF', 'DR2TCAFF', 'WTDR2D', 'SDMVSTRA', 'SDMVPSU']
bruto = s[raw_cols].copy()
for c in ['SEQN', 'RIAGENDR', 'RIDAGEYR', 'DPQ030', 'DPQ070', 'DR1DRSTZ', 'DR2DRSTZ', 'DR1DAY', 'DR2DAY', 'SDMVSTRA', 'SDMVPSU']:
    bruto[c] = bruto[c].astype(int)
bruto.insert(0, 'ID', s['ID'])
bruto.to_csv(os.path.join(OUT, 'dados_brutos.csv'), index=False)

idmap = dict(zip(s['SEQN'], s['ID']))
itens = it.sort_values(['SEQN', 'dia', 'seg']).copy()
itens_out = pd.DataFrame({
    'ID': itens['SEQN'].map(idmap),
    'SEQN (NHANES)': itens['SEQN'].astype(int),
    'Dia do recordatório': itens['dia'],
    'Dia da semana': itens['dow'].map(DOW),
    'Horário': itens['horario'],
    'Período': itens['periodo'],
    'Ocasião': itens['ocasiao'].map(OCASIAO),
    'Código USDA (FNDDS)': itens['code'],
    'Descrição (FNDDS)': itens['descricao_en'],
    'Bebida': itens['descricao_pt'],
    'Volume (mL ≈ g)': itens['g'].round(1),
    'Xícaras (240 mL)': (itens['g'] / CUP_G).round(3),
    'Cafeína (mg)': itens['caf'].round(1),
})
itens_out.to_csv(os.path.join(OUT, 'itens_cafe.csv'), index=False)


# ---------------------------------------------------------------- estatísticas
def desc(x):
    x = pd.Series(x, dtype=float)
    vc = x.round(6).value_counts()
    mode_val = float(vc[vc == vc.max()].index.min())
    return dict(n=int(x.size), soma=float(x.sum()), media=float(x.mean()), mediana=float(x.median()),
                moda=mode_val, moda_freq=int(vc.max()), minimo=float(x.min()), maximo=float(x.max()),
                amplitude=float(x.max() - x.min()), variancia=float(x.var(ddof=1)), dp=float(x.std(ddof=1)),
                q1=float(np.percentile(x, 25)), q3=float(np.percentile(x, 75)),
                sq_desvios=float(((x - x.mean()) ** 2).sum()),
                cv=float(x.std(ddof=1) / x.mean()) if x.mean() else None)


def freq(series, order):
    vc = series.value_counts()
    rows = [{'cat': str(k), 'n': int(vc.get(k, 0)), 'pct': float(vc.get(k, 0) / len(series))} for k in order]
    assert sum(r['n'] for r in rows) == len(series), (order, vc)
    return rows


def pearson_block(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float); n = len(x)
    Sx, Sy, Sxx, Syy, Sxy = x.sum(), y.sum(), (x * x).sum(), (y * y).sum(), (x * y).sum()
    num = n * Sxy - Sx * Sy
    t1_ = n * Sxx - Sx ** 2
    t2_ = n * Syy - Sy ** 2
    r = num / math.sqrt(t1_ * t2_)
    tt = r * math.sqrt((n - 2) / (1 - r * r))
    p = 2 * stats.t.sf(abs(tt), n - 2)
    z = math.atanh(r); se = 1 / math.sqrt(n - 3)
    lo, hi = math.tanh(z - 1.96 * se), math.tanh(z + 1.96 * se)
    rs, ps = stats.spearmanr(x, y)
    b = num / t1_
    a = y.mean() - b * x.mean()
    resid = y - (a + b * x)
    sse = float((resid ** 2).sum())
    se_b = math.sqrt(sse / (n - 2) / ((x - x.mean()) ** 2).sum())
    tcrit = stats.t.ppf(0.975, n - 2)
    return dict(n=n, Sx=Sx, Sy=Sy, Sxx=Sxx, Syy=Syy, Sxy=Sxy, num=num, t1=t1_, t2=t2_,
                den=math.sqrt(t1_ * t2_), r=r, r2=r * r, t=tt, p=p, ci_lo=lo, ci_hi=hi,
                spearman=rs, spearman_p=ps, b=b, a=a, se_b=se_b, t_b=b / se_b,
                b_lo=b - tcrit * se_b, b_hi=b + tcrit * se_b, xbar=x.mean(), ybar=y.mean())


R = {'n': N, 'fluxo': flow}

R['freq'] = {
    'genero': freq(s['genero'], ['Feminino', 'Masculino']),
    'faixa_etaria': freq(s['faixa_etaria'], ['18 a 21', '22 a 25', '26 a 29']),
    'situacao': freq(s['situacao'], ['Trabalhando', 'Estudando', 'Procurando trabalho', 'Outra situação']),
    'consumo': freq(s['consumo_cat'], ['Nenhum dos dois dias', 'Um dos dois dias', 'Os dois dias']),
    'tomou_cafe': freq(s['tomou_cafe'], ['Sim', 'Não']),
    'faixa_xicaras': freq(s['faixa_xicaras'], ['0', 'Até 1', 'Mais de 1 a 2', 'Mais de 2 a 3', 'Mais de 3']),
    'periodo': freq(s.loc[s['dias_cafe'] > 0, 'periodo_maior'], ['Manhã', 'Tarde', 'Noite']),
    'prob_sono': freq(s['prob_sono_txt'], list(LIK.values())),
    'dif_conc': freq(s['dif_conc_txt'], list(LIK.values())),
    'sono_prej': freq(s['sono_prej'], ['Sim', 'Não']),
    'conc_prej': freq(s['conc_prej'], ['Sim', 'Não']),
    'sono_insuf': freq(s['sono_insuf'], ['Sim', 'Não']),
}
sono_cls = pd.cut(s['sono_util'], [0, 5.99, 6.99, 7.99, 8.99, 24], labels=['Menos de 6 h', '6 a 6,5 h', '7 a 7,5 h', '8 a 8,5 h', '9 h ou mais']).astype(str)
R['freq']['sono_util'] = freq(sono_cls, ['Menos de 6 h', '6 a 6,5 h', '7 a 7,5 h', '8 a 8,5 h', '9 h ou mais'])

R['desc'] = {
    'idade': desc(s['idade']),
    'xicaras': desc(s['xicaras']),
    'xicaras_consumidores': desc(s.loc[s['dias_cafe'] > 0, 'xicaras']),
    'cafeina': desc(s['cafeina']),
    'cafeina_cafe': desc(s['caf_cafe']),
    'sono_util': desc(s['sono_util']),
    'sono_fds': desc(s['sono_fds']),
    'prob_sono': desc(s['prob_sono']),
    'dif_conc': desc(s['dif_conc']),
}

R['pearson'] = {
    'xic_conc': pearson_block(s['xicaras'], s['dif_conc']),
    'xic_probsono': pearson_block(s['xicaras'], s['prob_sono']),
    'xic_sono': pearson_block(s['xicaras'], s['sono_util']),
    'caf_conc': pearson_block(s['cafeina'], s['dif_conc']),
    'caf_sono': pearson_block(s['cafeina'], s['sono_util']),
    'caf_probsono': pearson_block(s['cafeina'], s['prob_sono']),
    'probsono_conc': pearson_block(s['prob_sono'], s['dif_conc']),
    'sono_conc': pearson_block(s['sono_util'], s['dif_conc']),
    'idade_xic': pearson_block(s['idade'], s['xicaras']),
}
# robustez: sem os consumidores extremos (> 4 xícaras/dia)
mk = s['xicaras'] <= 4
R['robustez'] = {
    'n_excluidos': int((~mk).sum()),
    'xic_conc_r': pearson_block(s.loc[mk, 'xicaras'], s.loc[mk, 'dif_conc'])['r'],
    'xic_probsono_r': pearson_block(s.loc[mk, 'xicaras'], s.loc[mk, 'prob_sono'])['r'],
    'xic_sono_r': pearson_block(s.loc[mk, 'xicaras'], s.loc[mk, 'sono_util'])['r'],
    'consumidores_xic_conc_r': pearson_block(s.loc[s['dias_cafe'] > 0, 'xicaras'], s.loc[s['dias_cafe'] > 0, 'dif_conc'])['r'],
    'consumidores_xic_sono_r': pearson_block(s.loc[s['dias_cafe'] > 0, 'xicaras'], s.loc[s['dias_cafe'] > 0, 'sono_util'])['r'],
    'consumidores_n': int((s['dias_cafe'] > 0).sum()),
}

# médias observadas por grupo (para o simulador e para os gráficos de linha)
grp = np.floor(s['xicaras'] + 0.5).clip(upper=5).astype(int)
R['grupos_xicaras'] = [
    {'x': k, 'n': int((grp == k).sum()),
     'conc': float(s.loc[grp == k, 'dif_conc'].mean()) if (grp == k).any() else None,
     'probsono': float(s.loc[grp == k, 'prob_sono'].mean()) if (grp == k).any() else None,
     'sono': float(s.loc[grp == k, 'sono_util'].mean()) if (grp == k).any() else None,
     'conc_prej': float((s.loc[grp == k, 'dif_conc'] >= 1).mean()) if (grp == k).any() else None,
     'sono_prej': float((s.loc[grp == k, 'prob_sono'] >= 1).mean()) if (grp == k).any() else None}
    for k in range(6)]
R['grupos_probsono'] = [
    {'x': k, 'n': int((s['prob_sono'] == k).sum()), 'conc': float(s.loc[s['prob_sono'] == k, 'dif_conc'].mean()),
     'conc_prej': float((s.loc[s['prob_sono'] == k, 'dif_conc'] >= 1).mean())} for k in range(4)]
R['grupos_dias'] = [
    {'dias': k, 'n': int((s['dias_cafe'] == k).sum()),
     'sono': float(s.loc[s['dias_cafe'] == k, 'sono_util'].mean()),
     'sono_insuf': float((s.loc[s['dias_cafe'] == k, 'sono_util'] < 7).mean()),
     'probsono': float(s.loc[s['dias_cafe'] == k, 'prob_sono'].mean()),
     'sono_prej': float((s.loc[s['dias_cafe'] == k, 'prob_sono'] >= 1).mean()),
     'conc': float(s.loc[s['dias_cafe'] == k, 'dif_conc'].mean()),
     'conc_prej': float((s.loc[s['dias_cafe'] == k, 'dif_conc'] >= 1).mean()),
     'cafeina': float(s.loc[s['dias_cafe'] == k, 'cafeina'].mean()),
     'idade': float(s.loc[s['dias_cafe'] == k, 'idade'].mean())} for k in range(3)]

# probabilidades e tabelas de contingência
A = s['dias_cafe'] > 0
B = s['prob_sono'] >= 1
C = s['dif_conc'] >= 1


def two_by_two(e1, e2):
    a_ = int((e1 & e2).sum()); b_ = int((e1 & ~e2).sum()); c_ = int((~e1 & e2).sum()); d_ = int((~e1 & ~e2).sum())
    chi2, p, dof, exp = stats.chi2_contingency([[a_, b_], [c_, d_]], correction=False)
    return dict(a=a_, b=b_, c=c_, d=d_, p_e2_dado_e1=a_ / (a_ + b_), p_e2_dado_nao_e1=c_ / (c_ + d_),
                p_e1_e_e2=a_ / N, chi2=float(chi2), p=float(p), esperado=[list(map(float, r)) for r in exp])


R['prob'] = {
    'P_A': float(A.mean()), 'n_A': int(A.sum()),
    'P_A2': float((s['dias_cafe'] == 2).mean()), 'n_A2': int((s['dias_cafe'] == 2).sum()),
    'P_B': float(B.mean()), 'n_B': int(B.sum()),
    'P_C': float(C.mean()), 'n_C': int(C.sum()),
    'A_B': two_by_two(A, B), 'A_C': two_by_two(A, C), 'B_C': two_by_two(B, C),
    'P_sono_insuf': float((s['sono_util'] < 7).mean()), 'n_sono_insuf': int((s['sono_util'] < 7).sum()),
}
p_ = R['prob']['P_A']
R['binomial'] = {'n': 5, 'p': p_, 'pk': [math.comb(5, k) * p_ ** k * (1 - p_) ** (5 - k) for k in range(6)]}

# horário do café
R['horario'] = {
    'itens': int(len(it)), 'consumidores': int(it['SEQN'].nunique()),
    'por_hora_itens': [int(((it['h'] >= h) & (it['h'] < h + 1)).sum()) for h in range(24)],
    'por_hora_ml': [float(it.loc[(it['h'] >= h) & (it['h'] < h + 1), 'g'].sum()) for h in range(24)],
    'por_periodo_itens': {k: int((it['periodo'] == k).sum()) for k in ['Manhã', 'Tarde', 'Noite']},
    'por_periodo_ml': {k: float(it.loc[it['periodo'] == k, 'g'].sum()) for k in ['Manhã', 'Tarde', 'Noite']},
    'antes_10h_ml_pct': float(it.loc[it['h'] < 10, 'g'].sum() / it['g'].sum()),
    'ate_12h_itens_pct': float((it['h'] < 12).mean()),
    'mediana_horario_itens': float(it['h'].median()),
    'descafeinado_itens': int(it['descafeinado'].sum()),
    'tipos': it.groupby('descricao_pt').size().sort_values(ascending=False).head(6).to_dict(),
    'coado_pct': float(it['descricao_en'].str.startswith('Coffee, brewed').mean() + 0),
}
gaps = last['intervalo']
R['intervalo'] = {
    'pessoa_dias': int(len(last)), 'mediana': float(gaps.median()), 'media': float(gaps.mean()),
    'q1': float(np.percentile(gaps, 25)), 'q3': float(np.percentile(gaps, 75)),
    'menor_88_pessoa_dias': int((gaps < GAP_LIMIT).sum()),
    'menor_6_pessoa_dias': int((gaps < 6).sum()),
    'pessoas_menor_88': int((gap_min < GAP_LIMIT).sum()), 'pessoas': int(gap_min.size),
    'pessoas_menor_6': int((gap_min < 6).sum()),
    'mediana_pessoa': float(gap_min.median()), 'q1_pessoa': float(np.percentile(gap_min, 25)), 'q3_pessoa': float(np.percentile(gap_min, 75)),
}
late = s['intervalo_min'] < GAP_LIMIT
early = s['intervalo_min'] >= GAP_LIMIT
non = s['dias_cafe'] == 0
R['tardio_vs_cedo'] = {lab: {'n': int(mm.sum()), 'sono': float(s.loc[mm, 'sono_util'].mean()),
                             'sono_insuf': float((s.loc[mm, 'sono_util'] < 7).mean()),
                             'sono_prej': float((s.loc[mm, 'prob_sono'] >= 1).mean()),
                             'conc_prej': float((s.loc[mm, 'dif_conc'] >= 1).mean()),
                             'cafeina': float(s.loc[mm, 'cafeina'].mean())}
                       for lab, mm in [('tardio', late), ('cedo', early), ('nao_bebe', non)]}

# fontes de cafeína (dias 1 e 2)
def caf_items(df, p):
    df = df[df['SEQN'].isin(s['SEQN'])].copy()
    df['code'] = df[p + 'IFDCD'].astype(int)
    df['caf'] = df[p + 'ICAFF'].astype(float)
    return df.loc[df['caf'] > 0, ['code', 'caf']]


cc = pd.concat([caf_items(i1, 'DR1'), caf_items(i2, 'DR2')])


def fonte(c):
    if 92100000 <= c < 92200000: return 'Café'
    if 92400000 <= c < 92600000: return 'Refrigerantes'
    if 92300000 <= c < 92400000: return 'Chás'
    if 95000000 <= c < 96000000: return 'Energéticos'
    return 'Outros (chocolate, sobremesas, drinks)'


cc['fonte'] = cc['code'].apply(fonte)
tot = cc['caf'].sum()
R['fontes_cafeina'] = {k: float(v / tot) for k, v in cc.groupby('fonte')['caf'].sum().sort_values(ascending=False).items()}
R['cafeina_acima_400'] = int((s['cafeina'] > 400).sum())

# sono: dias úteis × fim de semana
dif = s['sono_fds'] - s['sono_util']
tt, pp = stats.ttest_rel(s['sono_fds'], s['sono_util'])
R['sono_fds_vs_util'] = {'media_dif': float(dif.mean()), 'dp_dif': float(dif.std(ddof=1)), 't': float(tt), 'p': float(pp),
                         'pct_mais_1h': float((dif >= 1).mean())}

# subgrupos
R['por_situacao'] = {k: {'n': int((s['situacao'] == k).sum()),
                         'tomou_cafe': float((s.loc[s['situacao'] == k, 'dias_cafe'] > 0).mean()),
                         'xicaras': float(s.loc[s['situacao'] == k, 'xicaras'].mean()),
                         'sono': float(s.loc[s['situacao'] == k, 'sono_util'].mean()),
                         'conc_prej': float((s.loc[s['situacao'] == k, 'dif_conc'] >= 1).mean()),
                         'sono_prej': float((s.loc[s['situacao'] == k, 'prob_sono'] >= 1).mean())}
                     for k in ['Trabalhando', 'Estudando', 'Procurando trabalho', 'Outra situação']}
R['por_genero'] = {k: {'n': int((s['genero'] == k).sum()),
                       'tomou_cafe': float((s.loc[s['genero'] == k, 'dias_cafe'] > 0).mean()),
                       'xicaras': float(s.loc[s['genero'] == k, 'xicaras'].mean()),
                       'conc_prej': float((s.loc[s['genero'] == k, 'dif_conc'] >= 1).mean()),
                       'sono_prej': float((s.loc[s['genero'] == k, 'prob_sono'] >= 1).mean())}
                   for k in ['Feminino', 'Masculino']}
R['por_faixa'] = {k: {'n': int((s['faixa_etaria'] == k).sum()),
                      'tomou_cafe': float((s.loc[s['faixa_etaria'] == k, 'dias_cafe'] > 0).mean()),
                      'xicaras': float(s.loc[s['faixa_etaria'] == k, 'xicaras'].mean())}
                  for k in ['18 a 21', '22 a 25', '26 a 29']}

# estimativas ponderadas (peso de dois dias de dieta WTDR2D) — complemento
w = s['WTDR2D'].astype(float)
wm = lambda v: float(np.average(v.astype(float), weights=w))
R['ponderado'] = {'tomou_cafe': wm(A), 'dois_dias': wm(s['dias_cafe'] == 2), 'sono_insuf': wm(s['sono_util'] < 7),
                  'sono_prej': wm(B), 'conc_prej': wm(C), 'xicaras': wm(s['xicaras']), 'cafeina': wm(s['cafeina'])}

# concordância entre os dois dias
R['concordancia_dias'] = {
    'd1': int((s['g_d1'] > 0).sum()), 'd2': int((s['g_d2'] > 0).sum()),
    'd1_e_d2': int(((s['g_d1'] > 0) & (s['g_d2'] > 0)).sum()),
    'p_d2_dado_d1': float(((s['g_d1'] > 0) & (s['g_d2'] > 0)).sum() / (s['g_d1'] > 0).sum()),
    'p_d2_dado_nao_d1': float(((s['g_d1'] == 0) & (s['g_d2'] > 0)).sum() / (s['g_d1'] == 0).sum()),
}

# horários habituais de sono (dias úteis) — para o relógio do café
_bed = s['dormir_util_h'].where(s['dormir_util_h'] >= 12, s['dormir_util_h'] + 24)
R['horarios_sono'] = {'dormir_mediana': float(np.nanmedian(_bed)), 'dormir_q1': float(np.nanpercentile(_bed.dropna(), 25)),
                      'dormir_q3': float(np.nanpercentile(_bed.dropna(), 75)), 'acordar_mediana': float(np.nanmedian(s['acordar_util_h'])),
                      'n': int(_bed.notna().sum())}

# dados compactos para a apresentação (x=xícaras, c=concentração, b=problemas de sono, h=horas de sono, d=dias com café)
R['raw_html'] = ';'.join(f"{x:.2f},{c},{b},{h:g},{dd}" for x, c, b, h, dd in
                         zip(s['xicaras'], s['dif_conc'], s['prob_sono'], s['sono_util'], s['dias_cafe']))


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    return o


with open(os.path.join(OUT, 'results.json'), 'w', encoding='utf-8') as f:
    json.dump(clean(R), f, ensure_ascii=False, indent=1)
print('n =', N)
print(json.dumps(clean({k: R[k] for k in ['fluxo', 'freq']}), ensure_ascii=False, indent=0)[:6000])
