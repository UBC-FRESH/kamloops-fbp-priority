"""Download and unpack the provincial FBP fuel-type FGDB with ranged requests.

The BC Data Catalogue resource is a 2.48 GB zip. A single connection to the
public host is slow, so this script splits the file into eight byte ranges,
downloads them in parallel, concatenates the parts, verifies the zip, and
unpacks it. The final directory is ignored by git.
"""

from __future__ import annotations

import json
import shutil
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
FUEL = ROOT / "data" / "raw" / "fuel"
PARTS = FUEL / "parts"
URL = (
    "https://pub.data.gov.bc.ca/datasets/e18ef98c-e1bf-43ac-95e4-b473452f32ec/"
    "PROT_FUEL_TYPE_SP.gdb.zip"
)
TOTAL = 2_482_259_907
CHUNKS = 8
ZIP_PATH = FUEL / "PROT_FUEL_TYPE_SP.gdb.zip"
GDB_PATH = FUEL / "PROT_FUEL_TYPE_SP.gdb"


def download_part(index: int) -> Path:
    """Download one byte range and return the part path."""
    start = TOTAL * index // CHUNKS
    end = TOTAL * (index + 1) // CHUNKS - 1
    destination = PARTS / f"part_{index:02d}"
    expected = end - start + 1
    if destination.exists() and destination.stat().st_size == expected:
        return destination
    request = Request(URL, headers={"Range": f"bytes={start}-{end}"})
    with urlopen(request, timeout=300) as response, destination.open("wb") as handle:
        while chunk := response.read(4 * 1024 * 1024):
            handle.write(chunk)
    if destination.stat().st_size != expected:
        raise RuntimeError(
            f"part {index} has {destination.stat().st_size} bytes, expected {expected}"
        )
    return destination


def main() -> int:
    """Download, verify, and unpack the FGDB."""
    FUEL.mkdir(parents=True, exist_ok=True)
    PARTS.mkdir(parents=True, exist_ok=True)
    parts: list[Path] = []
    with ThreadPoolExecutor(max_workers=CHUNKS) as pool:
        futures = {pool.submit(download_part, index): index for index in range(CHUNKS)}
        for future in as_completed(futures):
            parts.append(future.result())
    with ZIP_PATH.open("wb") as output:
        for index in range(CHUNKS):
            with (PARTS / f"part_{index:02d}").open("rb") as source:
                shutil.copyfileobj(source, output, length=16 * 1024 * 1024)
    if not zipfile.is_zipfile(ZIP_PATH):
        raise RuntimeError("assembled file is not a valid zip")
    with zipfile.ZipFile(ZIP_PATH) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"zip member failed CRC: {bad}")
        archive.extractall(GDB_PATH)
    manifest = {
        "source": URL,
        "retrieved_utc": datetime.now(UTC).isoformat(),
        "bytes": ZIP_PATH.stat().st_size,
        "parts": CHUNKS,
        "destination": str(GDB_PATH.relative_to(ROOT)),
    }
    (FUEL / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"downloaded and unpacked {ZIP_PATH.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
