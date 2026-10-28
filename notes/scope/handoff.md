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

## What is blocked

The private GitHub repository was not created. `gh` is installed at `~/.local/bin/gh`, but no
GitHub account is authenticated. Two device-flow codes expired before authorization. There is no
`GITHUB_TOKEN`, SSH key, or credential helper in the environment.

To finish the GitHub step:

```bash
cd kamloops-fbp-priority
~/.local/bin/gh auth login --hostname github.com --git-protocol https --web
~/.local/bin/gh auth status
```

Then:

```bash
~/.local/bin/gh repo create UBC-FRESH/kamloops-fbp-priority --private --source=. --remote=origin
git push -u origin main
git push -u origin feature/p0-bootstrap
~/.local/bin/gh repo edit UBC-FRESH/kamloops-fbp-priority --default-branch main
```

Create the Phase 0 issues from `notes/scope/issues/` and link the children as sub-issues. The exact
commands and titles are in `notes/scope/github-issue-tree.md`. After the issues exist, set the parent
number and `Status: active` in `ROADMAP.md` and the tracker map. Do not mark the phase active before
the issues exist.

If the authenticated account cannot create a repository in `UBC-FRESH`, create it under the
authenticated account, record the transfer step, and do not change visibility or settings without a
separate approval.

## Next technical move

P1.1: decide the weather method. The current mean-summer scenario uses ClimateBC monthly means, a
fixed 20 km/h wind, and a 62-day FWI spin-up. Add a daily wind/daily-weather source (ERA5-Land or
BCWS stations) or explicitly accept the mean-summer scenario. Do not start LiDAR processing until
this and the BCWS fuel-typing algorithm access are settled.

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
