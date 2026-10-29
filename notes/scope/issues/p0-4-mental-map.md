Task identifier: P0.4
Parent phase issue: #1
Status: pr-open
Branch: `feature/p0-bootstrap`
Related planning: `ROADMAP.md` (Phase 0)

Goal:

Write the scope, scale, and shape map that Leah and the maintainers can use to plan the project to
April 2027.

Scope:

- the proposal in one page;
- the data audit and the six hard findings;
- the scale/compute table;
- the phase plan and the definition of done;
- the decisions needed now and the limitations of the speed run.

Out of scope:

- the thesis literature review;
- final results;
- the LiDAR experiment.

Subtasks:

- [ ] Write `notes/scope/mental-map.md`.
- [ ] Write `notes/scope/data-audit.md`.
- [ ] Record the five ADRs.
- [ ] Add the headline findings to `CHANGE_LOG.md`.

Acceptance criteria:

- every finding states the evidence and the consequence for the project;
- every open decision has a recommendation and a default;
- the critical path and the April 2027 gate are explicit.

Verification:

```bash
python scripts/check_workflow.py
```

Artifacts:

`notes/scope/mental-map.md`, `notes/scope/data-audit.md`, `notes/adr/`.

Risks:

The mental map can become a second proposal; keep it a decision document, not a literature review.

Completion metadata:

Added at closeout: merged in `eda7195` via pull request #7; dashboard green at `5e7602f`; CI run `40793125048` passed.
