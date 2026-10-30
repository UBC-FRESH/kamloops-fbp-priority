"""Build the point FBP input table for the LiDAR fuel-type changes.

Reads the three zone pilot GeoPackages, keeps the polygons whose fuel type changed when LiDAR
canopy metrics replaced the VRI cover and height, samples the existing 100 m FBP input stack at each
polygon centroid, and writes two rows per polygon (baseline and LiDAR) for ``cffdrs::fbp``.

Example:

    PYTHONPATH=analysis python analysis/prepare_lidar_fbp_points.py \
        --stack data/processed/fbp_inputs_three_zones_100m.tif \
        --output data/interim/lidar_fbp_changed_points.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kamloops_fbp.fuel import R_FUEL_NAMES, convert_bc_fuel

ZONES = ("ICH", "IDF", "PP")
BAND_NAMES = (
    "FUEL",
    "FFMC",
    "BUI",
    "WS",
    "WD",
    "GS",
    "ASPECT",
    "LAT",
    "LONG",
    "ELV",
    "DJ",
    "PC",
    "PDF",
    "CC",
    "CBH",
    "CFL",
)


def _row(
    feature_id: int,
    zone: str,
    scenario: str,
    fuel_type: str,
    bands: dict[str, float],
) -> dict[str, object]:
    """Build one FBP input row with fuel-type defaults."""
    conversion = convert_bc_fuel(fuel_type)
    return {
        "ID": f"{zone}-{feature_id}-{scenario}",
        "ZONE": zone,
        "FEATURE_ID": feature_id,
        "SCENARIO": scenario,
        "FUELTYPE": R_FUEL_NAMES[conversion.r_code],
        "FFMC": bands["FFMC"],
        "BUI": bands["BUI"],
        "WS": bands["WS"],
        "WD": bands["WD"],
        "GS": bands["GS"],
        "ASPECT": bands["ASPECT"],
        "PC": 50.0,
        "PDF": 35.0,
        "CC": bands["CC"],
        "CBH": conversion.cbh,
        "CFL": conversion.cfl,
        "LAT": bands["LAT"],
        "LONG": bands["LONG"],
        "ELV": bands["ELV"],
        "DJ": bands["DJ"],
    }


def main() -> int:
    """Write the baseline and LiDAR FBP input rows for changed polygons."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stack", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--suffix", type=str, default="", help="Suffix for the zone GPKG names.")
    args = parser.parse_args()

    rows: list[dict[str, object]] = []
    with rasterio.open(args.stack) as src:
        descriptions = [str(desc).upper() for desc in src.descriptions]
        index = {name: descriptions.index(name) + 1 for name in BAND_NAMES}
        for zone in ZONES:
            path = Path("data/interim/zone_samples") / f"{zone}_vri_lidar_fuel{args.suffix}.gpkg"
            frame = gpd.read_file(path)
            changed = frame[frame["CHANGED"].fillna(False)].copy()
            if changed.empty:
                continue
            points = changed.geometry.centroid
            coordinates = zip(points.x, points.y, strict=True)
            samples = np.array(
                list(src.sample(coordinates, indexes=[index[name] for name in BAND_NAMES]))
            )
            for row, values in zip(changed.itertuples(), samples, strict=True):
                bands = dict(zip(BAND_NAMES, values, strict=True))
                if not np.isfinite(bands["FFMC"]) or not np.isfinite(bands["BUI"]):
                    print(f"skip {zone} {row.FEATURE_ID}: no FBP stack values at centroid")
                    continue
                bands["ASPECT"] = 0.0 if not np.isfinite(bands["ASPECT"]) else bands["ASPECT"]
                rows.append(
                    _row(
                        int(row.FEATURE_ID),
                        zone,
                        "baseline",
                        str(row.FUEL_TYPE_BASE),
                        bands,
                    )
                )
                rows.append(
                    _row(
                        int(row.FEATURE_ID),
                        zone,
                        "lidar",
                        str(row.FUEL_TYPE_LIDAR),
                        bands,
                    )
                )

    output = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False)
    print(f"wrote {len(output)} rows for {len(output) // 2} changed polygons to {args.output}")
    print(output.groupby(["ZONE", "SCENARIO", "FUELTYPE"]).size().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
