#!/usr/bin/env bash
# Wrapper for the conda R environment used by the feasibility prototype.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
env_root="${KAMLOOPS_R_ENV:-$root/.conda/envs/fbp}"
if [[ ! -x "$env_root/bin/Rscript" ]]; then
  echo "R environment not found at $env_root" >&2
  echo "Run: micromamba create -p $env_root -c conda-forge r-base=4.4 r-terra r-sf r-data.table r-doparallel r-foreach r-geosphere r-jsonlite" >&2
  echo "Then: $env_root/bin/Rscript -e 'install.packages(\"cffdrs\", repos=\"https://cloud.r-project.org\")'" >&2
  exit 1
fi
export PROJ_DATA="$env_root/share/proj"
export PROJ_LIB="$env_root/share/proj"
export GDAL_DATA="$env_root/share/gdal"
exec "$env_root/bin/Rscript" "$root/analysis/run_fwi.R" "$@"
