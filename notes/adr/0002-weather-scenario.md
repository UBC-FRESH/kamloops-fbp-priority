# ADR 0002: Mean-summer weather scenario and the ClimateBC gap

Status: superseded by ADR 0006 (accepted 2026-10-29)
Date: 2026-10-28
Issues: #1

## Context

The proposal asks for mean July/August 13:00 temperature, RH, precipitation, wind speed, and wind
direction over the past ten years, sourced from ClimateBC. ClimateBC 7.60 publishes monthly means
and has no wind variable. The FWI System is a daily recursive system: FFMC, DMC, and DC depend on
the previous day's state. A single mean day is not a valid FWI input.

## Decision

For the Phase 0 prototype only:

- average the 2014–2023 July and August monthly Tmax, RH, and PPT rasters;
- use Tmax as the 13:00 temperature proxy and monthly RH as the 13:00 RH proxy;
- spread monthly precipitation evenly across the days of the month;
- use a fixed 20 km/h wind from 225° because ClimateBC has no wind;
- run a 62-day sequence (1 July–31 August) from FFMC 85, DMC 6, DC 15;
- take the 31 August FWI codes as the mean-summer scenario;
- compute FWI at 4 km for the prototype and resample the codes to the 100 m FBP grid.

This is a **climatological screening scenario**, not a reconstruction of a real fire-weather day.

## Consequences

- The baseline maps show what mean-summer weather produces under the current fuel layer; they are
  not comparable to PSTA extreme-weather maps.
- The FFMC is relatively low (mean 81) because rain is spread evenly; BUI is high (mean 120).
- The wind assumption dominates the FBP ROS/HFI uncertainty. P1.1 must run a wind sensitivity.
- The production method should add a daily source (ERA5-Land or BCWS stations) or a weather
  generator, and should keep ClimateBC for spatial normals and future scenarios.

## Alternatives considered

- Use a single mean day directly in `fwi()`. Rejected: the FWI codes are path-dependent.
- Use the 90th–99th percentile weather. Rejected for the baseline because the proposal explicitly
  wants mean weather and because the PSTA already covers the extreme case.
- Use ClimateBC monthly means as if they were daily. Rejected: it would misstate the method.
