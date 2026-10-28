"""Download ClimateBC monthly GeoTIFFs for the 2014-2023 July/August window.

ClimateBC exposes the historical-year rasters at a stable URL pattern documented on
its SpatialData page. The files are BC-wide 800 m GeoTIFFs in EPSG:4326. This script
downloads only the variables and years the prototype needs, and records a manifest.
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "climatebc"
OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://media.forestry.ubc.ca/ClimateNA/BC/800m/Year_1901-current"
YEARS = range(2014, 2024)
VARIABLES = ("Tmax07", "Tmax08", "Tmin07", "Tmin08", "RH07", "RH08", "PPT07", "PPT08")


def download(year: int, variable: str) -> Path:
    """Download one ClimateBC raster, skipping it when it already exists."""
    destination = OUT / f"{variable}_{year}.tif"
    if destination.exists() and destination.stat().st_size > 0:
        return destination
    url = f"{BASE}/Year_{year}/{variable}.tif"
    with urlopen(url, timeout=120) as response, destination.open("wb") as handle:
        handle.write(response.read())
    return destination


def main() -> int:
    """Download every requested raster and write a provenance manifest."""
    jobs = [(year, variable) for year in YEARS for variable in VARIABLES]
    completed: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {
            pool.submit(download, year, variable): (year, variable) for year, variable in jobs
        }
        for future in as_completed(futures):
            year, variable = futures[future]
            try:
                path = future.result()
                completed.append(
                    {
                        "year": year,
                        "variable": variable,
                        "path": str(path.relative_to(ROOT)),
                        "bytes": path.stat().st_size,
                    }
                )
            except Exception as exc:
                failures.append({"year": year, "variable": variable, "error": str(exc)})
    manifest = {
        "source": "ClimateBC v7.60, BC 800 m historical years",
        "url_pattern": f"{BASE}/Year_<year>/<variable>.tif",
        "retrieved_utc": datetime.now(UTC).isoformat(),
        "years": list(YEARS),
        "variables": list(VARIABLES),
        "files": sorted(completed, key=lambda item: (str(item["variable"]), int(item["year"]))),
        "failures": failures,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"downloaded {len(completed)} files, {len(failures)} failures")
    if failures:
        print(json.dumps(failures, indent=2))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
