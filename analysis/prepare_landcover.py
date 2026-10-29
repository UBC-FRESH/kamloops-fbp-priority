"""Rasterize the KFC mask, BEC zones, and WUI classes onto the 100 m grid."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from kamloops_fbp.grid import (
    grid_from_bounds,
    mask_from_polygon,
    rasterize_vector,
    write_raster,
)

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
RAW = ROOT / "data" / "raw"

ZONES = (
    "BAFA",
    "BG",
    "BWBS",
    "CDF",
    "CMA",
    "CWH",
    "ESSF",
    "ICH",
    "IDF",
    "IMA",
    "MH",
    "MS",
    "PP",
    "SBPS",
    "SBS",
    "SWB",
)
ZONE_CODES = {zone: index + 1 for index, zone in enumerate(ZONES)}


def main() -> int:
    """Write land-cover and WUI rasters plus a zone-code table."""
    kfc = gpd.read_file(INTERIM / "kfc.gpkg")
    grid = grid_from_bounds(tuple(float(v) for v in kfc.total_bounds), resolution=100.0)
    kfc_mask = mask_from_polygon(kfc, grid)
    write_raster(
        INTERIM / "kfc_mask_100m.tif", kfc_mask.astype("uint8"), grid, dtype="uint8", nodata=0
    )

    bec = gpd.read_file(INTERIM / "bec_kfc.gpkg")
    bec_codes = rasterize_vector(bec, grid, field="ZONE", mapping=ZONE_CODES, fill=0)
    bec_codes = np.where(kfc_mask, bec_codes, 0).astype("int32")
    write_raster(INTERIM / "bec_zone_100m.tif", bec_codes, grid, dtype="int32", nodata=0)
    pd.DataFrame({"zone": list(ZONE_CODES), "code": list(ZONE_CODES.values())}).to_csv(
        INTERIM / "bec_zone_codes.csv", index=False
    )

    buffer_path = next(RAW.glob("bcdc/*PROT_WUI_HMN_INTRFCE_BUFFR_SP/*.gpkg"))
    risk_path = next(RAW.glob("bcdc/*PROT_WUI_RISK_CLASS_SP/*.gpkg"))
    buffer = gpd.read_file(buffer_path)
    risk = gpd.read_file(risk_path)
    buffer_codes = rasterize_vector(buffer, grid, field="OBJECTID", mapping=None, fill=0)
    buffer_mask = buffer_codes > 0
    risk_codes = rasterize_vector(risk, grid, field="OBJECTID", mapping=None, fill=0)
    risk_mask = risk_codes > 0
    wui = np.zeros(grid.shape, dtype="uint8")
    wui[buffer_mask] = 1
    wui[risk_mask] = 2
    wui = np.where(kfc_mask, wui, 0).astype("uint8")
    write_raster(INTERIM / "wui_class_100m.tif", wui, grid, dtype="uint8", nodata=0)

    print("grid", grid.width, grid.height)
    print("KFC cells", int(kfc_mask.sum()), "area km2", round(float(kfc_mask.sum()) * 0.01, 1))
    counts = pd.Series(bec_codes[kfc_mask]).value_counts().sort_index()
    labels = {code: zone for zone, code in ZONE_CODES.items()}
    for code, count in counts.items():
        print(
            f"BEC {labels.get(int(code), '?'):<5} {int(count):>10} cells  {count * 0.01:>10.1f} km2"
        )
    print(
        "WUI classes",
        {int(k): int(v) for k, v in zip(*np.unique(wui, return_counts=True), strict=True)},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
