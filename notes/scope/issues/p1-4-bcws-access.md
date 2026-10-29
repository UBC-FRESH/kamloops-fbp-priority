Task identifier: P1.4
Parent phase issue: #8
Status: planned
Branch: `feature/p1-method-contract`
Related planning: `ROADMAP.md` (Phase 1), `notes/scope/mental-map.md`

Goal:

Obtain written permission and the exact version of the BCWS fuel-typing algorithm, and map the
project inputs to its schema.

Scope:

- request written permission for research use;
- record the algorithm version and any data-sharing constraints;
- map the 21 VRI attributes and 5 LiDAR attributes to the input schema;
- record a go/no-go for P3.

Out of scope:

- running the algorithm on the full study area (P3);
- redistributing the algorithm or restricted data;
- changing BCWS data or settings.

Subtasks:

- [ ] Identify the BCWS contact and the permission process.
- [ ] Obtain written permission and the algorithm version.
- [ ] Record the input schema and the 21 VRI attributes.
- [ ] Map the 5 LiDAR attributes to the schema.
- [ ] Record the go/no-go and the fallback if permission is denied.

Acceptance criteria:

- written permission and the algorithm version are stored in the project record;
- every input attribute has a source and a mapping;
- the P3 gate is explicitly go or no-go.

Verification:

```bash
python scripts/check_workflow.py
```

Artifacts:

Permission record, schema map, and a P1.4 decision note.

Risks:

This is the critical path. A denial or an unavailable version forces a different thesis method.
