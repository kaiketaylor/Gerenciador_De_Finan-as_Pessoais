"""
Monta a planilha do trabalho a partir dos dados reais do NHANES 2021–2023.
Os dados brutos ficam em 'Dados brutos' e 'Itens de café'; todas as variáveis
derivadas da aba 'Base' e todas as estatísticas são fórmulas.
"""
import json, os
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.worksheet.table import Table, TableStyleInfo

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'out')
R = json.load(open(os.path.join(OUT, 'results.json'), encoding='utf-8'))
base_v = pd.read_csv(os.path.join(OUT, 'base_analitica.csv'))
raw = pd.read_csv(os.path.join(OUT, 'dados_brutos.csv'), keep_default_na=False, na_values=[''])
itens = pd.read_csv(os.path.join(OUT, 'itens_cafe.csv'))
N = len(base_v)
NI = len(itens)
LAST = N + 1          # última linha de dados na Base / Dados brutos
LASTI = NI + 1        # última linha de dados em Itens de café

# ---------------------------------------------------------------- estilos
F = 'Arial'
COFFEE = '5B3A29'
CREAM = 'F6EFE7'
LINE = 'D9CBBE'
font = Font(name=F, size=10)
bold = Font(name=F, size=10, bold=True)
hfont = Font(name=F, size=10, bold=True, color='FFFFFF')
title_font = Font(name=F, size=14, bold=True, color=COFFEE)
sub_font = Font(name=F, size=10, italic=True, color='6B5B4E')
sec_font = Font(name=F, size=11, bold=True, color=COFFEE)
note_font = Font(name=F, size=9, italic=True, color='6B5B4E')
hfill = PatternFill('solid', fgColor=COFFEE)
sfill = PatternFill('solid', fgColor=CREAM)
kfill = PatternFill('solid', fgColor='FFF4D6')
thin = Side(style='thin', color=LINE)
border = Border(left=thin, right=thin, top=thin, bottom=thin)
wrap = Alignment(wrap_text=True, vertical='top')
center = Alignment(horizontal='center', vertical='center', wrap_text=True)

wb = Workbook()
wb.remove(wb.active)


def sheet(name, tab=None):
    ws = wb.create_sheet(name)
    ws.sheet_view.showGridLines = False
    if tab:
        ws.sheet_properties.tabColor = tab
    return ws


def put(ws, ref, value, f=None, fmt=None, fill=None, al=None, b=False):
    c = ws[ref]
    c.value = value
    c.font = f or font
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    if al:
        c.alignment = al
    if b:
        c.border = border
    return c


def header_row(ws, row, col, labels, widths=None):
    for k, lab in enumerate(labels):
        c = ws.cell(row=row, column=col + k, value=lab)
        c.font = hfont
        c.fill = hfill
        c.alignment = center
        c.border = border
        if widths:
            ws.column_dimensions[get_column_letter(col + k)].width = widths[k]


def name(nm, ref):
    wb.defined_names[nm] = DefinedName(nm, attr_text=ref)


# ================================================================ Dados brutos
wr = sheet('Dados brutos', '8C7B6B')
raw_cols = list(raw.columns)
header_row(wr, 1, 1, raw_cols)
for i, row in enumerate(raw.itertuples(index=False), start=2):
    for j, v in enumerate(row, start=1):
        if isinstance(v, float) and pd.isna(v):
            v = None
        c = wr.cell(row=i, column=j, value=v)
        c.font = font
for j, col in enumerate(raw_cols, start=1):
    wr.column_dimensions[get_column_letter(j)].width = 11 if col not in ('WTDR2D',) else 14
wr.freeze_panes = 'C2'
wr.auto_filter.ref = f'A1:{get_column_letter(len(raw_cols))}{LAST}'
RC = {c: get_column_letter(k + 1) for k, c in enumerate(raw_cols)}   # coluna de cada variável NHANES

# ================================================================ Itens de café
wi = sheet('Itens de café', '8C7B6B')
icols = ['ID', 'SEQN (NHANES)', 'Dia do recordatório', 'Dia da semana', 'Horário', 'Hora (decimal)',
         'Período', 'Hora cheia', 'Ocasião', 'Código USDA (FNDDS)', 'Descrição (FNDDS)', 'Bebida',
         'Volume (mL ≈ g)', 'Xícaras (240 mL)', 'Cafeína (mg)']
header_row(wi, 1, 1, icols, [6, 12, 11, 12, 9, 10, 10, 9, 16, 13, 44, 38, 12, 11, 11])
for i, r in enumerate(itens.itertuples(index=False), start=2):
    hh, mm = r[4].split(':')
    hdec = int(hh) + int(mm) / 60
    vals = [r[0], r[1], r[2], r[3], r[4], round(hdec, 4),
            f'=IF(AND(F{i}>=5,F{i}<12),"Manhã",IF(AND(F{i}>=12,F{i}<18),"Tarde","Noite"))',
            f'=INT(F{i})', r[6], r[7], r[8], r[9], r[10],
            f'=M{i}/XICARA_ML', r[12]]
    for j, v in enumerate(vals, start=1):
        c = wi.cell(row=i, column=j, value=v)
        c.font = font
    wi.cell(row=i, column=6).number_format = '0.00'
    wi.cell(row=i, column=14).number_format = '0.00'
wi.freeze_panes = 'C2'
wi.auto_filter.ref = f'A1:O{LASTI}'
IR = lambda col: f"'Itens de café'!${col}$2:${col}${LASTI}"

# ================================================================ Base (derivada por fórmulas)
wsb = sheet('Base', 'A0522D')
bcols = [
    ('ID', 6), ('SEQN (NHANES)', 11), ('Gênero', 11), ('Idade (anos)', 8), ('Faixa etária', 10),
    ('Situação na semana anterior', 18), ('Café no dia 1 (mL)', 10), ('Café no dia 2 (mL)', 10),
    ('Dias com café (0–2)', 9), ('Consumo de café', 19), ('Tomou café', 8), ('Xícaras/dia (240 mL)', 10),
    ('Faixa de xícaras/dia', 14), ('Café de manhã (mL)', 10), ('Café à tarde (mL)', 10),
    ('Café à noite (mL)', 10), ('Período de maior consumo', 13), ('Menor intervalo café→dormir (h)', 12),
    ('Cafeína dia 1 (mg)', 10), ('Cafeína dia 2 (mg)', 10), ('Cafeína total (mg/dia)', 10),
    ('Cafeína do café (mg/dia)', 10), ('Hora de dormir (dias úteis)', 10), ('Hora de acordar (dias úteis)', 10),
    ('Sono em dias úteis (h)', 9), ('Sono no fim de semana (h)', 9), ('Sono < 7 h', 8),
    ('Problemas de sono (0–3)', 9), ('Problemas de sono (frequência)', 20), ('Sono prejudicado', 9),
    ('Dificuldade de concentração (0–3)', 11), ('Dificuldade de concentração (frequência)', 20),
    ('Concentração prejudicada', 11), ('Xícaras/dia — só consumidores', 11),
]
header_row(wsb, 1, 1, [c[0] for c in bcols], [c[1] for c in bcols])
wsb.row_dimensions[1].height = 54
DB = "'Dados brutos'!"
FREQ4 = '"Nenhum dia","Vários dias","Mais da metade dos dias","Quase todos os dias"'
for i in range(2, LAST + 1):
    r = i
    f = {
        'A': f'={DB}A{r}',
        'B': f'={DB}{RC["SEQN"]}{r}',
        'C': f'=IF({DB}{RC["RIAGENDR"]}{r}=1,"Masculino","Feminino")',
        'D': f'={DB}{RC["RIDAGEYR"]}{r}',
        'E': f'=IF(D{r}<=21,"18 a 21",IF(D{r}<=25,"22 a 25","26 a 29"))',
        'F': (f'=IF(OR({DB}{RC["OCD150"]}{r}=1,{DB}{RC["OCD150"]}{r}=2),"Trabalhando",'
              f'IF({DB}{RC["OCD150"]}{r}=3,"Procurando trabalho",'
              f'IF(AND({DB}{RC["OCD150"]}{r}=4,{DB}{RC["OCQ383"]}{r}=2),"Estudando","Outra situação")))'),
        'G': f'=SUMIFS({IR("M")},{IR("A")},A{r},{IR("C")},1)',
        'H': f'=SUMIFS({IR("M")},{IR("A")},A{r},{IR("C")},2)',
        'I': f'=(G{r}>0)+(H{r}>0)',
        'J': f'=CHOOSE(I{r}+1,"Nenhum dos dois dias","Um dos dois dias","Os dois dias")',
        'K': f'=IF(I{r}>0,"Sim","Não")',
        'L': f'=(G{r}+H{r})/2/XICARA_ML',
        'M': f'=IF(L{r}=0,"0",IF(L{r}<=1,"Até 1",IF(L{r}<=2,"Mais de 1 a 2",IF(L{r}<=3,"Mais de 2 a 3","Mais de 3"))))',
        'N': f'=SUMIFS({IR("M")},{IR("A")},A{r},{IR("G")},"Manhã")',
        'O': f'=SUMIFS({IR("M")},{IR("A")},A{r},{IR("G")},"Tarde")',
        'P': f'=SUMIFS({IR("M")},{IR("A")},A{r},{IR("G")},"Noite")',
        'Q': f'=IF(I{r}=0,"Não consumiu",IF(AND(N{r}>=O{r},N{r}>=P{r}),"Manhã",IF(O{r}>=P{r},"Tarde","Noite")))',
        'S': f'={DB}{RC["DR1TCAFF"]}{r}',
        'T': f'={DB}{RC["DR2TCAFF"]}{r}',
        'U': f'=(S{r}+T{r})/2',
        'V': f'=SUMIFS({IR("O")},{IR("A")},A{r})/2',
        'W': f'=IF({DB}{RC["SLQ300"]}{r}="","",{DB}{RC["SLQ300"]}{r})',
        'X': f'=IF({DB}{RC["SLQ310"]}{r}="","",{DB}{RC["SLQ310"]}{r})',
        'Y': f'={DB}{RC["SLD012"]}{r}',
        'Z': f'={DB}{RC["SLD013"]}{r}',
        'AA': f'=IF(Y{r}<7,"Sim","Não")',
        'AB': f'={DB}{RC["DPQ030"]}{r}',
        'AC': f'=CHOOSE(AB{r}+1,{FREQ4})',
        'AD': f'=IF(AB{r}>=1,"Sim","Não")',
        'AE': f'={DB}{RC["DPQ070"]}{r}',
        'AF': f'=CHOOSE(AE{r}+1,{FREQ4})',
        'AG': f'=IF(AE{r}>=1,"Sim","Não")',
        'AH': f'=IF(K{r}="Sim",L{r},"")',
    }
    gap = base_v.loc[r - 2, 'Menor intervalo café→dormir (h)']
    f['R'] = None if pd.isna(gap) else float(gap)
    for col, v in f.items():
        c = wsb[f'{col}{r}']
        c.value = v
        c.font = font
    for col in ('L', 'AH'):
        wsb[f'{col}{r}'].number_format = '0.000'
    for col in ('G', 'H', 'N', 'O', 'P', 'S', 'T', 'U', 'V'):
        wsb[f'{col}{r}'].number_format = '0.0'
    wsb[f'R{r}'].number_format = '0.00'
    wsb[f'R{r}'].fill = kfill
wsb.freeze_panes = 'C2'
wsb.auto_filter.ref = f'A1:AH{LAST}'

rng = lambda col: f'Base!${col}$2:${col}${LAST}'
for nm, col in [('ID_', 'A'), ('Genero', 'C'), ('Idade', 'D'), ('FaixaEtaria', 'E'), ('Situacao', 'F'),
                ('DiasCafe', 'I'), ('ConsumoCafe', 'J'), ('TomouCafe', 'K'), ('Xicaras', 'L'),
                ('FaixaXicaras', 'M'), ('Periodo', 'Q'), ('Intervalo', 'R'), ('Cafeina', 'U'),
                ('CafeinaCafe', 'V'), ('SonoUtil', 'Y'), ('SonoFds', 'Z'), ('SonoInsuf', 'AA'),
                ('ProbSono', 'AB'), ('SonoPrej', 'AD'), ('DifConc', 'AE'), ('ConcPrej', 'AG'),
                ('XicarasCons', 'AH')]:
    name(nm, rng(col))

# ================================================================ Leia-me
wl = sheet('Leia-me', COFFEE)
wb.move_sheet(wl, offset=-wb.index(wl))
wl.column_dimensions['A'].width = 3
wl.column_dimensions['B'].width = 34
wl.column_dimensions['C'].width = 92
put(wl, 'B2', 'Consumo de café e produtividade acadêmica — base de dados real', title_font)
put(wl, 'B3', 'Fatec Presidente Prudente · Estatística Aplicada · Análise e Desenvolvimento de Sistemas · 2026', sub_font)
put(wl, 'B4', 'Bruna Lais Amorin · Kaike Taylor Antonio Santos · Lucas Gustavo Mendes · Rafael Gervazoni Bezerra', sub_font)
rows = [
    ('FONTE DOS DADOS', None),
    ('Pesquisa', 'National Health and Nutrition Examination Survey (NHANES), ciclo agosto/2021 – agosto/2023, '
                 'conduzida pelo National Center for Health Statistics (NCHS/CDC), Estados Unidos.'),
    ('Arquivos oficiais usados', 'DEMO_L (demografia), OCQ_L (ocupação), SLQ_L (sono), DPQ_L (PHQ-9), '
                                 'DR1IFF_L e DR2IFF_L (itens dos recordatórios de 24 h), DR1TOT_L e DR2TOT_L '
                                 '(totais diários), DRXFCD_L (descrição dos códigos de alimentos).'),
    ('Endereço', 'https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?Cycle=2021-2023'),
    ('Acesso', 'Microdados públicos, baixados em 07/11/2026 no formato SAS Transport (.xpt).'),
    ('AMOSTRA', None),
    ('Critérios de inclusão', '18 a 29 anos; respostas válidas (0 a 3) aos itens 3 e 7 do PHQ-9; horas de sono '
                              'em dias úteis e no fim de semana calculáveis; dois recordatórios alimentares de 24 h '
                              'classificados pelo NCHS como confiáveis (DR1DRSTZ = 1 e DR2DRSTZ = 1).'),
] + [(f'Etapa {k + 1}', f"{e['etapa']}: {e['n']:,}".replace(',', '.')) for k, e in enumerate(R['fluxo'])] + [
    ('Tamanho final', f'n = {N} participantes (todos os elegíveis; não houve sorteio adicional).'),
    ('COMO A PLANILHA ESTÁ ORGANIZADA', None),
    ('Resumo', 'Indicadores principais, todos calculados por fórmula a partir da aba Base.'),
    ('Base', 'Uma linha por participante. Colunas derivadas por fórmula de Dados brutos e Itens de café. '
             'A coluna R (destacada) foi calculada no script de preparo, por depender do dia da semana e do horário '
             'habitual de dormir.'),
    ('Frequências', 'Tabelas de frequência absoluta e relativa (CONT.SE / COUNTIF).'),
    ('Medidas', 'Média, mediana, moda, amplitude, variância, desvio padrão, quartis e coeficiente de variação.'),
    ('Correlação e regressão', 'Somatórios do r de Pearson, teste t do coeficiente e retas de regressão.'),
    ('Probabilidade', 'Probabilidades simples, tabelas de contingência, probabilidades condicionais, '
                      'qui-quadrado e distribuição binomial.'),
    ('Horário do café', 'Distribuição dos 357 registros de café por hora do dia e por período.'),
    ('Dados brutos', 'Variáveis originais do NHANES, com os códigos oficiais, para os 496 participantes.'),
    ('Itens de café', 'Cada bebida de café relatada nos dois recordatórios (horário, tipo, volume e cafeína).'),
    ('Dicionário', 'Definição, origem e classificação de cada variável.'),
    ('PARÂMETROS', None),
    ('Xícara-padrão (mL)', None),
    ('Limite de cafeína (mg/dia)', None),
    ('Antecedência mínima café→sono (h)', None),
    ('OBSERVAÇÕES', None),
    ('Unidade da análise', 'Os percentuais descrevem os 496 participantes. Para estimar a população '
                           'norte-americana seria preciso usar os pesos amostrais (WTDR2D) e o desenho '
                           'complexo (SDMVSTRA, SDMVPSU), ambos incluídos em Dados brutos.'),
    ('Volume de café', 'O NHANES registra gramas; para bebidas à base de água, 1 g ≈ 1 mL. '
                       'Xícaras = volume médio dos dois dias ÷ 240 mL.'),
    ('Período do dia', 'Manhã: 5h00–11h59 · Tarde: 12h00–17h59 · Noite: 18h00–4h59.'),
]
r0 = 6
param_rows = {}
for k, (a, b_) in enumerate(rows):
    r = r0 + k
    if b_ is None and a.isupper():
        put(wl, f'B{r}', a, sec_font)
        continue
    put(wl, f'B{r}', a, bold, al=wrap)
    if b_ is not None:
        put(wl, f'C{r}', b_, font, al=wrap)
    else:
        param_rows[a] = r
put(wl, f"C{param_rows['Xícara-padrão (mL)']}", 240, bold, fmt='0', fill=kfill)
put(wl, f"C{param_rows['Limite de cafeína (mg/dia)']}", 400, bold, fmt='0', fill=kfill)
put(wl, f"C{param_rows['Antecedência mínima café→sono (h)']}", 8.8, bold, fmt='0.0', fill=kfill)
name('XICARA_ML', f"'Leia-me'!$C${param_rows['Xícara-padrão (mL)']}")
name('LIMITE_CAF', f"'Leia-me'!$C${param_rows['Limite de cafeína (mg/dia)']}")
name('LIMITE_INTERVALO', f"'Leia-me'!$C${param_rows['Antecedência mínima café→sono (h)']}")
put(wl, f"D{param_rows['Xícara-padrão (mL)']}", 'USDA: 1 cup = 8 fl oz ≈ 240 mL', note_font)
put(wl, f"D{param_rows['Limite de cafeína (mg/dia)']}", 'FDA: até 400 mg/dia para adultos saudáveis', note_font)
put(wl, f"D{param_rows['Antecedência mínima café→sono (h)']}", 'Gardiner et al. (2023), Sleep Medicine Reviews 69', note_font)
wl.column_dimensions['D'].width = 44

# ================================================================ Frequências
wf = sheet('Frequências', 'C17A3A')
wf.column_dimensions['A'].width = 3
wf.column_dimensions['B'].width = 30
for c_ in 'CDE':
    wf.column_dimensions[c_].width = 13
put(wf, 'B2', 'Tabelas de frequência', title_font)
put(wf, 'B3', f'n = {N} adultos de 18 a 29 anos · NHANES ago/2021–ago/2023 · contagens por fórmula sobre a aba Base', sub_font)

tables = [
    ('Tabela 1 – Gênero', 'Genero', ['Feminino', 'Masculino'], 'N'),
    ('Tabela 2 – Faixa etária', 'FaixaEtaria', ['18 a 21', '22 a 25', '26 a 29'], 'N'),
    ('Tabela 3 – Situação na semana anterior à entrevista', 'Situacao',
     ['Trabalhando', 'Estudando', 'Procurando trabalho', 'Outra situação'], 'N'),
    ('Tabela 4 – Consumo de café nos dois dias de registro', 'ConsumoCafe',
     ['Nenhum dos dois dias', 'Um dos dois dias', 'Os dois dias'], 'N'),
    ('Tabela 5 – Xícaras de café por dia (média dos dois dias, 240 mL)', 'FaixaXicaras',
     ['0', 'Até 1', 'Mais de 1 a 2', 'Mais de 2 a 3', 'Mais de 3'], 'N'),
    ('Tabela 6 – Período de maior consumo (só quem tomou café)', 'Periodo', ['Manhã', 'Tarde', 'Noite'], 'C'),
    ('Tabela 7 – Horas de sono em dias úteis', 'SonoUtil',
     ['Menos de 6 h', '6 a 6,5 h', '7 a 7,5 h', '8 a 8,5 h', '9 h ou mais'], 'SONO'),
    ('Tabela 8 – Problemas de sono nas últimas 2 semanas (PHQ-9, item 3)', 'ProbSono',
     ['Nenhum dia', 'Vários dias', 'Mais da metade dos dias', 'Quase todos os dias'], 'LIK'),
    ('Tabela 9 – Dificuldade de concentração nas últimas 2 semanas (PHQ-9, item 7)', 'DifConc',
     ['Nenhum dia', 'Vários dias', 'Mais da metade dos dias', 'Quase todos os dias'], 'LIK'),
]
sono_crit = {'Menos de 6 h': ('"<6"', None), '6 a 6,5 h': ('">=6"', '"<7"'), '7 a 7,5 h': ('">=7"', '"<8"'),
             '8 a 8,5 h': ('">=8"', '"<9"'), '9 h ou mais': ('">=9"', None)}
r = 5
freq_pos = {}
for title, rngname, cats, kind in tables:
    put(wf, f'B{r}', title, sec_font)
    r += 1
    header_row(wf, r, 2, ['Categoria', 'Frequência (fi)', 'Percentual (fr)', 'Acumulado'])
    first = r + 1
    for k, cat in enumerate(cats):
        rr = first + k
        put(wf, f'B{rr}', cat, font, b=True)
        if kind == 'SONO':
            lo, hi = sono_crit[cat]
            fx = f'=COUNTIFS({rngname},{lo},{rngname},{hi})' if hi else f'=COUNTIF({rngname},{lo})'
        elif kind == 'LIK':
            fx = f'=COUNTIF({rngname},{k})'
        else:
            fx = f'=COUNTIF({rngname},"{cat}")'
        put(wf, f'C{rr}', fx, font, '0', b=True)
        tot = f'$C${first + len(cats)}'
        put(wf, f'D{rr}', f'=C{rr}/{tot}', font, '0.0%', b=True)
        put(wf, f'E{rr}', f'=SUM($D${first}:D{rr})', font, '0.0%', b=True)
    rt = first + len(cats)
    put(wf, f'B{rt}', 'Total', bold, fill=sfill, b=True)
    put(wf, f'C{rt}', f'=SUM(C{first}:C{rt - 1})', bold, '0', fill=sfill, b=True)
    put(wf, f'D{rt}', f'=SUM(D{first}:D{rt - 1})', bold, '0.0%', fill=sfill, b=True)
    put(wf, f'E{rt}', '', bold, fill=sfill, b=True)
    if kind == 'C':
        put(wf, f'B{rt + 1}', 'Percentuais calculados sobre quem tomou café em ao menos um dos dois dias.', note_font)
        rt += 1
    freq_pos[title] = (first, first + len(cats) - 1)
    r = rt + 3

# gráficos nativos ao lado das tabelas principais
def bar_chart(ws, title, cats_ref, vals_ref, anchor, color='9A5426', ytitle='Participantes'):
    ch = BarChart()
    ch.type = 'col'
    ch.title = title
    ch.style = 10
    ch.y_axis.title = ytitle
    ch.y_axis.majorGridlines = None
    ch.legend = None
    ch.height = 6.4
    ch.width = 12.5
    ch.add_data(vals_ref, titles_from_data=False)
    ch.set_categories(cats_ref)
    s = ch.series[0]
    s.graphicalProperties.solidFill = color
    s.graphicalProperties.line.solidFill = color
    ch.dataLabels = DataLabelList()
    ch.dataLabels.showVal = True
    ch.gapWidth = 80
    ws.add_chart(ch, anchor)


for title, color, anchor in [('Tabela 4 – Consumo de café nos dois dias de registro', '9A5426', 'G5'),
                             ('Tabela 5 – Xícaras de café por dia (média dos dois dias, 240 mL)', '9A5426', 'G22'),
                             ('Tabela 6 – Período de maior consumo (só quem tomou café)', 'B97A10', 'G39'),
                             ('Tabela 8 – Problemas de sono nas últimas 2 semanas (PHQ-9, item 3)', '3A62C4', 'G56'),
                             ('Tabela 9 – Dificuldade de concentração nas últimas 2 semanas (PHQ-9, item 7)', 'B97A10', 'G73')]:
    a, b_ = freq_pos[title]
    bar_chart(wf, title.split('–')[1].strip(), Reference(wf, min_col=2, min_row=a, max_row=b_),
              Reference(wf, min_col=3, min_row=a, max_row=b_), anchor, color)

# ================================================================ Medidas
wm = sheet('Medidas', 'C17A3A')
wm.column_dimensions['A'].width = 3
wm.column_dimensions['B'].width = 34
put(wm, 'B2', 'Medidas de posição e de dispersão', title_font)
put(wm, 'B3', 'Desvio padrão e variância amostrais (n − 1). Quartis pelo método inclusivo (QUARTIL / QUARTILE).', sub_font)
mvars = [('Idade (anos)', 'Idade', '0.00'), ('Xícaras/dia — todos os participantes', 'Xicaras', '0.000'),
         ('Xícaras/dia — só quem tomou café', 'XicarasCons', '0.000'), ('Cafeína total (mg/dia)', 'Cafeina', '0.0'),
         ('Sono em dias úteis (h)', 'SonoUtil', '0.00'), ('Sono no fim de semana (h)', 'SonoFds', '0.00'),
         ('Problemas de sono (0–3)', 'ProbSono', '0.000'), ('Dificuldade de concentração (0–3)', 'DifConc', '0.000')]
mh = ['Variável', 'n', 'Média', 'Mediana', 'Moda', 'Mínimo', 'Máximo', 'Amplitude', 'Variância', 'Desvio padrão', 'Q1', 'Q3', 'CV']
header_row(wm, 5, 2, mh, [34, 7, 10, 10, 9, 9, 9, 10, 11, 11, 9, 9, 8])
for k, (lab, nm, fm) in enumerate(mvars):
    rr = 6 + k
    put(wm, f'B{rr}', lab, font, b=True)
    fx = [f'=COUNT({nm})', f'=AVERAGE({nm})', f'=MEDIAN({nm})', f'=MODE({nm})', f'=MIN({nm})', f'=MAX({nm})',
          f'=H{rr}-G{rr}', f'=VAR({nm})', f'=STDEV({nm})', f'=QUARTILE({nm},1)', f'=QUARTILE({nm},3)', f'=K{rr}/D{rr}']
    fmts = ['0', fm, fm, fm, fm, fm, fm, fm, fm, fm, fm, '0.0%']
    for j, (x, fmt) in enumerate(zip(fx, fmts)):
        put(wm, f'{get_column_letter(3 + j)}{rr}', x, font, fmt, b=True)
rr = 6 + len(mvars) + 1
put(wm, f'B{rr}', 'CV = desvio padrão ÷ média. Valores acima de 100% indicam dispersão maior que a própria média.', note_font)

rr += 2
put(wm, f'B{rr}', 'Passo a passo — xícaras de café por dia (todos os 496 participantes)', sec_font)
steps = [
    ('n', '=COUNT(Xicaras)', '0'),
    ('Σx (soma das xícaras)', '=SUM(Xicaras)', '0.000'),
    ('Média = Σx ÷ n', f'=C{rr + 2}/C{rr + 1}', '0.0000'),
    ('Valor na 248ª posição (ordem crescente)', '=SMALL(Xicaras,248)', '0.000'),
    ('Valor na 249ª posição', '=SMALL(Xicaras,249)', '0.000'),
    ('Mediana = (x₂₄₈ + x₂₄₉) ÷ 2', f'=(C{rr + 4}+C{rr + 5})/2', '0.000'),
    ('Moda (valor mais frequente)', '=MODE(Xicaras)', '0.000'),
    ('Frequência da moda', '=COUNTIF(Xicaras,0)', '0'),
    ('Amplitude = máximo − mínimo', '=MAX(Xicaras)-MIN(Xicaras)', '0.000'),
    ('Σ(x − média)²', '=DEVSQ(Xicaras)', '0.0000'),
    ('Variância s² = Σ(x − média)² ÷ (n − 1)', f'=C{rr + 10}/(C{rr + 1}-1)', '0.0000'),
    ('Desvio padrão s = √s²', f'=SQRT(C{rr + 11})', '0.0000'),
    ('Q1 (25%)', '=QUARTILE(Xicaras,1)', '0.000'),
    ('Q3 (75%)', '=QUARTILE(Xicaras,3)', '0.000'),
    ('Média só de quem tomou café', '=AVERAGE(XicarasCons)', '0.0000'),
    ('Mediana só de quem tomou café', '=MEDIAN(XicarasCons)', '0.000'),
    ('Volume médio de quem tomou café (mL/dia)', f'=C{rr + 15}*XICARA_ML', '0'),
]
for k, (lab, fx, fmt) in enumerate(steps):
    put(wm, f'B{rr + 1 + k}', lab, font, b=True)
    put(wm, f'C{rr + 1 + k}', fx, bold, fmt, b=True)
wm.column_dimensions['C'].width = 12

# ================================================================ Correlação e regressão
wc = sheet('Correlação e regressão', '3A62C4')
wc.column_dimensions['A'].width = 3
wc.column_dimensions['B'].width = 40
put(wc, 'B2', 'Correlação de Pearson e regressão linear simples', title_font)
put(wc, 'B3', 'r = [nΣXY − ΣXΣY] ÷ √{[nΣX² − (ΣX)²][nΣY² − (ΣY)²]} · t = r√(n−2) ÷ √(1−r²) · p bilateral (DISTT / TDIST)', sub_font)
pairs = [('Xícaras × dificuldade de concentração', 'Xicaras', 'DifConc'),
         ('Xícaras × problemas de sono', 'Xicaras', 'ProbSono'),
         ('Xícaras × horas de sono (dias úteis)', 'Xicaras', 'SonoUtil'),
         ('Cafeína × horas de sono (dias úteis)', 'Cafeina', 'SonoUtil'),
         ('Problemas de sono × dificuldade de concentração', 'ProbSono', 'DifConc'),
         ('Idade × xícaras', 'Idade', 'Xicaras')]
lab_rows = ['n', 'ΣX', 'ΣY', 'ΣX²', 'ΣY²', 'ΣXY', 'Numerador: nΣXY − ΣXΣY', '1º termo: nΣX² − (ΣX)²',
            '2º termo: nΣY² − (ΣY)²', 'Denominador: √(1º × 2º)', 'r (pelos somatórios)', 'r (CORREL, conferência)',
            'r²', 't do coeficiente', 'p-valor (bilateral)', 'Inclinação b = SLOPE', 'Intercepto a = INTERCEPT',
            'R² = RSQ', 'Erro padrão de b', 'IC 95% de b — limite inferior', 'IC 95% de b — limite superior']
header_row(wc, 5, 2, ['Estatística'] + [p[0] for p in pairs], [40] + [19] * len(pairs))
wc.row_dimensions[5].height = 44
for k, lab in enumerate(lab_rows):
    put(wc, f'B{6 + k}', lab, font, b=True)
for j, (lab, X, Y) in enumerate(pairs):
    c = get_column_letter(3 + j)
    R_ = lambda k: f'{c}{6 + k}'
    fx = [f'=COUNT({X})', f'=SUM({X})', f'=SUM({Y})', f'=SUMPRODUCT({X},{X})', f'=SUMPRODUCT({Y},{Y})',
          f'=SUMPRODUCT({X},{Y})', f'={R_(0)}*{R_(5)}-{R_(1)}*{R_(2)}', f'={R_(0)}*{R_(3)}-{R_(1)}^2',
          f'={R_(0)}*{R_(4)}-{R_(2)}^2', f'=SQRT({R_(7)}*{R_(8)})', f'={R_(6)}/{R_(9)}', f'=CORREL({X},{Y})',
          f'={R_(10)}^2', f'={R_(10)}*SQRT(({R_(0)}-2)/(1-{R_(12)}))', f'=TDIST(ABS({R_(13)}),{R_(0)}-2,2)',
          f'=SLOPE({Y},{X})', f'=INTERCEPT({Y},{X})', f'=RSQ({Y},{X})',
          f'=STEYX({Y},{X})/SQRT(DEVSQ({X}))', f'={R_(15)}-TINV(0.05,{R_(0)}-2)*{R_(18)}',
          f'={R_(15)}+TINV(0.05,{R_(0)}-2)*{R_(18)}']
    fmts = ['0', '0.000', '0.000', '0.000', '0.000', '0.000', '#,##0.000', '#,##0.000', '#,##0.000', '#,##0.000',
            '0.0000', '0.0000', '0.0000', '0.000', '0.0000', '0.0000', '0.0000', '0.0000', '0.0000', '0.0000', '0.0000']
    for k, (x, fmt) in enumerate(zip(fx, fmts)):
        put(wc, R_(k), x, bold if k in (10, 14, 15, 17) else font, fmt, b=True,
            fill=kfill if k in (10, 17) else None)
r_ = 6 + len(lab_rows) + 1
put(wc, f'B{r_}', 'Leitura: |r| < 0,1 desprezível · 0,1–0,3 fraca · 0,3–0,5 moderada · > 0,5 forte. '
                  'p < 0,05 indica que a correlação dificilmente seria zero na população amostrada.', note_font)

r_ += 2
put(wc, f'B{r_}', 'Previsões das duas retas (Ŷ = a + bX)', sec_font)
header_row(wc, r_ + 1, 2, ['X', 'Modelo 1: dificuldade de concentração por xícaras/dia',
                           'Modelo 2: dificuldade de concentração por problemas de sono'])
for k in range(6):
    rr = r_ + 2 + k
    put(wc, f'B{rr}', k, font, '0', b=True)
    put(wc, f'C{rr}', f'=$C$22+$C$21*B{rr}', font, '0.0000', b=True)
    put(wc, f'D{rr}', f'=IF(B{rr}<=3,$G$22+$G$21*B{rr},"fora da escala")', font, '0.0000', b=True)
put(wc, f'B{r_ + 8}', 'Modelo 2 só vale de 0 a 3, a amplitude da escala de problemas de sono.', note_font)

r_ += 11
put(wc, f'B{r_}', 'Matriz de correlação (Pearson)', sec_font)
mv = [('Xícaras/dia', 'Xicaras'), ('Cafeína', 'Cafeina'), ('Sono dias úteis', 'SonoUtil'),
      ('Problemas de sono', 'ProbSono'), ('Dif. concentração', 'DifConc'), ('Idade', 'Idade')]
header_row(wc, r_ + 1, 2, [''] + [m[0] for m in mv])
for i_, (la, na) in enumerate(mv):
    rr = r_ + 2 + i_
    put(wc, f'B{rr}', la, bold, b=True)
    for j_, (lb, nb) in enumerate(mv):
        put(wc, f'{get_column_letter(3 + j_)}{rr}', f'=CORREL({na},{nb})', font, '0.000', b=True)

# ================================================================ Probabilidade
wp = sheet('Probabilidade', '6CA0DC')
wp.column_dimensions['A'].width = 3
wp.column_dimensions['B'].width = 46
for c_ in 'CDEFG':
    wp.column_dimensions[c_].width = 15
put(wp, 'B2', 'Probabilidade simples, condicional e distribuição binomial', title_font)
put(wp, 'B3', 'Sorteio de um participante ao acaso entre os 496: P(evento) = casos favoráveis ÷ total.', sub_font)
header_row(wp, 5, 2, ['Evento', 'Casos favoráveis', 'Total', 'Probabilidade'])
evs = [('A — tomou café em ao menos um dos dois dias', '=COUNTIF(TomouCafe,"Sim")'),
       ('A₂ — tomou café nos dois dias', '=COUNTIF(DiasCafe,2)'),
       ('B — problemas de sono em vários dias ou mais', '=COUNTIF(SonoPrej,"Sim")'),
       ('C — dificuldade de concentração em vários dias ou mais', '=COUNTIF(ConcPrej,"Sim")'),
       ('D — dorme menos de 7 h em dias úteis', '=COUNTIF(SonoInsuf,"Sim")'),
       ('E — cafeína acima do limite de 400 mg/dia', '=COUNTIF(Cafeina,">"&LIMITE_CAF)')]
for k, (lab, fx) in enumerate(evs):
    rr = 6 + k
    put(wp, f'B{rr}', lab, font, b=True)
    put(wp, f'C{rr}', fx, font, '0', b=True)
    put(wp, f'D{rr}', '=COUNT(ID_)', font, '0', b=True)
    put(wp, f'E{rr}', f'=C{rr}/D{rr}', bold, '0.0%', b=True)


def contingency(r0, title, ev1, ev1_lab, ev2_lab, crit1, crit2):
    put(wp, f'B{r0}', title, sec_font)
    header_row(wp, r0 + 1, 2, ['', f'{ev2_lab}: Sim', f'{ev2_lab}: Não', 'Total', f'P({ev2_lab[0]} | linha)'])
    lines = [(f'{ev1_lab}: Sim', f'{crit1}"Sim"'), (f'{ev1_lab}: Não', f'{crit1}"Não"')]
    for k, (lab, c1) in enumerate(lines):
        rr = r0 + 2 + k
        put(wp, f'B{rr}', lab, bold, b=True)
        put(wp, f'C{rr}', f'=COUNTIFS({c1},{crit2}"Sim")', font, '0', b=True)
        put(wp, f'D{rr}', f'=COUNTIFS({c1},{crit2}"Não")', font, '0', b=True)
        put(wp, f'E{rr}', f'=C{rr}+D{rr}', font, '0', b=True)
        put(wp, f'F{rr}', f'=C{rr}/E{rr}', bold, '0.0%', b=True, fill=kfill)
    rt = r0 + 4
    put(wp, f'B{rt}', 'Total', bold, fill=sfill, b=True)
    for col in 'CDE':
        put(wp, f'{col}{rt}', f'=SUM({col}{r0 + 2}:{col}{r0 + 3})', bold, '0', fill=sfill, b=True)
    put(wp, f'F{rt}', f'=C{rt}/E{rt}', bold, '0.0%', fill=sfill, b=True)
    # esperados e qui-quadrado
    put(wp, f'B{rt + 1}', 'Frequências esperadas sob independência', note_font)
    for k in range(2):
        rr = rt + 2 + k
        put(wp, f'B{rr}', f'esperado — linha {k + 1}', note_font)
        put(wp, f'C{rr}', f'=E{r0 + 2 + k}*C{rt}/E{rt}', font, '0.00', b=True)
        put(wp, f'D{rr}', f'=E{r0 + 2 + k}*D{rt}/E{rt}', font, '0.00', b=True)
    put(wp, f'B{rt + 4}', 'Diferença entre as probabilidades condicionais (p.p.)', font)
    put(wp, f'C{rt + 4}', f'=(F{r0 + 2}-F{r0 + 3})*100', bold, '0.0', b=True)
    put(wp, f'B{rt + 5}', 'Razão entre as probabilidades condicionais', font)
    put(wp, f'C{rt + 5}', f'=F{r0 + 2}/F{r0 + 3}', bold, '0.00', b=True)
    put(wp, f'B{rt + 6}', 'p-valor do qui-quadrado (TESTE.QUI / CHITEST)', font)
    put(wp, f'C{rt + 6}', f'=CHITEST(C{r0 + 2}:D{r0 + 3},C{rt + 2}:D{rt + 3})', bold, '0.0000', b=True)
    put(wp, f'B{rt + 7}', 'Estatística qui-quadrado (1 grau de liberdade)', font)
    put(wp, f'C{rt + 7}', f'=CHIINV(C{rt + 6},1)', bold, '0.000', b=True)
    return rt + 9


CT1 = 13
nr = contingency(CT1, 'Café (A) × dificuldade de concentração (C)', 'A', 'Tomou café', 'Concentração prejudicada',
                 'TomouCafe,', 'ConcPrej,')
CT2 = nr
nr = contingency(nr, 'Problemas de sono (B) × dificuldade de concentração (C)', 'B', 'Sono prejudicado',
                 'Concentração prejudicada', 'SonoPrej,', 'ConcPrej,')
nr = contingency(nr, 'Café (A) × problemas de sono (B)', 'A', 'Tomou café', 'Sono prejudicado',
                 'TomouCafe,', 'SonoPrej,')

put(wp, f'B{nr}', 'Distribuição binomial — 5 jovens sorteados de forma independente', sec_font)
put(wp, f'B{nr + 1}', 'n (tentativas)', font, b=True)
put(wp, f'C{nr + 1}', 5, bold, '0', b=True, fill=kfill)
put(wp, f'B{nr + 2}', 'p = P(A) (sucesso = tomou café)', font, b=True)
put(wp, f'C{nr + 2}', '=E6', bold, '0.0000', b=True)
put(wp, f'B{nr + 3}', 'q = 1 − p', font, b=True)
put(wp, f'C{nr + 3}', f'=1-C{nr + 2}', bold, '0.0000', b=True)
header_row(wp, nr + 5, 2, ['k (quantos tomaram café)', 'C(n,k)', 'pᵏ · qⁿ⁻ᵏ', 'P(X = k)', 'P(X ≤ k)'])
for k in range(6):
    rr = nr + 6 + k
    put(wp, f'B{rr}', k, font, '0', b=True)
    put(wp, f'C{rr}', f'=COMBIN($C${nr + 1},B{rr})', font, '0', b=True)
    put(wp, f'D{rr}', f'=$C${nr + 2}^B{rr}*$C${nr + 3}^($C${nr + 1}-B{rr})', font, '0.000000', b=True)
    put(wp, f'E{rr}', f'=BINOMDIST(B{rr},$C${nr + 1},$C${nr + 2},FALSE)', bold, '0.00%', b=True)
    put(wp, f'F{rr}', f'=BINOMDIST(B{rr},$C${nr + 1},$C${nr + 2},TRUE)', font, '0.00%', b=True)
rr = nr + 12
put(wp, f'B{rr}', 'Soma de P(X = k), de 0 a 5', bold, fill=sfill, b=True)
put(wp, f'E{rr}', f'=SUM(E{nr + 6}:E{nr + 11})', bold, '0.00%', fill=sfill, b=True)
put(wp, f'B{rr + 1}', 'P(X ≥ 1) = 1 − P(X = 0)', bold, b=True)
put(wp, f'E{rr + 1}', f'=1-E{nr + 6}', bold, '0.00%', b=True, fill=kfill)
put(wp, f'B{rr + 2}', 'P(X ≥ 3)', bold, b=True)
put(wp, f'E{rr + 2}', f'=SUM(E{nr + 9}:E{nr + 11})', bold, '0.00%', b=True)
put(wp, f'B{rr + 3}', 'Valor esperado E(X) = n·p', bold, b=True)
put(wp, f'E{rr + 3}', f'=C{nr + 1}*C{nr + 2}', bold, '0.00', b=True)
ch = BarChart()
ch.type = 'col'; ch.title = 'P(X = k), n = 5'; ch.legend = None; ch.style = 10
ch.height = 6.4; ch.width = 12.5; ch.y_axis.majorGridlines = None
ch.add_data(Reference(wp, min_col=5, min_row=nr + 6, max_row=nr + 11), titles_from_data=False)
ch.set_categories(Reference(wp, min_col=2, min_row=nr + 6, max_row=nr + 11))
ch.series[0].graphicalProperties.solidFill = '9A5426'
ch.dataLabels = DataLabelList(); ch.dataLabels.showVal = True
wp.add_chart(ch, f'H{nr}')

# ================================================================ Horário do café
wh = sheet('Horário do café', 'B97A10')
wh.column_dimensions['A'].width = 3
wh.column_dimensions['B'].width = 16
for c_ in 'CDEF':
    wh.column_dimensions[c_].width = 15
put(wh, 'B2', 'A que horas o café foi tomado', title_font)
put(wh, 'B3', f'{NI} bebidas de café relatadas por {R["horario"]["consumidores"]} participantes nos dois recordatórios de 24 h.', sub_font)
header_row(wh, 5, 2, ['Hora do dia', 'Registros', 'Volume (mL)', '% dos registros', '% do volume'])
for h in range(24):
    rr = 6 + h
    put(wh, f'B{rr}', f'{h:02d}h00–{h:02d}h59', font, b=True)
    put(wh, f'C{rr}', f"=COUNTIF({IR('H')},{h})", font, '0', b=True)
    put(wh, f'D{rr}', f"=SUMIF({IR('H')},{h},{IR('M')})", font, '#,##0', b=True)
    put(wh, f'E{rr}', f'=C{rr}/$C$30', font, '0.0%', b=True)
    put(wh, f'F{rr}', f'=D{rr}/$D$30', font, '0.0%', b=True)
put(wh, 'B30', 'Total', bold, fill=sfill, b=True)
put(wh, 'C30', '=SUM(C6:C29)', bold, '0', fill=sfill, b=True)
put(wh, 'D30', '=SUM(D6:D29)', bold, '#,##0', fill=sfill, b=True)
put(wh, 'E30', '=SUM(E6:E29)', bold, '0.0%', fill=sfill, b=True)
put(wh, 'F30', '=SUM(F6:F29)', bold, '0.0%', fill=sfill, b=True)
header_row(wh, 32, 2, ['Período', 'Registros', 'Volume (mL)', '% dos registros', '% do volume'])
for k, p in enumerate(['Manhã', 'Tarde', 'Noite']):
    rr = 33 + k
    put(wh, f'B{rr}', p, font, b=True)
    put(wh, f'C{rr}', f"=COUNTIF({IR('G')},\"{p}\")", font, '0', b=True)
    put(wh, f'D{rr}', f"=SUMIF({IR('G')},\"{p}\",{IR('M')})", font, '#,##0', b=True)
    put(wh, f'E{rr}', f'=C{rr}/$C$30', font, '0.0%', b=True)
    put(wh, f'F{rr}', f'=D{rr}/$D$30', font, '0.0%', b=True)
put(wh, 'B37', 'Mediana do horário (h decimal)', bold, b=True)
put(wh, 'C37', f"=MEDIAN({IR('F')})", bold, '0.00', b=True)
put(wh, 'B38', 'Registros antes do meio-dia', bold, b=True)
put(wh, 'C38', f"=COUNTIF({IR('F')},\"<12\")/C30", bold, '0.0%', b=True)
put(wh, 'B40', 'Café perto da hora de dormir', sec_font)
put(wh, 'B41', 'Participantes que tomaram café', font, b=True)
put(wh, 'C41', '=COUNT(Intervalo)', bold, '0', b=True)
put(wh, 'B42', 'Mediana do menor intervalo café→dormir (h)', font, b=True)
put(wh, 'C42', '=MEDIAN(Intervalo)', bold, '0.0', b=True)
put(wh, 'B43', 'Com café a menos de 8,8 h da hora habitual de dormir', font, b=True)
put(wh, 'C43', '=COUNTIF(Intervalo,"<"&LIMITE_INTERVALO)', bold, '0', b=True)
put(wh, 'D43', '=C43/C41', bold, '0.0%', b=True)
put(wh, 'B44', 'Com café a menos de 6 h da hora habitual de dormir', font, b=True)
put(wh, 'C44', '=COUNTIF(Intervalo,"<6")', bold, '0', b=True)
put(wh, 'D44', '=C44/C41', bold, '0.0%', b=True)
put(wh, 'B45', 'O intervalo usa o horário habitual de dormir de dias úteis (domingo a quinta) ou de fim de semana '
                '(sexta e sábado), conforme o dia do recordatório.', note_font)
ch = BarChart()
ch.type = 'col'; ch.title = 'Bebidas de café por hora do dia'; ch.legend = None; ch.style = 10
ch.height = 7.5; ch.width = 17; ch.y_axis.majorGridlines = None; ch.gapWidth = 40
ch.add_data(Reference(wh, min_col=3, min_row=6, max_row=29), titles_from_data=False)
ch.set_categories(Reference(wh, min_col=2, min_row=6, max_row=29))
ch.series[0].graphicalProperties.solidFill = '9A5426'
wh.add_chart(ch, 'H5')

# ================================================================ Resumo
wsr = sheet('Resumo', 'A0522D')
wb.move_sheet(wsr, offset=-(wb.index(wsr) - 1))
wsr.column_dimensions['A'].width = 3
wsr.column_dimensions['B'].width = 64
wsr.column_dimensions['C'].width = 14
wsr.column_dimensions['D'].width = 50
put(wsr, 'B2', 'Resumo dos resultados', title_font)
put(wsr, 'B3', 'Todos os valores abaixo são fórmulas: mudar a Base muda o Resumo.', sub_font)
header_row(wsr, 5, 2, ['Indicador', 'Valor', 'Como ler'])
CR = "'Correlação e regressão'!"
PR = "'Probabilidade'!"
HR = "'Horário do café'!"
res = [
    ('Participantes analisados', '=COUNT(ID_)', '0', 'adultos de 18 a 29 anos, NHANES 2021–2023'),
    ('Tomaram café em ao menos um dos dois dias', f'={PR}E6', '0.0%', 'evento A'),
    ('Tomaram café nos dois dias', f'={PR}E7', '0.0%', 'aproximação de consumo diário'),
    ('Xícaras/dia entre quem tomou café (média)', '=AVERAGE(XicarasCons)', '0.00', 'xícara-padrão de 240 mL'),
    ('Xícaras/dia entre quem tomou café (mediana)', '=MEDIAN(XicarasCons)', '0.00', ''),
    ('Quem tomou café com maior consumo pela manhã', '=COUNTIF(Periodo,"Manhã")/COUNTIF(TomouCafe,"Sim")', '0.0%', '5h00–11h59'),
    ('Cafeína total, todas as fontes (média, mg/dia)', '=AVERAGE(Cafeina)', '0.0', 'café, refrigerante, chá, energético etc.'),
    ('Acima de 400 mg/dia de cafeína', f'={PR}E11', '0.0%', 'limite de referência da FDA'),
    ('Café a menos de 8,8 h da hora de dormir (entre quem tomou)', f'={HR}D43', '0.0%', 'Gardiner et al. (2023)'),
    ('Sono médio em dias úteis (h)', '=AVERAGE(SonoUtil)', '0.00', ''),
    ('Dormem menos de 7 h em dias úteis', f'={PR}E10', '0.0%', 'recomendação mínima para adultos: 7 h'),
    ('Problemas de sono em vários dias ou mais', f'={PR}E8', '0.0%', 'evento B (PHQ-9, item 3)'),
    ('Dificuldade de concentração em vários dias ou mais', f'={PR}E9', '0.0%', 'evento C (PHQ-9, item 7)'),
    ('r — xícaras × dificuldade de concentração', f'={CR}C16', '0.000', 'praticamente nulo'),
    ('r — xícaras × problemas de sono', f'={CR}D16', '0.000', 'negativo e desprezível'),
    ('r — xícaras × horas de sono', f'={CR}E16', '0.000', 'praticamente nulo'),
    ('r — problemas de sono × dificuldade de concentração', f'={CR}G16', '0.000', 'positivo e moderado'),
    ('R² — concentração explicada pelas xícaras', f'={CR}C23', '0.00%', 'modelo 1'),
    ('R² — concentração explicada pelos problemas de sono', f'={CR}G23', '0.0%', 'modelo 2'),
    ('P(C | tomou café)', f'={PR}F{CT1 + 2}', '0.0%', 'igual a P(C | não tomou)'),
    ('P(C | não tomou café)', f'={PR}F{CT1 + 3}', '0.0%', ''),
    ('P(C | problemas de sono)', f'={PR}F{CT2 + 2}', '0.0%', 'mais que o dobro de P(C | sem problemas)'),
    ('P(C | sem problemas de sono)', f'={PR}F{CT2 + 3}', '0.0%', ''),
    ('Binomial: P(ao menos 1 de 5 jovens tomou café)', None, '0.0%', 'n = 5, p = P(A)'),
]
for k, (lab, fx, fmt, note) in enumerate(res):
    rr = 6 + k
    put(wsr, f'B{rr}', lab, font, b=True)
    put(wsr, f'C{rr}', fx, bold, fmt, b=True)
    put(wsr, f'D{rr}', note, note_font, b=True)
RES_BINOM_ROW = 6 + len(res) - 1

# ================================================================ Dicionário
wd = sheet('Dicionário', '8C7B6B')
wd.column_dimensions['A'].width = 3
wd.column_dimensions['B'].width = 32
wd.column_dimensions['C'].width = 56
wd.column_dimensions['D'].width = 26
wd.column_dimensions['E'].width = 30
put(wd, 'B2', 'Dicionário de variáveis', title_font)
header_row(wd, 4, 2, ['Variável (aba Base)', 'Definição e regra de construção', 'Origem no NHANES', 'Classificação'])
dic = [
    ('ID', 'Número sequencial do participante nesta análise (1 a 496).', '—', 'Identificador'),
    ('SEQN (NHANES)', 'Número do participante no NHANES; permite conferir qualquer linha nos arquivos oficiais.', 'SEQN', 'Identificador'),
    ('Gênero', 'Masculino ou feminino, como registrado na entrevista domiciliar.', 'DEMO_L: RIAGENDR', 'Qualitativa nominal'),
    ('Idade (anos)', 'Idade em anos completos na entrevista de triagem.', 'DEMO_L: RIDAGEYR', 'Quantitativa discreta'),
    ('Faixa etária', '18 a 21; 22 a 25; 26 a 29 anos.', 'derivada de RIDAGEYR', 'Qualitativa ordinal'),
    ('Situação na semana anterior', 'Trabalhando (OCD150 = 1 ou 2); procurando trabalho (OCD150 = 3); estudando (OCD150 = 4 e motivo principal OCQ383 = 2); outra situação nos demais casos.', 'OCQ_L: OCD150, OCQ383', 'Qualitativa nominal'),
    ('Café no dia 1 / dia 2 (mL)', 'Soma das bebidas com código FNDDS 92100000–92189999 (café coado, espresso, solúvel, latte, gelado, pronto etc.) em cada recordatório.', 'DR1IFF_L, DR2IFF_L: DR1IFDCD, DR1IGRMS', 'Quantitativa contínua'),
    ('Dias com café (0–2)', 'Em quantos dos dois dias registrados houve ao menos uma bebida de café.', 'derivada', 'Quantitativa discreta'),
    ('Consumo de café', 'Nenhum dos dois dias; um dos dois dias; os dois dias.', 'derivada', 'Qualitativa ordinal'),
    ('Tomou café', 'Sim quando houve café em ao menos um dos dois dias.', 'derivada', 'Qualitativa nominal dicotômica'),
    ('Xícaras/dia (240 mL)', 'Volume médio de café dos dois dias ÷ 240 mL.', 'derivada', 'Quantitativa contínua'),
    ('Faixa de xícaras/dia', '0; até 1; mais de 1 a 2; mais de 2 a 3; mais de 3.', 'derivada', 'Qualitativa ordinal (classes)'),
    ('Café de manhã / à tarde / à noite (mL)', 'Volume de café por período, somando os dois dias, a partir do horário de início de cada consumo.', 'DR1_020, DR2_020', 'Quantitativa contínua'),
    ('Período de maior consumo', 'Período com o maior volume de café; em empate, o mais cedo.', 'derivada', 'Qualitativa nominal'),
    ('Menor intervalo café→dormir (h)', 'Para cada dia com café: hora habitual de dormir menos o horário do último café do dia; vale o menor dos dois dias. Consumos entre 0h e 4h59 contam como continuação da noite.', 'DR1_020, DR1DAY, SLQ300, SLQ320', 'Quantitativa contínua'),
    ('Cafeína total (mg/dia)', 'Média dos dois dias da cafeína de todos os alimentos e bebidas.', 'DR1TOT_L, DR2TOT_L: DR1TCAFF, DR2TCAFF', 'Quantitativa contínua'),
    ('Cafeína do café (mg/dia)', 'Média dos dois dias da cafeína vinda apenas das bebidas de café.', 'DR1ICAFF, DR2ICAFF', 'Quantitativa contínua'),
    ('Hora de dormir / acordar (dias úteis)', 'Horário habitual em que adormece e acorda em dias úteis ou de trabalho.', 'SLQ_L: SLQ300, SLQ310', 'Quantitativa contínua (hora)'),
    ('Sono em dias úteis (h)', 'Horas habituais de sono calculadas pelo NCHS a partir dos horários; arredondadas para meia hora; "menos de 3 h" codificado como 2 e "14 h ou mais" como 14.', 'SLQ_L: SLD012', 'Quantitativa contínua'),
    ('Sono no fim de semana (h)', 'Mesma regra, para fins de semana ou dias de folga.', 'SLQ_L: SLD013', 'Quantitativa contínua'),
    ('Sono < 7 h', 'Sim quando o sono em dias úteis é menor que 7 h, mínimo recomendado para adultos.', 'derivada', 'Qualitativa nominal dicotômica'),
    ('Problemas de sono (0–3)', 'PHQ-9, item 3: com que frequência, nas últimas 2 semanas, teve dificuldade para pegar no sono, manter o sono ou dormiu demais. 0 nenhum dia; 1 vários dias; 2 mais da metade dos dias; 3 quase todos os dias.', 'DPQ_L: DPQ030', 'Qualitativa ordinal (escore 0–3)'),
    ('Sono prejudicado', 'Sim quando problemas de sono ≥ 1 (vários dias ou mais).', 'derivada', 'Qualitativa nominal dicotômica'),
    ('Dificuldade de concentração (0–3)', 'PHQ-9, item 7: com que frequência, nas últimas 2 semanas, teve dificuldade de se concentrar em coisas como ler ou assistir TV. Mesma escala 0–3.', 'DPQ_L: DPQ070', 'Qualitativa ordinal (escore 0–3)'),
    ('Concentração prejudicada', 'Sim quando dificuldade de concentração ≥ 1 (vários dias ou mais).', 'derivada', 'Qualitativa nominal dicotômica'),
]
for k, row in enumerate(dic):
    rr = 5 + k
    for j, v in enumerate(row):
        put(wd, f'{get_column_letter(2 + j)}{rr}', v, bold if j == 0 else font, al=wrap, b=True)
rr = 5 + len(dic) + 1
put(wd, f'B{rr}', 'Códigos das variáveis da aba Dados brutos', sec_font)
codes = [('RIAGENDR', '1 masculino; 2 feminino'), ('OCD150', '1 trabalhando; 2 com trabalho, mas afastado; 3 procurando trabalho; 4 sem trabalho'),
         ('OCQ383', 'motivo de não trabalhar: 1 cuida da casa/família; 2 estuda; 3 aposentado; 4 saúde/incapacidade; 5 sem trabalho/dispensado; 6 sazonal; 7 outro'),
         ('SLQ300 / SLQ310', 'hora habitual de dormir / acordar em dias úteis (HH:MM)'), ('SLQ320 / SLQ330', 'idem, fins de semana'),
         ('SLD012 / SLD013', 'horas de sono em dias úteis / fins de semana'), ('DPQ030 / DPQ070', 'PHQ-9, itens 3 e 7 (0 a 3)'),
         ('DR1DRSTZ / DR2DRSTZ', 'qualidade do recordatório: 1 = confiável e completo'), ('DR1DAY / DR2DAY', 'dia da semana do consumo: 1 domingo … 7 sábado'),
         ('DR1TCAFF / DR2TCAFF', 'cafeína total do dia (mg)'), ('WTDR2D', 'peso amostral de dois dias de dieta'),
         ('SDMVSTRA / SDMVPSU', 'estrato e unidade primária de amostragem mascarados (para variância)')]
for k, (a, b_) in enumerate(codes):
    put(wd, f'B{rr + 1 + k}', a, bold, al=wrap, b=True)
    put(wd, f'C{rr + 1 + k}', b_, font, al=wrap, b=True)

# ordem final das abas
order = ['Leia-me', 'Resumo', 'Base', 'Frequências', 'Medidas', 'Correlação e regressão', 'Probabilidade',
         'Horário do café', 'Dados brutos', 'Itens de café', 'Dicionário']
wb._sheets = [wb[n] for n in order]
# binomial no resumo (depende da linha final da aba Probabilidade)
binom_row = None
for row in wp.iter_rows(min_col=2, max_col=2):
    if row[0].value == 'P(X ≥ 1) = 1 − P(X = 0)':
        binom_row = row[0].row
wsr[f'C{RES_BINOM_ROW}'] = f"='Probabilidade'!E{binom_row}"
wsr[f'C{RES_BINOM_ROW}'].number_format = '0.0%'
wsr[f'C{RES_BINOM_ROW}'].font = bold
for ws in wb.worksheets:
    ws.sheet_view.zoomScale = 100
wb.active = 0
wb.calculation.fullCalcOnLoad = True   # Excel/LibreOffice recalculam ao abrir
dst = os.path.join(OUT, 'Base_Real_Cafe_NHANES_496.xlsx')
wb.save(dst)
print('saved', dst)
