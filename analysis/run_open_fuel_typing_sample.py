"""Run the published BC fuel-typing decision tree on a VRI sample.

The classifier is the vendored GPL-3.0 ``BC_CFFBPS_FuelTyping_Tool``. This script is the first
real-data check for P1.4: it maps the VRI columns to the 21 attributes, runs the decision tree, and
writes the assigned FBP fuel type, modifier, and process number back to a GeoPackage.

Example:

    python analysis/run_open_fuel_typing_sample.py --input <vri.gpkg> --output <out.gpkg>
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import pandas as pd

VENDOR = Path(__file__).resolve().parent / "vendor" / "BC_CFFBPS_FuelTyping_Tool"
sys.path.insert(0, str(VENDOR))

from bcwft2018 import FuelTyping  # noqa: E402  (import follows the vendor path setup)


def _clean(value: object) -> object:
    """Return None for missing values and the value otherwise."""
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return value


def _date(value: object) -> datetime | None:
    """Parse a VRI date value, or return None when it is missing."""
    clean = _clean(value)
    if clean is None:
        return None
    parsed = pd.to_datetime(clean, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.to_pydatetime()


def _int(value: object) -> int | None:
    """Return a rounded int, or None when the value is missing."""
    clean = _clean(value)
    if clean is None:
        return None
    return round(float(clean))


def _float(value: object) -> float | None:
    """Return a float, or None when the value is missing."""
    clean = _clean(value)
    if clean is None:
        return None
    return float(clean)


def _str(value: object) -> str | None:
    """Return a stripped string, or None when the value is missing."""
    clean = _clean(value)
    if clean is None:
        return None
    return str(clean).strip()


def classify_row(row: pd.Series) -> tuple[str | None, str | None, int | None, str | None]:
    """Classify one VRI polygon and return fuel type, modifier, process, and error."""
    classifier = FuelTyping()
    try:
        process, fuel_type, modifier = classifier.getFuelType(
            season="growing",
            COAST_INTERIOR_CD=_str(row.get("COAST_INTERIOR_CD")) or "I",
            BCLCS_LEVEL_1=_str(row.get("BCLCS_LEVEL_1")),
            BCLCS_LEVEL_2=_str(row.get("BCLCS_LEVEL_2")),
            BCLCS_LEVEL_3=_str(row.get("BCLCS_LEVEL_3")),
            BCLCS_LEVEL_4=_str(row.get("BCLCS_LEVEL_4")),
            BCLCS_LEVEL_5=_str(row.get("BCLCS_LEVEL_5")),
            BEC_ZONE_CODE=_str(row.get("BEC_ZONE_CODE")),
            BEC_SUBZONE=_str(row.get("BEC_SUBZONE")),
            EARLIEST_NONLOGGING_DIST_TYPE=_str(row.get("EARLIEST_NONLOGGING_DIST_TYPE")),
            EARLIEST_NONLOGGING_DIST_DATE=_date(row.get("EARLIEST_NONLOGGING_DIST_DATE")),
            HARVEST_DATE=_date(row.get("HARVEST_DATE")),
            CROWN_CLOSURE=_int(row.get("CROWN_CLOSURE")),
            PROJ_HEIGHT_1=_float(row.get("PROJ_HEIGHT_1")),
            PROJ_AGE_1=_int(row.get("PROJ_AGE_1")),
            VRI_LIVE_STEMS_PER_HA=_int(row.get("VRI_LIVE_STEMS_PER_HA")),
            VRI_DEAD_STEMS_PER_HA=_int(row.get("VRI_DEAD_STEMS_PER_HA")),
            STAND_PERCENTAGE_DEAD=_int(row.get("STAND_PERCENTAGE_DEAD")),
            INVENTORY_STANDARD_CD=_str(row.get("INVENTORY_STANDARD_CD")),
            NON_PRODUCTIVE_CD=_str(row.get("NON_PRODUCTIVE_CD")),
            LAND_COVER_CLASS_CD_1=_str(row.get("LAND_COVER_CLASS_CD_1")),
            SPECIES_CD_1=_str(row.get("SPECIES_CD_1")),
            SPECIES_PCT_1=_float(row.get("SPECIES_PCT_1")),
            SPECIES_CD_2=_str(row.get("SPECIES_CD_2")),
            SPECIES_PCT_2=_float(row.get("SPECIES_PCT_2")),
            SPECIES_CD_3=_str(row.get("SPECIES_CD_3")),
            SPECIES_PCT_3=_float(row.get("SPECIES_PCT_3")),
            SPECIES_CD_4=_str(row.get("SPECIES_CD_4")),
            SPECIES_PCT_4=_float(row.get("SPECIES_PCT_4")),
            SPECIES_CD_5=_str(row.get("SPECIES_CD_5")),
            SPECIES_PCT_5=_float(row.get("SPECIES_PCT_5")),
            SPECIES_CD_6=_str(row.get("SPECIES_CD_6")),
            SPECIES_PCT_6=_float(row.get("SPECIES_PCT_6")),
        )
        return fuel_type, modifier, process, None
    except Exception as exc:  # record bad VRI rows instead of stopping the sample
        return None, None, None, f"{type(exc).__name__}: {exc}"


def main() -> int:
    """Run the decision tree on the input VRI GeoPackage."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    vri = gpd.read_file(args.input)
    print(f"read {len(vri)} VRI polygons from {args.input}")

    results = vri.apply(classify_row, axis=1, result_type="expand")
    results.columns = ["FUEL_TYPE_OPEN", "FUEL_MODIFIER_OPEN", "FUEL_PROCESS_OPEN", "FUEL_ERROR"]
    out = pd.concat([vri, results], axis=1)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.to_file(args.output, driver="GPKG")

    print(out["FUEL_TYPE_OPEN"].value_counts(dropna=False).to_string())
    errors = out["FUEL_ERROR"].dropna()
    print(f"errors: {len(errors)}")
    if not errors.empty:
        print(errors.head(10).to_string())
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
