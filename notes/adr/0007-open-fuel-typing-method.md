# ADR 0007: Open published fuel-typing method, BCWS benchmark optional

Status: accepted 2026-10-29
Date: 2026-10-29
Issues: #12, #8

## Context

The Phase 0 plan treated the BCWS 21-attribute fuel-typing algorithm as a permission gate. That was
too restrictive. The method is published and the 2018 implementation is open:

- Perrakis, Eade, and Hicks (2018) document the BC fuel-typing decision tree and the 21 VRI
  attributes in the provincial fuel type layer report (BC-X-444).
- Gregory Greene's `BC_CFFBPS_FuelTyping_Tool` implements the 2018 decision tree in Python and is
  public under GPL-3.0: https://github.com/gagreene/BC_CFFBPS_FuelTyping_Tool.
- Baron et al. (2024, Fire Ecology) independently coded the same decision tree and found that 58% of
  field plots in interior BC had no suitable FBP fuel type; LiDAR can improve the canopy attributes
  (height, cover, CBH, CBD) that the decision tree depends on.

The provincial fuel-type layer is open under the BC Data Catalogue. LidarBC point clouds are open
under OGL-BC. No permission is needed to use the published method, the open code, or the open data.

## Decision

The primary P3 method is an open, reproducible fuel-typing workflow:

1. Use the published 2018 decision tree, implemented by the GPL-3.0
   `BC_CFFBPS_FuelTyping_Tool` or a clean reimplementation of the published rules, as the fuel-type
   classifier.
2. Feed it the 21 VRI attributes for the baseline run, and a LiDAR-adjusted version of the same
   attributes for the improved run. The LiDAR adjustments replace or supplement VRI canopy height,
   crown closure, live/dead stems, and the derived canopy base height and bulk density where the
   point cloud supports them.
3. Compare three treatments: provincial fuel-type layer (published baseline), decision tree on VRI
   (reproduced baseline), and decision tree on LiDAR-adjusted attributes (improved).
4. Validate with held-out VRI polygons, fire perimeters, and expert review. Use the Baron et al.
   (2024) field findings as context; do not claim field validation unless the plot data are shared.

The current BCWS operational algorithm and version are an **optional benchmark**, not a gate. If
BCWS provides them, run them as a fourth treatment. If not, the open method stands on its own.

## Consequences

- The permission dependency is removed. P3 can start as soon as the VRI and LiDAR inputs are ready.
- The method is reproducible and citable. The tool version/commit and GPL-3.0 licence must be
  recorded.
- The project cannot claim to reproduce the current BCWS operational output exactly. It can claim a
  transparent implementation of the published decision tree, which is the right claim for a methods
  comparison.
- The LiDAR adjustment is the research contribution; the decision tree is the common classifier that
  makes the baseline and improved runs comparable.
- GPL-3.0 is copyleft. Keep the vendored tool in its own directory with its licence and attribution;
  do not relicense it as MIT. The project's original code remains MIT.

## Alternatives considered

- **Wait for BCWS permission.** Rejected: it blocks the thesis on an external schedule and is not
  required for the published method.
- **Use only the provincial fuel-type layer.** Rejected: no LiDAR contribution, so no thesis.
- **Clean-room reimplementation of the 2018 decision tree from the report.** Possible and compatible
  with MIT, but unnecessary while the GPL-3.0 tool is public and citable. Revisit only if licensing
  becomes a release constraint.
- **Use the national FBP fuel layer only.** Rejected: 250 m and less detailed than the provincial
  layer; useful as a cross-check, not as the primary method.
