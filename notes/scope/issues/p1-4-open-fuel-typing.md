Task identifier: P1.4
Parent phase issue: #8
Status: active
Branch: `feature/p1-method-contract`
Related planning: `ROADMAP.md` (Phase 1), `notes/adr/0007-open-fuel-typing-method.md`

Goal:

Implement the published BC fuel-typing decision tree with the open
`BC_CFFBPS_FuelTyping_Tool`, and define how the LiDAR canopy metrics replace or supplement the 21
VRI attributes. The current BCWS operational version is an optional benchmark, not a gate.

Scope:

- record the open tool source, commit, GPL-3.0 licence, and dependencies;
- reproduce the published decision tree on a VRI sample;
- map the 21 VRI attributes and the LiDAR overrides (height, cover, live/dead stems, CBH, CBD);
- define the validation and sensitivity plan;
- decide whether the current BCWS operational version is run as an optional benchmark.

Out of scope:

- the full three-zone LiDAR run (P3);
- reproducing the current BCWS operational output exactly;
- changing the provincial fuel-type layer or BCWS systems.

Subtasks:

- [x] Record the open tool source, commit, licence, and dependencies.
- [ ] Reproduce the published decision tree on a VRI sample.
- [ ] Map the 21 VRI attributes and the LiDAR canopy overrides.
- [ ] Define the validation and sensitivity plan.
- [ ] Decide whether the current BCWS version is run as an optional benchmark.

Acceptance criteria:

- the open method runs on a VRI sample and returns FBP fuel types;
- the 21 attributes and LiDAR overrides have a documented source and mapping;
- the tool commit and GPL-3.0 licence are recorded;
- there is no permission gate in the P3 critical path.

Verification:

```bash
python -m pytest tests/
python scripts/check_workflow.py
```

Artifacts:

ADR 0007, `notes/reference/open-fuel-typing-sources.md`, the vendored tool at
`analysis/vendor/BC_CFFBPS_FuelTyping_Tool/` (commit `13bc0c9`, GPL-3.0), and the attribute mapping.

Progress:

The tool is vendored and the smoke test `analysis/smoke_open_fuel_typing.py` returns
`(599, 'C-3', None)`. Three 4 km × 4 km VRI samples (ICH, IDF, PP), chosen where LidarBC point
clouds exist, classified 385 polygons with **0 errors** and **84.1% agreement** with the provincial
layer on 383 comparable polygons after normalizing the grouped codes. Per-zone agreement: ICH 81.5%,
IDF 84.3%, PP 88.8%. That is a smoke comparison, not validation. The next step is the LiDAR
overrides on the same sample boxes.

Scripts: `analysis/run_open_fuel_typing_sample.py`, `analysis/compare_open_vs_provincial.py`.
Tables: `docs/tables/open_vs_provincial_agreement_by_zone.csv` and the per-zone CSV files.

The same three sample boxes are fully covered by LidarBC point-cloud tiles at 8 points/m² (ICH 13
tiles/2024; IDF 15 tiles/2017, 2024, 2025; PP 22 tiles/2017, 2024). Candidates are in
`docs/tables/lidar_candidates_three_zones.csv`; the P3 LiDAR pilot can use these boxes directly.

LiDAR pilot: one tile per zone was processed to 10 m canopy metrics (cover, height percentiles). The
LiDAR mean cover and p95 height replaced the VRI crown closure and height, then the decision tree was
rerun. Fuel-type changes: ICH 1/43 (C-5 to C-3), IDF 5/31 (four O-1b to C-7, one C-7 to C-3), PP 0/24.
This is a one-tile-per-zone pilot, not a zone-wide result; the next step is all tiles for the full
sample boxes and the FBP comparison.

Risks:

The open tool implements the 2018 decision tree, not the current BCWS version. VRI attributes are
often null, and LiDAR coverage is uneven. The GPL-3.0 licence must be kept separate from the MIT
project code.
