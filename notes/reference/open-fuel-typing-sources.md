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

## Three-zone real-data check (2026-10-29)

Three 4 km × 4 km VRI samples, one in each test zone, were chosen where LidarBC point-cloud tiles
exist. The open decision tree classified every polygon with zero errors.

| Zone | Sample bbox (EPSG:3005) | Polygons | Comparable | Agreement |
| --- | --- | ---: | ---: | ---: |
| ICH | `1498398,561944,1502398,565944` | 175 | 173 | 81.5% |
| IDF | `1465073,548635,1469073,552635` | 121 | 121 | 84.3% |
| PP | `1458035,522214,1462035,526214` | 89 | 89 | 88.8% |
| **All** | — | **385** | **383** | **84.1%** |

Open fuel-type counts by zone:

| Zone | Dominant open types |
| --- | --- |
| ICH | C-5 51, M-2 44, C-3 37, D-2 18, S-1 11 |
| IDF | O-1b 48, C-7 42, M-2 23, C-3 4 |
| PP | C-7 60, O-1b 15, N 10, D-2 3 |

The earlier single-zone Kamloops sample (35 polygons, 85.3%) is superseded by this three-zone check.
This is a smoke comparison, not a validation study: small boxes, a centroid join, and normalized
grouped codes. It proves the open method runs across all three test zones and produces a comparison
surface. The full P3 run needs the complete zones, LiDAR overrides, and a proper validation design.

Per-zone tables: `docs/tables/open_vs_provincial_ICH.csv`, `..._IDF.csv`, `..._PP.csv`. The combined
table is `docs/tables/open_vs_provincial_fuel_types_three_zones.csv`; the summary is
`docs/tables/open_vs_provincial_agreement_by_zone.csv`.

## LiDAR candidates for the same boxes

The three sample boxes are fully covered by LidarBC point-cloud tiles at 8 points/m²:

| Zone | Tiles intersecting the box | Acquisition years | Box coverage |
| --- | ---: | --- | ---: |
| ICH | 13 | 2024 | 100% |
| IDF | 15 | 2017, 2024, 2025 | 100% |
| PP | 22 | 2017, 2024 | 100% |

The candidate tiles are listed in `docs/tables/lidar_candidates_three_zones.csv`. This means the
same boxes can carry the P3 LiDAR pilot without changing the study design.

## LiDAR pilot (one tile per zone)

One LAZ tile per zone was processed on a 10 m grid with a two-pass method: class-2 ground returns
build a nearest-filled ground surface, then first returns give canopy cover and height percentiles.
The tile footprints cover only part of each 4 km sample box, so this is a pilot, not the full box.

Cell-level medians:

| Zone | Canopy cover | Height p50 | Height p95 |
| --- | ---: | ---: | ---: |
| ICH | 0.95 | 10 m | 17 m |
| IDF | 0.60 | 3 m | 5 m |
| PP | 0.75 | 6 m | 14 m |

The LiDAR mean cover replaced `CROWN_CLOSURE` and the LiDAR mean p95 replaced `PROJ_HEIGHT_1`;
all other VRI attributes stayed unchanged. Rerunning the published decision tree changed:

| Zone | Comparable polygons | Fuel-type changes | Transitions |
| --- | ---: | ---: | --- |
| ICH | 43 | 1 (2.3%) | C-5 -> C-3 |
| IDF | 31 | 5 (16.1%) | O-1b -> C-7 (4), C-7 -> C-3 (1) |
| PP | 24 | 0 | none |

The IDF result is the expected signal: LiDAR detects canopy structure in stands the VRI calls open,
so four O-1b polygons become C-7. This is a pilot on one tile per zone, not a zone-wide result. It
shows the LiDAR-adjusted decision tree works and produces fuel-type changes worth testing at scale.

Scripts: `analysis/lidar_canopy_metrics.py`, `analysis/apply_lidar_to_vri.py`. Tables:
`docs/tables/lidar_fuel_type_changes_three_zones.csv`,
`docs/tables/lidar_fuel_type_change_summary.csv`, and the per-zone CSVs.

## FBP pilot on the changed polygons

The six changed polygons were run through `cffdrs::fbp` with the existing 100 m weather and terrain
bands sampled at their centroids. The baseline and LiDAR rows use the same weather, terrain, and
location; only the fuel type and its Table 7 crown defaults differ.

| Transition | n | ROS change | HFI change | Crown fire |
| --- | ---: | ---: | ---: | --- |
| O-1b -> C-7 | 4 | **-84.8%** | **+33.9%** | none |
| C-5 -> C-3 | 1 | **+267.6%** | **+293.6%** | none |
| C-7 -> C-3 | 1 | **+29.8%** | **+85.0%** | none |

The direction depends on the transition: converting open grass to C-7 lowers ROS but raises HFI;
converting C-5 or C-7 to C-3 raises both. All six remained surface fire under the mean-summer
weather; no crown fire. This is a six-polygon pilot, not a zone-wide result, but it shows that the
LiDAR-induced fuel-type changes are large enough to matter for the priority map.

Scripts: `analysis/prepare_lidar_fbp_points.py`, `analysis/run_lidar_fbp_points.R`. Tables:
`docs/tables/lidar_fbp_changed_polygons.csv`,
`docs/tables/lidar_fbp_changed_polygons_paired.csv`, and
`docs/tables/lidar_fbp_change_summary.csv`.

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
