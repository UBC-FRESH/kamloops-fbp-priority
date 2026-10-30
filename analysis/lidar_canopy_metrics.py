"""Derive simple canopy metrics from one LidarBC LAZ tile.

The pilot uses a 10 m grid and two passes over the point cloud:

1. build a ground surface from class-2 returns (minimum z per cell, nearest-filled);
2. use first returns to compute canopy cover, height percentiles, and a canopy base height proxy.

These are screening metrics, not a calibrated LiDAR forest inventory. The output is a cell-level
GeoPackage that can be joined to VRI polygons and fed back into the published decision tree.

Example:

    python analysis/lidar_canopy_metrics.py \
        --laz data/raw/lidar/laz/bc_082e052_2_4_3_xyes_8_utm11_20240721_20240726.laz \
        --output data/interim/lidar/PP_canopy_metrics.gpkg --zone PP
"""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import laspy
import numpy as np
from scipy import ndimage

GROUND_CLASS = 2
CANOPY_MIN_HEIGHT = 2.0
MIN_FIRST_RETURNS = 5
HIST_MAX = 80.0
HIST_STEP = 1.0


def _grid_shape(header: laspy.LasHeader, resolution: float) -> tuple[float, float, int, int]:
    """Return the grid origin and shape for a tile header."""
    minx, miny = float(header.mins[0]), float(header.mins[1])
    maxx, maxy = float(header.maxs[0]), float(header.maxs[1])
    x0 = np.floor(minx / resolution) * resolution
    y0 = np.floor(miny / resolution) * resolution
    width = int(np.ceil((maxx - x0) / resolution))
    height = int(np.ceil((maxy - y0) / resolution))
    return x0, y0, width, height


def _cell_indices(
    x: np.ndarray, y: np.ndarray, x0: float, y0: float, resolution: float, width: int, height: int
) -> tuple[np.ndarray, np.ndarray]:
    """Map point coordinates to clipped grid indices."""
    ix = np.clip(((x - x0) / resolution).astype(np.int32), 0, width - 1)
    iy = np.clip(((y - y0) / resolution).astype(np.int32), 0, height - 1)
    return iy, ix


def ground_surface(
    path: Path, x0: float, y0: float, resolution: float, width: int, height: int
) -> np.ndarray:
    """Build a nearest-filled ground surface from class-2 returns."""
    ground = np.full((height, width), np.inf, dtype=np.float32)
    with laspy.open(path) as reader:
        for points in reader.chunk_iterator(4_000_000):
            is_ground = points.classification == GROUND_CLASS
            if not np.any(is_ground):
                continue
            iy, ix = _cell_indices(
                np.asarray(points.x[is_ground]),
                np.asarray(points.y[is_ground]),
                x0,
                y0,
                resolution,
                width,
                height,
            )
            np.minimum.at(ground, (iy, ix), np.asarray(points.z[is_ground], dtype=np.float32))

    valid = np.isfinite(ground)
    if not np.any(valid):
        raise ValueError(f"no ground returns in {path}")
    indices = ndimage.distance_transform_edt(~valid, return_distances=False, return_indices=True)
    return ground[tuple(indices)].astype(np.float32)


def canopy_metrics(
    path: Path,
    ground: np.ndarray,
    x0: float,
    y0: float,
    resolution: float,
    width: int,
    height: int,
) -> dict[str, np.ndarray]:
    """Compute canopy metrics from first returns."""
    bins = int(HIST_MAX / HIST_STEP) + 1
    total = np.zeros((height, width), dtype=np.int32)
    canopy = np.zeros((height, width), dtype=np.int32)
    max_height = np.zeros((height, width), dtype=np.float32)
    hist = np.zeros((height, width, bins), dtype=np.int32)

    with laspy.open(path) as reader:
        for points in reader.chunk_iterator(4_000_000):
            first = points.return_number == 1
            if not np.any(first):
                continue
            iy, ix = _cell_indices(
                np.asarray(points.x[first]),
                np.asarray(points.y[first]),
                x0,
                y0,
                resolution,
                width,
                height,
            )
            flat = iy * width + ix
            total += np.bincount(flat, minlength=height * width).reshape(height, width)

            h = np.asarray(points.z[first], dtype=np.float32) - ground[iy, ix]
            above = h >= CANOPY_MIN_HEIGHT
            if not np.any(above):
                continue
            flat_above = flat[above]
            h_above = h[above]
            canopy += np.bincount(flat_above, minlength=height * width).reshape(height, width)
            bin_index = np.clip((h_above / HIST_STEP).astype(np.int32), 0, bins - 1)
            hist_flat = np.bincount(
                flat_above * bins + bin_index, minlength=height * width * bins
            ).reshape(height, width, bins)
            hist += hist_flat
            np.maximum.at(max_height, (iy[above], ix[above]), h_above)

    with np.errstate(invalid="ignore", divide="ignore"):
        cover = canopy / total
    cover[total < MIN_FIRST_RETURNS] = np.nan
    max_height[canopy == 0] = np.nan

    cumulative = np.cumsum(hist, axis=2)
    percentiles: dict[str, np.ndarray] = {}
    for q in (0.10, 0.50, 0.90, 0.95, 0.99):
        target = q * canopy
        index = np.argmax(cumulative >= target[..., None], axis=2).astype(np.float32)
        value = index * HIST_STEP
        value[canopy == 0] = np.nan
        percentiles[f"p{int(q * 100):02d}"] = value

    return {
        "cover": cover.astype(np.float32),
        "max_height": max_height,
        **percentiles,
    }


def write_metrics(
    metrics: dict[str, np.ndarray],
    x0: float,
    y0: float,
    resolution: float,
    width: int,
    height: int,
    output: Path,
    zone: str,
    source: str,
) -> gpd.GeoDataFrame:
    """Write the cell metrics as a point GeoPackage."""
    xs = x0 + (np.arange(width) + 0.5) * resolution
    ys = y0 + (np.arange(height) + 0.5) * resolution
    xx, yy = np.meshgrid(xs, ys)
    data = {"zone": zone, "source": source}
    data.update({name: values.ravel() for name, values in metrics.items() if name != "cover"})
    data["cover"] = metrics["cover"].ravel()
    frame = gpd.GeoDataFrame(
        data,
        geometry=gpd.points_from_xy(xx.ravel(), yy.ravel()),
        crs="EPSG:2955",
    )
    frame = frame[np.isfinite(frame["cover"])].copy()
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_file(output, driver="GPKG")
    return frame


def main() -> int:
    """Run the two-pass canopy metric extraction."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--laz", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--zone", type=str, required=True)
    parser.add_argument("--resolution", type=float, default=10.0)
    args = parser.parse_args()

    with laspy.open(args.laz) as reader:
        header = reader.header
    x0, y0, width, height = _grid_shape(header, args.resolution)
    print(f"grid {width} x {height} at {args.resolution} m; points {header.point_count:,}")

    ground = ground_surface(args.laz, x0, y0, args.resolution, width, height)
    print(f"ground surface: {np.isfinite(ground).sum():,} cells")
    metrics = canopy_metrics(args.laz, ground, x0, y0, args.resolution, width, height)
    frame = write_metrics(
        metrics, x0, y0, args.resolution, width, height, args.output, args.zone, str(args.laz)
    )
    print(f"wrote {len(frame):,} cells to {args.output}")
    for name in ("cover", "p50", "p95"):
        values = frame[name].to_numpy()
        print(name, "median", round(float(np.nanmedian(values)), 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
