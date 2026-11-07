/* Relatório do projeto (DOCX) — gerado a partir de out/results.json e out/graficos/*.png
   Uso: node build_docx.js [arquivo_paginas.json]   (o JSON opcional traz as páginas do sumário) */
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, Header, Footer,
  AlignmentType, BorderStyle, WidthType, PageNumber, PageBreak, TabStopType, VerticalAlign,
  PositionalTab, PositionalTabAlignment, PositionalTabRelativeTo, PositionalTabLeader, LevelFormat,
  HeadingLevel, TableLayoutType, LeaderType, LineRuleType,
} = require('docx');

const ROOT = path.join(__dirname, '..');
const OUT = path.join(ROOT, 'out');
const R = JSON.parse(fs.readFileSync(path.join(OUT, 'results.json'), 'utf8'));
const PAGES = process.argv[2] && fs.existsSync(process.argv[2]) ? JSON.parse(fs.readFileSync(process.argv[2], 'utf8')) : {};
const DEST = process.argv[3] || path.join(OUT, 'Trabalho_Cafe_Dados_Reais_NHANES.docx');

// ------------------------------------------------------------------ formatação numérica pt-BR
const nf = (v, d = 1) => {
  const s = Math.abs(v).toFixed(d).split('.');
  s[0] = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return (v < 0 && Number(Math.abs(v).toFixed(d)) !== 0 ? '−' : '') + s.join(',');
};
const pc = (v, d = 1) => nf(v * 100, d) + '%';
const pv = (p) => (p < 0.001 ? '< 0,001' : nf(p, 3));
const F = R.freq, D = R.desc, P = R.pearson, PR = R.prob, N = R.n;
const fr = (key, cat) => F[key].find((r) => r.cat === cat);

// ------------------------------------------------------------------ estilo
const FONT = 'Arial';
const INK = '1F1A16';
const W_TEXT = 9071; // 16 cm em DXA
const BODY = { line: 360, before: 0, after: 80 };
const SRC = 'Fonte: elaborado pelos autores com microdados do NHANES ago./2021–ago./2023 (CDC/NCHS).';

function runs(text, base = {}) {
  // **negrito**, *itálico*
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const t = m[0];
    if (t.startsWith('**')) out.push(new TextRun({ ...base, text: t.slice(2, -2), bold: true }));
    else out.push(new TextRun({ ...base, text: t.slice(1, -1), italics: true }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}
const p = (text, o = {}) => mark(new Paragraph({
  children: runs(text), alignment: o.align || AlignmentType.JUSTIFIED,
  spacing: o.spacing || BODY, indent: o.noIndent ? undefined : { firstLine: 709 }, keepNext: o.keepNext,
}));
const pn = (text, o = {}) => p(text, { ...o, noIndent: true });
const eq = (text) => mark(new Paragraph({
  children: runs(text), alignment: AlignmentType.CENTER, spacing: { line: 300, before: 60, after: 60 },
}));
const h1 = (text, o = {}) => mark(new Paragraph({
  heading: HeadingLevel.HEADING_1, children: [new TextRun(text)], pageBreakBefore: !!o.newPage,
}));
const h2 = (text) => mark(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] }));
let lastKind = 'other', alphaInst = 0;
const mark = (x) => { lastKind = 'other'; return x; };
const bullet = (text, ref = 'bul') => {
  if (ref === 'alpha' && lastKind !== 'alpha') alphaInst += 1;
  lastKind = ref === 'alpha' ? 'alpha' : 'other';
  return new Paragraph({
    children: runs(text), numbering: { reference: ref, level: 0, instance: ref === 'alpha' ? alphaInst : 0 },
    alignment: AlignmentType.JUSTIFIED, spacing: { line: 360, before: 0, after: 40 },
  });
};
const lettered = (text) => bullet(text, 'alpha');
const blank = (n = 1) => Array.from({ length: n }, () => new Paragraph({ children: [new TextRun('')], spacing: { line: 360, before: 0, after: 0 } }));

// ------------------------------------------------------------------ tabelas (padrão IBGE: sem linhas verticais)
let tabN = 0, grafN = 0;
const NONE = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const LINE = (sz = 8) => ({ style: BorderStyle.SINGLE, size: sz, color: '000000' });
function caption(kind, n, title) {
  return new Paragraph({
    keepNext: true, spacing: { before: 200, after: 80, line: 276 }, alignment: AlignmentType.LEFT,
    children: [new TextRun({ text: `${kind} ${n} – `, bold: true, size: 20 }), ...runs(title, { size: 20 })],
  });
}
function source(text = SRC) {
  return new Paragraph({ spacing: { before: 60, after: 200, line: 240 }, children: runs(text, { size: 18 }) });
}
function table(title, head, rows, widths, opt = {}) {
  tabN += 1; lastKind = 'other';
  const total = widths.reduce((a, b) => a + b, 0);
  const align = opt.align || head.map((_, i) => (i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER));
  const cell = (txt, i, kind, last) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA },
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    verticalAlign: VerticalAlign.CENTER,
    borders: {
      top: kind === 'head' ? LINE(8) : NONE,
      bottom: kind === 'head' ? LINE(4) : last ? LINE(8) : NONE,
      left: NONE, right: NONE,
    },
    shading: kind === 'total' ? { fill: 'F2ECE6', type: 'clear', color: 'auto' } : undefined,
    children: [new Paragraph({
      alignment: align[i], spacing: { before: 0, after: 0, line: 240 },
      children: runs(String(txt), { size: opt.size || 19, bold: kind === 'head' || kind === 'total' }),
    })],
  });
  const tr = [new TableRow({ tableHeader: true, cantSplit: true, children: head.map((h, i) => cell(h, i, 'head', false)) })];
  rows.forEach((r, k) => {
    const isTotal = opt.totalLast && k === rows.length - 1;
    tr.push(new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, i, isTotal ? 'total' : 'body', k === rows.length - 1)) }));
  });
  return [
    caption('Tabela', tabN, title),
    new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED, rows: tr }),
    source(opt.source),
  ];
}
function figure(title, file, opt = {}) {
  grafN += 1; lastKind = 'other';
  const buf = fs.readFileSync(path.join(OUT, 'graficos', file));
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  const maxW = opt.widthPx || 604;
  const width = Math.round(maxW), height = Math.round(maxW * h / w);
  return [
    caption('Gráfico', grafN, title),
    new Paragraph({
      alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 0, after: 0, line: 240, lineRule: LineRuleType.AUTO },
      children: [new ImageRun({ type: 'png', data: buf, transformation: { width, height },
        altText: { title, description: title, name: file } })],
    }),
    source(opt.source),
  ];
}

// ------------------------------------------------------------------ cabeçalho e rodapé
const logoF = fs.readFileSync(path.join(ROOT, 'modelo', 'logo_fatec.png'));
const logoC = fs.readFileSync(path.join(ROOT, 'modelo', 'logo_cps_sp.png'));
const header = () => new Header({
  children: [new Paragraph({
    tabStops: [{ type: TabStopType.RIGHT, position: W_TEXT }], spacing: { before: 0, after: 0, line: 240, lineRule: LineRuleType.AUTO },
    children: [
      new ImageRun({ type: 'png', data: logoF, transformation: { width: 92, height: 50 },
        altText: { title: 'Fatec Presidente Prudente', description: 'Logotipo da Fatec Presidente Prudente', name: 'fatec' } }),
      new TextRun({ text: '\t' }),
      new ImageRun({ type: 'png', data: logoC, transformation: { width: 296, height: 51 },
        altText: { title: 'Centro Paula Souza e Governo do Estado de São Paulo', description: 'Logotipos do Centro Paula Souza e do Governo do Estado de São Paulo', name: 'cps' } }),
    ],
  })],
});
const footer = new Footer({
  children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ children: [PageNumber.CURRENT], size: 20 })] })],
});
const emptyFooter = new Footer({ children: [new Paragraph({ children: [] })] });

// ------------------------------------------------------------------ conteúdo
const C = [];
const add = (...xs) => xs.flat().forEach((x) => C.push(x));

// CAPA ------------------------------------------------------------------
const center = (text, o = {}) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { line: 360, before: 0, after: o.after ?? 0 },
  children: [new TextRun({ text, bold: o.bold, size: o.size || 24, allCaps: o.caps })],
});
add(
  center('Faculdade de Tecnologia de Presidente Prudente', { bold: true, caps: true }),
  center('Curso Superior de Tecnologia em Análise e Desenvolvimento de Sistemas'),
  blank(3),
  center('Bruna Lais Amorin', { caps: true }), center('Kaike Taylor Antonio Santos', { caps: true }),
  center('Lucas Gustavo Mendes', { caps: true }), center('Rafael Gervazoni Bezerra', { caps: true }),
  blank(4),
  center('Consumo de café e produtividade acadêmica:', { bold: true, caps: true, size: 28 }),
  center('café, sono e concentração em 496 adultos de 18 a 29 anos', { size: 26 }),
  center('(NHANES 2021–2023)', { size: 26, after: 240 }),
  blank(2),
  new Paragraph({
    indent: { left: 4535 }, alignment: AlignmentType.JUSTIFIED, spacing: { line: 240, after: 0 },
    children: [new TextRun({ text: 'Projeto estatístico apresentado à disciplina de Estatística Aplicada do curso de Análise e Desenvolvimento de Sistemas da Fatec Presidente Prudente, como atividade avaliativa do 2º bimestre.', size: 20 })],
  }),
  blank(6),
  center('Presidente Prudente – SP', { caps: true }),
  center('2026'),
);

// RESUMO ---------------------------------------------------------------
add(
  new Paragraph({ heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER, pageBreakBefore: true, children: [new TextRun('RESUMO')] }),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED, spacing: { line: 240, after: 200 },
    children: runs(
      `Este trabalho verifica se a quantidade de café consumida está associada à dificuldade de concentração e ao sono de adultos em idade universitária. ` +
      `Foram usados microdados públicos da National Health and Nutrition Examination Survey (NHANES), ciclo de agosto de 2021 a agosto de 2023, conduzida pelo National Center for Health Statistics dos Estados Unidos. ` +
      `A amostra reúne todos os ${N} participantes de 18 a 29 anos com dois recordatórios alimentares de 24 horas válidos, horas de sono calculáveis e respostas aos itens de sono e de concentração do questionário PHQ-9. ` +
      `O café foi medido pelo volume de cada bebida relatada, com horário. Tomaram café em ao menos um dos dois dias ${pc(PR.P_A)} dos participantes; entre eles, a média foi de ${nf(D.xicaras_consumidores.media, 2)} xícara de 240 mL por dia, e ${pc(fr('periodo', 'Manhã').pct)} concentraram o consumo pela manhã. ` +
      `A correlação entre xícaras por dia e dificuldade de concentração foi nula (r = ${nf(P.xic_conc.r, 3)}; p = ${pv(P.xic_conc.p)}), assim como a correlação com as horas de sono (r = ${nf(P.xic_sono.r, 3)}; p = ${pv(P.xic_sono.p)}). ` +
      `Os problemas de sono, por outro lado, acompanharam a dificuldade de concentração (r = ${nf(P.probsono_conc.r, 3)}; p < 0,001): ela atingiu ${pc(PR.B_C.p_e2_dado_e1)} de quem relatou problemas de sono e ${pc(PR.B_C.p_e2_dado_nao_e1)} de quem não relatou. ` +
      `Conclui-se que, nesse grupo, a quantidade de café não indica o nível de concentração e que ações voltadas à produtividade acadêmica devem priorizar o sono e o horário da cafeína, não o número de xícaras.`, { size: 24 }),
  }),
  new Paragraph({ alignment: AlignmentType.LEFT, spacing: { line: 240 }, children: runs('**Palavras-chave:** café; cafeína; sono; concentração; NHANES.', { size: 24 }) }),
);

// SUMÁRIO --------------------------------------------------------------
const TOC = [
  ['1', 'TÍTULO DO PROJETO'], ['2', 'TEMA ESCOLHIDO'], ['3', 'PROBLEMA DE PESQUISA'], ['4', 'OBJETIVO DO ESTUDO'],
  ['5', 'POPULAÇÃO E AMOSTRA'], ['6', 'TIPO DE AMOSTRAGEM'], ['7', 'VARIÁVEIS ANALISADAS E CLASSIFICAÇÃO'],
  ['8', 'PROCESSO DE COLETA DE DADOS'], ['9', 'ORGANIZAÇÃO DOS DADOS'], ['10', 'TABELAS DE FREQUÊNCIA'],
  ['11', 'GRÁFICOS'], ['12', 'CÁLCULOS ESTATÍSTICOS'], ['13', 'CORRELAÇÃO E INTERPRETAÇÃO'],
  ['14', 'REGRESSÃO LINEAR SIMPLES'], ['15', 'PROBABILIDADE SIMPLES'], ['16', 'DISTRIBUIÇÃO BINOMIAL'],
  ['17', 'ANÁLISE DOS RESULTADOS'], ['18', 'CONCLUSÃO'], ['19', 'TOMADA DE DECISÃO'], ['20', 'REFERÊNCIAS'], ['21', 'ANEXOS'],
];
add(new Paragraph({ heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER, pageBreakBefore: true, children: [new TextRun('SUMÁRIO')] }));
TOC.forEach(([n, t]) => add(new Paragraph({
  spacing: { line: 360, before: 0, after: 0 },
  tabStops: [{ type: TabStopType.LEFT, position: 567 }, { type: TabStopType.RIGHT, position: W_TEXT, leader: LeaderType.DOT }],
  children: [
    new TextRun({ text: `${n}\t${t}`, bold: Number(n) <= 21 }),
    new TextRun({ text: `\t${PAGES[n] || '00'}` }),
  ],
})));

// 1 ---------------------------------------------------------------------
add(h1('1  TÍTULO DO PROJETO', { newPage: true }),
  p('**Consumo de café e produtividade acadêmica: análise estatística da relação entre a quantidade de café, a dificuldade de concentração e o sono de 496 adultos de 18 a 29 anos, com microdados reais do NHANES 2021–2023.**'));

// 2 ---------------------------------------------------------------------
add(h1('2  TEMA ESCOLHIDO'),
  p(`O café é a principal fonte de cafeína da dieta e é usado por estudantes para manter o alerta em aulas, provas e madrugadas de estudo. No Brasil, a Pesquisa de Orçamentos Familiares 2017–2018 registrou o café como o alimento consumido com maior frequência: 78,1% das pessoas com 10 anos ou mais o relataram no dia investigado, com média de 163,2 gramas por dia (IBGE, 2020).`),
  p(`A cafeína bloqueia os receptores de adenosina, substância que se acumula ao longo do dia e produz sonolência. Esse mecanismo explica o benefício e o custo do café. O benefício aparece sobretudo quando a pessoa dormiu pouco: em revisão sistemática, doses agudas de cafeína melhoraram atenção e tempo de reação após privação de sono (IRWIN et al., 2020). O custo aparece quando a cafeína chega perto da hora de dormir: a metanálise de Gardiner et al. (2023) estimou que o café precisa ser consumido ao menos 8,8 horas antes de deitar para não reduzir o tempo total de sono. Há ainda a tolerância: em quem toma café todos os dias, parte do ganho percebido é apenas a reversão dos sintomas de abstinência acumulados desde a última dose (JAMES; ROGERS, 2005).`),
  p(`O tema reúne, portanto, dois efeitos que podem se compensar na rotina de um estudante: o café como recurso para concentração e como possível prejuízo ao sono, que por sua vez também afeta a concentração. Medir os dois efeitos nas mesmas pessoas exige dados de consumo, de sono e de concentração coletados de forma padronizada.`),
  h2('2.1  Por que uma base pública e por que o NHANES'),
  p(`Antes de definir a fonte, o grupo procurou bases abertas que reunissem, para os mesmos indivíduos, consumo de café, sono e alguma medida de concentração. As grandes pesquisas brasileiras não cobrem as três dimensões juntas: a POF 2017–2018 detalha o café, mas não investiga o sono; a Pesquisa Nacional de Saúde aplica o questionário PHQ-9, que pergunta sobre sono e concentração, mas não registra o consumo de café. Também foi avaliado um questionário com estudantes publicado no repositório Mendeley Data (ABDULLAH; RAHMAN, 2025), que trata de cafeína e desempenho acadêmico. Ele foi descartado porque traz apenas respostas categóricas, sem quantidade de café, e porque 205 das 996 respostas têm data de dezembro de 2024, fora do período de coleta informado (outubro e novembro), com até nove respostas registradas no mesmo minuto.`),
  p(`O NHANES atende aos três requisitos. É uma pesquisa oficial do governo dos Estados Unidos, com amostra probabilística, protocolo publicado, controle de qualidade documentado e microdados identificados por um número de participante (SEQN). Isso permite que qualquer leitor baixe os mesmos arquivos e confira cada valor deste relatório.`));

// 3 ---------------------------------------------------------------------
add(h1('3  PROBLEMA DE PESQUISA'),
  p('**Entre adultos de 18 a 29 anos, a quantidade de café consumida por dia está associada à dificuldade de concentração e à qualidade do sono?**'),
  h2('3.1  Questões complementares'),
  lettered('Com que frequência esses jovens tomam café, em que quantidade e em que horário do dia?'),
  lettered('Quantos dormem menos do que as 7 horas recomendadas para adultos e quantos relatam problemas de sono?'),
  lettered('Se a quantidade de café não acompanhar a dificuldade de concentração, alguma outra variável disponível na base acompanha?'),
  h2('3.2  Hipóteses'),
  p('Para cada par de variáveis analisado, foram testadas as hipóteses abaixo, com nível de significância de 5%:'),
  bullet('H₀: não existe correlação linear na população amostrada (ρ = 0);'),
  bullet('H₁: existe correlação linear (ρ ≠ 0).'),
  p('Como os dados vêm de uma amostra probabilística, é possível testar essas hipóteses com o teste t do coeficiente de Pearson e, para as tabelas de contingência, com o teste qui-quadrado de independência.'));

// 4 ---------------------------------------------------------------------
add(h1('4  OBJETIVO DO ESTUDO'),
  p(`**Objetivo geral:** analisar, com dados reais, a relação entre a quantidade de café consumida e a dificuldade de concentração e o sono de adultos de 18 a 29 anos.`),
  pn('**Objetivos específicos:**', { keepNext: true }),
  lettered('descrever o perfil da amostra (gênero, idade e situação de trabalho ou estudo);'),
  lettered('medir a frequência, a quantidade e o horário do consumo de café e a ingestão total de cafeína;'),
  lettered('descrever a duração do sono, os problemas de sono e a dificuldade de concentração;'),
  lettered('calcular medidas de posição e de dispersão;'),
  lettered('estimar correlações de Pearson e testar sua significância;'),
  lettered('ajustar retas de regressão linear simples para a dificuldade de concentração;'),
  lettered('calcular probabilidades simples e condicionais e uma distribuição binomial;'),
  lettered('propor decisões coerentes com o que os dados sustentam.'));

// 5 ---------------------------------------------------------------------
const fl = R.fluxo;
add(h1('5  POPULAÇÃO E AMOSTRA'),
  p(`**População-alvo:** adultos de 18 a 29 anos — faixa que concentra a maior parte dos estudantes de graduação — da população civil não institucionalizada dos Estados Unidos, representada pelo NHANES.`),
  p(`O ciclo de agosto de 2021 a agosto de 2023 do NHANES reuniu ${nf(fl[0].n, 0)} participantes de todas as idades. A amostra deste trabalho resultou de quatro filtros sucessivos, apresentados na Tabela 1.`),
  table('Etapas de seleção da amostra', ['Etapa', 'Participantes'], [
    ['Participantes do NHANES ago./2021–ago./2023', nf(fl[0].n, 0)],
    ['Com 18 a 29 anos na entrevista', nf(fl[1].n, 0)],
    ['Responderam aos itens 3 (sono) e 7 (concentração) do PHQ-9', nf(fl[2].n, 0)],
    ['Informaram horários habituais de dormir e acordar', nf(fl[3].n, 0)],
    ['Completaram os dois recordatórios alimentares com qualidade', nf(fl[4].n, 0)],
  ], [7071, 2000]),
  p(`A maior perda ocorreu na última etapa (${nf(fl[3].n - fl[4].n, 0)} pessoas), porque o segundo recordatório é feito por telefone, dias depois do primeiro, e nem todos o completam. Exigir os dois dias foi uma escolha deliberada: um único recordatório descreve o que a pessoa consumiu em um dia; dois dias não consecutivos aproximam melhor o consumo habitual e permitem separar quem toma café todo dia de quem tomou por acaso (seção 10.2).`),
  p(`**Amostra final: n = ${N} participantes.** Por usar todos os elegíveis, o tamanho da amostra foi definido pelos critérios, e não por sorteio.`),
  h2('5.1  Alcance dos resultados'),
  p(`Os participantes vivem nos Estados Unidos. Os resultados descrevem esse grupo e não podem ser transferidos automaticamente para estudantes da Fatec. Os hábitos diferem: entre os jovens desta amostra, ${pc(PR.P_A)} tomaram café em ao menos um de dois dias, enquanto a POF registrou café em 78,1% dos brasileiros com 10 anos ou mais em um único dia. As medidas não são idênticas, mas a distância indica que o café é mais difundido no Brasil — ponto retomado na tomada de decisão.`));

// 6 ---------------------------------------------------------------------
const W = R.ponderado;
add(h1('6  TIPO DE AMOSTRAGEM'),
  p(`O NHANES usa **amostragem probabilística complexa, estratificada e por conglomerados, em quatro estágios**: (1) sorteio de unidades primárias, formadas por condados ou grupos de condados, dentro de estratos; (2) sorteio de segmentos — quarteirões ou conjuntos de quarteirões — dentro de cada unidade; (3) sorteio de domicílios dentro dos segmentos; e (4) sorteio de pessoas dentro dos domicílios. O ciclo 2021–2023 tem 15 estratos e 30 unidades primárias mascaradas. Diferentemente dos ciclos anteriores, sobreamostrou certas faixas etárias e deixou de sobreamostrar grupos de raça e renda (CDC, 2024; TERRY et al., 2024).`),
  p(`Sobre essa amostra, este trabalho **não fez novo sorteio**: foram incluídos todos os participantes que atendiam aos critérios da Tabela 1. Tecnicamente, trata-se de uma subamostra por critérios de elegibilidade extraída de uma amostra probabilística.`),
  h2('6.1  Consequência para a análise'),
  p(`No NHANES, cada participante representa um número diferente de pessoas da população, informado pelo peso amostral. As tabelas deste trabalho descrevem os ${N} participantes sem ponderação, como pede o escopo da disciplina. Para verificar se essa escolha distorce os resultados, os principais percentuais foram recalculados com o peso de dois dias de dieta (WTDR2D): o consumo de café passa de ${pc(PR.P_A)} para ${pc(W.tomou_cafe)}; o sono abaixo de 7 horas, de ${pc(PR.P_sono_insuf)} para ${pc(W.sono_insuf)}; os problemas de sono, de ${pc(PR.P_B)} para ${pc(W.sono_prej)}; e a dificuldade de concentração, de ${pc(PR.P_C)} para ${pc(W.conc_prej)}. As diferenças são pequenas e não alteram nenhuma conclusão.`),
  p(`Os testes de hipóteses foram calculados como se a amostra fosse aleatória simples. Como o desenho por conglomerados costuma aumentar a variância, os p-valores apresentados tendem a ser um pouco otimistas; por isso, resultados no limite de 5% são tratados com cautela no texto.`));

// 7 ---------------------------------------------------------------------
add(h1('7  VARIÁVEIS ANALISADAS E CLASSIFICAÇÃO'),
  table('Variáveis, origem no NHANES e classificação', ['Variável', 'Origem (arquivo: variável)', 'Classificação'], [
    ['Gênero', 'DEMO_L: RIAGENDR', 'Qualitativa nominal'],
    ['Idade (anos)', 'DEMO_L: RIDAGEYR', 'Quantitativa discreta'],
    ['Faixa etária', 'derivada da idade', 'Qualitativa ordinal'],
    ['Situação na semana anterior', 'OCQ_L: OCD150, OCQ383', 'Qualitativa nominal'],
    ['Dias com café (nenhum, um, os dois)', 'DR1IFF_L, DR2IFF_L: código do alimento', 'Qualitativa ordinal'],
    ['Tomou café (sim ou não)', 'derivada', 'Qualitativa nominal dicotômica'],
    ['Xícaras de café por dia (240 mL)', 'DR1IFF_L, DR2IFF_L: gramas', 'Quantitativa contínua'],
    ['Período de maior consumo', 'DR1IFF_L, DR2IFF_L: horário', 'Qualitativa nominal'],
    ['Cafeína total (mg/dia)', 'DR1TOT_L, DR2TOT_L: DR1TCAFF, DR2TCAFF', 'Quantitativa contínua'],
    ['Horas de sono em dias úteis e no fim de semana', 'SLQ_L: SLD012, SLD013', 'Quantitativa contínua'],
    ['Problemas de sono (0 a 3)', 'DPQ_L: DPQ030 (PHQ-9, item 3)', 'Qualitativa ordinal'],
    ['Dificuldade de concentração (0 a 3)', 'DPQ_L: DPQ070 (PHQ-9, item 7)', 'Qualitativa ordinal'],
  ], [3300, 3471, 2300], { align: [AlignmentType.LEFT, AlignmentType.LEFT, AlignmentType.LEFT] }),
  p(`A concentração foi medida pelo item 7 do PHQ-9: "Nas últimas duas semanas, com que frequência você se sentiu incomodado por dificuldade de se concentrar nas coisas, como ler o jornal ou assistir à televisão?". O item 3 pergunta, na mesma escala, sobre "dificuldade para pegar no sono ou permanecer dormindo, ou dormir mais do que de costume". As respostas valem 0 (nenhum dia), 1 (vários dias), 2 (mais da metade dos dias) e 3 (quase todos os dias). Os itens medem a **frequência de uma dificuldade**, e não um nível de desempenho: valores maiores indicam pior concentração ou pior sono.`),
  p(`Nos cálculos de média, correlação e regressão, os escores de 0 a 3 foram tratados como numéricos, procedimento comum para escalas ordinais de quatro pontos. Para não depender dessa simplificação, todas as correlações foram conferidas com o coeficiente de Spearman, adequado a dados ordinais (Tabela 10).`));

// 8 ---------------------------------------------------------------------
const H = R.horario;
add(h1('8  PROCESSO DE COLETA DE DADOS'),
  h2('8.1  Como o NHANES coletou as informações'),
  p(`**Entrevista domiciliar.** Entrevistadores treinados aplicaram questionários em computador (sistema CAPI), na casa do participante ou por telefone. Dessa etapa vêm gênero, idade, situação de trabalho e os horários habituais de dormir e acordar, perguntas adaptadas do Munich ChronoType Questionnaire (ROENNEBERG; WIRZ-JUSTICE; MERROW, 2003). O NCHS calculou as horas de sono a partir desses horários.`),
  p(`**Centro móvel de exames.** O PHQ-9 foi respondido pelo próprio participante em computador com áudio (ACASI), sem entrevistador, recurso usado para reduzir o constrangimento em perguntas sobre saúde mental (KROENKE; SPITZER; WILLIAMS, 2001).`),
  p(`**Recordatórios alimentares de 24 horas.** Em dois dias não consecutivos, por telefone, o participante relatou tudo o que comeu e bebeu da meia-noite à meia-noite do dia anterior, com horário, ocasião e quantidade, apoiado por utensílios de medida enviados pelo NHANES. A entrevista segue o Método Automatizado de Múltiplas Passagens do Departamento de Agricultura dos EUA, desenhado para reduzir esquecimentos (MOSHFEGH et al., 2008). Cada item recebeu um código da base FNDDS 2021–2023, que fornece o peso em gramas e a cafeína de cada bebida (USDA, 2024).`),
  p(`A pesquisa é aprovada pelo comitê de ética do NCHS, todos os participantes assinam termo de consentimento, e os arquivos públicos não contêm nomes nem endereços.`),
  h2('8.2  Como os dados foram obtidos e tratados neste trabalho'),
  p(`Em 7 de novembro de 2026 foram baixados do site do NHANES nove arquivos no formato SAS Transport (.xpt): DEMO_L, OCQ_L, SLQ_L, DPQ_L, DR1IFF_L, DR2IFF_L, DR1TOT_L, DR2TOT_L e DRXFCD_L. Os arquivos foram lidos com a biblioteca pandas, em Python, e unidos pelo número do participante. O tratamento seguiu seis passos:`),
  lettered('**Seleção:** aplicação dos filtros da Tabela 1.'),
  lettered(`**Identificação do café:** entre as 5.432 descrições de alimentos do FNDDS, foram consideradas bebidas de café os códigos 92100000 a 92189999 — café coado, espresso, solúvel preparado, latte, cappuccino, café gelado e café pronto em garrafa ou lata, inclusive descafeinado (${H.descafeinado_itens} registros). Ficaram de fora creme para café, bolos e licores com "coffee" no nome e café solúvel em pó ainda não preparado.`),
  lettered('**Conversão em xícaras:** o volume de café de cada dia foi somado e dividido por 240 mL, a xícara-padrão de 8 onças usada pelo USDA. Para bebidas à base de água, 1 grama equivale a cerca de 1 mL. O resultado é a média dos dois dias.'),
  lettered('**Horário:** cada bebida tem o horário em que o consumo começou. Foram definidos manhã (5h00 às 11h59), tarde (12h00 às 17h59) e noite (18h00 às 4h59).'),
  lettered('**Intervalo até o sono:** para cada dia com café, calculou-se a diferença entre o horário habitual de dormir — de dia útil ou de fim de semana, conforme o dia da semana do recordatório — e o horário do último café.'),
  lettered('**Conferência:** nenhuma variável analisada tem valor ausente. As respostas "recusou" e "não sabe" do PHQ-9 foram eliminadas pelo critério de completude.'),
  p(`Nenhum valor foi alterado ou imputado. Os cinco participantes com mais de 4 xícaras por dia foram mantidos — o maior consumo, 8 xícaras em média, corresponde a quem relatou 2,9 litros de café coado distribuídos em cinco momentos do primeiro dia. A seção 13 mostra que retirá-los não muda as conclusões.`));

// 9 ---------------------------------------------------------------------
add(h1('9  ORGANIZAÇÃO DOS DADOS'),
  p(`A planilha que acompanha este relatório (Anexo A) separa os dados brutos das variáveis derivadas, para que cada número possa ser rastreado até a resposta original:`),
  bullet('**Dados brutos:** as 22 variáveis originais do NHANES para os 496 participantes, com os códigos oficiais;'),
  bullet(`**Itens de café:** as ${H.itens} bebidas de café relatadas nos dois recordatórios, uma por linha, com horário, tipo, volume e cafeína;`),
  bullet('**Base:** uma linha por participante; as colunas derivadas (xícaras, período de maior consumo, cafeína, faixas e rótulos) são fórmulas que leem as duas abas anteriores;'),
  bullet('**Frequências, Medidas, Correlação e regressão, Probabilidade e Horário do café:** os resultados deste relatório, todos calculados por fórmula;'),
  bullet('**Leia-me e Dicionário:** fonte, critérios, parâmetros e definição de cada variável.'),
  p(`Nas tabelas de frequência, o denominador é n = ${N}, exceto na Tabela 6, que usa os ${PR.n_A} participantes que tomaram café. Os percentuais podem não somar exatamente 100,0% por arredondamento.`));

// 10 --------------------------------------------------------------------
const frRows = (key, total = N) => {
  const rows = F[key].map((r) => [r.cat, nf(r.n, 0), pc(r.pct)]);
  rows.push(['Total', nf(total, 0), '100,0%']);
  return rows;
};
const SIT = R.por_situacao, FX = R.por_faixa, GD = R.grupos_dias, CD = R.concordancia_dias;
add(h1('10  TABELAS DE FREQUÊNCIA'),
  h2('10.1  Perfil da amostra'),
  table('Perfil dos participantes', ['Característica', 'Frequência (fᵢ)', 'Percentual (frᵢ)'], [
    ['**Gênero**', '', ''], ...F.genero.map((r) => ['   ' + r.cat, nf(r.n, 0), pc(r.pct)]),
    ['**Faixa etária**', '', ''], ...F.faixa_etaria.map((r) => ['   ' + r.cat + ' anos', nf(r.n, 0), pc(r.pct)]),
    ['**Situação na semana anterior**', '', ''], ...F.situacao.map((r) => ['   ' + r.cat, nf(r.n, 0), pc(r.pct)]),
    ['Total', nf(N, 0), '100,0%'],
  ], [4871, 2100, 2100], { totalLast: true }),
  p(`As mulheres são ${pc(fr('genero', 'Feminino').pct)} da amostra, e a faixa de 18 a 21 anos é a maior (${pc(fr('faixa_etaria', '18 a 21').pct)}). A idade média é de ${nf(D.idade.media, 1)} anos. Dois terços (${pc(fr('situacao', 'Trabalhando').pct)}) trabalhavam na semana anterior à entrevista, e ${pc(fr('situacao', 'Estudando').pct)} não trabalhavam porque estudavam. O NHANES não pergunta se quem trabalha também estuda; por isso, o número real de estudantes é maior que ${fr('situacao', 'Estudando').n}.`),
  h2('10.2  Consumo de café nos dois dias'),
  table('Consumo de café nos dois dias de recordatório', ['Dias com café', 'Frequência (fᵢ)', 'Percentual (frᵢ)'], frRows('consumo'), [4871, 2100, 2100], { totalLast: true }),
  p(`Ao todo, ${fr('consumo', 'Nenhum dos dois dias').n} participantes (${pc(fr('consumo', 'Nenhum dos dois dias').pct)}) não tomaram café em nenhum dos dois dias, e ${fr('consumo', 'Os dois dias').n} (${pc(fr('consumo', 'Os dois dias').pct)}) tomaram nos dois. Os dois recordatórios funcionam como teste de hábito: dos ${CD.d1} que tomaram café no primeiro dia, ${CD.d1_e_d2} (${pc(CD.p_d2_dado_d1)}) voltaram a tomar no segundo; entre os ${N - CD.d1} que não tomaram no primeiro, apenas ${pc(CD.p_d2_dado_nao_d1)} tomaram no segundo. O café, nesse grupo, é hábito de uma parcela definida das pessoas, e não um consumo eventual distribuído entre todos.`),
  p(`O consumo cresce com a idade: tomaram café ${pc(FX['18 a 21'].tomou_cafe)} dos participantes de 18 a 21 anos, ${pc(FX['22 a 25'].tomou_cafe)} dos de 22 a 25 e ${pc(FX['26 a 29'].tomou_cafe)} dos de 26 a 29. Também foi maior entre as mulheres (${pc(R.por_genero.Feminino.tomou_cafe)}, contra ${pc(R.por_genero.Masculino.tomou_cafe)} dos homens) e entre quem trabalhava (${pc(SIT.Trabalhando.tomou_cafe)}, contra ${pc(SIT.Estudando.tomou_cafe)} de quem estudava).`),
  h2('10.3  Xícaras de café por dia'),
  table('Xícaras de café por dia (média dos dois dias; xícara de 240 mL)', ['Xícaras por dia', 'Frequência (fᵢ)', 'Percentual (frᵢ)'], frRows('faixa_xicaras'), [4871, 2100, 2100], { totalLast: true }),
  p(`A distribuição é concentrada no zero e longa à direita. Entre os ${PR.n_A} que tomaram café, metade consumiu entre ${nf(D.xicaras_consumidores.q1, 2)} e ${nf(D.xicaras_consumidores.q3, 2)} xícara por dia (primeiro e terceiro quartis), o que equivale a ${nf(D.xicaras_consumidores.q1 * 240, 0)} a ${nf(D.xicaras_consumidores.q3 * 240, 0)} mL. Só ${fr('faixa_xicaras', 'Mais de 3').n} participantes (${pc(fr('faixa_xicaras', 'Mais de 3').pct)}) passaram de 3 xícaras por dia.`),
  h2('10.4  Período de maior consumo'),
  table(`Período de maior consumo de café (somente quem tomou café, n = ${PR.n_A})`, ['Período', 'Frequência (fᵢ)', 'Percentual (frᵢ)'], frRows('periodo', PR.n_A), [4871, 2100, 2100], { totalLast: true }),
  p(`Dos ${PR.n_A} que tomaram café, ${fr('periodo', 'Manhã').n} (${pc(fr('periodo', 'Manhã').pct)}) concentraram o consumo pela manhã e apenas ${fr('periodo', 'Noite').n} (${pc(fr('periodo', 'Noite').pct)}) à noite. Considerando cada uma das ${H.itens} bebidas, ${pc(H.por_periodo_itens['Manhã'] / H.itens)} começaram entre 5h00 e 11h59, e a mediana do horário foi ${nf(Math.floor(H.mediana_horario_itens), 0)}h${String(Math.round((H.mediana_horario_itens % 1) * 60)).padStart(2, '0')}.`),
  h2('10.5  Sono e concentração'),
  table('Horas habituais de sono em dias úteis', ['Horas de sono', 'Frequência (fᵢ)', 'Percentual (frᵢ)'], frRows('sono_util'), [4871, 2100, 2100], { totalLast: true }),
  p(`A média de sono em dias úteis é de ${nf(D.sono_util.media, 2)} horas, e ${PR.n_sono_insuf} participantes (${pc(PR.P_sono_insuf)}) dormem menos de 7 horas, o mínimo recomendado para adultos (WATSON et al., 2015). No fim de semana a média sobe para ${nf(D.sono_fds.media, 2)} horas: ${pc(R.sono_fds_vs_util.pct_mais_1h)} dormem pelo menos uma hora a mais nos dias de folga, sinal de sono acumulado em falta durante a semana (diferença média de ${nf(R.sono_fds_vs_util.media_dif, 2)} h; teste t pareado, p < 0,001).`),
  table('Problemas de sono e dificuldade de concentração nas últimas duas semanas (PHQ-9)', ['Frequência', 'Problemas de sono (item 3)', 'Dificuldade de concentração (item 7)'],
    [...F.prob_sono.map((r, i) => [r.cat, `${r.n} (${pc(r.pct)})`, `${F.dif_conc[i].n} (${pc(F.dif_conc[i].pct)})`]), ['Total', `${N} (100,0%)`, `${N} (100,0%)`]],
    [3271, 2900, 2900], { totalLast: true }),
  p(`Problemas de sono são mais comuns que dificuldade de concentração: ${pc(PR.P_B)} relataram problemas de sono em vários dias ou mais, e ${pc(PR.P_C)} relataram dificuldade de concentração. Em ${pc(fr('prob_sono', 'Quase todos os dias').pct)} dos casos, os problemas de sono ocorreram quase todos os dias.`));

// 11 --------------------------------------------------------------------
const FC = R.fontes_cafeina;
add(h1('11  GRÁFICOS'),
  p('Os gráficos desta seção acompanham as tabelas de frequência. Os gráficos analíticos — box plots, dispersões, probabilidades condicionais e distribuição binomial — aparecem nas seções em que são discutidos.'),
  figure('Perfil dos participantes por gênero, faixa etária e situação na semana anterior', 'g01_perfil.png'),
  figure('Consumo de café nos dois dias de recordatório e proporção que tomou café por faixa etária', 'g02_consumo.png'),
  p(`O gráfico da direita mostra o gradiente etário: a proporção que tomou café dobra entre o grupo de 18 a 21 anos e o de 26 a 29 anos.`),
  figure('Xícaras de café por dia (média dos dois dias)', 'g03_xicaras.png', { widthPx: 520 }),
  figure(`Horário de início das ${H.itens} bebidas de café registradas`, 'g04_horario.png'),
  p(`O pico ocorre entre 8h e 11h, e há uma segunda elevação, menor, logo após o almoço. Após as 18h foram registradas apenas ${H.por_periodo_itens['Noite']} bebidas.`),
  figure('Fontes da cafeína ingerida pelos participantes nos dois dias', 'g12_fontes_cafeina.png', { widthPx: 520 }),
  p(`O café responde por ${pc(FC['Café'])} da cafeína ingerida; refrigerantes (${pc(FC.Refrigerantes)}), chás (${pc(FC['Chás'])}) e energéticos (${pc(FC['Energéticos'])}) somam a maior parte do restante. Medir apenas o café, portanto, deixa de fora cerca de 40% da exposição à cafeína — razão pela qual a cafeína total também foi analisada.`),
  figure('Horas habituais de sono em dias úteis', 'g05_sono_horas.png', { widthPx: 520 }),
  figure('Frequência de problemas de sono e de dificuldade de concentração nas últimas duas semanas', 'g06_phq9.png'));

// 12 --------------------------------------------------------------------
const dx = D.xicaras, dxc = D.xicaras_consumidores;
const mrow = (lab, d, k = 2) => [lab, nf(d.media, k), nf(d.mediana, k), nf(d.moda, k), nf(d.amplitude, k), nf(d.dp, k), nf(d.q1, k), nf(d.q3, k), pc(d.cv, 0)];
add(h1('12  CÁLCULOS ESTATÍSTICOS'),
  p('Foram calculadas as seguintes medidas, com as fórmulas usuais para amostras:'),
  bullet('média: x̄ = Σx ÷ n;'),
  bullet(`mediana: valor central dos dados ordenados; com n = ${N} (par), é a média entre o 248º e o 249º valores;`),
  bullet('moda: valor de maior frequência;'),
  bullet('amplitude: A = valor máximo − valor mínimo;'),
  bullet('variância amostral: s² = Σ(x − x̄)² ÷ (n − 1); desvio padrão: s = √s²;'),
  bullet('quartis Q1 e Q3: valores que deixam 25% e 75% dos dados abaixo, pelo método inclusivo (função QUARTIL do Excel);'),
  bullet('coeficiente de variação: CV = s ÷ x̄, que compara a dispersão de variáveis com unidades diferentes.'),
  table('Medidas de posição e de dispersão', ['Variável', 'Média', 'Mediana', 'Moda', 'Ampl.', 'DP', 'Q1', 'Q3', 'CV'], [
    mrow('Idade (anos)', D.idade, 1),
    mrow('Xícaras/dia — todos', dx, 2),
    mrow(`Xícaras/dia — quem tomou café (n = ${dxc.n})`, dxc, 2),
    mrow('Cafeína total (mg/dia)', D.cafeina, 1),
    mrow('Sono em dias úteis (h)', D.sono_util, 2),
    mrow('Sono no fim de semana (h)', D.sono_fds, 2),
    mrow('Problemas de sono (0 a 3)', D.prob_sono, 2),
    mrow('Dificuldade de concentração (0 a 3)', D.dif_conc, 2),
  ], [2631, 800, 1000, 760, 780, 760, 760, 780, 800], { size: 17, source: SRC + ' DP = desvio padrão amostral; CV = coeficiente de variação.' }),
  h2(`12.1  Demonstração completa: xícaras de café por dia (n = ${N})`),
  eq(`Σx = ${nf(dx.soma, 3)}     x̄ = ${nf(dx.soma, 3)} ÷ ${N} = **${nf(dx.media, 4)} xícara por dia**`),
  eq(`Mediana: o 248º e o 249º valores ordenados são 0 (há ${dx.moda_freq} zeros)  →  **Md = 0**`),
  eq(`Moda: o valor 0 aparece ${dx.moda_freq} vezes  →  **Mo = 0**     Amplitude: A = ${nf(dx.maximo, 3)} − 0 = **${nf(dx.amplitude, 3)}**`),
  eq(`Σ(x − x̄)² = ${nf(dx.sq_desvios, 3)}     s² = ${nf(dx.sq_desvios, 3)} ÷ ${N - 1} = **${nf(dx.variancia, 4)}**     s = √${nf(dx.variancia, 4)} = **${nf(dx.dp, 4)}**`),
  eq(`Q1 = **${nf(dx.q1, 3)}**     Q3 = **${nf(dx.q3, 3)}**     CV = ${nf(dx.dp, 3)} ÷ ${nf(dx.media, 3)} = **${pc(dx.cv, 1)}**`),
  p(`Média e mediana contam histórias diferentes. A média de ${nf(dx.media, 2)} xícara sugere um consumo pequeno e espalhado por todos; a mediana zero mostra que a maioria simplesmente não tomou café. A distribuição é assimétrica à direita (média maior que a mediana, CV de ${pc(dx.cv, 0)}). Por isso, para descrever **quanto bebe quem bebe**, as medidas do grupo que tomou café são mais adequadas: média de ${nf(dxc.media, 2)} xícara (${nf(dxc.media * 240, 0)} mL) e mediana de ${nf(dxc.mediana, 2)} xícara (${nf(dxc.mediana * 240, 0)} mL) por dia.`),
  h2('12.2  Leitura das demais medidas'),
  p(`**Cafeína.** A média de ${nf(D.cafeina.media, 1)} mg por dia é menor que a cafeína de uma xícara de café coado de 240 mL (cerca de 96 mg na base FNDDS) e fica muito abaixo do limite de 400 mg/dia indicado pela FDA para adultos saudáveis (FDA, 2024), ultrapassado por apenas ${R.cafeina_acima_400} participantes (${pc(R.cafeina_acima_400 / N)}).`),
  p(`**Sono.** Mediana e moda de 8 horas, com desvio padrão de ${nf(D.sono_util.dp, 2)} hora. A média esconde extremos: ${fr('sono_util', 'Menos de 6 h').n} pessoas dormem menos de 6 horas, e a amplitude de ${nf(D.sono_util.amplitude, 0)} horas inclui os códigos-limite do NHANES ("menos de 3 h", registrado como 2, e "14 h ou mais", registrado como 14).`),
  p(`**PHQ-9.** A mediana 0 da dificuldade de concentração indica que mais da metade dos participantes não teve o problema nas duas semanas anteriores; a média de ${nf(D.dif_conc.media, 2)} é puxada por ${fr('dif_conc', 'Mais da metade dos dias').n + fr('dif_conc', 'Quase todos os dias').n} pessoas (${pc((fr('dif_conc', 'Mais da metade dos dias').n + fr('dif_conc', 'Quase todos os dias').n) / N)}) com dificuldade em mais da metade dos dias ou quase todos.`),
  figure('Box plots de xícaras por dia (quem tomou café), cafeína total, horas de sono e idade', 'g07_boxplots.png', { source: SRC + ' A caixa vai de Q1 a Q3; o traço vertical é a mediana; o losango, a média.' }));

// 13 --------------------------------------------------------------------
const rrow = (lab, k, interp) => [lab, nf(P[k].r, 3), `${nf(P[k].ci_lo, 3)} a ${nf(P[k].ci_hi, 3)}`, pv(P[k].p), nf(P[k].spearman, 3), interp];
const xc = P.xic_conc;
const RB = R.robustez;
add(h1('13  CORRELAÇÃO E INTERPRETAÇÃO'),
  p(`O coeficiente de correlação de Pearson (r) mede a intensidade da relação linear entre duas variáveis, de −1 a +1. A Tabela 10 reúne os pares analisados, com o intervalo de 95% de confiança, o p-valor do teste t (t = r√(n − 2) ÷ √(1 − r²), com ${N - 2} graus de liberdade) e o coeficiente de Spearman, calculado sobre as posições dos valores.`),
  table(`Correlações entre as variáveis (n = ${N})`, ['Par de variáveis', 'r', 'IC 95%', 'p-valor', 'Spearman', 'Leitura'], [
    rrow('Xícaras × dificuldade de concentração', 'xic_conc', 'nula'),
    rrow('Xícaras × problemas de sono', 'xic_probsono', 'desprezível'),
    rrow('Xícaras × horas de sono (dias úteis)', 'xic_sono', 'nula'),
    rrow('Cafeína × horas de sono (dias úteis)', 'caf_sono', 'nula'),
    rrow('Problemas de sono × dificuldade de concentração', 'probsono_conc', 'moderada, positiva'),
    rrow('Horas de sono × dificuldade de concentração', 'sono_conc', 'nula'),
    rrow('Idade × xícaras', 'idade_xic', 'fraca, positiva'),
  ], [2971, 800, 1500, 850, 1100, 1850], { size: 18, source: SRC + ' Leitura de |r|: < 0,1 nula ou desprezível; 0,1 a 0,3 fraca; 0,3 a 0,5 moderada; > 0,5 forte.' }),
  h2('13.1  Demonstração: xícaras (X) e dificuldade de concentração (Y)'),
  eq('r = [nΣXY − (ΣX)(ΣY)] ÷ √{[nΣX² − (ΣX)²] · [nΣY² − (ΣY)²]}'),
  eq(`n = ${N}   ΣX = ${nf(xc.Sx, 3)}   ΣY = ${nf(xc.Sy, 0)}   ΣX² = ${nf(xc.Sxx, 3)}   ΣY² = ${nf(xc.Syy, 0)}   ΣXY = ${nf(xc.Sxy, 3)}`),
  eq(`Numerador = ${N} × ${nf(xc.Sxy, 3)} − ${nf(xc.Sx, 3)} × ${nf(xc.Sy, 0)} = **${nf(xc.num, 2)}**`),
  eq(`1º termo do denominador = ${N} × ${nf(xc.Sxx, 3)} − ${nf(xc.Sx, 3)}² = **${nf(xc.t1, 2)}**`),
  eq(`2º termo do denominador = ${N} × ${nf(xc.Syy, 0)} − ${nf(xc.Sy, 0)}² = **${nf(xc.t2, 0)}**`),
  eq(`r = ${nf(xc.num, 2)} ÷ √(${nf(xc.t1, 2)} × ${nf(xc.t2, 0)}) = ${nf(xc.num, 2)} ÷ ${nf(xc.den, 2)} = **${nf(xc.r, 4)}**`),
  eq(`t = ${nf(xc.r, 4)} × √${N - 2} ÷ √(1 − ${nf(xc.r, 4)}²) = **${nf(xc.t, 3)}**     p = **${nf(xc.p, 3)}**`),
  figure('Dispersão entre xícaras por dia e dificuldade de concentração, com a reta de regressão', 'g08_disp_conc.png', { source: SRC + ' Pontos deslocados levemente na vertical (e, no zero, na horizontal) para evitar sobreposição.' }),
  figure('Dispersão entre xícaras por dia e horas de sono em dias úteis, com a reta de regressão', 'g09_disp_sono.png'),
  h2('13.2  Interpretação'),
  p(`**A quantidade de café não acompanha a concentração.** O coeficiente de ${nf(xc.r, 3)} é indistinguível de zero (p = ${pv(xc.p)}), e o intervalo de confiança vai de ${nf(xc.ci_lo, 2)} a ${nf(xc.ci_hi, 2)}: mesmo no limite mais favorável, a quantidade de café explicaria menos de 1% da variação da dificuldade de concentração. O Gráfico 9 mostra o mesmo de forma visual: em todos os níveis de dificuldade há pessoas que não tomam café e pessoas que tomam duas ou três xícaras. Não se rejeita H₀.`),
  p(`**Com o sono, a relação é desprezível e tem o sinal oposto ao esperado.** Com os problemas de sono, r = ${nf(P.xic_probsono.r, 3)} fica no limite da significância (p = ${pv(P.xic_probsono.p)}), mas explica ${pc(P.xic_probsono.r2)} da variação e, considerando o efeito do desenho amostral (seção 6.1), não deve ser tratado como achado firme. Com as horas de sono, r = ${nf(P.xic_sono.r, 3)} não é significativo, e o mesmo vale para a cafeína total (r = ${nf(P.caf_sono.r, 3)}). Uma explicação possível para o sinal negativo é a causalidade reversa: quem dorme mal pode evitar o café, e não o contrário. Dados transversais não permitem separar essas hipóteses.`),
  p(`**O que acompanha a concentração é o sono.** Entre todos os pares testados, o único com correlação moderada é problemas de sono × dificuldade de concentração (r = ${nf(P.probsono_conc.r, 3)}; p < 0,001; Spearman ${nf(P.probsono_conc.spearman, 3)}). Como as duas perguntas vêm do mesmo questionário de saúde mental, parte dessa associação reflete um mal-estar geral que afeta ambas; ainda assim, é a relação mais forte da base. Curiosamente, a **duração** do sono não acompanha a concentração (r = ${nf(P.sono_conc.r, 3)}): o que pesa é a **qualidade** relatada, e não as horas na cama.`),
  p(`**Robustez.** Retirando os ${RB.n_excluidos} participantes com mais de 4 xícaras por dia, a correlação entre xícaras e concentração passa a ${nf(RB.xic_conc_r, 3)}; considerando só os ${RB.consumidores_n} que tomaram café, fica em ${nf(RB.consumidores_xic_conc_r, 3)}. Nenhuma versão se aproxima de uma associação relevante.`),
  p(`**Correlação não é causalidade.** Além da causalidade reversa, outros fatores atuam ao mesmo tempo sobre café, sono e concentração: idade (que se correlaciona com o consumo, r = ${nf(P.idade_xic.r, 3)}), jornada de trabalho, saúde mental e tolerância à cafeína em consumidores habituais (JAMES; ROGERS, 2005).`));

// 14 --------------------------------------------------------------------
const m2 = P.probsono_conc;
const G2 = R.grupos_probsono;
add(h1('14  REGRESSÃO LINEAR SIMPLES'),
  p('A reta de regressão Ŷ = a + bX estima o valor médio de Y para cada valor de X, com b = [nΣXY − (ΣX)(ΣY)] ÷ [nΣX² − (ΣX)²] e a = Ȳ − b·X̄. Foram ajustados dois modelos com a mesma variável dependente, a dificuldade de concentração (0 a 3).'),
  h2('14.1  Modelo 1: dificuldade de concentração explicada pelas xícaras de café'),
  eq(`b = ${nf(xc.num, 2)} ÷ ${nf(xc.t1, 2)} = **${nf(xc.b, 4)}**     a = ${nf(xc.ybar, 4)} − (${nf(xc.b, 4)} × ${nf(xc.xbar, 4)}) = **${nf(xc.a, 4)}**`),
  eq(`**Ŷ = ${nf(xc.a, 4)} − ${nf(Math.abs(xc.b), 4)}X**     R² = ${nf(xc.r2, 5)} (${pc(xc.r2, 2)})`),
  p(`Cada xícara adicional altera a dificuldade de concentração estimada em ${nf(xc.b, 3)} ponto numa escala de 0 a 3 — na prática, nada. O erro padrão de b é ${nf(xc.se_b, 3)}, e o intervalo de 95% de confiança, de ${nf(xc.b_lo, 3)} a ${nf(xc.b_hi, 3)}, contém o zero. Para X = 0, Ŷ = ${nf(xc.a, 3)}; para X = 2 xícaras, Ŷ = ${nf(xc.a + 2 * xc.b, 3)}. A reta é praticamente horizontal, e o modelo explica ${pc(xc.r2, 2)} da variação da concentração.`),
  h2('14.2  Modelo 2: dificuldade de concentração explicada pelos problemas de sono'),
  eq(`b = ${nf(m2.num, 0)} ÷ ${nf(m2.t1, 0)} = **${nf(m2.b, 4)}**     a = ${nf(m2.ybar, 4)} − (${nf(m2.b, 4)} × ${nf(m2.xbar, 4)}) = **${nf(m2.a, 4)}**`),
  eq(`**Ŷ = ${nf(m2.a, 4)} + ${nf(m2.b, 4)}X**     R² = ${nf(m2.r2, 4)} (${pc(m2.r2, 1)})`),
  table('Valores estimados pelo modelo 2 e médias observadas', ['Problemas de sono (X)', 'n', 'Ŷ estimado', 'Média observada'],
    G2.map((g) => [['0 · nenhum dia', '1 · vários dias', '2 · mais da metade dos dias', '3 · quase todos os dias'][g.x], nf(g.n, 0), nf(m2.a + m2.b * g.x, 3), nf(g.conc, 3)]),
    [3871, 1400, 1900, 1900]),
  p(`Quem não relata problemas de sono tem dificuldade de concentração estimada em ${nf(m2.a, 2)}; quem tem problemas quase todos os dias, em ${nf(m2.a + 3 * m2.b, 2)} — perto das médias observadas, ${nf(G2[0].conc, 2)} e ${nf(G2[3].conc, 2)}. A inclinação tem intervalo de confiança de ${nf(m2.b_lo, 3)} a ${nf(m2.b_hi, 3)} e o modelo explica ${pc(m2.r2, 1)} da variação: muito mais que o café, mas longe de explicar o fenômeno sozinho.`),
  h2('14.3  Limites dos modelos'),
  p('Os dois modelos tratam uma escala ordinal de quatro pontos como numérica, não controlam outras variáveis e só valem dentro da faixa observada (0 a 8 xícaras no modelo 1; 0 a 3 no modelo 2). Servem para descrever a tendência média do grupo, e não para prever a concentração de uma pessoa nem para provar efeito causal.'));

// 15 --------------------------------------------------------------------
const AC = PR.A_C, BC = PR.B_C, AB = PR.A_B;
add(h1('15  PROBABILIDADE SIMPLES'),
  p(`Considere o experimento de sortear ao acaso um dos ${N} participantes, todos com a mesma chance. A probabilidade de um evento é o número de casos favoráveis dividido pelo total de casos.`),
  bullet(`**A** — tomou café em ao menos um dos dois dias: P(A) = ${PR.n_A} ÷ ${N} = **${nf(PR.P_A, 4)}** (${pc(PR.P_A)})`),
  bullet(`**B** — problemas de sono em vários dias ou mais: P(B) = ${PR.n_B} ÷ ${N} = **${nf(PR.P_B, 4)}** (${pc(PR.P_B)})`),
  bullet(`**C** — dificuldade de concentração em vários dias ou mais: P(C) = ${PR.n_C} ÷ ${N} = **${nf(PR.P_C, 4)}** (${pc(PR.P_C)})`),
  bullet(`**D** — dorme menos de 7 horas em dias úteis: P(D) = ${PR.n_sono_insuf} ÷ ${N} = **${nf(PR.P_sono_insuf, 4)}** (${pc(PR.P_sono_insuf)})`),
  h2('15.1  Probabilidade condicional e independência'),
  p('Com dados reais e completos, é possível ir além da probabilidade simples e perguntar se saber algo sobre a pessoa muda a chance de outro evento. As Tabelas 12 e 13 cruzam os eventos.'),
  table('Consumo de café (A) e dificuldade de concentração (C)', ['', 'C: sim', 'C: não', 'Total'], [
    ['Tomou café (A)', AC.a, AC.b, AC.a + AC.b], ['Não tomou café (Ā)', AC.c, AC.d, AC.c + AC.d],
    ['Total', AC.a + AC.c, AC.b + AC.d, N]].map((r) => r.map((v, i) => (i ? nf(v, 0) : v))), [3571, 1800, 1800, 1900], { totalLast: true }),
  eq(`P(C | A) = ${AC.a} ÷ ${AC.a + AC.b} = **${nf(AC.p_e2_dado_e1, 4)}**     P(C | Ā) = ${AC.c} ÷ ${AC.c + AC.d} = **${nf(AC.p_e2_dado_nao_e1, 4)}**`),
  eq(`P(A ∩ C) = ${AC.a} ÷ ${N} = **${nf(AC.p_e1_e_e2, 4)}**     P(A) × P(C) = ${nf(PR.P_A, 4)} × ${nf(PR.P_C, 4)} = **${nf(PR.P_A * PR.P_C, 4)}**`),
  p(`Como P(A ∩ C) é praticamente igual a P(A) × P(C), **os eventos se comportam como independentes**: saber que alguém tomou café não altera a chance de essa pessoa ter dificuldade de concentração — ${pc(AC.p_e2_dado_e1)} contra ${pc(AC.p_e2_dado_nao_e1)}. O teste qui-quadrado confirma (χ² = ${nf(AC.chi2, 3)}; p = ${pv(AC.p)}).`),
  table('Problemas de sono (B) e dificuldade de concentração (C)', ['', 'C: sim', 'C: não', 'Total'], [
    ['Problemas de sono (B)', BC.a, BC.b, BC.a + BC.b], ['Sem problemas de sono (B̄)', BC.c, BC.d, BC.c + BC.d],
    ['Total', BC.a + BC.c, BC.b + BC.d, N]].map((r) => r.map((v, i) => (i ? nf(v, 0) : v))), [3571, 1800, 1800, 1900], { totalLast: true }),
  eq(`P(C | B) = ${BC.a} ÷ ${BC.a + BC.b} = **${nf(BC.p_e2_dado_e1, 4)}**     P(C | B̄) = ${BC.c} ÷ ${BC.c + BC.d} = **${nf(BC.p_e2_dado_nao_e1, 4)}**`),
  p(`Aqui a condição muda muito a probabilidade: entre quem tem problemas de sono, a chance de dificuldade de concentração é **${nf(BC.p_e2_dado_e1 / BC.p_e2_dado_nao_e1, 2)} vezes** a de quem não tem (${pc(BC.p_e2_dado_e1)} contra ${pc(BC.p_e2_dado_nao_e1)}; χ² = ${nf(BC.chi2, 2)}; p < 0,001). O Gráfico 11 mostra que a proporção cresce a cada nível de problema de sono: ${R.grupos_probsono.map((g) => pc(g.conc_prej)).join(', ').replace(/, ([^,]*)$/, ' e $1')}.`),
  p(`O mesmo cruzamento entre café e problemas de sono reforça o resultado da seção 13: P(B | A) = ${pc(AB.p_e2_dado_e1)} e P(B | Ā) = ${pc(AB.p_e2_dado_nao_e1)} (χ² = ${nf(AB.chi2, 2)}; p = ${pv(AB.p)}).`),
  figure('Proporção com dificuldade de concentração segundo o consumo de café e a frequência de problemas de sono', 'g10_condicional.png'));

// 16 --------------------------------------------------------------------
const BI = R.binomial, pB = BI.p, qB = 1 - pB;
let acc = 0;
add(h1('16  DISTRIBUIÇÃO BINOMIAL'),
  p(`Considere sortear 5 participantes de forma independente e contar quantos tomaram café (sucesso). Cada sorteio tem dois resultados possíveis, a probabilidade de sucesso é constante, p = P(A) = ${nf(pB, 4)}, e q = 1 − p = ${nf(qB, 4)}. O número X de sucessos segue a distribuição binomial com n = 5 e p = ${nf(pB, 4)}:`),
  eq('P(X = k) = C(n, k) · pᵏ · qⁿ⁻ᵏ,   com C(n, k) = n! ÷ [k! (n − k)!]'),
  pn('**Exemplo 1 — exatamente dois tomaram café:**', { keepNext: true }),
  eq(`P(X = 2) = C(5, 2) × ${nf(pB, 4)}² × ${nf(qB, 4)}³ = 10 × ${nf(pB ** 2, 5)} × ${nf(qB ** 3, 5)} = **${nf(BI.pk[2], 4)}** (${pc(BI.pk[2], 2)})`),
  pn('**Exemplo 2 — nenhum tomou café:**', { keepNext: true }),
  eq(`P(X = 0) = ${nf(qB, 4)}⁵ = **${nf(BI.pk[0], 4)}** (${pc(BI.pk[0], 2)})`),
  pn('**Exemplo 3 — pelo menos um tomou café (evento complementar):**', { keepNext: true }),
  eq(`P(X ≥ 1) = 1 − P(X = 0) = 1 − ${nf(BI.pk[0], 4)} = **${nf(1 - BI.pk[0], 4)}** (${pc(1 - BI.pk[0], 2)})`),
  table('Distribuição binomial com n = 5 e p = ' + nf(pB, 4), ['k (quantos tomaram café)', 'C(5, k)', 'P(X = k)', 'P(X ≤ k)'],
    BI.pk.map((v, k) => { acc += v; return [String(k), String([1, 5, 10, 10, 5, 1][k]), pc(v, 2), pc(acc, 2)]; }),
    [3271, 1600, 2100, 2100]),
  p(`O resultado mais provável é X = 2 (${pc(BI.pk[2], 2)}), coerente com o valor esperado E(X) = n·p = 5 × ${nf(pB, 4)} = ${nf(5 * pB, 2)}. Em cerca de 9 de cada 100 grupos de cinco jovens sorteados, ninguém teria tomado café; em ${pc(BI.pk[3] + BI.pk[4] + BI.pk[5], 1)}, três ou mais teriam. A independência entre os sorteios é razoável em uma população grande, mas não valeria para um grupo de amigos ou colegas de turma, que costumam compartilhar hábitos.`),
  figure('Distribuição binomial do número de jovens que tomaram café em grupos de 5', 'g11_binomial.png', { widthPx: 520 }));

// 17 --------------------------------------------------------------------
const IV = R.intervalo;
add(h1('17  ANÁLISE DOS RESULTADOS'),
  h2('17.1  Síntese dos achados'),
  lettered(`**O café é hábito de uma parte dos jovens e cresce com a idade.** ${pc(PR.P_A)} tomaram café em ao menos um dos dois dias e ${pc(PR.P_A2)} nos dois; a proporção vai de ${pc(FX['18 a 21'].tomou_cafe)} aos 18–21 anos a ${pc(FX['26 a 29'].tomou_cafe)} aos 26–29.`),
  lettered(`**O consumo é moderado e matinal.** Quem toma café consome em média ${nf(dxc.media, 2)} xícara de 240 mL por dia; ${pc(fr('periodo', 'Manhã').pct)} concentram o consumo pela manhã, e só ${pc(R.cafeina_acima_400 / N)} passam de 400 mg de cafeína.`),
  lettered(`**Ainda assim, uma parcela toma café tarde demais.** ${IV.pessoas_menor_88} dos ${IV.pessoas} que tomaram café (${pc(IV.pessoas_menor_88 / IV.pessoas)}) o fizeram a menos de 8,8 horas do horário habitual de dormir, e ${IV.pessoas_menor_6} (${pc(IV.pessoas_menor_6 / IV.pessoas)}) a menos de 6 horas. A mediana do menor intervalo entre o último café e o sono foi de ${nf(IV.mediana_pessoa, 0)} horas.`),
  lettered(`**A quantidade de café não se associa à concentração.** r = ${nf(xc.r, 3)}; R² = ${pc(xc.r2, 2)}; P(C | A) = ${pc(AC.p_e2_dado_e1)} e P(C | Ā) = ${pc(AC.p_e2_dado_nao_e1)}.`),
  lettered(`**Os problemas de sono, sim.** r = ${nf(P.probsono_conc.r, 3)}; R² = ${pc(P.probsono_conc.r2)}; P(C | B) = ${pc(BC.p_e2_dado_e1)} contra P(C | B̄) = ${pc(BC.p_e2_dado_nao_e1)}.`),
  lettered(`**A duração do sono é adequada na média, mas não para todos.** Média de ${nf(D.sono_util.media, 2)} h em dias úteis; ${pc(PR.P_sono_insuf)} dormem menos de 7 h e ${pc(R.sono_fds_vs_util.pct_mais_1h)} dormem ao menos uma hora a mais no fim de semana.`),
  h2('17.2  Discussão'),
  p(`A ausência de relação entre a quantidade de café e a concentração é coerente com a literatura. Os ganhos de atenção atribuídos à cafeína aparecem principalmente em doses agudas e em pessoas privadas de sono (IRWIN et al., 2020); em consumidores habituais, boa parte do efeito percebido corresponde à reversão da abstinência, e não a um ganho acima do estado normal (JAMES; ROGERS, 2005). Um estudo que mede o consumo de dois dias e a concentração das duas semanas anteriores capta o hábito, não o efeito da xícara tomada antes da prova — e, no hábito, os consumidores não se diferenciam dos não consumidores.`),
  p(`O efeito negativo do café sobre o sono, bem documentado em estudos experimentais (GARDINER et al., 2023), também não apareceu. Os dados oferecem uma explicação: a maior parte do café foi tomada cedo, com mediana de ${nf(IV.mediana_pessoa, 0)} horas entre o último café e a hora de dormir. Para a maioria desses jovens, a cafeína já foi metabolizada quando eles se deitam. O grupo que toma café no período crítico é pequeno (${IV.pessoas_menor_88} pessoas) para comparações confiáveis.`),
  p(`O achado mais robusto não fazia parte da hipótese inicial: a dificuldade de concentração acompanha a qualidade do sono, de forma gradual, e não a sua duração nem o consumo de café. Para o tema da produtividade acadêmica, isso desloca a atenção da xícara para a noite de sono.`),
  h2('17.3  Limitações'),
  lettered('**Medida de concentração.** O item 7 do PHQ-9 mede a frequência de uma dificuldade nas duas semanas anteriores, e não desempenho. O NHANES não tem notas, frequência às aulas nem tempo de estudo.'),
  lettered('**Itens do mesmo questionário.** Sono e concentração vêm do PHQ-9, que rastreia depressão; parte da correlação entre eles reflete o humor, e não apenas o sono.'),
  lettered('**Consumo de dois dias.** Dois recordatórios aproximam o hábito, mas não o medem exatamente; o horário de dormir usado no cálculo do intervalo é o habitual, e não o daquela noite.'),
  lettered('**Desenho transversal.** Todas as medidas foram tomadas no mesmo período; não é possível saber o que veio antes.'),
  lettered('**População.** Os participantes vivem nos Estados Unidos, onde o café é menos difundido entre jovens do que no Brasil.'),
  lettered('**Ponderação.** As estatísticas não usam os pesos amostrais; a comparação da seção 6.1 indica que isso pouco altera os percentuais, mas os p-valores ignoram o efeito do desenho por conglomerados.'));

// 18 --------------------------------------------------------------------
add(h1('18  CONCLUSÃO'),
  p(`Respondendo ao problema de pesquisa: entre os ${N} adultos de 18 a 29 anos analisados, **a quantidade de café consumida por dia não está associada à dificuldade de concentração** (r = ${nf(xc.r, 3)}; p = ${pv(xc.p)}) **nem à duração do sono** (r = ${nf(P.xic_sono.r, 3)}; p = ${pv(P.xic_sono.p)}), e tem associação negativa desprezível com os problemas de sono (r = ${nf(P.xic_probsono.r, 3)}). As hipóteses nulas não foram rejeitadas para concentração e horas de sono.`),
  p(`O resultado mais consistente do estudo não envolve o café: a dificuldade de concentração atinge ${pc(R.grupos_probsono[0].conc_prej)} de quem não relata problemas de sono e ${pc(R.grupos_probsono[3].conc_prej)} de quem os tem quase todos os dias. O café, nesse grupo, é um hábito matinal de ${pc(PR.P_A, 0)} dos jovens, moderado na quantidade e crescente com a idade.`),
  p('Os microdados reais permitiram o que uma base simulada não permite: testar hipóteses com p-valores e intervalos de confiança, medir o horário de cada bebida, cruzar o consumo com a hora de dormir e refazer a análise sem os casos extremos para confirmar que a conclusão não dependia deles.'));

// 19 --------------------------------------------------------------------
add(h1('19  TOMADA DE DECISÃO'),
  h2('19.1  Decisão'),
  p('**Não recomendar o aumento nem a redução do consumo de café como estratégia de produtividade acadêmica.** Os dados não dão base para nenhuma das duas orientações. A recomendação é tratar o sono como a variável prioritária e controlar apenas o horário da cafeína.'),
  h2('19.2  Ações recomendadas'),
  lettered('**Para os estudantes:** manter horários regulares de sono durante a semana, reduzindo a compensação no fim de semana; quando houver café, mantê-lo no período da manhã e evitá-lo nas 8,8 horas anteriores ao horário de dormir — para quem dorme às 23h, nada de café depois das 14h; procurar orientação quando os problemas de sono ocorrerem em mais da metade dos dias.'),
  lettered('**Para a coordenação do curso:** incluir orientações sobre sono nas ações de acolhimento e nos períodos de avaliação, em vez de campanhas sobre consumo de café, que os dados não justificam.'),
  lettered('**Para o grupo e a disciplina:** repetir o estudo com estudantes da Fatec, usando o mesmo método de registro do café em dois dias com horário, o Índice de Qualidade do Sono de Pittsburgh (PSQI) e, com autorização, as notas do semestre. A amostra deve ser aleatória e estratificada por curso e turno.'),
  h2('19.3  Tamanho da amostra para o estudo na Fatec'),
  p('Para estimar uma proporção com margem de erro de 5 pontos percentuais e 95% de confiança, sem informação prévia sobre a proporção (p = 0,5):'),
  eq('n₀ = z² · p · (1 − p) ÷ E² = 1,96² × 0,5 × 0,5 ÷ 0,05² = 384,2  →  **385 estudantes**'),
  p('Se o número total de alunos (N) for conhecido, aplica-se a correção para população finita, n = n₀ ÷ [1 + (n₀ − 1) ÷ N]; para 1.000 alunos, por exemplo, bastariam 278 respondentes.'),
  h2('19.4  Quando rever a decisão'),
  p(`A decisão deve ser revista se o estudo com estudantes da Fatec encontrar correlação entre consumo de café e concentração acima de 0,3, ou consumo noturno de café muito acima dos ${pc(fr('periodo', 'Noite').pct)} observados aqui, situação em que o horário da cafeína passaria a ser um problema coletivo, e não individual.`));

// 20 --------------------------------------------------------------------
const ref = (t) => new Paragraph({ alignment: AlignmentType.LEFT, spacing: { line: 240, before: 0, after: 240 }, children: runs(t) });
add(h1('20  REFERÊNCIAS', { newPage: true }),
  ref('ABDULLAH, A.; RAHMAN, M. S. **Student insomnia and educational outcomes dataset.** Mendeley Data, v. 3, 2025. DOI: 10.17632/5mvrx4v62z.3. Base avaliada e não utilizada (ver seção 2.1).'),
  ref('ANTHROPIC. **Claude.** Assistente de inteligência artificial usado no apoio ao processamento dos microdados, à conferência dos cálculos e à revisão do texto. 2026.'),
  ref('CENTERS FOR DISEASE CONTROL AND PREVENTION. National Center for Health Statistics. **National Health and Nutrition Examination Survey: August 2021–August 2023 data documentation, codebook, and frequencies.** Hyattsville: NCHS, 2024. Disponível em: https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?Cycle=2021-2023. Acesso em: 7 nov. 2026.'),
  ref('GARCIA, M. **Projeto estatístico aplicado: da coleta à tomada de decisão.** Presidente Prudente: Fatec, 2026. Material de orientação da disciplina de Estatística Aplicada.'),
  ref('GARDINER, C. et al. The effect of caffeine on subsequent sleep: a systematic review and meta-analysis. **Sleep Medicine Reviews**, v. 69, art. 101764, 2023. DOI: 10.1016/j.smrv.2023.101764.'),
  ref('IBGE. **Pesquisa de orçamentos familiares 2017-2018: análise do consumo alimentar pessoal no Brasil.** Rio de Janeiro: IBGE, 2020.'),
  ref('IRWIN, C. et al. Effects of acute caffeine consumption following sleep loss on cognitive, physical, occupational and driving performance: a systematic review and meta-analysis. **Neuroscience & Biobehavioral Reviews**, v. 108, p. 877-888, 2020.'),
  ref('JAMES, J. E.; ROGERS, P. J. Effects of caffeine on performance and mood: withdrawal reversal is the most plausible explanation. **Psychopharmacology**, v. 182, n. 1, p. 1-8, 2005.'),
  ref('KROENKE, K.; SPITZER, R. L.; WILLIAMS, J. B. W. The PHQ-9: validity of a brief depression severity measure. **Journal of General Internal Medicine**, v. 16, n. 9, p. 606-613, 2001.'),
  ref('MOSHFEGH, A. J. et al. The US Department of Agriculture Automated Multiple-Pass Method reduces bias in the collection of energy intakes. **The American Journal of Clinical Nutrition**, v. 88, n. 2, p. 324-332, 2008.'),
  ref('ROENNEBERG, T.; WIRZ-JUSTICE, A.; MERROW, M. Life between clocks: daily temporal patterns of human chronotypes. **Journal of Biological Rhythms**, v. 18, n. 1, p. 80-90, 2003.'),
  ref('TERRY, A. L. et al. Plan and operations of the National Health and Nutrition Examination Survey, August 2021–August 2023. **Vital and Health Statistics**, Hyattsville, ser. 1, n. 66, 2024.'),
  ref('U.S. DEPARTMENT OF AGRICULTURE. Agricultural Research Service. **Food and Nutrient Database for Dietary Studies 2021-2023.** Beltsville: USDA, 2024.'),
  ref('U.S. FOOD AND DRUG ADMINISTRATION. **Spilling the beans: how much caffeine is too much?** Silver Spring: FDA, [2024?]. Disponível em: https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much. Acesso em: 7 nov. 2026.'),
  ref('WATSON, N. F. et al. Recommended amount of sleep for a healthy adult: a joint consensus statement of the American Academy of Sleep Medicine and Sleep Research Society. **Sleep**, v. 38, n. 6, p. 843-844, 2015.'));

// 21 --------------------------------------------------------------------
add(h1('21  ANEXOS'),
  pn('**Anexo A — Planilha de dados e cálculos.** Arquivo Base_Real_Cafe_NHANES_496.xlsx, com as abas Leia-me, Resumo, Base, Frequências, Medidas, Correlação e regressão, Probabilidade, Horário do café, Dados brutos, Itens de café e Dicionário, descritas na seção 9.', { align: AlignmentType.LEFT }),
  pn('**Anexo B — Arquivos do NHANES utilizados.** Todos disponíveis em https://wwwn.cdc.gov/nchs/nhanes, ciclo August 2021–August 2023.', { align: AlignmentType.LEFT }),
  table('Arquivos do NHANES ago./2021–ago./2023 utilizados', ['Arquivo', 'Conteúdo', 'Variáveis usadas'], [
    ['DEMO_L', 'Demografia e pesos amostrais', 'SEQN, RIAGENDR, RIDAGEYR, SDMVSTRA, SDMVPSU'],
    ['OCQ_L', 'Ocupação', 'OCD150, OCQ383'],
    ['SLQ_L', 'Sono (horários habituais)', 'SLQ300, SLQ310, SLD012, SLQ320, SLQ330, SLD013'],
    ['DPQ_L', 'Questionário PHQ-9', 'DPQ030, DPQ070'],
    ['DR1IFF_L, DR2IFF_L', 'Itens dos recordatórios de 24 h (dias 1 e 2)', 'código do alimento, gramas, horário, cafeína'],
    ['DR1TOT_L, DR2TOT_L', 'Totais diários dos recordatórios', 'DR1DRSTZ, DR2DRSTZ, DR1TCAFF, DR2TCAFF, WTDR2D'],
    ['DRXFCD_L', 'Descrição dos códigos de alimentos', 'DRXFDCD, DRXFCLD'],
  ], [2271, 3300, 3500], { size: 18, align: [AlignmentType.LEFT, AlignmentType.LEFT, AlignmentType.LEFT] }),
  pn('**Anexo C — Roteiro de reprodução.** Os scripts em Python que leem os arquivos .xpt, constroem a base, calculam as estatísticas e geram os gráficos acompanham o trabalho na pasta scripts. Executados na ordem build_dataset.py, build_xlsx.py e build_charts.py, reproduzem todos os números deste relatório.', { align: AlignmentType.LEFT }),
  pn('**Anexo D — Apresentação.** Arquivo apresentacao-cafe.html, com os mesmos resultados em formato de slides para a apresentação oral.', { align: AlignmentType.LEFT }));

// ------------------------------------------------------------------ documento
const doc = new Document({
  creator: 'Bruna Lais Amorin; Kaike Taylor Antonio Santos; Lucas Gustavo Mendes; Rafael Gervazoni Bezerra',
  title: 'Consumo de café e produtividade acadêmica — NHANES 2021–2023',
  description: 'Projeto estatístico de Estatística Aplicada, Fatec Presidente Prudente, 2026',
  styles: {
    default: { document: { run: { font: FONT, size: 24, color: INK }, paragraph: { spacing: BODY } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: 24, bold: true, color: '000000' },
        paragraph: { spacing: { before: 480, after: 240, line: 360 }, keepNext: true, keepLines: true, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: 24, bold: true, color: '000000' },
        paragraph: { spacing: { before: 280, after: 120, line: 360 }, keepNext: true, keepLines: true, outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [
      { reference: 'bul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 709, hanging: 283 } } } }] },
      { reference: 'alpha', levels: [{ level: 0, format: LevelFormat.LOWER_LETTER, text: '%1)', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 709, hanging: 360 } } } }] },
    ],
  },
  sections: [{
    properties: {
      titlePage: true,
      page: { size: { width: 11906, height: 16838 }, margin: { top: 1701, left: 1701, bottom: 1134, right: 1134, header: 567, footer: 567 } },
    },
    headers: { default: header(), first: header() },
    footers: { default: footer, first: emptyFooter },
    children: C,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(DEST, buf);
  console.log('saved', DEST, 'tabelas:', tabN, 'graficos:', grafN);
});
