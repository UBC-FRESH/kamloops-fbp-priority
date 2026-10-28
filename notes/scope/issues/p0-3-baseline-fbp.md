Task identifier: P0.3
Parent phase issue: #1
Status: active
Branch: `feature/p0-bootstrap`
Related planning: `ROADMAP.md` (Phase 0), `notes/adr/0001-python-prep-r-cffdrs.md`

Goal:

Build a real baseline FWI/FBP chain for the KFC and the three test zones using the official cffdrs
R raster functions.

Scope:

- 100 m EPSG:3005 grid, KFC mask, BEC/fuel/WUI rasterization;
- DEM mosaic and slope/aspect;
- 62-day mean-summer FWI sequence;
- 100 m and 200 m FBP input stacks;
- official `fwiRaster` and `fbpRaster` runs;
- post-processing, provisional classes, zonal summaries, and figures.

Out of scope:

- the LiDAR-improved fuel type (P3);
- the final priority rule (P1.5);
- climate scenarios (P5).

Subtasks:

- [ ] Build the grid and land-cover rasters.
- [ ] Build the terrain rasters.
- [ ] Build the ClimateBC mean stack and weather sequence.
- [ ] Run `fwiRaster`.
- [ ] Build the FBP input stacks.
- [ ] Run `fbpRaster` for the 200 m KFC and the 100 m three zones.
- [ ] Post-process and write figures/tables.

Acceptance criteria:

- ROS, HFI, flame length, fuel consumption, CFB, and fire type exist for every valid cell;
- the three-zone summary is reproducible;
- the run commands and assumptions are documented.

Verification:

```bash
PYTHONPATH=analysis .venv/bin/python analysis/prepare_fbp_inputs.py
./analysis/run_fbp.sh data/processed/fbp_inputs_200m.tif data/processed/fbp_200m.tif 8
PYTHONPATH=analysis .venv/bin/python analysis/postprocess.py
```

Artifacts:

`data/processed/fbp_200m.tif`, `data/processed/fbp_three_zones_100m.tif`,
`docs/tables/fbp_summary_by_bec.csv`, `docs/figures/`.

Risks:

The R `fbpRaster` loop is slow on the full 100 m rectangle; the 200 m KFC and 100 m three-zone
split is a prototype compromise.
