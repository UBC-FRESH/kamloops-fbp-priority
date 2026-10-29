"""Analysis grid, rasterization, and terrain helpers.

The project grid is a 100 m NAD83 / BC Albers (EPSG:3005) grid covering the
Kamloops Fire Centre. It is deliberately aligned to a 100 m origin so the same
extent can be aggregated by an integer factor to 200 m, 400 m, or 800 m without
resampling. ClimateBC is native at 800 m; the grid lets the prototype compare
native-resolution weather with finer fuel and terrain layers without pretending
that the climate data has 100 m information.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from affine import Affine
from rasterio.enums import Resampling
from rasterio.features import rasterize
from rasterio.vrt import WarpedVRT
from rasterio.warp import calculate_default_transform
from rasterio.windows import from_bounds

CRS = "EPSG:3005"
DEFAULT_RESOLUTION = 100.0


@dataclass(frozen=True)
class Grid:
    """A north-up raster grid in EPSG:3005.

    Attributes
    ----------
    transform : affine.Affine
        Affine transform from pixel to map coordinates.
    width : int
        Number of columns.
    height : int
        Number of rows.
    crs : str
        Coordinate reference system. The prototype uses ``EPSG:3005``.
    """

    transform: Affine
    width: int
    height: int
    crs: str = CRS

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        """Return ``(minx, miny, maxx, maxy)`` in map units."""
        left, top = self.transform * (0, 0)
        right, bottom = self.transform * (self.width, self.height)
        return (float(left), float(bottom), float(right), float(top))

    @property
    def shape(self) -> tuple[int, int]:
        """Return ``(height, width)``."""
        return (self.height, self.width)

    @property
    def plot_extent(self) -> tuple[float, float, float, float]:
        """Return ``(left, right, bottom, top)`` for :func:`matplotlib.pyplot.imshow`."""
        minx, miny, maxx, maxy = self.bounds
        return (minx, maxx, miny, maxy)

    def cell_centers(self) -> tuple[np.ndarray, np.ndarray]:
        """Return 1-D x and y coordinate arrays for cell centres."""
        cols = np.arange(self.width, dtype=np.float64) + 0.5
        rows = np.arange(self.height, dtype=np.float64) + 0.5
        xs = self.transform.c + cols * self.transform.a
        ys = self.transform.f + rows * self.transform.e
        return xs, ys


def grid_from_bounds(
    bounds: tuple[float, float, float, float],
    *,
    resolution: float = DEFAULT_RESOLUTION,
    origin: tuple[float, float] | None = None,
) -> Grid:
    """Build a north-up grid that covers ``bounds``.

    Parameters
    ----------
    bounds : tuple of float
        ``(minx, miny, maxx, maxy)`` in EPSG:3005.
    resolution : float, optional
        Cell size in metres. Defaults to 100 m.
    origin : tuple of float or None, optional
        Top-left origin. When omitted, the origin is the bounds rounded down to
        a multiple of ``resolution``.

    Returns
    -------
    Grid
        A grid whose extent contains the requested bounds.
    """
    minx, miny, maxx, maxy = bounds
    if origin is None:
        origin_x = np.floor(minx / resolution) * resolution
        origin_y = np.ceil(maxy / resolution) * resolution
    else:
        origin_x, origin_y = origin
    width = int(np.ceil((maxx - origin_x) / resolution))
    height = int(np.ceil((origin_y - miny) / resolution))
    transform = Affine(resolution, 0.0, origin_x, 0.0, -resolution, origin_y)
    return Grid(transform=transform, width=width, height=height)


def mask_from_polygon(
    polygon: gpd.GeoDataFrame | gpd.GeoSeries,
    grid: Grid,
) -> np.ndarray:
    """Rasterize a polygon to a boolean mask on ``grid``.

    Parameters
    ----------
    polygon : geopandas.GeoDataFrame or geopandas.GeoSeries
        Polygon geometry in EPSG:3005.
    grid : Grid
        Target grid.

    Returns
    -------
    numpy.ndarray
        Boolean array with ``True`` inside the polygon.
    """
    geometries = list(polygon.geometry) if isinstance(polygon, gpd.GeoDataFrame) else list(polygon)
    burned = rasterize(
        [(geom, 1) for geom in geometries],
        out_shape=grid.shape,
        transform=grid.transform,
        fill=0,
        dtype="uint8",
        all_touched=False,
    )
    return burned.astype(bool)


def rasterize_vector(
    frame: gpd.GeoDataFrame,
    grid: Grid,
    *,
    field: str,
    mapping: dict[str, int] | None = None,
    fill: int = 0,
    all_touched: bool = False,
) -> np.ndarray:
    """Rasterize a vector field to an integer grid.

    Parameters
    ----------
    frame : geopandas.GeoDataFrame
        Vector features in EPSG:3005.
    grid : Grid
        Target grid.
    field : str
        Attribute column to burn.
    mapping : dict of str to int or None, optional
        Optional explicit value mapping. When omitted, ``field`` must already
        contain integers.
    fill : int, optional
        Background value. Defaults to 0.
    all_touched : bool, optional
        Passed to :func:`rasterio.features.rasterize`. Defaults to ``False``.

    Returns
    -------
    numpy.ndarray
        Integer array on ``grid``.
    """
    if frame.crs is None:
        raise ValueError("vector frame must have a CRS")
    if str(frame.crs).upper() != CRS:
        frame = frame.to_crs(CRS)
    if mapping is not None:
        codes = frame[field].map(mapping).fillna(fill).astype("int32")
    else:
        codes = frame[field].astype("int32")
    shapes = list(zip(frame.geometry, codes, strict=True))
    return rasterize(
        shapes,
        out_shape=grid.shape,
        transform=grid.transform,
        fill=fill,
        dtype="int32",
        all_touched=all_touched,
    )


def reproject_raster_to_grid(
    source: Path,
    grid: Grid,
    *,
    resampling: Resampling = Resampling.bilinear,
    dtype: str = "float32",
    nodata: float = np.nan,
    src_crs: str | None = None,
) -> np.ndarray:
    """Reproject and resample a raster onto ``grid``.

    Parameters
    ----------
    source : pathlib.Path
        Input raster.
    grid : Grid
        Target grid.
    resampling : rasterio.enums.Resampling, optional
        Resampling method. Use bilinear for continuous layers and nearest for
        categorical layers.
    dtype : str, optional
        Output dtype.
    nodata : float, optional
        Output nodata value.
    src_crs : str or None, optional
        Source CRS override for rasters that omit their CRS tag, such as the
        ClimateBC GeoTIFFs. Ignored when the source declares a CRS.

    Returns
    -------
    numpy.ndarray
        Array on ``grid``.

    Raises
    ------
    ValueError
        When neither the source nor the caller supplies a CRS.
    """
    with rasterio.open(source) as src:
        source_crs = src.crs or src_crs
        if source_crs is None:
            raise ValueError(f"{source} has no CRS; pass src_crs")
        with WarpedVRT(
            src,
            src_crs=source_crs,
            crs=grid.crs,
            transform=grid.transform,
            width=grid.width,
            height=grid.height,
            resampling=resampling,
            src_nodata=src.nodata,
            nodata=nodata,
        ) as vrt:
            destination = vrt.read(1, masked=False)
    return destination.astype(dtype)


def write_raster(
    path: Path,
    array: np.ndarray,
    grid: Grid,
    *,
    dtype: str = "float32",
    nodata: float = np.nan,
    band_description: str | None = None,
) -> Path:
    """Write a single-band GeoTIFF on ``grid``.

    Parameters
    ----------
    path : pathlib.Path
        Destination path. Parent directories are created.
    array : numpy.ndarray
        Two-dimensional array.
    grid : Grid
        Grid definition.
    dtype : str, optional
        Output dtype.
    nodata : float, optional
        Nodata value.
    band_description : str or None, optional
        Optional band description.

    Returns
    -------
    pathlib.Path
        The written path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    profile = {
        "driver": "GTiff",
        "height": grid.height,
        "width": grid.width,
        "count": 1,
        "dtype": dtype,
        "crs": grid.crs,
        "transform": grid.transform,
        "nodata": nodata,
        "compress": "deflate",
        "predictor": 2 if dtype.startswith("float") else 1,
        "BIGTIFF": "IF_SAFER",
    }
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(array.astype(dtype), 1)
        if band_description:
            dst.set_band_description(1, band_description)
    return path


def read_raster(path: Path) -> tuple[np.ndarray, Grid]:
    """Read a single-band raster and its grid.

    Parameters
    ----------
    path : pathlib.Path
        Input raster.

    Returns
    -------
    tuple of (numpy.ndarray, Grid)
        The array and its grid definition.
    """
    with rasterio.open(path) as src:
        array = src.read(1)
        grid = Grid(transform=src.transform, width=src.width, height=src.height, crs=str(src.crs))
    return array, grid


def slope_aspect(
    elevation: np.ndarray,
    grid: Grid,
) -> tuple[np.ndarray, np.ndarray]:
    """Derive slope percent and aspect degrees from an elevation array.

    Uses Horn's finite-difference formulation on the cell-centre grid. Aspect is
    the direction of steepest descent, clockwise from north (0 = north, 90 =
    east). Flat cells are assigned aspect 0 and slope 0.

    Parameters
    ----------
    elevation : numpy.ndarray
        Elevation in metres. NaN marks nodata.
    grid : Grid
        Grid definition.

    Returns
    -------
    tuple of (numpy.ndarray, numpy.ndarray)
        ``(slope_percent, aspect_degrees)`` as float32 arrays.
    """
    if elevation.shape != grid.shape:
        raise ValueError("elevation shape does not match grid")
    values = elevation.astype(np.float64)
    values = np.where(np.isfinite(values), values, np.nan)
    # np.gradient returns d/drow and d/dcol; row 0 is north, so negate d/drow.
    dz_drow, dz_dcol = np.gradient(values, edge_order=1)
    dz_dy = -dz_drow / abs(grid.transform.e)
    dz_dx = dz_dcol / grid.transform.a
    slope = np.sqrt(dz_dx**2 + dz_dy**2) * 100.0
    aspect = np.degrees(np.arctan2(-dz_dx, -dz_dy)) % 360.0
    slope = np.where(np.isfinite(values), slope, np.nan)
    aspect = np.where(np.isfinite(values) & (slope > 0), aspect, 0.0)
    return slope.astype("float32"), aspect.astype("float32")


def crop_raster_to_grid(source: Path, grid: Grid, *, resampling: Resampling) -> np.ndarray:
    """Read a raster window matching ``grid`` when the source overlaps it.

    This is a faster path than :func:`reproject_raster_to_grid` when the source
    already shares the grid CRS and only needs a window read.
    """
    with rasterio.open(source) as src:
        if src.crs is None or str(src.crs).upper() != grid.crs.upper():
            return reproject_raster_to_grid(source, grid, resampling=resampling)
        window = from_bounds(*grid.bounds, transform=src.transform)
        data = src.read(1, window=window, out_shape=grid.shape, resampling=resampling)
        return data


def destination_grid_for_raster(source: Path, *, resolution: float) -> tuple[Grid, None]:
    """Build a destination grid in the source CRS at a requested resolution.

    Kept for completeness when a caller needs to align a source raster before
    reprojecting it to the project grid.
    """
    with rasterio.open(source) as src:
        transform, width, height = calculate_default_transform(
            src.crs, src.crs, src.width, src.height, *src.bounds, resolution=resolution
        )
    return Grid(transform=transform, width=width, height=height, crs=str(src.crs)), None
