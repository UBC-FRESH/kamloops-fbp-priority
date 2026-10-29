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
- implement the published open fuel-typing decision tree and define the LiDAR input mapping;
- decide whether the current BCWS operational version is run as an optional benchmark;
- define the 10-class FBP and two-class WUI priority rule with alternatives.

Out of scope:

- the LiDAR/VRI fuel-typing experiment (P3);
- the production baseline and validation runs (P2);
- climate-change scenarios (P5);
- any claim that the provisional priority map is the thesis result.

Architecture notes:

Every open choice in `notes/scope/mental-map.md` becomes an ADR or a named deferral. The published
2018 BC decision tree and the open `BC_CFFBPS_FuelTyping_Tool` (GPL-3.0) are the primary fuel-typing
method; the current BCWS operational version is an optional benchmark, not a gate. P1.4 records the
tool commit, licence, and the LiDAR attribute mapping.

Child task checklist:

- [ ] #9 P1.1: Decide the weather method and record it as an ADR
- [ ] #10 P1.2: Approve the fuel crosswalk and grouped-code sensitivity plan
- [ ] #11 P1.3: Decide the analysis resolution and effective-resolution table
- [ ] #12 P1.4: Implement the open fuel-typing method and define the LiDAR input mapping
- [ ] #13 P1.5: Define the 10-class FBP and two-class WUI priority rule

Acceptance criteria:

- every open choice in `notes/scope/mental-map.md` has an accepted ADR or a named deferral;
- the published decision tree and open tool (or a clean reimplementation) are recorded, with the
  tool commit and GPL-3.0 licence; the current BCWS version is an optional benchmark;
- the weather method runs end to end on the three test zones;
- the priority rule is cited, reproducible, and has at least two alternatives for sensitivity.

Verification:

```bash
python scripts/dashboard.py
python scripts/check_workflow.py
```

Closeout requirements:

- post a closeout comment with the ADR list, the open fuel-typing tool record, and the weather-method run;
- open the phase pull request with the report in `notes/reports/p1-closeout.md`;
- do not close the parent issue until the phase pull request has merged.
