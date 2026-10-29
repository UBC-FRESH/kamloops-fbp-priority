# ADR 0006: Daily weather method for FWI and FBP

Status: proposed; P1.1 decision pending
Date: 2026-10-29
Issues: #9

## Context

ADR 0002 documents the Phase 0 compromise: ClimateBC monthly means, a fixed 20 km/h wind from 225°,
and a 62-day spin-up. ClimateBC has no wind variable and does not provide a daily sequence. The FWI
System is recursive, so a single mean day is not a valid input. The proposal asks for mean July and
August 13:00 weather, but the method must still produce a physically consistent daily sequence.

P1.1 must choose a daily source, define the sequence and spin-up, and define the mean-summer versus
percentile comparison. The choice affects every downstream FBP result and must be defensible to Leah
and BCWS.

## Decision

Use **ERA5-Land** as the primary daily weather source for 2014–2023:

- extract hourly 2 m temperature, 2 m dewpoint temperature, 10 m u and v wind, and total
  precipitation for the KFC bounding box;
- aggregate to 13:00 local time and derive relative humidity from temperature and dewpoint;
- compute wind speed and direction from the 10 m components;
- run the FWI sequence on the native 0.1° (~9 km) grid; if the 4 km pipeline grid is retained for
  compatibility, record it as interpolation in the effective-resolution table;
- run a full fire-season spin-up (1 April–31 August) for each year rather than a 62-day July start;
- define two scenarios: a mean-summer sequence (the 2014–2023 average of daily 13:00 weather for
  1 July–31 August) and percentile sequences (90th, 95th, and 99th percentile fire weather);
- retain the fixed 20 km/h wind from 225° as a sensitivity case, not as the primary method.

Use BCWS station observations, if access is granted, to validate the ERA5-Land temperature, RH, and
wind at the station locations. Do not use station data to silently correct the gridded fields; record
any bias correction as a separate, tested step.

Keep ClimateBC for spatial climate normals and future scenarios. Do not use it as a daily weather
source.

## Consequences

- The wind gap is resolved with an open, documented, daily product.
- ERA5-Land is ~9 km and cannot resolve local terrain channeling or stand-level wind. The thesis must
  state this and treat the FWI field as regional, not stand-level.
- The daily sequence makes the FWI codes physically consistent and allows percentile scenarios that
  are comparable to the mean-summer case.
- The data volume and runtime are larger than the monthly prototype: ten fire seasons of daily FWI
  rather than one 62-day sequence.
- Access requires a Copernicus Climate Data Store account and acceptance of the Copernicus licence.
  Creating an external account needs maintainer approval before the download.
- BCWS station data are sparse in the mountains; validation may be limited to a few stations.

## Alternatives considered

- **BCWS stations only.** Rejected as the primary source: the network is sparse, station records have
  gaps, and access is not guaranteed. Retained as validation.
- **ClimateBC monthly means plus a fixed wind.** Rejected as the primary method: it is not a daily
  sequence and the wind is an assumption. Retained as a sensitivity case.
- **Weather generator calibrated to ClimateBC.** Deferred: more parameters and harder to defend than
  a documented reanalysis, with no clear gain for a methods comparison.
- **ERA5 (0.25°) or a coarser reanalysis.** Rejected: ERA5-Land provides a finer grid at no extra
  licensing cost.
- **Daymet or a similar 1 km daily product.** Rejected for this decision: it provides daily
  temperature and precipitation but not the 13:00 RH and wind fields the FWI method needs.
