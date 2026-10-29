Task identifier: P1.2
Parent phase issue: #8
Status: planned
Branch: `feature/p1-method-contract`
Related planning: `ROADMAP.md` (Phase 1), `notes/adr/0003-fuel-type-crosswalk.md`

Goal:

Approve the fuel crosswalk, including the grouped and modifier-prefixed codes, and define the
alternate-choice sensitivity run.

Scope:

- document the Phase 0 mapping for `D-1/2`, `M-1/2`, `M-3/4`, and `O-1a/b`;
- confirm the choices with BCWS;
- define at least one alternate mapping for each grouped choice;
- define the sensitivity run and the comparison metric.

Out of scope:

- the LiDAR/VRI fuel-typing algorithm (P3);
- changing the provincial fuel layer itself;
- the final priority rule (P1.5).

Subtasks:

- [ ] Review the Phase 0 crosswalk and the normalized prefix rules.
- [ ] Confirm the grouped-code choices with BCWS.
- [ ] Define the alternate choices and the sensitivity run.
- [ ] Record the accepted mapping in ADR 0003 or a superseding ADR.

Acceptance criteria:

- each grouped-code choice has a documented reason and a named alternate;
- BCWS review is recorded;
- the sensitivity run is scripted and reproducible.

Verification:

```bash
python -m pytest tests/test_fuel.py
PYTHONPATH=analysis python analysis/prepare_landcover.py
```

Artifacts:

Updated ADR 0003, crosswalk table, and sensitivity-run configuration.

Risks:

BCWS may use a different convention; a changed choice changes every downstream FBP result.
