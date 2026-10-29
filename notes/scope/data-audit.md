# Data audit for the Kamloops FBP project

This page records what was actually downloaded, what it cost, and what a downstream user must know
before using it. It complements `notes/scope/mental-map.md`; the mental map holds the interpretation,
this page holds the receipts.

All raw data lives under ignored `data/raw/`. Each fetch writes a manifest next to the payload. The
commands below are the ones used in the October 2026 speed run.

## 1. Administrative and ecological boundaries

### Kamloops Fire Centre

- Dataset: `bc-wildfire-fire-centres` (`WHSE_LEGAL_ADMIN_BOUNDARIES.DRP_MOF_FIRE_CENTRES_SP`).
- Access: `python -m femic data bcdc-fetch WHSE_LEGAL_ADMIN_BOUNDARIES.DRP_MOF_FIRE_CENTRES_SP --bbox ...`
- Result: one polygon, 71,579.2 km², EPSG:3005. The polygon has 124,319 vertices.
- Use: it is the mask, not the bounding box. The bounding box is 397 km × 433 km and includes
  surrounding fire centres and parts of the Cariboo, Coastal, and Prince George centres.

### BEC map

- Dataset: `bec-map` (`WHSE_FOREST_VEGETATION.BEC_BIOGEOCLIMATIC_POLY`), version 13.1 (July 2026).
- Access: WFS via `femic data bcdc-fetch`; 2,982 polygons clipped to the KFC.
- Measured areas: ESSF 21,587; IDF 18,504; ICH 13,324; MS 10,847; PP 2,950; IMA 1,863; BG 1,648;
  SBS 657; SBPS 124; BAFA 49; CWH 24; MH 0.4; CMA 0.2 km².
- The current map has 13 zones with non-zero area in the KFC. The proposal says all 16 occur; CDF,
  BWBS, and SWB are absent. This is a small but real discrepancy to reconcile in the thesis.

## 2. Fuel data

- Dataset: `bc-wildfire-fire-fuel-types-public`, provincial FGDB
  (`PROT_FUEL_TYPE_SP.gdb.zip`, 2,482,259,907 bytes).
- Access: parallel ranged download, then `pyogrio.read_dataframe(..., bbox=kfc_bounds)`.
- Result: 1,388,353 polygons intersect the KFC bounding box. The KFC clip is smaller.
- Codes include standard FBP types and modifier-prefixed variants:
  `C-3`, `C-7`, `C-5`, `O-1a/b`, `B26_O-1a/b`, `M-1/2`, `D-1/2`, `B71_S-2`, `B26_D-1/2`, `N`,
  `B01_N`, `B46_M-1/2`, `B21_D-1/2`, `C-2`, `W`, `C-6`, `B03_N`, `S-1`, `S-3`, `S-2`, `C-4`.
- The prefix before the first underscore is a BC modifier; the FBP type is the suffix. The prototype
  normalizes `B<digits>_` prefixes before the cffdrs crosswalk.
- The layer is a VRI-derived product, not raw inventory. It is the baseline against which the
  LiDAR-improved fuel types will be compared.
- VRI 2025 R1 (`vri-2025-forest-vegetation-composite-rank-1-layer-r1-`) is a 4,176,172,794-byte
  zipped FGDB. It is not needed for the baseline but is the main input to P3.

## 3. LiDAR index

- Service: `https://services6.arcgis.com/ubm4tcTYICKBpist/arcgis/rest/services/LiDAR_BC_S3_Public/FeatureServer`.
- Layers: 0 project extents, 1 DSM 1:2,500, 2 DSM 1:10,000 (empty), 3 DSM 1:20,000, 4 point-cloud
  index, 5 DEM 1:2,500, 6 DEM 1:20,000.
- KFC-bbox feature counts: 0→10, 1→18,868, 2→0, 3→218, 4→34,245, 5→18,549, 6→573.
- Coverage of the KFC (100 m raster intersection):

| Product | KFC | ICH | IDF | PP |
| --- | ---: | ---: | ---: | ---: |
| Project extent (0) | 45.7% | 26.8% | 58.3% | 71.0% |
| Point cloud (4) | 26.8% | 19.2% | 31.2% | 58.8% |
| DEM 1:20k (6) | 30.0% | 9.0% | 46.1% | 30.2% |
| DSM 1:2.5k (1) | 19.1% | 17.8% | 18.8% | 48.0% |
| DSM 1:20k (3) | 17.0% | 9.0% | 23.4% | 13.4% |

- The proposal's 54% is not reproduced by any of these product-specific calculations. The thesis
  must name the product and the formula. For the five proposed LiDAR attributes, point-cloud
  coverage is the relevant number, and it is 19.2% in ICH, 31.2% in IDF, and 58.8% in PP.
- Tile attributes include `year`, `density`, `maptile`, and `s3Url`; the point-cloud tiles are 8
  points/m² for 32,185 of the 34,245 tiles, with smaller counts at 4, 7, and 12 points/m².

## 4. ClimateBC

- Source: `https://climatebc.ca/SpatialData`; direct GeoTIFF pattern
  `https://media.forestry.ubc.ca/ClimateNA/BC/800m/Year_1901-current/Year_<year>/<variable>.tif`.
- Downloaded: 2014–2023, variables Tmax07, Tmax08, Tmin07, Tmin08, RH07, RH08, PPT07, PPT08 (80
  files, ~240 MB).
- The files have no CRS tag; the metadata says GCS WGS 1984. The prototype passes
  `src_crs="EPSG:4326"` explicitly.
- Variable list: the annual/seasonal/monthly/monthly2 lists include temperature, precipitation, RH,
  radiation, degree days, and drought indices. There is **no wind speed or wind direction**.
- The proposal's "average daily 13:00 weather" is not directly available: ClimateBC is monthly.
  The prototype's mean-summer spin-up is a documented assumption, not a reconstruction.

## 5. DEM

- Proposal source: `digital-elevation-model-for-british-columbia-cded-1-250-000`, zipped CDED tiles
  by NTS 1:20,000 sheet (e.g., `092h16_w.dem.zip`, ~1.6 MB, 1,201 × 1,201 at ~20 m).
- Prototype substitute: 24 Copernicus GLO-30 COG tiles (~800 MB), mosaicked and reprojected to the
  100 m grid. The terrain code is source-agnostic; the production run should switch the path to
  CDED and keep the same slope/aspect function.
- Slope/aspect are derived with Horn's finite differences; aspect is the direction of steepest
  descent, clockwise from north. The prototype's slope p50/p90/p99 are 19.7/60.7/95.5%.

## 6. WUI and fire perimeters

- WUI Human Interface Buffer: `bc-wildfire-wui-human-interface-buffer`, 413 polygons in the KFC
  bbox, 2.1 MB FGDB; 2 km buffer around >6 structures/km².
- WUI Risk Class: `bc-wildfire-wildland-urban-interface-risk-class`, 2.9 MB FGDB; 2.75 km buffer
  around >25 structures/km².
- Rasterized WUI classes: class 1 5,437 km², class 2 9,727 km², total 15,164 km² (21.2% of KFC).
  The two layers are not nested; class 2 is larger in the KFC, so the prototype uses
  `max(class1, class2)` with class 2 overriding.
- Fire perimeters current/historical are available from the BC Data Catalogue, but were not
  materialized in the speed run. They are required for the BCWS recent-burn rule in P3.

## 7. Accessibility and licence notes

- BC Data Catalogue layers are Open Government Licence – British Columbia unless the dataset page
  says otherwise. Record the licence and access date for each layer in the thesis appendix.
- ClimateBC data are CC-BY; cite Wang et al. (2016) and the ClimateBC version.
- Copernicus DEM is free and open under the Copernicus licence; the proposal's CDED source should be
  used in production.
- LidarBC data are Open Government Licence – British Columbia. Point-cloud tiles are large LAZ
  files served from `nrs.objectstore.gov.bc.ca`; budget storage and download time per tile.
- No raw data, credentials, or machine-specific paths are tracked in git.
