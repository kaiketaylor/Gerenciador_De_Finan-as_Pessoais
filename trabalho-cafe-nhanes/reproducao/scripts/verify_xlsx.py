import json, math
import pandas as pd
from openpyxl import load_workbook
R=json.load(open('out/results.json'))
wb=load_workbook('out/Base_Real_Cafe_NHANES_496.xlsx',data_only=True)
bv=pd.read_csv('out/base_analitica.csv')
ws=wb['Base']
hdr=[c.value for c in ws[1]]
rows=list(ws.iter_rows(min_row=2,values_only=True))
df=pd.DataFrame(rows,columns=hdr)
print('rows',len(df))
chk=[('Gênero','Gênero'),('Idade (anos)','Idade (anos)'),('Faixa etária','Faixa etária'),('Situação na semana anterior','Situação na semana anterior'),
('Café no dia 1 (mL)','Café no dia 1 (mL)'),('Café no dia 2 (mL)','Café no dia 2 (mL)'),('Dias com café (0–2)','Dias com café (0–2)'),('Consumo de café','Consumo de café'),
('Tomou café','Tomou café (Sim/Não)'),('Xícaras/dia (240 mL)','Xícaras/dia (240 mL)'),('Faixa de xícaras/dia','Faixa de xícaras/dia'),('Período de maior consumo','Período de maior consumo'),
('Cafeína total (mg/dia)','Cafeína total (mg/dia)'),('Cafeína do café (mg/dia)','Cafeína do café (mg/dia)'),('Hora de dormir (dias úteis)','Hora de dormir (dias úteis)'),
('Sono em dias úteis (h)','Sono em dias úteis (h)'),('Sono < 7 h','Sono < 7 h em dias úteis'),('Problemas de sono (frequência)','Problemas de sono (frequência)'),
('Sono prejudicado','Sono prejudicado (Sim/Não)'),('Dificuldade de concentração (frequência)','Dificuldade de concentração (frequência)'),('Concentração prejudicada','Concentração prejudicada (Sim/Não)')]
bad=0
for a,b in chk:
    x=df[a]; y=bv[b]
    if pd.api.types.is_numeric_dtype(y):
        diff=(pd.to_numeric(x)-y).abs().max()
        ok=diff<1e-3
    else:
        xs=x.fillna('').astype(str); ys=y.fillna('').astype(str)
        ok=(xs==ys).all(); diff=(xs!=ys).sum()
    if not ok: bad+=1
    print(('OK ' if ok else 'BAD'),a,diff)
def find(ws,label,col_offset=1,col='B'):
    for r in ws.iter_rows(min_col=2,max_col=2):
        if r[0].value==label: return r[0].row
wr=wb['Resumo']
for r in wr.iter_rows(min_row=6,values_only=True):
    if r[1]: print('RESUMO', r[1], '=>', r[2])
wc=wb['Correlação e regressão']
print('r row', [wc.cell(row=16,column=c).value for c in range(3,9)])
print('CORREL', [wc.cell(row=17,column=c).value for c in range(3,9)])
print('p', [wc.cell(row=20,column=c).value for c in range(3,9)])
print('b', [wc.cell(row=21,column=c).value for c in range(3,9)], 'a', [wc.cell(row=22,column=c).value for c in range(3,9)])
print('blo', [wc.cell(row=25,column=c).value for c in range(3,9)], 'bhi', [wc.cell(row=26,column=c).value for c in range(3,9)])
P=R['pearson']
for j,k in enumerate(['xic_conc','xic_probsono','xic_sono','caf_sono','probsono_conc','idade_xic']):
    v=wc.cell(row=16,column=3+j).value
    print(k, 'py', round(P[k]['r'],6), 'xl', round(v,6), 'p py', P[k]['p'], 'xl', wc.cell(row=20,column=3+j).value, 'blo', P[k]['b_lo'], wc.cell(row=25,column=3+j).value)
wm=wb['Medidas']
for r in wm.iter_rows(min_row=6,max_row=13,values_only=True):
    print('MED', r[1:14])
for r in wm.iter_rows(min_row=16,max_row=33,values_only=True):
    if r[1]: print('STEP', r[1], r[2])
wf=wb['Frequências']
for r in wf.iter_rows(min_row=5,values_only=True):
    if r[1] is not None and r[2] is not None: print('FREQ', r[1:5])
wp=wb['Probabilidade']
for r in wp.iter_rows(min_row=5,values_only=True):
    if r[1] is not None: print('PROB', r[1:7])
wh=wb['Horário do café']
for r in wh.iter_rows(min_row=30,max_row=45,values_only=True):
    if r[1] is not None: print('HOR', r[1:6])
print('hourly xl', [wh.cell(row=6+h,column=3).value for h in range(24)])
print('hourly py', R['horario']['por_hora_itens'])
print('BAD COUNT', bad)
