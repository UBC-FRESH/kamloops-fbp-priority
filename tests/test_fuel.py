"""Unit tests for the BC-to-cffdrs fuel crosswalk."""

from __future__ import annotations

import math

import pytest

from kamloops_fbp.fuel import (
    BC_TO_R,
    CBH_DEFAULT,
    CFL_DEFAULT,
    R_FUEL_NAMES,
    convert_bc_fuel,
    normalize_bc_fuel_code,
    percent_conifer,
    percent_dead_fir,
)


def test_every_bc_code_maps_to_a_documented_r_code() -> None:
    """Every crosswalk value has a cffdrs name and crown defaults."""
    assert set(BC_TO_R.values()) <= set(R_FUEL_NAMES)
    assert set(BC_TO_R.values()) <= set(CBH_DEFAULT)
    assert set(BC_TO_R.values()) <= set(CFL_DEFAULT)


def test_grouped_codes_are_explicit() -> None:
    """Grouped BC codes map to the documented single code and say so."""
    assert convert_bc_fuel("D-1/2").r_code == 8
    assert convert_bc_fuel("M-1/2").r_code == 10
    assert convert_bc_fuel("M-3/4").r_code == 11
    assert convert_bc_fuel("O-1a/b").r_code == 15
    assert "grouped" in convert_bc_fuel("D-1/2").notes
    assert convert_bc_fuel("C-3").notes == ""


def test_c3_crown_defaults() -> None:
    """C-3 uses the Table 7 crown base height and fuel load."""
    result = convert_bc_fuel("C-3")
    assert result.r_code == 3
    assert result.cbh == 8.0
    assert result.cfl == 1.15


def test_non_fuel_codes_have_nan_crown_defaults() -> None:
    """NF and WA have no crown fuel defaults."""
    assert math.isnan(convert_bc_fuel("N").cbh)
    assert math.isnan(convert_bc_fuel("W").cfl)


def test_modifier_prefix_is_stripped() -> None:
    """BC modifier prefixes such as B26_ do not become non-fuel."""
    assert normalize_bc_fuel_code("B26_O-1a/b") == "O-1a/b"
    assert normalize_bc_fuel_code("B71_S-2") == "S-2"
    assert normalize_bc_fuel_code("B01_N") == "N"
    assert convert_bc_fuel("B26_O-1a/b").r_code == 15
    assert convert_bc_fuel("B71_S-2").r_code == 17


def test_unknown_code_raises() -> None:
    """An unknown BC code is a hard error, not a silent default."""
    with pytest.raises(ValueError, match="unknown BC fuel type"):
        convert_bc_fuel("X-9")


def test_percent_conifer_prefers_the_m1_m2_field() -> None:
    """M1/M2 use the dedicated conifer field when it is populated."""
    assert percent_conifer("M-1/2", 60.0, 32.0) == 32.0
    assert percent_conifer("M-1/2", 60.0, 0.0) == 60.0
    assert percent_conifer("C-3", 99.0, 0.0) == 50.0


def test_percent_dead_fir_only_applies_to_m3_m4() -> None:
    """Dead-fir percentage is used only for the M3/M4 group."""
    assert percent_dead_fir("M-3/4", 65.0) == 65.0
    assert percent_dead_fir("C-3", 65.0) == 35.0
