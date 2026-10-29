"""Build the 100 m elevation, slope, and aspect layers for the KFC grid."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.fill import fillnodata
from rasterio.merge import merge

from kamloops_fbp.grid import (
    grid_from_bounds,
    reproject_raster_to_grid,
    slope_aspect,
    write_raster,
)

ROOT = Path(__file__).resolve().parents[1]
RAW_DEM = ROOT / "data" / "raw" / "dem" / "copernicus"
INTERIM = ROOT / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)


def build_dem_mosaic() -> Path:
    """Mosaic the Copernicus tiles at native 30 m resolution, once."""
    destination = INTERIM / "dem_copernicus_30m.tif"
    if destination.exists():
        return destination
    tiles = sorted(RAW_DEM.glob("Copernicus_DSM_COG_10_*.tif"))
    if not tiles:
        raise FileNotFoundError("no Copernicus DEM tiles found")
    sources = [rasterio.open(tile) for tile in tiles]
    try:
        mosaic, transform = merge(sources, resampling=Resampling.bilinear)
        profile = sources[0].profile.copy()
        profile.update(
            height=mosaic.shape[1],
            width=mosaic.shape[2],
            transform=transform,
            count=1,
            dtype="float32",
            compress="deflate",
            predictor=2,
            BIGTIFF="IF_SAFER",
        )
        with rasterio.open(destination, "w", **profile) as dst:
            dst.write(mosaic[0].astype("float32"), 1)
    finally:
        for source in sources:
            source.close()
    return destination


def main() -> int:
    """Create terrain rasters on the project grid."""
    kfc = gpd.read_file(INTERIM / "kfc.gpkg")
    grid = grid_from_bounds(tuple(float(v) for v in kfc.total_bounds), resolution=100.0)
    mosaic_path = build_dem_mosaic()
    elevation = reproject_raster_to_grid(
        mosaic_path, grid, resampling=Resampling.bilinear, dtype="float32", nodata=np.nan
    )
    # Fill small edge voids with nearest-neighbour values before deriving terrain.
    elevation_filled = fillnodata(
        np.where(np.isfinite(elevation), elevation, -9999.0).astype("float32"),
        mask=np.isfinite(elevation).astype("uint8"),
        max_search_distance=100,
    )
    elevation_filled = np.where(elevation_filled == -9999.0, np.nan, elevation_filled)
    slope, aspect = slope_aspect(elevation_filled, grid)
    write_raster(
        INTERIM / "elevation_100m.tif", elevation_filled, grid, band_description="elevation_m"
    )
    write_raster(INTERIM / "slope_pct_100m.tif", slope, grid, band_description="slope_percent")
    write_raster(INTERIM / "aspect_deg_100m.tif", aspect, grid, band_description="aspect_degrees")
    valid = np.isfinite(elevation_filled)
    print("grid", grid.width, grid.height)
    print("elevation valid", int(valid.sum()), "of", valid.size)
    print(
        "elevation min/mean/max",
        float(np.nanmin(elevation_filled)),
        float(np.nanmean(elevation_filled)),
        float(np.nanmax(elevation_filled)),
    )
    print("slope p50/p90/p99", *(round(float(v), 2) for v in np.nanpercentile(slope, [50, 90, 99])))
    print("aspect p50/p90", *(round(float(v), 1) for v in np.nanpercentile(aspect, [50, 90])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
