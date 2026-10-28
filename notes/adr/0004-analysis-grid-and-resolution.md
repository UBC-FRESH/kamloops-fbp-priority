# ADR 0004: 100 m analysis grid and explicit effective resolution

Status: proposed; confirm in P1.3
Date: 2026-10-28
Issues: #1

## Context

The proposal resamples every layer to 30 m. The effective resolutions are mixed: ClimateBC is
~800 m, CDED 1:250k is a 20 m grid from a coarse source map, VRI polygons are variable, LiDAR is
~1 m, and WUI layers are vector buffers. A 30 m KFC grid has 79.5 M pixels; the three test zones
have 38.6 M. A 100 m grid has 7.16 M and 3.48 M respectively.

## Decision

Use a 100 m EPSG:3005 grid for the Phase 0/2 method comparison. Use 4 km for the prototype FWI
calculation because the official R loop is single-threaded; resample the FWI codes to 100 m. Keep
30 m as the target only for the LiDAR-derived canopy/fuel core where the data supports it. Publish
an effective-resolution table and a resolution sensitivity run.

## Consequences

- The method comparison can iterate in minutes rather than hours.
- The 30 m claim in the proposal is not silently repeated; the thesis must justify the resolution.
- The production 30 m run needs chunking/parallelism and a storage budget of tens of GB per
  multi-scenario experiment.
- The 4 km FWI grid is a prototype compromise; the production run should return to 800 m or 1.6 km
  with a parallel daily loop.

## Alternatives considered

- Run the full 30 m KFC now. Rejected for the speed run: the single-threaded R loop and 79.5 M
  pixels would take too long and would obscure the method questions.
- Run everything at 800 m. Rejected: it would lose the fuel/terrain detail that the LiDAR comparison
  is meant to test.
