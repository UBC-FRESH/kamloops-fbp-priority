Task identifier: P1.1
Parent phase issue: #8
Status: active
Branch: `feature/p1-method-contract`
Related planning: `ROADMAP.md` (Phase 1), `notes/adr/0002-weather-scenario.md`,
`notes/adr/0006-weather-method.md`

Data access: the open ERA5-Land Zarr mirror recorded in ADR 0006; no CDS account is required for the
prototype. The mirror is a third-party copy, so the fetch code records the URL and missing chunks.

Goal:

Replace the Phase 0 mean-summer weather scenario with a defensible daily method, or explicitly
accept the scenario with a documented sensitivity plan.

Scope:

- resolve the ClimateBC wind gap with ERA5-Land, BCWS station data, or a documented design wind;
- define the daily weather sequence and the FWI spin-up;
- define the mean-summer versus percentile scenario comparison;
- run the method end to end on the three test zones.

Out of scope:

- the full production FBP run (P2);
- climate-change projections (P5);
- station-network installation or field data collection.

Subtasks:

- [ ] Inventory ERA5-Land and BCWS station access, coverage, and licensing.
- [ ] Compare daily sources against ClimateBC normals.
- [ ] Define the daily sequence, wind treatment, and spin-up.
- [ ] Define the mean-summer and percentile scenarios.
- [ ] Write ADR 0006 and supersede or confirm ADR 0002.
- [ ] Run the method on the three test zones and record the comparison.

Acceptance criteria:

- the chosen source and downscaling method are documented with provenance;
- the method produces a daily FWI sequence for the three zones;
- the fixed-wind assumption is replaced or retained only as a sensitivity case;
- ADR 0006 is accepted and linked from this issue.

Verification:

```bash
PYTHONPATH=analysis python analysis/prepare_climate.py
PYTHONPATH=analysis python analysis/coarsen_weather.py
./analysis/run_fwi.sh data/interim/weather_4km data/processed/fwi_4km.tif
```

Artifacts:

`notes/adr/0006-weather-method.md`, weather manifests, and a three-zone FWI comparison table.

Risks:

ERA5-Land is ~9 km and needs downscaling; BCWS stations are sparse and may have gaps; daily data
volume is much larger than the monthly prototype.
