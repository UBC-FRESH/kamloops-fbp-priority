"""Crosswalk from BC fuel-type codes to the cffdrs R raster codes.

The BC provincial fuel-type layer uses grouped codes for some fuel types
(``D-1/2``, ``M-1/2``, ``M-3/4``, ``O-1a/b``). The FBP raster functions need a
single code per cell. The choices below are explicit modelling decisions, not
facts about the layer:

- ``D-1/2`` -> D-1 (leafless aspen, the more flammable of the pair),
- ``M-1/2`` -> M-2 (green mixedwood, matching July/August),
- ``M-3/4`` -> M-3 (leafless dead-fir mixedwood, the more flammable of the pair),
- ``O-1a/b`` -> O-1b (standing grass, the usual summer condition).

A future sensitivity run should test the alternate choice for each grouped code.
"""

from __future__ import annotations

from dataclasses import dataclass

# cffdrs::fbpRaster fuel codes, in the order documented by the package.
R_FUEL_NAMES: dict[int, str] = {
    1: "C-1",
    2: "C-2",
    3: "C-3",
    4: "C-4",
    5: "C-5",
    6: "C-6",
    7: "C-7",
    8: "D-1",
    9: "M-1",
    10: "M-2",
    11: "M-3",
    12: "M-4",
    13: "NF",
    14: "O-1a",
    15: "O-1b",
    16: "S-1",
    17: "S-2",
    18: "S-3",
    19: "WA",
}

BC_TO_R: dict[str, int] = {
    "C-1": 1,
    "C-2": 2,
    "C-3": 3,
    "C-4": 4,
    "C-5": 5,
    "C-6": 6,
    "C-7": 7,
    "D-1": 8,
    "D-2": 8,
    "D-1/2": 8,
    "M-1": 9,
    "M-2": 10,
    "M-1/2": 10,
    "M-3": 11,
    "M-4": 12,
    "M-3/4": 11,
    "O-1a": 14,
    "O-1b": 15,
    "O-1a/b": 15,
    "S-1": 16,
    "S-2": 17,
    "S-3": 18,
    "N": 13,
    "NF": 13,
    "W": 19,
    "WA": 19,
}

# Table 7 defaults from FCFDG (1992), mirrored from cffdrs.
CBH_DEFAULT: dict[int, float] = {
    1: 2.0,
    2: 3.0,
    3: 8.0,
    4: 4.0,
    5: 18.0,
    6: 7.0,
    7: 10.0,
    8: 0.0,
    9: 6.0,
    10: 6.0,
    11: 6.0,
    12: 6.0,
    13: float("nan"),
    14: 0.0,
    15: 0.0,
    16: 0.0,
    17: 0.0,
    18: 0.0,
    19: float("nan"),
}

CFL_DEFAULT: dict[int, float] = {
    1: 0.75,
    2: 0.8,
    3: 1.15,
    4: 1.2,
    5: 1.2,
    6: 1.8,
    7: 0.5,
    8: 0.0,
    9: 0.8,
    10: 0.8,
    11: 0.8,
    12: 0.8,
    13: float("nan"),
    14: 0.0,
    15: 0.0,
    16: 0.0,
    17: 0.0,
    18: 0.0,
    19: float("nan"),
}


def normalize_bc_fuel_code(code: str) -> str:
    """Strip the BC modifier prefix from a fuel-type code.

    The full provincial layer contains values such as ``B26_O-1a/b`` and
    ``B71_S-2``. The segment before the first underscore is a BC modifier; the
    FBP fuel type is the segment after it.

    Parameters
    ----------
    code : str
        Raw ``FUEL_TYPE_CD`` value.

    Returns
    -------
    str
        The fuel-type segment, or the stripped input when there is no modifier
        prefix.
    """
    text = code.strip()
    if "_" in text:
        prefix, suffix = text.split("_", 1)
        if prefix.startswith("B") and prefix[1:].isdigit():
            return suffix
    return text


@dataclass(frozen=True)
class FuelConversion:
    """Converted fuel attributes for one BC fuel-type string.

    Attributes
    ----------
    r_code : int
        cffdrs raster fuel code from 1 to 19.
    cbh : float
        Crown base height in metres.
    cfl : float
        Crown fuel load in kg/m2.
    notes : str
        The assumption applied to a grouped BC code.
    """

    r_code: int
    cbh: float
    cfl: float
    notes: str


def convert_bc_fuel(code: str) -> FuelConversion:
    """Convert one BC fuel-type code to cffdrs attributes.

    Parameters
    ----------
    code : str
        BC ``FUEL_TYPE_CD`` value, such as ``C-3`` or ``O-1a/b``.

    Returns
    -------
    FuelConversion
        The cffdrs code plus Table 7 crown defaults.

    Raises
    ------
    ValueError
        When the BC code is not in the crosswalk.
    """
    normalized = normalize_bc_fuel_code(code)
    if normalized not in BC_TO_R:
        raise ValueError(f"unknown BC fuel type: {code!r}")
    r_code = BC_TO_R[normalized]
    note = ""
    if normalized in {"D-1/2", "M-1/2", "M-3/4", "O-1a/b"}:
        note = f"grouped BC code {normalized} mapped to {R_FUEL_NAMES[r_code]}"
    return FuelConversion(
        r_code=r_code,
        cbh=CBH_DEFAULT[r_code],
        cfl=CFL_DEFAULT[r_code],
        notes=note,
    )


def percent_conifer(code: str, percent_conifer: float, m1_2_percent: float) -> float:
    """Return the percent-conifer input for M1/M2 fuel types.

    Parameters
    ----------
    code : str
        BC fuel-type code.
    percent_conifer : float
        ``PERCENT_CONIFER`` from the BC layer.
    m1_2_percent : float
        ``M1_2_PERCENT_CONIFER`` from the BC layer.

    Returns
    -------
    float
        The M1/M2 conifer percentage when applicable, otherwise 50.
    """
    if normalize_bc_fuel_code(code) in {"M-1/2", "M-1", "M-2"}:
        if m1_2_percent is not None and m1_2_percent > 0:
            return float(m1_2_percent)
        if percent_conifer is not None and percent_conifer > 0:
            return float(percent_conifer)
    return 50.0


def percent_dead_fir(code: str, percent_dead_fir: float) -> float:
    """Return the percent-dead-fir input for M3/M4 fuel types.

    Parameters
    ----------
    code : str
        BC fuel-type code.
    percent_dead_fir : float
        ``PERCENT_DEAD_FIR`` from the BC layer.

    Returns
    -------
    float
        The dead-fir percentage when applicable, otherwise 35.
    """
    if (
        normalize_bc_fuel_code(code) in {"M-3/4", "M-3", "M-4"}
        and percent_dead_fir is not None
        and percent_dead_fir > 0
    ):
        return float(percent_dead_fir)
    return 35.0
