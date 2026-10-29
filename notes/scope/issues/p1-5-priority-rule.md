Task identifier: P1.5
Parent phase issue: #8
Status: planned
Branch: `feature/p1-method-contract`
Related planning: `ROADMAP.md` (Phase 1), `notes/adr/0005-provisional-priority-rule.md`

Goal:

Replace the provisional priority rule with a cited, reproducible 10-class FBP and two-class WUI
rule, and define at least two alternatives for sensitivity.

Scope:

- HFI class breaks and the fire-type dimension;
- WUI buffer and WUI risk weighting;
- the outside-WUI zero rule;
- at least two alternative rules for sensitivity.

Out of scope:

- the final map production (P5);
- treatment-cost or operational constraints;
- the LiDAR fuel-typing experiment (P3).

Subtasks:

- [ ] Review the proposal, BCWS practice, and the literature for class breaks.
- [ ] Define the primary 10-class FBP and two-class WUI rule.
- [ ] Implement the rule reproducibly.
- [ ] Define at least two alternatives.
- [ ] Record the accepted rule in ADR 0005 or a superseding ADR.

Acceptance criteria:

- the rule has a cited basis and explicit units;
- the implementation is reproducible from the baseline rasters;
- two alternatives produce a sensitivity comparison;
- Leah and the maintainers approve the rule.

Verification:

```bash
PYTHONPATH=analysis python analysis/postprocess.py --resolution 200
PYTHONPATH=analysis python analysis/postprocess.py --resolution 100 --three-zones
```

Artifacts:

Updated ADR 0005, rule implementation, and the alternative-rule comparison.

Risks:

The proposal does not define the classes; a rule chosen without review will not be defensible.
