"""Download Copernicus GLO-30 DEM tiles covering the Kamloops Fire Centre.

The proposal names the BC CDED 1:250,000 DEM. That product is distributed as
hundreds of 1:20,000 GeoTIFF tiles. The prototype uses the public Copernicus
GLO-30 COG tiles as a drop-in 30 m DEM so the terrain pipeline can be exercised
without assembling the full CDED tile mosaic. The production run should switch
the source path to CDED and keep the same slope/aspect code.
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "dem" / "copernicus"
OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://copernicus-dem-30m.s3.amazonaws.com"
TILES = [
    f"Copernicus_DSM_COG_10_N{lat:02d}_00_W{lon:03d}_00_DEM"
    for lat in range(49, 53)
    for lon in range(118, 124)
]


def download(tile: str) -> Path:
    """Download one Copernicus tile unless it is already present."""
    destination = OUT / f"{tile}.tif"
    if destination.exists() and destination.stat().st_size > 0:
        return destination
    url = f"{BASE}/{tile}/{tile}.tif"
    with urlopen(url, timeout=300) as response, destination.open("wb") as handle:
        while chunk := response.read(1024 * 1024):
            handle.write(chunk)
    return destination


def main() -> int:
    """Download every tile and write a provenance manifest."""
    files: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(download, tile): tile for tile in TILES}
        for future in as_completed(futures):
            tile = futures[future]
            try:
                path = future.result()
                files.append(
                    {
                        "tile": tile,
                        "path": str(path.relative_to(ROOT)),
                        "bytes": path.stat().st_size,
                    }
                )
            except Exception as exc:
                failures.append({"tile": tile, "error": str(exc)})
    manifest = {
        "source": "Copernicus GLO-30 COG, AWS Open Data",
        "url_pattern": f"{BASE}/<tile>/<tile>.tif",
        "retrieved_utc": datetime.now(UTC).isoformat(),
        "files": sorted(files, key=lambda item: str(item["tile"])),
        "failures": failures,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"downloaded {len(files)} tiles, {len(failures)} failures")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
