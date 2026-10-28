Phase identifier: P0
Status: planned
Branch: `feature/p0-bootstrap`
Roadmap: `ROADMAP.md`, section "Phase 0: Bootstrap and feasibility speed run"
Pull request: not opened yet

Goal:

Stand up the project on the UBC-FRESH seed, audit every named dataset, and run a real baseline FBP
chain for the Kamloops Fire Centre and the three test BEC zones so the scope and scale of Leah
Nash's MGEM project are concrete.

Scope:

- adapt the agent contract, README, and roadmap to the KFC project;
- fetch and audit the KFC boundary, BEC map, provincial fuel types, WUI layers, ClimateBC,
  LidarBC, VRI, CDED, fire perimeters, and PSP access;
- build the 100 m analysis grid and the baseline FWI/FBP chain;
- write the mental map, data audit, and method ADRs;
- create the private GitHub repository and the Phase 0 issue tree.

Out of scope:

- the LiDAR/VRI fuel-typing experiment (P3);
- the final 10-class/WUI rule (P1.5);
- climate-change scenarios (P5);
- any claim that the provisional priority map is the thesis result.

Architecture notes:

The prototype uses Python for data preparation and R `cffdrs` 1.9.2 for `fwiRaster` and
`fbpRaster`. The hand-off is a 16-band GeoTIFF with a documented band order. Raw data is ignored by
git; derived rasters are ignored; headline tables and figures are tracked. See
`notes/scope/mental-map.md` and `notes/adr/0001-python-prep-r-cffdrs.md`.

Child task checklist:

- [ ] P0.1: Adapt the agent contract, README, and roadmap
- [ ] P0.2: Fetch and audit the named datasets
- [ ] P0.3: Build the 100 m baseline FBP chain
- [ ] P0.4: Write the scope, scale, and shape map
- [ ] P0.5: Create the private repository and Phase 0 issues

Acceptance criteria:

- the dashboard is green on `feature/p0-bootstrap`;
- raw inputs are reproducible by script and absent from git;
- the baseline FBP outputs and zonal summary exist for the KFC and the three zones;
- the mental map names the data gaps, the critical path, and the decisions needed before P3.

Verification:

```bash
python scripts/dashboard.py
python scripts/check_workflow.py
PYTHONPATH=analysis .venv/bin/python analysis/prepare_fbp_inputs.py
./analysis/run_fbp.sh data/processed/fbp_inputs_200m.tif data/processed/fbp_200m.tif 8
PYTHONPATH=analysis .venv/bin/python analysis/postprocess.py
```

Closeout requirements:

- post a closeout comment with the commit, the dashboard result, and the paths to the mental map,
  data audit, and baseline outputs;
- record the GitHub authentication blocker and the exact commands that resolved it;
- do not close the parent issue until the Phase 0 pull request has merged.
