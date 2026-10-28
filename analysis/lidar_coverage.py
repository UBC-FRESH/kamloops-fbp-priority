"""Quantify LidarBC point-cloud coverage by BEC zone in the Kamloops Fire Centre.

The LidarBC Open LiDAR Data Index is an ArcGIS Feature Service. Layer 4 is the
point-cloud tile index and carries the S3 URL, acquisition year, and point
density for every tile. This script queries the tiles intersecting the KFC,
rasterizes their footprints on the 100 m grid, and reports coverage by BEC zone.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
from shapely.ops import unary_union

from kamloops_fbp.grid import grid_from_bounds, rasterize_vector, read_raster, write_raster

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
TABLES = ROOT / "docs" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)
SERVICE = (
    "https://services6.arcgis.com/ubm4tcTYICKBpist/arcgis/rest/services/"
    "LiDAR_BC_S3_Public/FeatureServer/4/query"
)


def query_tiles(bbox: tuple[float, float, float, float]) -> list[dict[str, object]]:
    """Query every tile feature intersecting ``bbox`` in EPSG:3005."""
    minx, miny, maxx, maxy = bbox
    base_params = {
        "where": "1=1",
        "geometry": json.dumps(
            {
                "xmin": minx,
                "ymin": miny,
                "xmax": maxx,
                "ymax": maxy,
                "spatialReference": {"wkid": 3005},
            }
        ),
        "geometryType": "esriGeometryEnvelope",
        "inSR": "3005",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "year,density,maptile",
        "returnGeometry": "true",
        "outSR": "3005",
        "f": "json",
        "resultRecordCount": "1000",
    }
    features: list[dict[str, object]] = []
    offset = 0
    while True:
        params = dict(base_params, resultOffset=str(offset))
        with urlopen(f"{SERVICE}?{urlencode(params)}", timeout=120) as response:
            payload = json.load(response)
        batch = payload.get("features", [])
        if not batch:
            break
        features.extend(batch)
        offset += len(batch)
        print(f"queried {offset} tiles")
        if len(batch) < 1000:
            break
    return features


def to_frame(features: list[dict[str, object]]) -> gpd.GeoDataFrame:
    """Convert ArcGIS tile features to a GeoDataFrame."""
    rows = []
    for feature in features:
        attributes = feature.get("attributes", {})
        geometry = feature.get("geometry") or {}
        rings = geometry.get("rings") or []
        if not rings:
            continue
        polygons = [Polygon(ring) for ring in rings if len(ring) >= 4]
        if not polygons:
            continue
        geom = unary_union(polygons)
        rows.append(
            {
                "year": attributes.get("year"),
                "density": attributes.get("density"),
                "maptile": attributes.get("maptile"),
                "geometry": geom,
            }
        )
    return gpd.GeoDataFrame(rows, crs="EPSG:3005")


def main() -> int:
    """Compute and write the LiDAR coverage table."""
    kfc = gpd.read_file(INTERIM / "kfc.gpkg")
    grid = grid_from_bounds(tuple(float(v) for v in kfc.total_bounds), resolution=100.0)
    bec, _ = read_raster(INTERIM / "bec_zone_100m.tif")
    kfc_mask, _ = read_raster(INTERIM / "kfc_mask_100m.tif")
    kfc_mask = kfc_mask.astype(bool)
    features = query_tiles(tuple(float(v) for v in kfc.total_bounds))
    tiles = to_frame(features)
    print("tile polygons", len(tiles))
    tiles["PRESENT"] = 1
    lidar = rasterize_vector(tiles, grid, field="PRESENT", fill=0).astype(bool)
    lidar = lidar & kfc_mask
    write_raster(
        INTERIM / "lidar_coverage_100m.tif", lidar.astype("uint8"), grid, dtype="uint8", nodata=0
    )
    tiles.to_file(INTERIM / "lidar_tiles_kfc.gpkg", driver="GPKG")

    zone_codes = pd.read_csv(INTERIM / "bec_zone_codes.csv")
    rows = []
    for _, row in zone_codes.iterrows():
        zone = str(row["zone"])
        code = int(row["code"])
        zone_mask = (bec == code) & kfc_mask
        area = float(zone_mask.sum()) * 0.01
        covered = float((zone_mask & lidar).sum()) * 0.01
        rows.append(
            {
                "zone": zone,
                "area_km2": round(area, 1),
                "lidar_area_km2": round(covered, 1),
                "lidar_coverage_pct": round(100.0 * covered / area, 1) if area else 0.0,
            }
        )
    table = pd.DataFrame(rows).sort_values("area_km2", ascending=False)
    table.to_csv(TABLES / "lidar_coverage_by_bec.csv", index=False)
    print(table.to_string(index=False))
    total_area = float(kfc_mask.sum()) * 0.01
    total_covered = float((kfc_mask & lidar).sum()) * 0.01
    coverage_pct = 100 * total_covered / total_area
    print(f"KFC coverage: {total_covered:.0f} / {total_area:.0f} km2 = {coverage_pct:.1f}%")
    print(
        f"tiles in KFC bbox: {len(tiles)}; years {sorted(tiles['year'].dropna().unique().tolist())}"
    )
    print("density counts:", tiles["density"].value_counts().sort_index().to_dict())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
