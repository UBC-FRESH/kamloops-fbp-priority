"""Build the ClimateBC mean July/August stack and a 62-day FWI weather sequence.

The proposal asks for mean July/August 13:00 weather over the past ten years.
ClimateBC provides monthly means, not daily 13:00 observations. This script makes
the assumption explicit:

- temperature is the monthly mean daily maximum (a 13:00 proxy),
- relative humidity is the monthly mean,
- precipitation is spread evenly across the days of the month,
- wind speed is a fixed design value of 20 km/h because ClimateBC publishes no
  wind variable.

Those assumptions are recorded in the output manifest and are the first thing a
reviewer should challenge.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from affine import Affine
from pyproj import Transformer
from rasterio.enums import Resampling

from kamloops_fbp.grid import Grid, mask_from_polygon, reproject_raster_to_grid

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "climatebc"
INTERIM = ROOT / "data" / "interim"
CLIMATE = INTERIM / "climatebc"
WEATHER = INTERIM / "weather"
CLIMATE.mkdir(parents=True, exist_ok=True)
WEATHER.mkdir(parents=True, exist_ok=True)

KFC = gpd.read_file(INTERIM / "kfc.gpkg")
MINX, MINY, MAXX, MAXY = (float(v) for v in KFC.total_bounds)
GRID = Grid(
    transform=Affine(
        800.0, 0.0, np.floor(MINX / 800.0) * 800.0, 0.0, -800.0, np.ceil(MAXY / 800.0) * 800.0
    ),
    width=int(np.ceil((MAXX - np.floor(MINX / 800.0) * 800.0) / 800.0)),
    height=int(np.ceil((np.ceil(MAXY / 800.0) * 800.0 - MINY) / 800.0)),
)
YEARS = range(2014, 2024)
WIND_SPEED_KMH = 20.0
MONTH_VARS = {"07": 31, "08": 31}


def mean_raster(variable: str) -> np.ndarray:
    """Average the ten yearly rasters for one ClimateBC variable."""
    stack = []
    for year in YEARS:
        path = RAW / f"{variable}_{year}.tif"
        if not path.exists():
            raise FileNotFoundError(path)
        stack.append(
            reproject_raster_to_grid(
                path,
                GRID,
                resampling=Resampling.bilinear,
                dtype="float32",
                src_crs="EPSG:4326",
            )
        )
    return np.nanmean(np.stack(stack), axis=0).astype("float32")


def latitude_raster() -> np.ndarray:
    """Return latitude in degrees for each 800 m cell centre."""
    xs, ys = GRID.cell_centers()
    xx, yy = np.meshgrid(xs, ys)
    transformer = Transformer.from_crs(GRID.crs, "EPSG:4326", always_xy=True)
    _, lat = transformer.transform(xx, yy)
    return lat.astype("float32")


def write_stack(path: Path, bands: list[np.ndarray], names: list[str]) -> None:
    """Write a multi-band float32 GeoTIFF with band descriptions."""
    profile = {
        "driver": "GTiff",
        "height": GRID.height,
        "width": GRID.width,
        "count": len(bands),
        "dtype": "float32",
        "crs": GRID.crs,
        "transform": GRID.transform,
        "nodata": np.nan,
        "compress": "deflate",
        "predictor": 2,
        "BIGTIFF": "IF_SAFER",
    }
    with rasterio.open(path, "w", **profile) as dst:
        for index, (band, name) in enumerate(zip(bands, names, strict=True), start=1):
            dst.write(band.astype("float32"), index)
            dst.set_band_description(index, name)


def main() -> int:
    """Build the mean stack and daily weather files."""
    means = {}
    for variable in ("Tmax07", "Tmax08", "RH07", "RH08", "PPT07", "PPT08"):
        means[variable] = mean_raster(variable)
        print(
            variable,
            "min/mean/max",
            *(round(float(v), 2) for v in np.nanpercentile(means[variable], [0, 50, 100])),
        )
    kfc_mask = mask_from_polygon(KFC, GRID)
    lat = latitude_raster()
    write_stack(
        CLIMATE / "climatebc_mean_stack_800m.tif",
        [means[v] for v in ("Tmax07", "Tmax08", "RH07", "RH08", "PPT07", "PPT08")],
        ["Tmax07", "Tmax08", "RH07", "RH08", "PPT07", "PPT08"],
    )
    write_stack(CLIMATE / "lat_800m.tif", [lat], ["lat"])

    day = 0
    for month, days in MONTH_VARS.items():
        for _ in range(days):
            day += 1
            temp = np.where(kfc_mask, means[f"Tmax{month}"], np.nan).astype("float32")
            rh = np.where(kfc_mask, means[f"RH{month}"], np.nan).astype("float32")
            prec = np.where(kfc_mask, means[f"PPT{month}"] / days, np.nan).astype("float32")
            ws = np.where(kfc_mask, WIND_SPEED_KMH, np.nan).astype("float32")
            write_stack(
                WEATHER / f"weather_day_{day:03d}.tif",
                [temp, rh, ws, prec, lat],
                ["temp", "rh", "ws", "prec", "lat"],
            )
    manifest = {
        "source": "ClimateBC v7.60, BC 800 m historical years",
        "years": list(YEARS),
        "months": [7, 8],
        "temperature_assumption": "monthly mean daily maximum used as the 13:00 temperature proxy",
        "relative_humidity_assumption": "monthly mean RH used as the 13:00 RH proxy",
        "precipitation_assumption": "monthly total spread evenly across days",
        "wind_assumption": (
            f"fixed {WIND_SPEED_KMH} km/h because ClimateBC publishes no wind variable"
        ),
        "days": day,
        "grid": {"crs": GRID.crs, "width": GRID.width, "height": GRID.height},
        "retrieved_utc": datetime.now(UTC).isoformat(),
    }
    (CLIMATE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("wrote", day, "weather days on", GRID.width, "x", GRID.height, "grid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
