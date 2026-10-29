Task identifier: P0.2
Parent phase issue: #1
Status: pr-open
Branch: `feature/p0-bootstrap`
Related planning: `ROADMAP.md` (Phase 0), `notes/scope/data-audit.md`

Goal:

Fetch and audit every dataset the proposal names, and record access, size, resolution, licence, and
quirks.

Scope:

- KFC boundary, BEC map, provincial fuel types, WUI buffer, and WUI risk class via `femic`;
- ClimateBC 2014–2023 July/August GeoTIFFs;
- LidarBC index coverage by product and BEC zone;
- VRI 2025, CDED, fire perimeters, and PSP access notes;
- manifests under `data/raw/`.

Out of scope:

- processing the LiDAR point clouds;
- clipping the full VRI (P3);
- the BCWS fuel-typing algorithm run (P3).

Subtasks:

- [ ] Fetch the KFC, BEC, fuel, and WUI layers.
- [ ] Fetch and validate the ClimateBC rasters.
- [ ] Query the LidarBC index and compute coverage by product and zone.
- [ ] Record VRI, CDED, fire-perimeter, and PSP access paths.
- [ ] Write `notes/scope/data-audit.md`.

Acceptance criteria:

- every named layer has a source URL, access method, size, resolution, and licence note;
- the LiDAR coverage table names the product and the formula;
- no raw data is tracked in git.

Verification:

```bash
python scripts/check_workflow.py
ls data/raw/*/manifest.json
```

Artifacts:

`notes/scope/data-audit.md`, `data/raw/*/manifest.json`.

Risks:

The proposal's 54% LiDAR coverage is not reproducible from the current index; the audit must state
the measured numbers and the open question.

Completion metadata:

Added at closeout: merged in `eda7195` via pull request #7; dashboard green at `5e7602f`; CI run `40793125048` passed.
