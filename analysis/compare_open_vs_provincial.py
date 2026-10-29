"""Compare the open fuel-typing decision tree with the provincial fuel-type layer.

This is a small-area smoke comparison, not a validation study. It assigns each VRI polygon's
centroid to the provincial fuel polygon and reports agreement after normalizing the grouped codes
(``O-1a/b``, ``D-1/2``, ``M-1/2``).

Example:

    python analysis/compare_open_vs_provincial.py --vri <vri.gpkg> \
        --provincial <provincial.gpkg> --output <table.csv>
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import geopandas as gpd
import pandas as pd

PREFIX = re.compile(r"^B\d+_")
GROUPS = {
    "O-1": "O-1",
    "O-1a": "O-1",
    "O-1b": "O-1",
    "O-1a/b": "O-1",
    "D-1": "D-1/2",
    "D-2": "D-1/2",
    "D-1/2": "D-1/2",
    "M-1": "M-1/2",
    "M-2": "M-1/2",
    "M-1/2": "M-1/2",
}


def normalize_fuel(code: object) -> str | None:
    """Normalize a provincial or open fuel-type code to a comparable group."""
    if code is None or pd.isna(code):
        return None
    text = PREFIX.sub("", str(code).strip())
    return GROUPS.get(text, text)


def compare(vri_path: Path, provincial_path: Path) -> pd.DataFrame:
    """Return one row per VRI polygon with both normalized fuel types."""
    vri = gpd.read_file(vri_path)
    provincial = gpd.read_file(provincial_path)
    if vri.crs != provincial.crs:
        provincial = provincial.to_crs(vri.crs)

    centroids = vri.copy()
    centroids["geometry"] = centroids.centroid
    joined = gpd.sjoin(
        centroids,
        provincial[["FUEL_TYPE_CD", "geometry"]],
        how="left",
        predicate="within",
    )
    joined["FUEL_TYPE_OPEN_NORM"] = joined["FUEL_TYPE_OPEN"].map(normalize_fuel)
    joined["FUEL_TYPE_PROV_NORM"] = joined["FUEL_TYPE_CD"].map(normalize_fuel)
    return joined


def main() -> int:
    """Run the comparison and write the attribute table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vri", type=Path, required=True)
    parser.add_argument("--provincial", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    joined = compare(args.vri, args.provincial)
    valid = joined.dropna(subset=["FUEL_TYPE_OPEN_NORM", "FUEL_TYPE_PROV_NORM"])
    agreement = float((valid["FUEL_TYPE_OPEN_NORM"] == valid["FUEL_TYPE_PROV_NORM"]).mean())

    print(f"polygons: {len(joined)}; comparable: {len(valid)}; agreement: {agreement:.3f}")
    print(pd.crosstab(valid["FUEL_TYPE_OPEN_NORM"], valid["FUEL_TYPE_PROV_NORM"]).to_string())

    args.output.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "FEATURE_ID",
        "POLYGON_ID",
        "FUEL_TYPE_OPEN",
        "FUEL_MODIFIER_OPEN",
        "FUEL_PROCESS_OPEN",
        "FUEL_TYPE_CD",
        "FUEL_TYPE_OPEN_NORM",
        "FUEL_TYPE_PROV_NORM",
        "PROJ_HEIGHT_1",
        "CROWN_CLOSURE",
        "SPECIES_CD_1",
        "BEC_ZONE_CODE",
    ]
    available = [column for column in columns if column in joined.columns]
    joined[available].to_csv(args.output, index=False)
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
