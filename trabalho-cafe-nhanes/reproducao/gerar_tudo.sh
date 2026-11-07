#!/bin/bash
# Refaz base, estatísticas, planilha, gráficos, relatório e apresentação a partir dos arquivos .xpt.
# Requisitos: Python 3 com pandas, numpy, scipy, openpyxl e matplotlib; Node.js com o pacote "docx".
# A planilha sai com fórmulas e é recalculada automaticamente ao ser aberta no Excel ou no LibreOffice.
set -euo pipefail
cd "$(dirname "$0")"
[ -f raw/DEMO_L.xpt ] || ./baixar_nhanes.sh
python3 scripts/build_dataset.py > /dev/null      # out/base_analitica.csv, itens_cafe.csv, dados_brutos.csv, results.json
python3 scripts/build_xlsx.py                     # out/Base_Real_Cafe_NHANES_496.xlsx (fórmulas)
python3 scripts/build_charts.py                   # out/graficos/*.png
node scripts/build_docx.js out/toc_pages.json     # out/Trabalho_Cafe_Dados_Reais_NHANES.docx
python3 scripts/fix_docx_ids.py out/Trabalho_Cafe_Dados_Reais_NHANES.docx
python3 scripts/build_html.py                     # out/apresentacao-cafe.html
echo "pronto: arquivos em $(pwd)/out"
