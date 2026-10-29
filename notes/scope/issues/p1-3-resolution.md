Task identifier: P1.3
Parent phase issue: #8
Status: planned
Branch: `feature/p1-method-contract`
Related planning: `ROADMAP.md` (Phase 1), `notes/adr/0004-analysis-grid-and-resolution.md`

Goal:

Decide the analysis resolution and record an effective-resolution table that separates source
information from raster cell size.

Scope:

- 100 m screening grid and 30 m LiDAR core;
- source resolutions for ClimateBC, VRI, DEM, fuel, and LiDAR;
- pixel counts, runtime, and storage estimates;
- the resolution sensitivity run (100 m versus 200 m at minimum).

Out of scope:

- the full 30 m production run (P2/P3);
- changing the source datasets;
- the final priority rule (P1.5).

Subtasks:

- [ ] Build the effective-resolution table with source, native resolution, and analysis use.
- [ ] Record KFC and three-zone pixel counts at 100 m, 200 m, and 30 m.
- [ ] Define the 100 m versus 200 m sensitivity comparison.
- [ ] Define the 30 m LiDAR core extent and the chunking plan.
- [ ] Record the decision in ADR 0004 or a superseding ADR.

Acceptance criteria:

- every input has a stated native resolution and analysis resolution;
- no interpolated climate is described as 30 m information;
- the resolution sensitivity run is defined and costed.

Verification:

```bash
PYTHONPATH=analysis python analysis/prepare_fbp_inputs.py
PYTHONPATH=analysis python analysis/resample_inputs.py
```

Artifacts:

Effective-resolution table, updated ADR 0004, and runtime/storage estimates.

Risks:

The 30 m KFC grid is 79.5 M cells; full-resolution runs can be slow and memory-heavy.
