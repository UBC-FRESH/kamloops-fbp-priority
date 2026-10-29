Phase identifier: P1
Status: active
Branch: `feature/p1-method-contract`
Roadmap: `ROADMAP.md`, section "Phase 1: Method contract"
Repository: https://github.com/UBC-FRESH/kamloops-fbp-priority
Pull request: not opened yet

Goal:

Turn the Phase 0 feasibility findings into a written method contract that Leah and BCWS can approve
before any LiDAR fuel-typing work starts.

Scope:

- replace or explicitly accept the mean-summer weather scenario with a daily weather method;
- approve the fuel crosswalk and the grouped-code sensitivity plan;
- decide the analysis resolution and record the effective-resolution table;
- obtain the BCWS fuel-typing algorithm permission, version, and input schema;
- define the 10-class FBP and two-class WUI priority rule with alternatives.

Out of scope:

- the LiDAR/VRI fuel-typing experiment (P3);
- the production baseline and validation runs (P2);
- climate-change scenarios (P5);
- any claim that the provisional priority map is the thesis result.

Architecture notes:

Every open choice in `notes/scope/mental-map.md` becomes an ADR or a named deferral. P1.4 is the
critical path: no LiDAR processing starts until the BCWS permission, algorithm version, and input
schema are recorded. P1.1 replaces ADR 0002 or explicitly accepts it with a sensitivity plan.

Child task checklist:

- [ ] #9 P1.1: Decide the weather method and record it as an ADR
- [ ] #10 P1.2: Approve the fuel crosswalk and grouped-code sensitivity plan
- [ ] #11 P1.3: Decide the analysis resolution and effective-resolution table
- [ ] #12 P1.4: Confirm BCWS fuel-typing algorithm access and input schema
- [ ] #13 P1.5: Define the 10-class FBP and two-class WUI priority rule

Acceptance criteria:

- every open choice in `notes/scope/mental-map.md` has an accepted ADR or a named deferral;
- the BCWS fuel-typing algorithm permission and version are recorded in writing;
- the weather method runs end to end on the three test zones;
- the priority rule is cited, reproducible, and has at least two alternatives for sensitivity.

Verification:

```bash
python scripts/dashboard.py
python scripts/check_workflow.py
```

Closeout requirements:

- post a closeout comment with the ADR list, the BCWS permission record, and the weather-method run;
- open the phase pull request with the report in `notes/reports/p1-closeout.md`;
- do not close the parent issue until the phase pull request has merged.
