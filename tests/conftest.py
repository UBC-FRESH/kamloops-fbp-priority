"""Make the framework scripts and the analysis package importable from tests."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[1]
SCRIPTS: Path = ROOT / "scripts"
ANALYSIS: Path = ROOT / "analysis"
for path in (SCRIPTS, ANALYSIS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
