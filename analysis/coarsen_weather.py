"""Coarsen the 800 m ClimateBC mean stack to a 4 km FWI weather grid.

The official fwiRaster loop is single-threaded. At 800 m and 62 days it takes
hours in this environment. The prototype therefore runs FWI at 4 km, where the
weather fields are still spatially meaningful, and resamples the resulting
codes to the 100 m FBP grid. The production run should keep 800 m and
parallelize the daily loop.
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from affine import Affine
from pyproj import Transformer
from rasterio.enums import Resampling

from kamloops_fbp.grid import Grid, mask_from_polygon, reproject_raster_to_grid

ROOT = Path(__file__).resolve().parents[1]
CLIMATE = ROOT / "data" / "interim" / "climatebc"
WEATHER = ROOT / "data" / "interim" / "weather_4km"
WEATHER.mkdir(parents=True, exist_ok=True)
KFC = gpd.read_file(ROOT / "data" / "interim" / "kfc.gpkg")
MINX, MINY, MAXX, MAXY = (float(v) for v in KFC.total_bounds)
GRID = Grid(
    transform=Affine(
        4000.0,
        0.0,
        np.floor(MINX / 4000.0) * 4000.0,
        0.0,
        -4000.0,
        np.ceil(MAXY / 4000.0) * 4000.0,
    ),
    width=int(np.ceil((MAXX - np.floor(MINX / 4000.0) * 4000.0) / 4000.0)),
    height=int(np.ceil((np.ceil(MAXY / 4000.0) * 4000.0 - MINY) / 4000.0)),
)
WIND_SPEED_KMH = 20.0


def read_mean(name: str) -> np.ndarray:
    """Read one band from the 800 m mean stack and reproject it to 4 km."""
    path = CLIMATE / "climatebc_mean_stack_800m.tif"
    with rasterio.open(path) as src:
        descriptions = [str(desc) for desc in src.descriptions]
        index = descriptions.index(name) + 1
        temp = ROOT / "data" / "interim" / f"_mean_{name}.tif"
        profile = src.profile.copy()
        profile.update(count=1)
        with rasterio.open(temp, "w", **profile) as dst:
            dst.write(src.read(index), 1)
    return reproject_raster_to_grid(temp, GRID, resampling=Resampling.bilinear)


def latitude() -> np.ndarray:
    """Return latitude in degrees on the 4 km grid."""
    xs, ys = GRID.cell_centers()
    xx, yy = np.meshgrid(xs, ys)
    transformer = Transformer.from_crs(GRID.crs, "EPSG:4326", always_xy=True)
    _, lat = transformer.transform(xx, yy)
    return lat.astype("float32")


def write_day(path: Path, bands: list[np.ndarray]) -> None:
    """Write one 5-band daily weather raster."""
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
    }
    with rasterio.open(path, "w", **profile) as dst:
        for index, band in enumerate(bands, start=1):
            dst.write(band.astype("float32"), index)
            dst.set_band_description(index, ["temp", "rh", "ws", "prec", "lat"][index - 1])


def main() -> int:
    """Write the 62-day 4 km weather sequence."""
    values = {
        name: read_mean(name) for name in ("Tmax07", "Tmax08", "RH07", "RH08", "PPT07", "PPT08")
    }
    mask = mask_from_polygon(KFC, GRID)
    lat = latitude()
    day = 0
    for month, days in (("07", 31), ("08", 31)):
        for _ in range(days):
            day += 1
            temp = np.where(mask, values[f"Tmax{month}"], np.nan).astype("float32")
            rh = np.where(mask, values[f"RH{month}"], np.nan).astype("float32")
            prec = np.where(mask, values[f"PPT{month}"] / days, np.nan).astype("float32")
            ws = np.where(mask, WIND_SPEED_KMH, np.nan).astype("float32")
            write_day(WEATHER / f"weather_day_{day:03d}.tif", [temp, rh, ws, prec, lat])
    (WEATHER / "manifest.json").write_text(
        json.dumps(
            {
                "source": "ClimateBC 2014-2023 July/August means, coarsened to 4 km",
                "grid": {"width": GRID.width, "height": GRID.height, "resolution_m": 4000},
                "days": day,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("wrote", day, "days on", GRID.width, "x", GRID.height, "grid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
