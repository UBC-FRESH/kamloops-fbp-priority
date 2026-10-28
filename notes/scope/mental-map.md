# Kamloops FBP priority project: scope, scale, and shape

Status: draft for Leah and the FRESH maintainers. This is the feasibility map produced by the
October 2026 speed run. It is deliberately blunt about what is known, what is assumed, and what
still has to be decided.

## 1. What Leah has agreed to deliver

The MGEM project is a methods-comparison and decision-support project, not a single map. By April
2027 it needs to answer:

1. Can a LiDAR-improved fuel-type layer produce materially different FBP fire behaviour than the
   existing VRI-derived provincial fuel-type layer?
2. How do those differences propagate into a fuel-treatment priority map for the Wildland-Urban
   Interface (WUI)?
3. How sensitive are the priorities to treatment assumptions, weather scenario, and climate change?

The study area is the Kamloops Fire Centre (KFC), 71,579 km². The proposal chooses three BEC zones
as the method test: ICH, IDF, and PP. Those three cover 34,778 km², or 48.6% of the KFC. The
methods are meant to be repeatable for the other five fire centres.

The final "boss" is a reproducible pipeline plus a defensible priority map, not just a raster:

- VRI 2025 + LidarBC + PSP → improved fuel attributes and FBP fuel types per BEC zone;
- ClimateBC + DEM + fire perimeters → FWI codes and topography;
- cffdrs FBP → ROS, HFI, flame length, fuel consumption, CFB, fire type;
- BCWS WUI layers + FBP classes → fuel-management priority classes;
- sensitivity analysis, thesis, and a public repository.

## 2. The proposal in one page

The proposal's method chain (Figure 4 of the draft) is:

```text
VRI attributes ─┐
LiDAR attributes ─┼─> train per-BEC model ─> adjusted VRI attributes ─┐
fire perimeters ──┘                                                   │
                                                                      v
ClimateBC mean July/August weather ─> FWI codes ───────────────> BCWS fuel typing ─> FBP fuel types
DEM ─> elevation, slope, aspect ────────────────────────────────────────────────┘
                                                                      │
                                                                      v
                                          cffdrs FBP ─> ROS, HFI, fuel consumption, CFB, fire type
                                                                      │
WUI Human Interface Buffer + WUI Risk Class ─────────────────────────> priority map
```

The proposal's key methodological choice is to use **mean July/August weather over the past ten
years**, not the 90th–99th percentile extreme weather used by the PSTA. That is a deliberate
attempt to avoid over-prioritising rare fire weather. It is also the choice that creates the
largest data-method gap (see Finding 1).

## 3. What the speed run actually built

The speed run proves the data plumbing and the baseline FBP chain, not the LiDAR research
contribution:

- rendered the UBC-FRESH dev-workflow seed into this repository;
- fetched the KFC boundary, BEC map, WUI layers, and the provincial fuel-type layer from the BC
  Data Catalogue through `femic`'s documented WFS/FGDB paths;
- fetched 2014–2023 ClimateBC July/August rasters and built 10-year means;
- fetched a 30 m Copernicus DEM and derived slope/aspect on a 100 m BC Albers grid;
- built a 100 m analysis grid (7.16 million KFC cells) and rasterized BEC, fuel type, WUI, and
  terrain;
- ran the official `cffdrs::fwiRaster` over a 62-day mean-summer weather sequence;
- ran the official `cffdrs::fbpRaster` over the 100 m stack;
- produced baseline fire-behaviour rasters, a provisional priority surface, zonal summaries, and
  the figures in `docs/figures/`.

What it deliberately did **not** do is the LiDAR/VRI fuel-typing experiment. That is the research
core and the critical path. The speed run tells us how much work that core is and what it depends
on.

## 3a. What the baseline actually shows

The first real result is a mean-summer baseline, not an extreme-weather PSTA-style map. The 4 km
FWI sequence ends with FFMC 56.6–88.0 (mean 81.0), BUI 1.4–209.1 (mean 119.8), and FWI 0.3–35.9
(mean 18.1). The moderate FFMC is a consequence of spreading monthly rain evenly; the high BUI is
the accumulated seasonal drought. The FBP maps are therefore dominated by surface fire, with crown
fire concentrated in the driest IDF/PP valleys.

The 100 m three-zone run (the method test):

| Zone | Area km² | HFI mean | HFI p90 | HFI p99 | HFI max | ROS mean | ROS p90 | Flame mean | Flame p90 | CFB mean | Crown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| IDF | 18,503 | 1,828 | 3,013 | 21,061 | 118,907 | 4.99 | 12.71 | 2.00 | 3.09 | 0.007 | 0.1% |
| ICH | 13,322 | 697 | 1,674 | 7,517 | 72,324 | 1.17 | 2.86 | 1.05 | 2.36 | 0.008 | 0.0% |
| PP | 2,950 | 1,562 | 2,943 | 11,274 | 104,045 | 7.46 | 18.00 | 1.79 | 3.05 | 0.001 | 0.0% |

The 200 m full-KFC run gives the same ordering but higher values and much more crown fire:

| Zone | HFI mean | HFI p90 | HFI p99 | ROS mean | CFB mean | Crown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| IDF | 1,972 | 3,334 | 21,921 | 5.11 | 0.094 | 4.2% |
| ICH | 751 | 1,871 | 7,819 | 1.22 | 0.030 | 0.6% |
| PP | 1,656 | 3,119 | 11,693 | 7.58 | 0.075 | 4.8% |
| ESSF | 716 | 1,475 | 10,204 | 1.51 | 0.037 | 0.8% |
| MS | 1,804 | 3,172 | 17,908 | 2.58 | 0.080 | 1.4% |

That difference is not noise. Coarsening fuel and terrain from 100 m to 200 m increases the
connected fuel/terrain combinations and changes the crown-fire classification by an order of
magnitude in IDF and PP. The thesis must treat resolution as a sensitivity axis, not as a
cosmetic choice. The 100 m run is the method test; the 200 m run is the KFC overview.

The provisional priority surface is deliberately conservative. Within the three zones, the WUI
covers 12,996 km² (IDF 7,492; ICH 3,091; PP 2,413), but only 109.6 km² in IDF, 32.9 km² in ICH, and
29.7 km² in PP reach provisional priority 7 or higher. Most WUI area falls in classes 1–5 under
mean-summer weather. That is a useful finding: the mean-weather scenario does not produce a map
dominated by extreme HFI; it concentrates the high-priority cells in the dry valley bottoms and
their immediate slopes. Whether that is the right policy signal is exactly what P1.5 and P4 must
test.

## 4. Data audit

| Layer | Source and access | Size / extent | Resolution / CRS | Measured facts | Quirks that matter |
| --- | --- | --- | --- | --- | --- |
| KFC boundary | BC Data Catalogue `bc-wildfire-fire-centres`, WFS via `femic` | 1 polygon | vector, EPSG:3005 | 71,579.2 km²; bounds 1,159,610–1,556,647 E, 457,489–890,472 N | Boundary is a single polygon with 124k vertices; use it as the mask, not the bbox |
| BEC map | `bec-map`, WFS via `femic` | 2,982 polygons clipped to KFC; 13 zones present | vector, EPSG:3005 | ESSF 21,587; IDF 18,504; ICH 13,324; MS 10,847; PP 2,950; BG 1,648; IMA 1,863; SBS 657; SBPS 124; BAFA 49; CWH 24 km² | The proposal says all 16 zones occur in the KFC; only 13 have non-zero area in the current map. CDF, BWBS, SWB are absent |
| FBP fuel types | `bc-wildfire-fire-fuel-types-public`; 2.48 GB provincial FGDB | 1,388,353 polygons in the KFC bbox | vector, EPSG:3005 | C-3, O-1a/b, C-7, N, C-2, D-1/2, C-5, W, M-1/2, S-1, C-4 | Grouped codes (`D-1/2`, `M-1/2`, `M-3/4`, `O-1a/b`) need explicit crosswalk decisions; WFS is not viable at 1.39 M features |
| VRI 2025 R1 | BC Data Catalogue direct FGDB | 4.17 GB zipped | vector, EPSG:3005 | 100+ attributes; no public WFS path in the package | Provincial download; must be clipped and staged. This is the largest single data object |
| LidarBC index | ArcGIS Feature Service `LiDAR_BC_S3_Public` | 34,245 point-cloud tiles in the KFC bbox; 10 project extents | vector, EPSG:3005 | Project extents cover 45.7% of KFC; point-cloud tiles 26.8%; DEM 1:20k 30.0%; DSM 1:2.5k 19.1%; DSM 1:20k 17.0% | The proposal's "54% of KFC" is not reproducible from the current index with a simple KFC intersection. See Finding 3 |
| ClimateBC | `climatebc.ca/SpatialData`, direct GeoTIFFs | 80 files × ~3 MB for 2014–2023 July/August Tmax/Tmin/RH/PPT | 0.008333°, EPSG:4326 (tag missing in the files) | July Tmax 5.8–32.1 °C; RH 47–83%; PPT 10–173 mm | No wind variable; monthly means, not daily 13:00 observations; no CRS tag; historical years end at 2023 |
| DEM | BC CDED 1:250,000 (`digital-elevation-model-for-british-columbia-cded-1-250-000`), zipped by NTS 1:20k tile | hundreds of tiles; ~2 MB each; 20 m | CDED raster, NAD83 geographic | Prototype used 24 Copernicus GLO-30 tiles (~800 MB) as a drop-in 30 m DEM | CDED must be assembled from many NTS tiles; the production run should use the named BC source, not the Copernicus substitute |
| WUI buffer | `bc-wildfire-wui-human-interface-buffer`, WFS | 413 polygons, 2.1 MB FGDB | vector, EPSG:3005 | 2 km buffer around >6 structures/km² | Direct FGDB and WFS both work; WFS returned 413 features for the KFC bbox |
| WUI risk class | `bc-wildfire-wildland-urban-interface-risk-class`, WFS | 2.9 MB FGDB | vector, EPSG:3005 | 2.75 km buffer around >25 structures/km² | Class 2 area is larger than class 1 in the KFC (15,164 km² vs 5,437 km²) because the layers are separate products, not nested |
| Fire perimeters | `bc-wildfire-fire-perimeters-current` and `...-historical` | current: zipped shapefile; historical: KMZ by season or WFS | vector, EPSG:3005 | Not yet materialized in the prototype | Needed for the BCWS fuel-typing "recent burn" rule (fires since 2016) |
| PSP plots | `forest-inventory-ground-plot-data...` | province-wide; optional | vector | Not used in the prototype | The proposal itself marks PSP comparison as optional; it is not on the critical path |

The demo's data footprint is already material: 2.5 GB fuel FGDB, 4.2 GB VRI, ~0.8 GB DEM, ~0.25 GB
ClimateBC, plus 34k LiDAR tile records. The raw data must stay out of git and be fetched by script.

## 5. The hard findings

### Finding 1: ClimateBC cannot supply the weather the proposal specifies

The proposal lists temperature, RH, precipitation, **wind speed, and wind direction** from
ClimateBC. ClimateBC 7.60's published variable list (annual, seasonal, monthly, and monthly2) has no
wind variable. It also provides monthly means, not daily 13:00 observations. The FWI System is a
daily recursive bookkeeping system: FFMC, DMC, and DC on day *t* depend on day *t−1*. A single
"mean July/August day" cannot be fed into `fwi()` without an explicit antecedent-state assumption.

The speed run used this explicit, documented scenario:

- temperature = 2014–2023 mean July/August Tmax (a 13:00 proxy);
- RH = 2014–2023 mean July/August RH (a 13:00 proxy);
- precipitation = monthly total spread evenly across days;
- wind = fixed 20 km/h from 225° (no ClimateBC source);
- a 62-day spin-up from FFMC 85, DMC 6, DC 15;
- FWI codes taken from the final day (31 August).

That is a defensible **mean-summer scenario**, but it is not the proposal's "average daily 13:00
weather". The project must choose one of:

1. add a daily weather source (ERA5-Land or BCWS station observations) for wind and for the daily
   sequence, and use ClimateBC for the spatial climate normals/future scenarios;
2. use a weather generator to disaggregate ClimateBC monthly means into daily sequences;
3. keep the mean-summer scenario and state that it is a climatological screening scenario, not a
   reconstruction of a real fire-weather day.

This decision changes every downstream FBP number. It needs to be made before the LiDAR comparison,
not after.

### Finding 2: the fuel layer is grouped, enormous, and already a model output

The provincial fuel-type layer is not raw data. It is the VRI-derived output of the BCWS fuel
typing algorithm. The research contribution is to re-derive or adjust it with LiDAR, so the
baseline and the improved layer must use the same FBP code crosswalk.

The BC layer uses grouped codes that do not map one-to-one to the cffdrs R raster codes (1–19):

- `D-1/2` → D-1 (leafless, more flammable) in the prototype;
- `M-1/2` → M-2 (green summer mixedwood) in the prototype;
- `M-3/4` → M-3 (leafless dead-fir, more flammable) in the prototype;
- `O-1a/b` → O-1b (standing grass) in the prototype.

The cffdrs R `fbpRaster` does not support D-2 at all; the Python port does. A sensitivity run that
tests the alternate grouped-code choice is mandatory. The 1.39 M polygons also mean the fuel layer
should be processed as an FGDB, not through WFS paging.

### Finding 3: the LiDAR coverage claim is method-dependent

The proposal says 54% of the KFC has LiDAR coverage. The current LidarBC index gives different
numbers depending on which product is counted:

| Product | KFC coverage | ICH | IDF | PP |
| --- | ---: | ---: | ---: | ---: |
| Project extent (layer 0) | 45.7% | 26.8% | 58.3% | 71.0% |
| Point-cloud tiles (layer 4) | 26.8% | 19.2% | 31.2% | 58.8% |
| DEM 1:20k (layer 6) | 30.0% | 9.0% | 46.1% | 30.2% |
| DSM 1:2,500 (layer 1) | 19.1% | 17.8% | 18.8% | 48.0% |
| DSM 1:20k (layer 3) | 17.0% | 9.0% | 23.4% | 13.4% |

None of these is 54%. The likely explanations are a different index vintage, a different KFC
boundary version, or a calculation that unions project extents rather than intersecting point-cloud
tiles. This matters because **only point clouds support the five LiDAR attributes the proposal
needs** (canopy cover, height, live stems, dead stems, and BCLCS level 5). DSM/DEM products support
canopy height and cover but not stand density or dead stems.

The practical consequence: the LiDAR-improved fuel typing may be feasible in IDF and PP (31% and
59% point-cloud coverage) and much weaker in ICH (19%). The per-BEC extrapolation model must be
honest about where it is extrapolating. The 54% claim should be replaced with a table that names the
product, the index version, and the calculation.

### Finding 4: 30 m is a false-resolution trap

The proposal converts every layer to 30 m. The effective resolutions are:

| Input | Native resolution | What 30 m actually carries |
| --- | --- | --- |
| ClimateBC | 0.008333° (~800 m) | interpolated smooth weather, not 30 m information |
| CDED 1:250k | 20 m grid, 1:250k source | terrain detail, but the source map is coarse |
| VRI polygons | variable, often 0.02–1 ha | polygon boundaries and attributes, not 30 m truth |
| LiDAR | ~1 m point cloud, 8 pts/m² | genuine fine-scale canopy structure |
| WUI | vector buffers | boundaries, not 30 m data |

A 30 m grid creates 79.5 M pixels for the KFC and 38.6 M for the three test zones. That is feasible
with chunking, but it does not create 30 m climate or 30 m VRI. A defensible design is a 100 m
screening grid (7.16 M KFC pixels) for the climate/fuel comparison, with a 30 m core for the
LiDAR-derived canopy/fuel layers where the data actually supports it. The thesis should include an
effective-resolution table and a resolution sensitivity run.

### Finding 5: the BCWS fuel-typing algorithm is the critical path

The proposal's central method is to re-run the BCWS 21-attribute fuel-typing algorithm on
LiDAR-adjusted VRI attributes. The algorithm is not a public code library in the same sense as
`cffdrs`; the proposal says it has been provided for the project and that permission must be
obtained. Until that permission and the exact algorithm version are in hand, the project cannot
produce the LiDAR-improved fuel types. It can only:

- compare the provincial fuel-type layer with LiDAR-derived canopy attributes;
- run FBP on the provincial baseline;
- show where the baseline and LiDAR disagree.

That is still useful, but it is not the thesis the proposal describes. Confirm access in writing
before January 2027. This is the number-one schedule risk.

### Finding 6: the final 10-class and WUI rule is undefined

The proposal says the FBP outputs will be classified into ten classes based on suppression efficacy,
then combined with two WUI classes. It does not define the class breaks or the combination matrix.
The prototype uses a provisional 10-class HFI scale and a simple WUI overlay. Those are placeholders,
not results.

The project needs a written classification rule, with citations:

- HFI class breaks and whether fire type (surface/intermittent/crown) is a separate dimension;
- whether ROS, CFB, and fuel consumption enter the class or only HFI;
- how the two WUI density classes weight the FBP class;
- whether areas outside the WUI are shown as hazard-only or excluded from priority.

This is a decision for Leah with BCWS input, not something an agent should invent.

## 6. Scale and compute

| Grid | KFC pixels | Three-zone pixels | Notes |
| --- | ---: | ---: | --- |
| 800 m | 111,842 | 54,340 | ClimateBC native; FWI prototype now at 4 km |
| 200 m | 1,789,475 | 869,450 | useful sensitivity scale |
| 100 m | 7,157,982 | 3,477,800 | prototype analysis grid |
| 30 m | 79,532,222 | 38,642,222 | proposal target; needs chunking/parallelism |

At 30 m, one float32 layer is 318 MB before compression; six FBP outputs are ~1.9 GB per scenario.
A multi-scenario, multi-fuel-variant experiment will be tens of GB. The 100 m prototype is ~1/11th
of the pixels and is the right scale for method development.

Measured runtimes on this host (72 cores, 754 GB RAM, 8 R workers):

| Run | Cells in the raster | Wall time |
| --- | ---: | ---: |
| 200 m full KFC FBP | 4,301,676 | 0.97 min |
| 100 m three-zone FBP (full rectangle) | 17,198,401 | 3.73 min |
| 4 km FWI, 62 days | 11,009 | minutes |

The FBP kernel is not the bottleneck at 100 m. A 30 m full-KFC FBP is roughly 4.6× the 100 m
rectangle, so about 17 minutes per scenario with the same worker count; the input stack and
data.table memory are the practical constraints, not the cpu time. The bottleneck is the daily FWI
loop: the 800 m `fwiRaster` run reached day 10 in roughly 20 minutes before it was stopped, while the
4 km run completed all 62 days in minutes. The production FWI should stay at 800 m or 1.6 km and
parallelize the daily loop, or use a vectorized implementation validated against `cffdrs`. There is
no reason to compute FWI at 30 m; the weather is not 30 m information. The production FWI grid
should be 800 m or 1.6 km, not 4 km, once the daily loop is parallelized.

## 7. The shape of the work: phase plan to April 2027

This is aggressive but realistic if the critical path is protected. The dates are working targets,
not promises.

| Phase | Window | Deliverable | Gate |
| --- | --- | --- | --- |
| P0 Bootstrap and feasibility | Oct 2026 | This repo, data audit, baseline FBP speed run, mental map | Repo green; baseline outputs exist |
| P1 Method contract | Nov 2026 | Weather decision, fuel crosswalk, class/WUI rule, resolution decision; ADRs | Leah + BCWS sign off on the contract |
| P2 Baseline KFC | Dec 2026 | Baseline FBP rasters for KFC and three zones; validation against published FBP values; first priority map | Baseline reproducible; sensitivity to wind and resolution |
| P3 LiDAR/VRI experiment | Jan 2027 | VRI clip, LiDAR tile processing, canopy metrics, PSP comparison, per-BEC model | Improved attributes and fuel types for three zones |
| P4 Comparison | Feb 2027 | Baseline vs LiDAR-improved FBP; map differences; uncertainty | Research question 1 answered |
| P5 Priority and scenarios | Mar 2027 | WUI overlay, 10-class rule, treatment assumptions, climate scenarios, sensitivity | Research questions 2 and 3 answered |
| P6 Thesis and release | Apr 2027 | Thesis, repo release, data provenance, defense | Committee-ready |

The LiDAR/VRI experiment must start by January. If BCWS algorithm access or point-cloud coverage is
not resolved by then, the project should narrow to a two-zone comparison (IDF and PP) rather than
pretend the ICH coverage is adequate.

## 8. The boss: definition of done

- [ ] Data provenance and licences recorded for every layer; raw data reproducible by script.
- [ ] A documented weather method that resolves the ClimateBC wind/daily gap.
- [ ] Baseline FBP outputs: ROS, HFI, flame length, fuel consumption, CFB, fire type.
- [ ] A LiDAR-improved fuel-type layer for at least IDF and PP, validated against VRI and PSP.
- [ ] A quantitative baseline-vs-LiDAR comparison of fire behaviour.
- [ ] A WUI overlay and a written 10-class priority rule.
- [ ] Sensitivity analysis: grouped fuel codes, wind, weather scenario, resolution, class breaks.
- [ ] A reproducible repository with tests, docs, and a tagged release.
- [ ] Thesis chapters, figures, and a committee-ready defense.

## 9. Decisions needed now

1. **Weather source.** Add ERA5-Land/BCWS daily data, or accept a ClimateBC monthly-mean scenario?
   Recommendation: add daily wind and a daily sequence; keep ClimateBC for spatial normals/future
   scenarios.
2. **LiDAR product and coverage claim.** Which LidarBC product defines "coverage"? Recommendation:
   report point-cloud coverage separately from project/DSM coverage, and replace "54%" with the
   product-specific table.
3. **BCWS algorithm access.** Confirm the exact algorithm version, permission, and input schema.
   Recommendation: make this a written gate before P3.
4. **Analysis resolution.** Recommendation: 100 m for the method comparison, 30 m only for the
   LiDAR core; include a resolution sensitivity run.
5. **Priority rule.** Recommendation: adopt an explicit HFI × fire-type × WUI matrix with citations,
   and test at least two alternatives.
6. **Study-area scope.** Recommendation: ICH, IDF, PP as the method test, but report ICH with a
   stated LiDAR-coverage limitation; do not extrapolate ICH results as if they were observed.

## 10. What the speed run did not do

- No LiDAR point-cloud processing, canopy metrics, or VRI/LiDAR model.
- No PSP validation.
- No BCWS fuel-typing algorithm run.
- No climate-change scenarios.
- No final 10-class/WUI rule; the prototype's priorities are provisional.
- No 30 m full-KFC run; the 100 m run is the method prototype.
- No GitHub repository or issues yet; the local repository is seeded and on the Phase 0 branch.

## 11. Reproducibility

Every downloaded layer has a manifest under `data/raw/*/manifest.json`. The analysis scripts are in
`analysis/`; the R wrappers use the conda environment in `.conda/envs/fbp` (ignored by git) and the
official `cffdrs` 1.9.2 package. The green dashboard covers the seed's framework; the prototype
scripts are linted but not yet coverage-gated. The production pipeline should promote the vetted
functions into the project package and add them to the gate.
