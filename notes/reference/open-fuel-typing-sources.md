# Open fuel-typing sources

Status: reference note for ADR 0007. Verified 2026-10-29.

## Why this note exists

The BCWS 21-attribute fuel-typing algorithm is often treated as a permission gate. It is not: the
method and the 2018 implementation are public. This note records the open sources, what each one
contains, and the smoke test that confirms the code runs.

## Sources

| Source | What it provides | Access |
| --- | --- | --- |
| Perrakis, Eade & Hicks (2018), *British Columbia Wildfire Fuel Typing and Fuel Type Layer Description*, BC-X-444 | The 21 VRI attributes, the decision-tree logic, assumptions, and limitations | https://publications.gc.ca/collections/collection_2019/rncan-nrcan/Fo143-2-444-eng.pdf |
| Perrakis, Eade & Hicks (2017), provincial fuel type layer report | The 2017 operational algorithm and Appendix A5 process charts | https://www2.gov.bc.ca/assets/gov/public-safety-and-emergency-services/wildfire-status/prevention/fire-fuel-management/fuels-management/bc_fuel_type_layer_2017.pdf |
| Perrakis, Eade & Hicks (2015), provincial fuel type layer report | The 2015 algorithm with the full decision table in Appendix A4 | https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/wildfire-management/fire-fuel-management/bcws_bc_provincial_fuel_type_layer_overview_2015_report.pdf |
| Greene (2023), `BC_CFFBPS_FuelTyping_Tool` | Python implementation of the 2018 decision tree; `bcwft2018.py` is a standalone class with `FuelTyping.getFuelType(...)` returning `(process, fuel type, modifier)` | https://github.com/gagreene/BC_CFFBPS_FuelTyping_Tool (GPL-3.0) |
| Swystun, Taylor & Simpson (2018), *FBP Fuel Layer Decision Rules* | National FBP decision rules for the 250 m Canadian Forest FBP fuel layer; useful cross-check | https://cwfis.cfs.nrcan.gc.ca/downloads/fuels/development/Canadian_Forest_FBP_Fuel_Types/FBP_Fuel_Layer_Decision_Rules.pdf |
| Baron et al. (2024), *Fuel types misrepresent forest structure and composition in interior British Columbia: a way forward*, Fire Ecology 20:14 | Independent assessment of provincial and national fuel maps against 76 field plots; 58% had no suitable FBP match; LiDAR can improve canopy height, cover, CBH, and CBD | https://doi.org/10.1186/s42408-024-00249-z |
| BC Data Catalogue, BC Wildfire Fire Fuel Types - Public | Provincial fuel-type polygon layer; open licence | https://catalogue.data.gov.bc.ca/dataset/bc-wildfire-fire-fuel-types-public |
| LidarBC Open LiDAR Data Portal | Point clouds, DEM, DSM; OGL-BC | https://lidar.gov.bc.ca |

## Smoke test

The 2018 tool ran in the project environment on 2026-10-29. A mature interior lodgepole-pine stand
with 50% crown closure, 20 m height, and 100% pine returned:

```text
(599, 'C-3', None)
```

The tuple is `(process number, FBP fuel type, modifier)`. The tool imports only `pandas`, `numpy`,
and the standard library; it does not require ArcGIS for this call.

The tool is vendored at `analysis/vendor/BC_CFFBPS_FuelTyping_Tool/` (commit
`13bc0c913437141e2984f530a2197296fb6da0b0`, GPL-3.0). Reproduce the check with:

```bash
python analysis/smoke_open_fuel_typing.py
```

## First real-data check (2026-10-29)

A 4 km × 4 km VRI sample around Kamloops (EPSG:3005 bbox `1398265,642886,1402265,646886`) returned
35 polygons. The open decision tree classified all 35 with no errors:

| Open fuel type | Count |
| --- | ---: |
| O-1b | 20 |
| N | 10 |
| C-7 | 4 |
| D-2 | 1 |

A centroid join to the provincial fuel-type layer gave 34 comparable polygons and **85.3% agreement**
after normalizing `O-1a/b`, `D-1/2`, and `M-1/2`:

| Open \ Provincial | C-7 | D-1/2 | N | O-1 | W |
| --- | ---: | ---: | ---: | ---: | ---: |
| C-7 | 3 | 0 | 0 | 1 | 0 |
| D-1/2 | 0 | 1 | 0 | 0 | 0 |
| N | 0 | 0 | 8 | 2 | 0 |
| O-1 | 0 | 0 | 1 | 17 | 1 |

This is a smoke comparison, not a validation study: one small area, a centroid join, and 34 polygons.
It proves the open method runs on real VRI data and produces a comparison surface. The full P3 run
needs the three zones, LiDAR overrides, and a proper validation design.

## What this changes

- The provincial decision tree can be run without BCWS permission.
- The LiDAR experiment can start from the published 21 attributes; the LiDAR metrics replace or
  supplement the canopy attributes, and the same decision tree classifies both runs.
- The current BCWS operational version remains an optional benchmark, not a gate.
- The 2024 Fire Ecology paper supplies the research gap and the validation context: the existing maps
  misrepresent dry interior, mixedwood/deciduous, and post-harvest stands; LiDAR improves the canopy
  attributes that the decision tree uses.

## Limits

- The open tool implements the 2018 decision tree, not necessarily the current BCWS operational
  version. Do not claim exact reproduction of current BCWS output.
- The tool is GPL-3.0. Keep it in its own vendored directory with its licence; do not relicense it as
  MIT.
- The Baron et al. field plots are not open; the paper's findings are context, not a validation
  dataset. Use held-out VRI polygons, fire perimeters, and expert review unless the plot data are
  shared.
