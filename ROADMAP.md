# Kamloops FBP Priority Mapping Roadmap

This roadmap is the plan of record for the Kamloops Fire Centre feasibility and methods project. It
mirrors the phases, tasks, and subtasks in GitHub issues once the private repository is created. The
validator `scripts/check_workflow.py` parses the phase headers, status lines, and checkboxes below,
so keep their format.

The project is Leah Nash's MGEM fuel-treatment priority mapping project. The study area is the
Kamloops Fire Centre (KFC), 71,579 km². The method test uses three BEC zones: ICH, IDF, and PP.

## Issue Tracker Map

| Phase | Parent issue | Branch | Status |
| --- | --- | --- | --- |
| P0 Bootstrap and feasibility speed run | #1 | `feature/p0-bootstrap` | active |
| P1 Method contract | TBD | `feature/p1-method-contract` | planned |
| P2 Baseline KFC fire behaviour | TBD | `feature/p2-baseline-kfc` | planned |
| P3 LiDAR and VRI fuel typing | TBD | `feature/p3-lidar-vri` | planned |
| P4 Baseline versus LiDAR comparison | TBD | `feature/p4-comparison` | planned |
| P5 Priority and scenarios | TBD | `feature/p5-priority-scenarios` | planned |
| P6 Thesis and release | TBD | `feature/p6-thesis-release` | planned |

## Lifecycle Map

| Stage | Phases | Exit criteria |
| --- | --- | --- |
| Scope and design | P0, P1 | Question, scope, data audit, weather/fuel/class decisions recorded in ADRs |
| Build | P2, P3 | Baseline and LiDAR-improved fuel/FBP pipelines committed and reproducible |
| Verify | P4, P5 | Baseline-vs-LiDAR comparison and sensitivity evidence in the close-out report |
| Release and deploy | P6 | Thesis, tagged repo, docs, and data provenance published with approval |
| Operate and maintain | P6 (procedure) | Review cadence and retirement decision recorded |
| Retire | P6 (procedure) | Archive notice, final changelog entry, and issues closed |

## Conventions

- A phase is `P<n>`. A task is `P<n>.<m>`. A subtask is a checklist item inside the task's issue body.
  Three levels at most.
- Status values are `planned`, `active`, `pr-open`, `complete`, and `deferred`.
- A phase becomes `complete` only after its pull request merges to `main` and its parent issue closes.
- The Phase 0 work was performed locally before the private GitHub repository existed. That deviation
  is recorded in `CHANGE_LOG.md` and in the issue-tree manifest; it does not change the phase gate.

## Phase 0: Bootstrap and feasibility speed run

Parent issue: #1
Branch: `feature/p0-bootstrap`
Status: active

Goal: stand up the project on the UBC-FRESH seed, audit every named dataset, and run a real baseline
FBP chain for the KFC and the three test BEC zones so the scope and scale of Leah's project are
concrete rather than hypothetical.

- [ ] P0.1 Adapt the agent contract, README, and roadmap to the KFC project
  - [ ] Replace the seed's placeholder purpose and status text
  - [ ] Add the data, CRS, unit, and weather guardrails to `AGENTS.md`
  - [ ] Record the analysis/ versus scripts/ gate distinction
- [ ] P0.2 Fetch and audit the named datasets
  - [ ] KFC boundary, BEC map, provincial fuel types, WUI buffer, and WUI risk class
  - [ ] ClimateBC 2014-2023 July/August rasters and the wind-variable gap
  - [ ] LidarBC index coverage by BEC zone and by product
  - [ ] VRI 2025, CDED, fire perimeters, and PSP access notes
- [ ] P0.3 Build the 100 m baseline FBP chain
  - [ ] 100 m EPSG:3005 grid, KFC mask, BEC/fuel/WUI rasterization
  - [ ] DEM mosaic and slope/aspect
  - [ ] 62-day mean-summer FWI sequence with the official `fwiRaster`
  - [ ] 100 m FBP inputs and official `fbpRaster`
  - [ ] Provisional HFI classes, WUI priority, zonal summaries, figures
- [ ] P0.4 Write the scope, scale, and shape map
  - [ ] `notes/scope/mental-map.md` with findings, timeline, and decisions
  - [ ] `notes/scope/data-audit.md` with source, size, resolution, and quirks
  - [ ] ADRs for the weather scenario, fuel crosswalk, and resolution
- [x] P0.5 Create the private GitHub repository and Phase 0 issues
  - [x] Render and push the seed to `UBC-FRESH/kamloops-fbp-priority`
  - [x] Create the P0 parent issue and child issues as sub-issues
  - [x] Activate P0 and post the activation comment

Acceptance criteria:

- The dashboard is green on the Phase 0 branch.
- The raw inputs are reproducible by script and absent from git.
- The baseline FBP outputs and the zonal summary exist for the KFC and the three zones.
- The mental map names the data gaps, the critical path, and the decisions needed before P3.

Verification:

- `python scripts/dashboard.py`
- `python scripts/check_workflow.py`
- `PYTHONPATH=analysis .venv/bin/python analysis/prepare_fbp_inputs.py`
- `./analysis/run_fbp.sh data/processed/fbp_inputs_100m.tif data/processed/fbp_100m.tif 8`
- `PYTHONPATH=analysis .venv/bin/python analysis/postprocess.py`

## Phase 1: Method contract

Parent issue: TBD
Branch: `feature/p1-method-contract`
Status: planned

Goal: turn the feasibility findings into a written method contract that Leah and BCWS can approve
before any LiDAR fuel-typing work starts.

- [ ] P1.1 Decide the weather method and record it as an ADR
  - [ ] Resolve the ClimateBC wind gap (ERA5-Land, BCWS stations, or design wind)
  - [ ] Define the daily sequence or weather-generator method
  - [ ] Define the mean-summer versus percentile scenario comparison
- [ ] P1.2 Approve the fuel crosswalk and grouped-code sensitivity plan
  - [ ] Confirm D-1/2, M-1/2, M-3/4, and O-1a/b choices with BCWS
  - [ ] Define the alternate-choice sensitivity run
- [ ] P1.3 Decide the analysis resolution and effective-resolution table
  - [ ] 100 m screening grid and 30 m LiDAR core
  - [ ] Resolution sensitivity run
- [ ] P1.4 Confirm BCWS fuel-typing algorithm access and input schema
  - [ ] Obtain written permission and the algorithm version
  - [ ] Map the 21 VRI attributes and 5 LiDAR attributes to the schema
- [ ] P1.5 Define the 10-class FBP and two-class WUI priority rule
  - [ ] Class breaks, fire-type dimension, and WUI weighting
  - [ ] At least two alternative rules for sensitivity

Acceptance criteria:

- Every open choice in the mental map has an accepted ADR or a named deferral.
- The fuel-typing algorithm permission and version are recorded.
- The weather method can be run end to end on the three zones.

## Phase 2: Baseline KFC fire behaviour

Parent issue: TBD
Branch: `feature/p2-baseline-kfc`
Status: planned

Goal: produce a validated baseline FBP product for the KFC and the three test zones.

- [ ] P2.1 Run the baseline FBP at the agreed resolution for the KFC and three zones
- [ ] P2.2 Validate against published FBP examples and the cffdrs test data
- [ ] P2.3 Produce the first documented priority map and uncertainty summary
- [ ] P2.4 Write the baseline methods and data-provenance pages

Acceptance criteria:

- ROS, HFI, flame length, fuel consumption, CFB, and fire type exist for every cell.
- The validation table shows agreement with known FBP values.
- The first priority map is reproducible from a clean checkout.

## Phase 3: LiDAR and VRI fuel typing

Parent issue: TBD
Branch: `feature/p3-lidar-vri`
Status: planned

Goal: implement the research contribution: use LiDAR to improve VRI fuel attributes and re-derive
FBP fuel types per BEC zone.

- [ ] P3.1 Acquire and clip VRI 2025 R1 for the three zones
- [ ] P3.2 Select and process LiDAR tiles for canopy height, cover, live stems, and dead stems
- [ ] P3.3 Compare VRI and LiDAR attributes with PSP plots
- [ ] P3.4 Train and validate the per-BEC adjustment model
- [ ] P3.5 Produce the improved 21-attribute stack and FBP fuel-type map

Acceptance criteria:

- The LiDAR coverage and extrapolation limits are explicit per zone.
- The VRI-versus-LiDAR differences are quantified with uncertainty.
- The improved fuel-type map is reproducible and documented.

## Phase 4: Baseline versus LiDAR comparison

Parent issue: TBD
Branch: `feature/p4-comparison`
Status: planned

Goal: answer the first research question: does LiDAR-improved fuel typing materially change FBP fire
behaviour and priority?

- [ ] P4.1 Run FBP on the improved fuel type with the identical weather/topography
- [ ] P4.2 Quantify the difference in ROS, HFI, flame length, CFB, and fire type
- [ ] P4.3 Propagate the difference into the priority map
- [ ] P4.4 Write the comparison results and uncertainty

Acceptance criteria:

- The comparison uses the same weather, terrain, and class rules on both sides.
- The difference maps and summary tables are reproducible.
- The answer to research question 1 is stated with evidence and limits.

## Phase 5: Priority and scenarios

Parent issue: TBD
Branch: `feature/p5-priority-scenarios`
Status: planned

Goal: answer the second and third research questions: how do treatment assumptions and climate change
change the priority map?

- [ ] P5.1 Finalize the 10-class FBP and WUI priority rule
- [ ] P5.2 Run treatment cost/effectiveness assumptions
- [ ] P5.3 Run future climate scenarios from ClimateBC
- [ ] P5.4 Complete the sensitivity analysis and uncertainty communication

Acceptance criteria:

- At least two treatment-assumption and two climate scenarios are compared.
- The priority map is accompanied by a sensitivity table and a limitations section.
- The results answer research questions 2 and 3.

## Phase 6: Thesis and release

Parent issue: TBD
Branch: `feature/p6-thesis-release`
Status: planned

Goal: deliver the thesis, the reproducible repository, and the public-facing products.

- [ ] P6.1 Write the thesis chapters and figures
- [ ] P6.2 Tag and document the reproducible release
- [ ] P6.3 Prepare the defense and the plain-language summary
- [ ] P6.4 Close the project with a final changelog and archive note

Acceptance criteria:

- The thesis is committee-ready.
- A clean checkout reproduces the headline figures and tables.
- The release names the data versions, licences, and known gaps.

## Detailed Next Steps Notes

1. The repository is rendered from `UBC-FRESH/ubc-fresh-dev-workflow` and is on
   `feature/p0-bootstrap`. The private repository is
   https://github.com/UBC-FRESH/kamloops-fbp-priority; the Phase 0 parent issue is #1 and the task
   issues are #2-#6. The work is not merged to `main` until the phase close-out is approved. The
   issue map and verification commands are in `notes/scope/github-issue-tree.md`.
2. The 100 m baseline pipeline is built. It uses real BC Data Catalogue layers, real ClimateBC
   2014-2023 July/August means, a 30 m Copernicus DEM, the official `cffdrs` 1.9.2 `fwiRaster` and
   `fbpRaster`, and the BCWS WUI layers. Raw data is under ignored `data/raw/`; derived rasters are
   under ignored `data/processed/`; headline tables and figures are tracked.
3. The KFC is 71,579.2 km². The three test zones cover 34,778 km² (ICH 13,324; IDF 18,504; PP 2,950).
   Only 13 of the proposal's 16 BEC zones have non-zero area in the current BEC map.
4. Finding 1 is the weather gap. ClimateBC publishes no wind variable and only monthly means. The
   prototype uses a fixed 20 km/h wind from 225° and a 62-day mean-summer spin-up. This must be
   replaced or explicitly accepted in P1.1.
5. Finding 2 is the fuel crosswalk. The full provincial layer contains modifier-prefixed codes such
   as `B26_O-1a/b` and `B71_S-2`; these are normalized before the cffdrs crosswalk. The grouped
   codes remain a modelling choice and need a sensitivity run.
6. Finding 3 is the LiDAR coverage claim. Point-cloud tiles cover 26.8% of the KFC; project extents
   cover 45.7%; DEM 1:20k covers 30.0%; DSM 1:2.5k covers 19.1%; DSM 1:20k covers 17.0%. None is the
   proposal's 54%. The P1.3/P3 gate must name the product and the calculation.
7. Finding 4 is resolution. The proposal's 30 m grid is 79.5 M KFC pixels; the prototype uses 100 m
   (7.16 M). ClimateBC is ~800 m and CDED is a 1:250k source; 30 m does not create 30 m climate or
   30 m VRI. P1.3 should adopt an effective-resolution table and a resolution sensitivity run.
8. Finding 5 is the critical path. The BCWS 21-attribute fuel-typing algorithm and its permission are
   required before P3 can produce the thesis's central result. Confirm this in writing before
   January 2027.
9. Finding 6 is the priority rule. The proposal does not define the 10 FBP classes or the WUI
   combination. The prototype's rule is provisional: HFI 10-class scale, buffer half-scale, risk
   full-scale, outside WUI zero. P1.5 must replace it with a cited, approved rule.
10. The next move after the Phase 0 close-out is P1.1 (weather method). Do not start LiDAR processing
    until the weather method and BCWS algorithm access are settled.
11. The Phase 0 local work is complete through P0.4. The phase remains `planned` because its parent
    issue cannot exist until the private repository is created; do not mark it `active` or check its
    tasks until `gh auth status` succeeds and the issues exist. The local evidence is in
    `notes/scope/mental-map.md`, `notes/scope/data-audit.md`, `docs/tables/`, and `docs/figures/`.
12. Baseline results: the 100 m three-zone method test gives IDF HFI mean 1,828 kW/m, ICH 697, and
    PP 1,562 under mean-summer weather; the 200 m full-KFC overview gives IDF 1,972, ICH 751, and
    PP 1,656. The 200 m run produces 4.2% crown fire in IDF and 4.8% in PP, versus 0.1% and 0.0% at
    100 m. Resolution is a sensitivity axis, not a cosmetic choice.
