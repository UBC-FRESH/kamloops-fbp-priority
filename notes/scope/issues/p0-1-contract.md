Task identifier: P0.1
Parent phase issue: #TBD
Status: planned
Branch: `feature/p0-bootstrap`
Related planning: `ROADMAP.md` (Phase 0), `notes/scope/mental-map.md`

Goal:

Adapt the seed's agent contract, README, and roadmap to the Kamloops FBP project.

Scope:

- replace the seed placeholder purpose, status, and repository map;
- add the project data, CRS, unit, weather, fuel-crosswalk, resolution, and R-environment rules to
  `AGENTS.md`;
- rewrite `ROADMAP.md` as the P0–P6 plan to April 2027;
- record the analysis/ versus scripts/ gate distinction.

Out of scope:

- changing the seed framework's gates or validator;
- creating GitHub issues.

Subtasks:

- [ ] Update `AGENTS.md` project-specific rules.
- [ ] Update `README.md` purpose, status, quick start, and repository map.
- [ ] Rewrite `ROADMAP.md` with the P0–P6 phases and tasks.
- [ ] Update `CHANGE_LOG.md` with the contract change.

Acceptance criteria:

- the seed placeholders are gone;
- the roadmap parses under `scripts/check_workflow.py`;
- the dashboard is green.

Verification:

```bash
python scripts/check_workflow.py
python scripts/dashboard.py
```

Artifacts:

`AGENTS.md`, `README.md`, `ROADMAP.md`, `CHANGE_LOG.md`.

Risks:

The seed's generic phases do not match the thesis timeline; the mapping must stay explicit.

Completion metadata:

Added at closeout: commit hash, verification result, and pull request number.
