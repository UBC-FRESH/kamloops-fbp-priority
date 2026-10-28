"""Create a 200 m KFC stack and a 100 m three-zone stack from the 100 m inputs."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio
from affine import Affine

from kamloops_fbp.grid import Grid, read_raster, write_raster

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
INTERIM = ROOT / "data" / "interim"
BANDS = [
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
NEAREST = {"FUEL"}
ROUND = {"PC", "PDF", "cc"}


def read_stack(path: Path) -> tuple[list[np.ndarray], Grid]:
    """Read all bands and the grid from a multi-band GeoTIFF."""
    with rasterio.open(path) as src:
        bands = [src.read(i + 1).astype("float32") for i in range(src.count)]
        grid = Grid(transform=src.transform, width=src.width, height=src.height, crs=str(src.crs))
    return bands, grid


def write_stack(path: Path, bands: list[np.ndarray], grid: Grid, names: list[str]) -> None:
    """Write a multi-band float32 GeoTIFF with descriptions."""
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
    with rasterio.open(path, "w", **profile) as dst:
        for index, (band, name) in enumerate(zip(bands, names, strict=True), start=1):
            dst.write(band, index)
            dst.set_band_description(index, name)


def aggregate_2x2(array: np.ndarray, *, nearest: bool, round_result: bool = False) -> np.ndarray:
    """Aggregate a 2-D array by 2x2 blocks, padding with NaN when needed."""
    height, width = array.shape
    pad_h = height % 2
    pad_w = width % 2
    if pad_h or pad_w:
        array = np.pad(array, ((0, pad_h), (0, pad_w)), constant_values=np.nan)
    if nearest:
        return array.reshape(array.shape[0] // 2, 2, array.shape[1] // 2, 2)[:, 0, :, 0]
    with np.errstate(invalid="ignore"):
        result = np.nanmean(
            array.reshape(array.shape[0] // 2, 2, array.shape[1] // 2, 2), axis=(1, 3)
        )
    if round_result:
        result = np.round(result)
    return result.astype("float32")


def main() -> int:
    """Write both derived stacks."""
    bands, grid = read_stack(PROCESSED / "fbp_inputs_100m.tif")
    minx, _, _, maxy = grid.bounds
    coarse = Grid(
        transform=Affine(200.0, 0.0, minx, 0.0, -200.0, maxy),
        width=int(np.ceil(grid.width / 2)),
        height=int(np.ceil(grid.height / 2)),
        crs=grid.crs,
    )
    coarse_bands = [
        aggregate_2x2(band, nearest=name in NEAREST, round_result=name in ROUND)
        for band, name in zip(bands, BANDS, strict=True)
    ]
    # The 200 m grid may be one cell larger than the aggregated arrays; pad if needed.
    for index, band in enumerate(coarse_bands):
        if band.shape != coarse.shape:
            coarse_bands[index] = np.pad(
                band,
                ((0, coarse.height - band.shape[0]), (0, coarse.width - band.shape[1])),
                constant_values=np.nan,
            )
    write_stack(PROCESSED / "fbp_inputs_200m.tif", coarse_bands, coarse, BANDS)

    zones, _ = read_raster(INTERIM / "bec_zone_100m.tif")
    three_zone_mask = np.isin(zones, [8, 9, 13])  # ICH, IDF, PP
    write_raster(
        INTERIM / "three_zone_mask_100m.tif",
        three_zone_mask.astype("uint8"),
        grid,
        dtype="uint8",
        nodata=0,
    )
    # fbpRaster recycles values when the FUEL layer contains NA. Fill outside
    # the three zones with valid non-fuel inputs, then mask the FBP output.
    fills = {
        "FUEL": 13.0,
        "FFMC": 85.0,
        "BUI": 50.0,
        "WS": 20.0,
        "WD": 225.0,
        "GS": 0.0,
        "Aspect": 0.0,
        "LAT": None,
        "LONG": None,
        "ELV": 0.0,
        "Dj": 227.0,
        "PC": 50.0,
        "PDF": 35.0,
        "cc": 80.0,
        "CBH": 0.0,
        "CFL": 0.0,
    }
    masked_bands = []
    for band, name in zip(bands, BANDS, strict=True):
        fill = fills[name]
        masked_bands.append(band if fill is None else np.where(three_zone_mask, band, fill))
    write_stack(PROCESSED / "fbp_inputs_three_zones_100m.tif", masked_bands, grid, BANDS)
    print(
        "wrote 200 m",
        coarse.width,
        "x",
        coarse.height,
        "and three-zone 100 m",
        grid.width,
        "x",
        grid.height,
    )
    print(
        "three-zone cells",
        int(three_zone_mask.sum()),
        "area km2",
        round(float(three_zone_mask.sum()) * 0.01, 1),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
