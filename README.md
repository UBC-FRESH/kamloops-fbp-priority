# Kamloops FBP Priority Mapping

A reproducible Fire Behaviour Prediction (FBP) screening workflow for the Kamloops Fire Centre
(KFC), built to scope Leah Nash's MGEM fuel-treatment priority mapping project. The study area is
71,579 km²; the method test uses three BEC zones: ICH, IDF, and PP (34,778 km²).

This repository is a feasibility prototype, not the final thesis result. It proves the data
plumbing, the baseline FBP chain, and the scale of the problem; it does not yet contain the
LiDAR-improved fuel-type experiment that is the research contribution.

## Status

Phase 0 (bootstrap and feasibility speed run) is in review via
[pull request #7](https://github.com/UBC-FRESH/kamloops-fbp-priority/pull/7) on
`feature/p0-bootstrap`. The Phase 0 parent issue is #1 and the task issues are #2-#6. The work is not
merged to `main` until the close-out is approved. The issue map is in
`notes/scope/github-issue-tree.md`; the close-out evidence is in `notes/reports/p0-closeout.md`.
Documentation is published at https://ubc-fresh.github.io/kamloops-fbp-priority/.

The scope, data audit, findings, and 18-month timeline are in
[`notes/scope/mental-map.md`](notes/scope/mental-map.md). Read that first.

## What the speed run produced

- a 100 m NAD83 / BC Albers analysis grid for the KFC;
- rasterized BEC zones, provincial FBP fuel types, WUI classes, and terrain;
- a 2014–2023 ClimateBC July/August mean stack and a 62-day mean-summer FWI sequence;
- official `cffdrs` 1.9.2 `fwiRaster` and `fbpRaster` runs;
- baseline ROS, HFI, flame length, fuel consumption, CFB, and fire-type rasters;
- a provisional 10-class HFI / WUI priority surface and zonal summaries;
- figures and tables under `docs/figures/` and `docs/tables/`.

The 100 m method test gives IDF a mean HFI of 1,828 kW/m, ICH 697, and PP 1,562 under the
mean-summer scenario. The 200 m full-KFC overview gives 1,972/751/1,656 and much more crown fire,
which is a resolution-sensitivity result, not a second truth. See
[`docs/tables/three_zones_fbp_summary_by_bec.csv`](docs/tables/three_zones_fbp_summary_by_bec.csv)
and [`docs/figures/`](docs/figures/).

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip install "femic @ git+https://github.com/UBC-FRESH/femic.git@e42e6e9" \
  "cffdrs @ git+https://github.com/cffdrs/cffdrs_py.git@2480d435"
python -m ruff check .
python -m pytest
sphinx-build -b html docs _build/html -W
python scripts/check_workflow.py
```

The R side uses `cffdrs` 1.9.2 in a local conda environment:

```bash
micromamba create -p .conda/envs/fbp -c conda-forge \
  r-base=4.4 r-terra r-sf r-data.table r-doparallel r-foreach r-geosphere r-jsonlite
.conda/envs/fbp/bin/Rscript -e 'install.packages("cffdrs", repos="https://cloud.r-project.org")'
```

The analysis scripts are in `analysis/` and are run with `PYTHONPATH=analysis`. The R wrappers are
`analysis/run_fwi.sh` and `analysis/run_fbp.sh`; they set the `PROJ_DATA` and `GDAL_DATA` paths that
the conda R environment needs.

The end-to-end prototype commands are:

```bash
PYTHONPATH=analysis .venv/bin/python analysis/prepare_terrain.py
PYTHONPATH=analysis .venv/bin/python analysis/prepare_landcover.py
PYTHONPATH=analysis .venv/bin/python analysis/prepare_climate.py
PYTHONPATH=analysis .venv/bin/python analysis/coarsen_weather.py
./analysis/run_fwi.sh data/interim/weather_4km data/processed/fwi_4km.tif
PYTHONPATH=analysis .venv/bin/python analysis/prepare_fbp_inputs.py
./analysis/run_fbp.sh data/processed/fbp_inputs_200m.tif data/processed/fbp_200m.tif 8
PYTHONPATH=analysis .venv/bin/python analysis/postprocess.py
```

The raw data fetches are separate because they are large and network-bound:

```bash
.venv/bin/python -m femic data bcdc-fetch <layer> --bbox <minx,miny,maxx,maxy> ...
PYTHONPATH=analysis .venv/bin/python analysis/fetch_climatebc.py
PYTHONPATH=analysis .venv/bin/python analysis/fetch_dem.py
PYTHONPATH=analysis .venv/bin/python analysis/fetch_fuel_fgdb.py
```

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Operating contract for coding agents |
| `ROADMAP.md` | Phase/task plan and issue tracker map |
| `CHANGE_LOG.md` | Dated narrative of the work |
| `notes/scope/mental-map.md` | Scope, findings, timeline, decisions |
| `notes/scope/data-audit.md` | Source, size, resolution, and quirks of each dataset |
| `notes/adr/` | Method decisions |
| `analysis/` | Prototype Python and R pipeline |
| `docs/figures/` | Headline maps |
| `docs/tables/` | Headline summary tables |
| `scripts/` | Seed framework: validator and dashboard |
| `tests/` | Python tests, including the fuel crosswalk |

## Data sources and licences

The project uses public BC data: BC Wildfire Service fire centres, fuel types, WUI layers, and fire
perimeters; the BEC map; the VRI; LidarBC; ClimateBC; and a DEM. The BC Data Catalogue layers are
Open Government Licence – British Columbia unless a dataset page says otherwise. ClimateBC data are
CC-BY. Copernicus DEM is open under the Copernicus licence. Raw data is not committed; each fetch
writes a manifest under `data/raw/`.

## Licence

The code is MIT-licensed; see `LICENSE`. The data licences are separate and must be recorded in the
thesis appendix.
