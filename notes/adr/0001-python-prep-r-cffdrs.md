# ADR 0001: Python for data preparation, R cffdrs for FWI and FBP

Status: proposed for the Phase 0 close-out
Date: 2026-10-28
Issues: TBD

## Context

The project must use the Canadian Forest Fire Behaviour Prediction System through the official
`cffdrs` code. The R package is the reference implementation and provides `fwiRaster` and
`fbpRaster`, which are designed for raster stacks. The official Python port is useful for point
calculations and validation but has no raster functions. The lab's `femic` package provides the
BC Data Catalogue WFS/FGDB acquisition path and is Python.

## Decision

Use Python for data acquisition, rasterization, terrain, post-processing, and figures. Use R
`cffdrs` 1.9.2 in a local conda environment for `fwiRaster` and `fbpRaster`. The hand-off is a
documented multi-band GeoTIFF plus a band-order manifest. The R environment is ignored by git; the
environment recipe and wrapper scripts are tracked.

## Consequences

- The FBP and FWI calculations use the same code as the paper and BCWS, not a reimplementation.
- The project is polyglot. A new contributor needs both Python and R; the wrapper scripts hide the
  R invocation.
- The conda R environment must be recreated on a new machine. P1 should add an exported environment
  lock file and a clean-checkout test.
- The Python port remains available for independent point validation and for the vectorized
  performance work if the R raster path becomes a bottleneck.

## Alternatives considered

- Python port only. Rejected for the baseline because it has no raster API and the 100 m/30 m
  production path would require a reimplementation.
- R only. Rejected because the lab's BC Data Catalogue and raster tooling is Python.
- Desktop FBP software. Rejected by the proposal and by the reproducibility requirement.
