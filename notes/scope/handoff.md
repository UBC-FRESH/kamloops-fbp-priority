# Handoff: Kamloops FBP feasibility speed run

Date: 2026-10-28
Branch: `feature/p0-bootstrap`
Local commits: see `git log --oneline` (seed commit plus the P0.1–P0.5 work)
Dashboard: green (lint, format, strict types, tests, validator, docs)

## What is done

- The seed was rendered and adapted to the KFC project.
- The data audit is in `notes/scope/data-audit.md`.
- The scope, findings, timeline, and decisions are in `notes/scope/mental-map.md`.
- The baseline pipeline is in `analysis/`; the headline figures are in `docs/figures/` and the
  zonal summaries in `docs/tables/`.
- The 100 m three-zone FBP result and the 200 m KFC overview are reproducible from the scripts.
- The green dashboard passes on the branch.

## GitHub (resolved)

The private repository now exists at https://github.com/UBC-FRESH/kamloops-fbp-priority. `main` has
the seed commit and `feature/p0-bootstrap` has the Phase 0 work. The parent issue is #1; the child
issues are #2-#6 and are linked as sub-issues. P0.5 (#6) is complete; P0.1-P0.4 remain open until
the Phase 0 close-out pull request #7 is approved. The close-out report is
`notes/reports/p0-closeout.md`.

The first session's device-flow codes expired before authorization. The maintainer authenticated
separately; no credentials are stored in the repository. The issue map and verification commands are
in `notes/scope/github-issue-tree.md`.

## Next technical move

P1.1: decide the weather method. The current mean-summer scenario uses ClimateBC monthly means, a
fixed 20 km/h wind, and a 62-day FWI spin-up. Add a daily wind/daily-weather source (ERA5-Land or
BCWS stations) or explicitly accept the mean-summer scenario. Do not start LiDAR processing until
this and the BCWS fuel-typing algorithm access are settled.

The Phase 0 close-out move is separate: pull request #7 is open from `feature/p0-bootstrap`, the
report is `notes/reports/p0-closeout.md`, and the phase waits for maintainer approval before merging
or closing #1.

## Reproduce the baseline

```bash
. .venv/bin/activate
./analysis/fetch_bcdc.sh
python analysis/fetch_fuel_fgdb.py
python analysis/fetch_climatebc.py
python analysis/fetch_dem.py
PYTHONPATH=analysis python analysis/prepare_terrain.py
PYTHONPATH=analysis python analysis/prepare_landcover.py
PYTHONPATH=analysis python analysis/prepare_climate.py
PYTHONPATH=analysis python analysis/coarsen_weather.py
./analysis/run_fwi.sh data/interim/weather_4km data/processed/fwi_4km.tif
PYTHONPATH=analysis python analysis/prepare_fbp_inputs.py
PYTHONPATH=analysis python analysis/resample_inputs.py
./analysis/run_fbp.sh data/processed/fbp_inputs_200m.tif data/processed/fbp_200m.tif 8
./analysis/run_fbp.sh data/processed/fbp_inputs_three_zones_100m.tif data/processed/fbp_three_zones_100m.tif 8
PYTHONPATH=analysis python analysis/postprocess.py --resolution 200
PYTHONPATH=analysis python analysis/postprocess.py --resolution 100 --three-zones
```
