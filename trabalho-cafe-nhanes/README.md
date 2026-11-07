# Consumo de café e produtividade acadêmica — dados reais

Projeto de Estatística Aplicada (ADS, Fatec Presidente Prudente, 2026) refeito com microdados públicos do
**NHANES ago./2021–ago./2023** (CDC/NCHS, EUA), no lugar da base simulada.

## Arquivos

| Arquivo | O que é |
|---|---|
| `Trabalho_Cafe_Dados_Reais_NHANES.docx` | Relatório completo (21 seções, 15 tabelas, 12 gráficos, ABNT) |
| `Base_Real_Cafe_NHANES_496.xlsx` | Planilha: dados brutos do NHANES, base derivada por fórmulas e todos os cálculos |
| `apresentacao-cafe.html` | Apresentação (38 slides). Abra no navegador: ← → navegam, N mostra as notas, T troca o tema |

## Amostra

11.933 participantes do NHANES → 1.248 com 18 a 29 anos → 819 com os itens de sono e concentração do PHQ-9
→ 816 com horas de sono calculáveis → **496 com dois recordatórios alimentares de 24 h válidos**.

## Principais resultados

- 38,3% tomaram café em ao menos um dos dois dias; 80,0% deles concentram o consumo pela manhã.
- Xícaras por dia × dificuldade de concentração: r = −0,012 (p = 0,79), associação nula.
- Problemas de sono × dificuldade de concentração: r = 0,392 (p < 0,001); 54,2% contra 25,0%.

## Reproduzir

```bash
cd reproducao
./baixar_nhanes.sh   # baixa os 9 arquivos .xpt oficiais (~150 MB) para raw/
./gerar_tudo.sh      # refaz base, estatísticas, planilha, gráficos, relatório e apresentação em out/
```

Requisitos: Python 3 com `pandas`, `numpy`, `scipy`, `openpyxl` e `matplotlib`; Node.js com o pacote `docx`.
`out/` já traz a base analítica (`base_analitica.csv`), as bebidas de café (`itens_cafe.csv`), as variáveis
originais (`dados_brutos.csv`), todos os resultados (`results.json`) e os gráficos do relatório.
