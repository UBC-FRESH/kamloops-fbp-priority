"""Scratch exploration: KFC boundary, BEC zones, and LiDAR index coverage."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)

FC_PATH = next((RAW / "bcdc").glob("WHSE_LEGAL_ADMIN_BOUNDARIES_DRP_MOF_FIRE_CENTRES_SP/*.geojson"))
BEC_PATH = next((RAW / "bcdc").glob("WHSE_FOREST_VEGETATION_BEC_BIOGEOCLIMATIC_POLY/*.gpkg"))

fc = gpd.read_file(FC_PATH)
kfc = fc.loc[fc["MOF_FIRE_CENTRE_NAME"] == "Kamloops Fire Centre"].copy()
assert len(kfc) == 1
kfc = kfc.to_crs(3005)
print("KFC area km2:", round(float(kfc.area.sum()) / 1e6, 1))
print("KFC bounds:", tuple(round(float(v), 0) for v in kfc.total_bounds))
kfc[["MOF_FIRE_CENTRE_NAME", "geometry"]].to_file(INTERIM / "kfc.gpkg", driver="GPKG")

bec = gpd.read_file(BEC_PATH)
bec = bec.to_crs(3005)
bec_kfc = gpd.overlay(bec, kfc[["geometry"]], how="intersection", keep_geom_type=False)
bec_kfc["area_km2"] = bec_kfc.area / 1e6
print("\nBEC area in KFC (km2):")
print(bec_kfc.groupby("ZONE")["area_km2"].sum().sort_values(ascending=False).round(1).to_string())
print("\nTotal BEC intersection km2:", round(float(bec_kfc["area_km2"].sum()), 1))
bec_kfc.to_file(INTERIM / "bec_kfc.gpkg", driver="GPKG")

# LiDAR point-cloud tile index query.
BASE = (
    "https://services6.arcgis.com/ubm4tcTYICKBpist/arcgis/rest/services/"
    "LiDAR_BC_S3_Public/FeatureServer/4/query"
)
minx, miny, maxx, maxy = (float(v) for v in kfc.total_bounds)
params = {
    "where": "1=1",
    "geometry": json.dumps(
        {"xmin": minx, "ymin": miny, "xmax": maxx, "ymax": maxy, "spatialReference": {"wkid": 3005}}
    ),
    "geometryType": "esriGeometryEnvelope",
    "inSR": "3005",
    "spatialRel": "esriSpatialRelIntersects",
    "returnCountOnly": "true",
    "f": "json",
}
with urlopen(f"{BASE}?{urlencode(params)}") as response:
    print("\nLiDAR tile count in KFC bbox:", json.load(response))
