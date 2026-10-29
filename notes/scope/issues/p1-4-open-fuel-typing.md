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
`(599, 'C-3', None)`. The next step is a real VRI sample, not a synthetic stand.

Risks:

The open tool implements the 2018 decision tree, not the current BCWS version. VRI attributes are
often null, and LiDAR coverage is uneven. The GPL-3.0 licence must be kept separate from the MIT
project code.
