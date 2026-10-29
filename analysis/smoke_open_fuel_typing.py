"""Smoke-test the vendored BC fuel-typing decision tree.

The tool is GPL-3.0 third-party code; see
``analysis/vendor/BC_CFFBPS_FuelTyping_Tool/README.md``. This script is a reproducible check that
the vendored file imports and returns a fuel type for a simple interior pine stand.
"""

from __future__ import annotations

import sys
from pathlib import Path

VENDOR = Path(__file__).resolve().parent / "vendor" / "BC_CFFBPS_FuelTyping_Tool"
sys.path.insert(0, str(VENDOR))

from bcwft2018 import FuelTyping  # noqa: E402  (import follows the vendor path setup)


def main() -> None:
    """Run one mature interior lodgepole-pine stand through the decision tree."""
    result = FuelTyping().getFuelType(
        season="growing",
        COAST_INTERIOR_CD="I",
        BCLCS_LEVEL_1="V",
        BCLCS_LEVEL_2="T",
        BCLCS_LEVEL_3="U",
        BCLCS_LEVEL_4="TC",
        BCLCS_LEVEL_5="DE",
        BEC_ZONE_CODE="IDF",
        BEC_SUBZONE="dk",
        EARLIEST_NONLOGGING_DIST_TYPE=None,
        EARLIEST_NONLOGGING_DIST_DATE=None,
        HARVEST_DATE=None,
        CROWN_CLOSURE=50,
        PROJ_HEIGHT_1=20.0,
        PROJ_AGE_1=80,
        VRI_LIVE_STEMS_PER_HA=1200,
        VRI_DEAD_STEMS_PER_HA=0,
        STAND_PERCENTAGE_DEAD=0,
        INVENTORY_STANDARD_CD="V",
        NON_PRODUCTIVE_CD=None,
        LAND_COVER_CLASS_CD_1=None,
        SPECIES_CD_1="PL",
        SPECIES_PCT_1=100.0,
        SPECIES_CD_2=None,
        SPECIES_PCT_2=None,
        SPECIES_CD_3=None,
        SPECIES_PCT_3=None,
        SPECIES_CD_4=None,
        SPECIES_PCT_4=None,
        SPECIES_CD_5=None,
        SPECIES_PCT_5=None,
        SPECIES_CD_6=None,
        SPECIES_PCT_6=None,
    )
    print(result)
    if result[1] != "C-3":
        raise SystemExit(f"expected C-3 for mature interior pine, got {result[1]!r}")


if __name__ == "__main__":
    main()
