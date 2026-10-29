#!/usr/bin/env bash
# Fetch the BC Data Catalogue layers used by the KFC prototype.
#
# Run from the repository root with the Python environment active:
#   . .venv/bin/activate
#   ./analysis/fetch_bcdc.sh
#
# The fuel-type provincial FGDB is fetched separately by
# analysis/fetch_fuel_fgdb.py because it is 2.48 GB.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
bbox="1159610,457489,1556647,890472"

python -m femic data bcdc-fetch \
  WHSE_LEGAL_ADMIN_BOUNDARIES.DRP_MOF_FIRE_CENTRES_SP \
  --bbox "$bbox" --output-format geojson \
  --download-root data/raw/bcdc \
  --manifest-path data/raw/bcdc/fire_centres_manifest.json

python -m femic data bcdc-fetch \
  WHSE_FOREST_VEGETATION.BEC_BIOGEOCLIMATIC_POLY \
  --bbox "$bbox" --output-format gpkg \
  --download-root data/raw/bcdc \
  --manifest-path data/raw/bcdc/bec_kfc_manifest.json

python -m femic data bcdc-fetch \
  WHSE_LAND_AND_NATURAL_RESOURCE.PROT_WUI_HMN_INTRFCE_BUFFR_SP \
  --bbox "$bbox" --output-format gpkg \
  --download-root data/raw/bcdc \
  --manifest-path data/raw/bcdc/wui_buffer_kfc_manifest.json

python -m femic data bcdc-fetch \
  WHSE_LAND_AND_NATURAL_RESOURCE.PROT_WUI_RISK_CLASS_SP \
  --bbox "$bbox" --output-format gpkg \
  --download-root data/raw/bcdc \
  --manifest-path data/raw/bcdc/wui_risk_kfc_manifest.json

echo "BCDC layers fetched. Next: analysis/fetch_fuel_fgdb.py, analysis/fetch_climatebc.py, analysis/fetch_dem.py."
