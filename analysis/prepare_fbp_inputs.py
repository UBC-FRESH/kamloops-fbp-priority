"""Build the 100 m FBP input stack for the cffdrs R raster function.

The stack follows the cffdrs::fbpRaster contract. The band order is written to a
manifest so the R runner does not have to guess names.

Modelling assumptions carried into this stack:

- wind speed is a fixed 20 km/h and wind direction a fixed 225 degrees because
  ClimateBC publishes neither variable;
- day of year is 227 (15 August), the middle of the mean July/August window;
- grass curing is 80 percent for O-1b;
- grouped BC fuel codes follow analysis/kamloops_fbp/fuel.py.
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pyogrio
import rasterio
from pyproj import Transformer
from rasterio.enums import Resampling

from kamloops_fbp.fuel import (
    BC_TO_R,
    CBH_DEFAULT,
    CFL_DEFAULT,
    normalize_bc_fuel_code,
    percent_conifer,
    percent_dead_fir,
)
from kamloops_fbp.grid import (
    Grid,
    grid_from_bounds,
    mask_from_polygon,
    rasterize_vector,
    reproject_raster_to_grid,
)

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

BAND_ORDER = [
    "FUEL",
    "FFMC",
    "BUI",
    "WS",
    "WD",
    "GS",
    "Aspect",
    "LAT",
    "LONG",
    "ELV",
    "Dj",
    "PC",
    "PDF",
    "cc",
    "CBH",
    "CFL",
]
WIND_SPEED_KMH = 20.0
WIND_DIRECTION_DEG = 225.0
DAY_OF_YEAR = 227
GRASS_CURING = 80.0


def lat_lon(grid: Grid) -> tuple[np.ndarray, np.ndarray]:
    """Return latitude and longitude arrays for the 100 m grid."""
    xs, ys = grid.cell_centers()
    xx, yy = np.meshgrid(xs, ys)
    transformer = Transformer.from_crs(grid.crs, "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(xx, yy)
    return lat.astype("float32"), lon.astype("float32")


def fwi_band(path: Path, name: str) -> Path:
    """Return a single-band extraction of a named FWI layer."""
    with rasterio.open(path) as src:
        descriptions = [str(desc).upper() for desc in src.descriptions]
        try:
            index = descriptions.index(name.upper()) + 1
        except ValueError as exc:
            raise ValueError(f"{name} not found in {path}: {descriptions}") from exc
        output = PROCESSED / f"fwi_{name.lower()}_800m.tif"
        profile = src.profile.copy()
        profile.update(count=1)
        with rasterio.open(output, "w", **profile) as dst:
            dst.write(src.read(index), 1)
            dst.set_band_description(1, name.upper())
    return output


def load_fuel(gdb: Path, bbox: tuple[float, float, float, float]) -> gpd.GeoDataFrame:
    """Read the fuel polygon layer clipped to the KFC bounding box."""
    layers = pyogrio.list_layers(gdb)
    if len(layers) == 0:
        raise ValueError(f"no layers in {gdb}")
    layer = next((name for name, _ in layers if "FUEL" in str(name).upper()), str(layers[0][0]))
    frame = pyogrio.read_dataframe(
        gdb,
        layer=layer,
        bbox=bbox,
        columns=[
            "FUEL_TYPE_CD",
            "PERCENT_CONIFER",
            "M1_2_PERCENT_CONIFER",
            "PERCENT_DEAD_FIR",
        ],
    )
    if frame.crs is None:
        frame = frame.set_crs("EPSG:3005")
    elif str(frame.crs).upper() != "EPSG:3005":
        frame = frame.to_crs("EPSG:3005")
    return frame


def main() -> int:
    """Create the FBP input stack."""
    kfc = gpd.read_file(INTERIM / "kfc.gpkg")
    grid = grid_from_bounds(tuple(float(v) for v in kfc.total_bounds), resolution=100.0)
    kfc_mask = mask_from_polygon(kfc, grid).astype(bool)

    elevation, _ = _read(INTERIM / "elevation_100m.tif")
    slope, _ = _read(INTERIM / "slope_pct_100m.tif")
    aspect, _ = _read(INTERIM / "aspect_deg_100m.tif")
    lat, lon = lat_lon(grid)

    fwi_path = PROCESSED / "fwi_4km.tif"
    if not fwi_path.exists():
        raise FileNotFoundError(f"{fwi_path} is missing; run analysis/run_fwi.sh first")
    ffmc = reproject_raster_to_grid(
        fwi_band(fwi_path, "FFMC"), grid, resampling=Resampling.bilinear
    )
    bui = reproject_raster_to_grid(fwi_band(fwi_path, "BUI"), grid, resampling=Resampling.bilinear)

    gdb_candidates = [
        path
        for path in (ROOT / "data" / "raw" / "fuel").rglob("*.gdb")
        if (path / "a00000001.gdbtable").exists()
    ]
    if not gdb_candidates:
        raise FileNotFoundError("no unpacked fuel FGDB found")
    fuel = load_fuel(gdb_candidates[0], tuple(float(v) for v in kfc.total_bounds))
    print("fuel polygons in bbox:", len(fuel))
    fuel["BC_CODE"] = fuel["FUEL_TYPE_CD"].map(normalize_bc_fuel_code)
    fuel["R_CODE"] = fuel["BC_CODE"].map(BC_TO_R).fillna(13).astype("int32")
    fuel["PC_INT"] = [
        round(percent_conifer(code, pc, m12))
        for code, pc, m12 in zip(
            fuel["BC_CODE"],
            fuel["PERCENT_CONIFER"],
            fuel["M1_2_PERCENT_CONIFER"],
            strict=True,
        )
    ]
    fuel["PDF_INT"] = [
        round(percent_dead_fir(code, pdf))
        for code, pdf in zip(fuel["BC_CODE"], fuel["PERCENT_DEAD_FIR"], strict=True)
    ]
    fuel_r = rasterize_vector(fuel, grid, field="R_CODE", fill=13).astype("int32")
    pc_r = rasterize_vector(fuel, grid, field="PC_INT", fill=50).astype("int32")
    pdf_r = rasterize_vector(fuel, grid, field="PDF_INT", fill=35).astype("int32")
    cbh_r = np.full(grid.shape, np.nan, dtype="float32")
    cfl_r = np.full(grid.shape, np.nan, dtype="float32")
    for code, value in CBH_DEFAULT.items():
        cbh_r[fuel_r == code] = value
    for code, value in CFL_DEFAULT.items():
        cfl_r[fuel_r == code] = value
    fuel_r = np.where(kfc_mask, fuel_r, 13).astype("int32")
    pc_r = np.where(kfc_mask, pc_r, 50).astype("int32")
    pdf_r = np.where(kfc_mask, pdf_r, 35).astype("int32")
    for array in (ffmc, bui, elevation, slope, aspect, lat, lon):
        array[~kfc_mask] = np.nan

    bands = [
        fuel_r.astype("float32"),
        ffmc,
        bui,
        np.where(kfc_mask, WIND_SPEED_KMH, np.nan).astype("float32"),
        np.where(kfc_mask, WIND_DIRECTION_DEG, np.nan).astype("float32"),
        slope,
        aspect,
        lat,
        lon,
        elevation,
        np.where(kfc_mask, DAY_OF_YEAR, np.nan).astype("float32"),
        pc_r.astype("float32"),
        pdf_r.astype("float32"),
        np.where(kfc_mask, GRASS_CURING, np.nan).astype("float32"),
        cbh_r,
        cfl_r,
    ]
    output = PROCESSED / "fbp_inputs_100m.tif"
    profile = {
        "driver": "GTiff",
        "height": grid.height,
        "width": grid.width,
        "count": len(bands),
        "dtype": "float32",
        "crs": grid.crs,
        "transform": grid.transform,
        "nodata": np.nan,
        "compress": "deflate",
        "predictor": 2,
        "BIGTIFF": "IF_SAFER",
    }
    with rasterio.open(output, "w", **profile) as dst:
        for index, (band, name) in enumerate(zip(bands, BAND_ORDER, strict=True), start=1):
            dst.write(band, index)
            dst.set_band_description(index, name)
    manifest = {
        "band_order": BAND_ORDER,
        "fuel_codes": {str(code): name for code, name in sorted(BC_TO_R.items())},
        "assumptions": {
            "wind_speed_kmh": WIND_SPEED_KMH,
            "wind_direction_deg": WIND_DIRECTION_DEG,
            "day_of_year": DAY_OF_YEAR,
            "grass_curing_percent": GRASS_CURING,
        },
    }
    (PROCESSED / "fbp_inputs_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print("wrote", output)
    print(
        "fuel code counts",
        {
            int(k): int(v)
            for k, v in zip(*np.unique(fuel_r[kfc_mask], return_counts=True), strict=True)
        },
    )
    return 0


def _read(path: Path) -> tuple[np.ndarray, Grid]:
    """Read a single-band raster without importing the public reader at module load."""
    from kamloops_fbp.grid import read_raster

    return read_raster(path)


if __name__ == "__main__":
    raise SystemExit(main())
