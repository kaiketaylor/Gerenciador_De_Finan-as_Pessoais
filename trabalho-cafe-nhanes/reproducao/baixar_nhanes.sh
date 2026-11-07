#!/bin/bash
# Baixa os 9 arquivos oficiais do NHANES ago./2021–ago./2023 usados no trabalho (≈ 150 MB).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p raw
BASE="https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles"
for f in DEMO_L OCQ_L SLQ_L DPQ_L DR1IFF_L DR2IFF_L DR1TOT_L DR2TOT_L DRXFCD_L; do
  echo "baixando $f.xpt"
  curl -fsSL -o "raw/$f.xpt" "$BASE/$f.xpt"
done
echo "ok: arquivos em $(pwd)/raw"
