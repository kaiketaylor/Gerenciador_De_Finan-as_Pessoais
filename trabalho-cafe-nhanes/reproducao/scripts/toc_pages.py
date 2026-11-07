import subprocess, json, re, sys
pdf=sys.argv[1]; out=sys.argv[2]
n=int(re.search(r'Pages:\s+(\d+)',subprocess.run(['pdfinfo',pdf],capture_output=True,text=True).stdout).group(1))
heads={'1':'TÍTULO DO PROJETO','2':'TEMA ESCOLHIDO','3':'PROBLEMA DE PESQUISA','4':'OBJETIVO DO ESTUDO','5':'POPULAÇÃO E AMOSTRA','6':'TIPO DE AMOSTRAGEM','7':'VARIÁVEIS ANALISADAS E CLASSIFICAÇÃO','8':'PROCESSO DE COLETA DE DADOS','9':'ORGANIZAÇÃO DOS DADOS','10':'TABELAS DE FREQUÊNCIA','11':'GRÁFICOS','12':'CÁLCULOS ESTATÍSTICOS','13':'CORRELAÇÃO E INTERPRETAÇÃO','14':'REGRESSÃO LINEAR SIMPLES','15':'PROBABILIDADE SIMPLES','16':'DISTRIBUIÇÃO BINOMIAL','17':'ANÁLISE DOS RESULTADOS','18':'CONCLUSÃO','19':'TOMADA DE DECISÃO','20':'REFERÊNCIAS','21':'ANEXOS'}
texts=[subprocess.run(['pdftotext','-f',str(i),'-l',str(i),'-layout',pdf,'-'],capture_output=True,text=True).stdout for i in range(1,n+1)]
toc_page=next(i for i,t in enumerate(texts,1) if 'SUMÁRIO' in t)
res={}
for k,h in heads.items():
    pat=re.compile(r'^\s*'+re.escape(k)+r'\s+'+re.escape(h)+r'\s*$',re.M)
    for i,t in enumerate(texts,1):
        if i<=toc_page: continue
        if pat.search(t): res[k]=i; break
print(res, 'missing', [k for k in heads if k not in res])
json.dump(res,open(out,'w'))
