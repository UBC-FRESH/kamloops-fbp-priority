"""Apply LiDAR canopy metrics to VRI polygons and rerun the fuel-typing decision tree.

For each polygon, the mean LiDAR canopy cover replaces ``CROWN_CLOSURE`` and the mean LiDAR p95
height replaces ``PROJ_HEIGHT_1``. All other VRI attributes stay unchanged. The baseline and
LiDAR-adjusted runs use the same published decision tree, so the comparison isolates the effect of
the two LiDAR canopy attributes.

Example:

    python analysis/apply_lidar_to_vri.py --zone PP \
        --vri data/interim/zone_samples/PP_vri_fuel.gpkg \
        --lidar data/interim/lidar/PP_canopy_metrics.gpkg \
        --output data/interim/zone_samples/PP_vri_lidar_fuel.gpkg \
        --table docs/tables/lidar_fuel_type_changes_PP.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_open_fuel_typing_sample import classify_row


def _aggregate_lidar(cells: gpd.GeoDataFrame, vri: gpd.GeoDataFrame) -> pd.DataFrame:
    """Aggregate cell metrics to VRI polygons by centroid-in-polygon."""
    if cells.crs != vri.crs:
        cells = cells.to_crs(vri.crs)
    joined = gpd.sjoin(cells, vri[["FEATURE_ID", "geometry"]], how="inner", predicate="within")
    return (
        joined.groupby("FEATURE_ID")
        .agg(
            lidar_cover=("cover", "mean"),
            lidar_p10=("p10", "mean"),
            lidar_p50=("p50", "mean"),
            lidar_p95=("p95", "mean"),
            lidar_cells=("cover", "size"),
        )
        .reset_index()
    )


def _classify_adjusted(row: pd.Series) -> tuple[str | None, str | None, str | None]:
    """Classify one polygon with the LiDAR-adjusted cover and height."""
    if pd.isna(row.get("CROWN_CLOSURE_LIDAR")) or pd.isna(row.get("PROJ_HEIGHT_1_LIDAR")):
        return None, None, "no LiDAR cells"
    adjusted = row.copy()
    adjusted["CROWN_CLOSURE"] = round(float(row["CROWN_CLOSURE_LIDAR"]))
    adjusted["PROJ_HEIGHT_1"] = float(row["PROJ_HEIGHT_1_LIDAR"])
    fuel_type, modifier, _process, error = classify_row(adjusted)
    return fuel_type, modifier, error


def main() -> int:
    """Join LiDAR metrics, classify the adjusted polygons, and write the comparison."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zone", type=str, required=True)
    parser.add_argument("--vri", type=Path, required=True)
    parser.add_argument("--lidar", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--table", type=Path, required=True)
    args = parser.parse_args()

    vri = gpd.read_file(args.vri)
    cells = gpd.read_file(args.lidar)
    metrics = _aggregate_lidar(cells, vri)
    merged = vri.merge(metrics, on="FEATURE_ID", how="left")

    merged["CROWN_CLOSURE_LIDAR"] = (merged["lidar_cover"] * 100).round().clip(0, 100)
    merged["PROJ_HEIGHT_1_LIDAR"] = merged["lidar_p95"].round(1)
    adjusted = merged.apply(_classify_adjusted, axis=1, result_type="expand")
    adjusted.columns = ["FUEL_TYPE_LIDAR", "FUEL_MODIFIER_LIDAR", "FUEL_ERROR_LIDAR"]
    merged = pd.concat([merged, adjusted], axis=1)
    merged["FUEL_TYPE_BASE"] = merged["FUEL_TYPE_OPEN"]
    merged["CHANGED"] = (
        merged["FUEL_TYPE_BASE"].notna()
        & merged["FUEL_TYPE_LIDAR"].notna()
        & (merged["FUEL_TYPE_BASE"] != merged["FUEL_TYPE_LIDAR"])
    )

    comparable = merged.dropna(subset=["FUEL_TYPE_BASE", "FUEL_TYPE_LIDAR"])
    changes = int(comparable["CHANGED"].sum())
    print(f"{args.zone}: {len(comparable)} comparable polygons; {changes} fuel-type changes")
    print(pd.crosstab(comparable["FUEL_TYPE_BASE"], comparable["FUEL_TYPE_LIDAR"]).to_string())

    args.output.parent.mkdir(parents=True, exist_ok=True)
    merged.to_file(args.output, driver="GPKG")

    columns = [
        "ZONE",
        "FEATURE_ID",
        "BEC_ZONE_CODE",
        "SPECIES_CD_1",
        "CROWN_CLOSURE",
        "PROJ_HEIGHT_1",
        "CROWN_CLOSURE_LIDAR",
        "PROJ_HEIGHT_1_LIDAR",
        "FUEL_TYPE_BASE",
        "FUEL_TYPE_LIDAR",
        "CHANGED",
        "lidar_cover",
        "lidar_p10",
        "lidar_p50",
        "lidar_p95",
        "lidar_cells",
    ]
    merged["ZONE"] = args.zone
    available = [column for column in columns if column in merged.columns]
    args.table.parent.mkdir(parents=True, exist_ok=True)
    merged[available].to_csv(args.table, index=False)
    print(f"wrote {args.output} and {args.table}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
