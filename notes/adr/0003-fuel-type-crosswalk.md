# ADR 0003: BC fuel-type crosswalk to cffdrs raster codes

Status: proposed; confirm with BCWS in P1.2
Date: 2026-10-28
Issues: TBD

## Context

The BC provincial fuel-type layer uses grouped codes (`D-1/2`, `M-1/2`, `M-3/4`, `O-1a/b`) and
modifier-prefixed codes (`B26_O-1a/b`, `B71_S-2`, ...). The cffdrs R `fbpRaster` needs one numeric
code per cell, in the order 1–19, and does not include D-2. The scientific question is how much the
grouped-code choice changes the fire-behaviour comparison.

## Decision

- Strip a leading `B<digits>_` modifier before mapping; the suffix is the FBP fuel type.
- Map `D-1/2` to D-1 (leafless, more flammable).
- Map `M-1/2` to M-2 (green summer mixedwood).
- Map `M-3/4` to M-3 (leafless dead-fir, more flammable).
- Map `O-1a/b` to O-1b (standing grass).
- Use Table 7 crown base height and crown fuel load defaults by fuel type.
- Use `M1_2_PERCENT_CONIFER` for M1/M2 and `PERCENT_DEAD_FIR` for M3/M4 when populated.

## Consequences

- The baseline is reproducible and every choice is explicit.
- The grouped-code choice is a sensitivity axis, not a fact. P1.2 must run the alternate choices.
- D-2 cannot be represented in the R `fbpRaster` path. If D-2 matters, use the Python port for a
  point comparison or map D-2 to D-1 and state the bias.
- Modifier prefixes affect a large share of the layer; failing to normalize them would silently
  turn hundreds of thousands of polygons into non-fuel.

## Alternatives considered

- Treat every grouped code as non-fuel. Rejected: it would erase most of the KFC.
- Use the Python port only. Rejected for the raster baseline because it has no raster API.
- Ask BCWS for a disaggregated fuel-type raster. Preferred if available; record the version.
