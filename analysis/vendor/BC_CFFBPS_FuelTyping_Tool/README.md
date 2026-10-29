# BC_CFFBPS_FuelTyping_Tool (vendored)

Third-party code. Do not edit `bcwft2018.py` in place; record any wrapper or patch in the project
code instead.

- Source: https://github.com/gagreene/BC_CFFBPS_FuelTyping_Tool
- Commit: `13bc0c913437141e2984f530a2197296fb6da0b0`
- Vendored file: `bcwft2018.py`
- Licence: GPL-3.0; see `LICENSE`
- Author: Gregory A. Greene
- Used by: `analysis/smoke_open_fuel_typing.py`, P1.4, and P3

The file implements the 2018 BC fuel-typing decision tree. The class `FuelTyping` has one public
entry point:

```python
FuelTyping().getFuelType(...)
```

It returns `(process_number, fuel_type, modifier)`. The wrapper supplies the 21 VRI attributes.

The project's original code is MIT-licensed. This vendored directory remains GPL-3.0; do not
relicense it as MIT.
