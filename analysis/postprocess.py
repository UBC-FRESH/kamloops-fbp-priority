"""Post-process FBP outputs, build provisional priority classes, and draw maps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

from kamloops_fbp.fuel import R_FUEL_NAMES
from kamloops_fbp.grid import Grid, mask_from_polygon, read_raster, write_raster

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
INTERIM = ROOT / "data" / "interim"
FIGURES = ROOT / "docs" / "figures"
TABLES = ROOT / "docs" / "tables"
FIGURES.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)

HFI_BREAKS = np.array([0, 500, 1000, 2000, 3000, 4000, 6000, 8000, 10000, 30000, np.inf])
HFI_LABELS = [
    "0-500",
    "500-1k",
    "1-2k",
    "2-3k",
    "3-4k",
    "4-6k",
    "6-8k",
    "8-10k",
    "10-30k",
    ">30k",
]
HFI_COLORS = [
    "#f7f7f7",
    "#fee8c8",
    "#fdd49e",
    "#fdbb84",
    "#fc8d59",
    "#ef6548",
    "#d7301f",
    "#b30000",
    "#7f0000",
    "#4d0000",
]
ZONE_COLORS = [
    "#8dd3c7",
    "#ffffb3",
    "#bebada",
    "#fb8072",
    "#80b1d3",
    "#fdb462",
    "#b3de69",
    "#fccde5",
    "#d9d9d9",
    "#bc80bd",
    "#ccebc5",
    "#ffed6f",
    "#e5c494",
    "#66c2a5",
    "#fc8d62",
    "#8da0cb",
]


def resample_categorical(path: Path, grid: Grid) -> np.ndarray:
    """Resample a categorical raster to ``grid`` with nearest-neighbour."""
    with (
        rasterio.open(path) as src,
        WarpedVRT(
            src,
            crs=grid.crs,
            transform=grid.transform,
            width=grid.width,
            height=grid.height,
            resampling=Resampling.nearest,
        ) as vrt,
    ):
        return vrt.read(1)


def load_fbp(path: Path, mask: np.ndarray) -> tuple[dict[str, np.ndarray], Grid]:
    """Read the primary FBP bands and mask them to the KFC."""
    fallback = ["CFB", "CFC", "FD", "HFI", "RAZ", "ROS", "SFC", "TFC"]
    with rasterio.open(path) as src:
        descriptions = [str(desc).upper() for desc in src.descriptions]
        if len(descriptions) != src.count or any(not desc for desc in descriptions):
            descriptions = fallback[: src.count]
        data = {
            name: src.read(index + 1).astype("float32") for index, name in enumerate(descriptions)
        }
        grid = Grid(transform=src.transform, width=src.width, height=src.height, crs=str(src.crs))
    for name in data:
        data[name] = np.where(mask, data[name], np.nan)
    return data, grid


def classify_hfi(hfi: np.ndarray, fuel: np.ndarray) -> np.ndarray:
    """Assign the provisional 10-class HFI scale; 0 is non-fuel/outside."""
    classes = np.digitize(hfi, HFI_BREAKS[1:-1], right=False) + 1
    classes = np.where(np.isfinite(hfi), classes, 0)
    classes = np.where(np.isin(fuel, [13, 19]), 0, classes)
    return classes.astype("uint8")


def priority_from_hfi(hfi_class: np.ndarray, wui: np.ndarray) -> np.ndarray:
    """Combine the HFI class and WUI class with a transparent provisional rule."""
    priority = hfi_class.copy()
    priority[wui == 1] = np.ceil(hfi_class[wui == 1] / 2.0).astype("uint8")
    priority[wui == 2] = hfi_class[wui == 2]
    priority[(wui == 0) | (hfi_class == 0)] = 0
    return priority.astype("uint8")


def zonal_summary(
    zones: np.ndarray,
    zone_codes: pd.DataFrame,
    kfc: np.ndarray,
    arrays: dict[str, np.ndarray],
    fuel: np.ndarray,
    wui: np.ndarray,
    priority: np.ndarray,
    *,
    cell_area_km2: float,
) -> pd.DataFrame:
    """Compute one row of fire-behaviour statistics per BEC zone."""
    rows: list[dict[str, object]] = []
    for _, row in zone_codes.iterrows():
        zone = str(row["zone"])
        code = int(row["code"])
        mask = (zones == code) & kfc
        area = float(mask.sum()) * cell_area_km2
        if area <= 0:
            continue
        hfi = arrays["HFI"][mask]
        ros = arrays["ROS"][mask]
        fl = arrays["FLAME"][mask]
        cfb = arrays["CFB"][mask]
        fd = arrays["FD"][mask]
        rows.append(
            {
                "zone": zone,
                "area_km2": round(area, 1),
                "hfi_mean": round(float(np.nanmean(hfi)), 1),
                "hfi_p50": round(float(np.nanpercentile(hfi, 50)), 1),
                "hfi_p90": round(float(np.nanpercentile(hfi, 90)), 1),
                "hfi_p99": round(float(np.nanpercentile(hfi, 99)), 1),
                "hfi_max": round(float(np.nanmax(hfi)), 1),
                "ros_mean_m_min": round(float(np.nanmean(ros)), 2),
                "ros_p90_m_min": round(float(np.nanpercentile(ros, 90)), 2),
                "flame_mean_m": round(float(np.nanmean(fl)), 2),
                "flame_p90_m": round(float(np.nanpercentile(fl, 90)), 2),
                "cfb_mean": round(float(np.nanmean(cfb)), 3),
                "pct_surface": round(100.0 * float(np.mean(fd == 1)), 1),
                "pct_intermittent": round(100.0 * float(np.mean(fd == 2)), 1),
                "pct_crown": round(100.0 * float(np.mean(fd == 3)), 1),
                "pct_nonfuel": round(100.0 * float(np.mean(np.isin(fuel[mask], [13, 19]))), 1),
                "wui_area_km2": round(
                    float(((wui == 1) | (wui == 2))[mask].sum()) * cell_area_km2, 1
                ),
                "priority_ge7_km2": round(float((priority[mask] >= 7).sum()) * cell_area_km2, 1),
            }
        )
    return pd.DataFrame(rows).sort_values("area_km2", ascending=False)


def fuel_table(fuel: np.ndarray, kfc: np.ndarray, *, cell_area_km2: float) -> pd.DataFrame:
    """Summarize fuel-type area within the KFC."""
    rows = []
    for code, count in zip(*np.unique(fuel[kfc], return_counts=True), strict=True):
        rows.append(
            {
                "r_code": int(code),
                "fuel_type": R_FUEL_NAMES.get(int(code), "unknown"),
                "area_km2": round(float(count) * cell_area_km2, 1),
            }
        )
    return pd.DataFrame(rows).sort_values("area_km2", ascending=False)


def map_setup(ax: plt.Axes, grid: Grid, title: str) -> None:
    """Apply the common map frame."""
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel("Easting (m, EPSG:3005)", fontsize=8)
    ax.set_ylabel("Northing (m, EPSG:3005)", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.set_aspect("equal")


def add_scale_and_north(ax: plt.Axes, grid: Grid) -> None:
    """Add a 50 km scale bar and a north arrow."""
    minx, miny, maxx, maxy = grid.bounds
    x0 = minx + 0.04 * (maxx - minx)
    y0 = miny + 0.04 * (maxy - miny)
    ax.plot([x0, x0 + 50000], [y0, y0], color="black", linewidth=2)
    ax.text(x0 + 25000, y0 + 0.012 * (maxy - miny), "50 km", ha="center", fontsize=7)
    ax.annotate(
        "N",
        xy=(maxx - 0.06 * (maxx - minx), maxy - 0.06 * (maxy - miny)),
        xytext=(maxx - 0.06 * (maxx - minx), maxy - 0.12 * (maxy - miny)),
        arrowprops={"arrowstyle": "-|>", "color": "black"},
        ha="center",
        fontsize=8,
        fontweight="bold",
    )


def plot_bec(
    grid: Grid,
    bec: np.ndarray,
    kfc: gpd.GeoDataFrame,
    zones: gpd.GeoDataFrame,
    zone_codes: pd.DataFrame,
    *,
    prefix: str,
) -> None:
    """Draw the BEC zone map."""
    fig, ax = plt.subplots(figsize=(7.2, 7.8))
    cmap = ListedColormap(ZONE_COLORS[:16])
    norm = BoundaryNorm(np.arange(0.5, 17.5, 1), cmap.N)
    ax.imshow(
        np.where(bec > 0, bec, np.nan),
        extent=grid.plot_extent,
        cmap=cmap,
        norm=norm,
        interpolation="nearest",
    )
    kfc.boundary.plot(ax=ax, color="black", linewidth=1.0)
    zones.boundary.plot(ax=ax, color="white", linewidth=0.25, alpha=0.7)
    for zone in ("ICH", "IDF", "PP"):
        sub = zones[zones["ZONE"] == zone]
        if not sub.empty:
            point = sub.geometry.representative_point().iloc[0]
            ax.text(
                point.x,
                point.y,
                zone,
                fontsize=8,
                fontweight="bold",
                ha="center",
                color="black",
                bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "alpha": 0.65, "lw": 0},
            )
    map_setup(ax, grid, "Biogeoclimatic zones in the Kamloops Fire Centre")
    add_scale_and_north(ax, grid)
    present = {int(v) for v in np.unique(bec) if v > 0}
    handles = [
        Patch(
            facecolor=ZONE_COLORS[int(row["code"]) - 1],
            edgecolor="gray",
            label=str(row["zone"]),
        )
        for _, row in zone_codes.sort_values("code").iterrows()
        if int(row["code"]) in present
    ]
    ax.legend(handles=handles, loc="upper left", fontsize=5, ncol=2, framealpha=0.8)
    fig.tight_layout()
    fig.savefig(FIGURES / f"{prefix}bec_zones.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_lidar(grid: Grid, lidar: np.ndarray, kfc: gpd.GeoDataFrame, *, prefix: str) -> None:
    """Draw the point-cloud tile coverage map."""
    fig, ax = plt.subplots(figsize=(7.2, 7.8))
    ax.imshow(
        np.where(lidar > 0, 1, np.nan),
        extent=grid.plot_extent,
        cmap=ListedColormap(["#2c7fb8"]),
        interpolation="nearest",
    )
    kfc.boundary.plot(ax=ax, color="black", linewidth=1.0)
    map_setup(ax, grid, "LidarBC point-cloud tile coverage in the KFC")
    add_scale_and_north(ax, grid)
    ax.legend(
        [Patch(facecolor="#2c7fb8")], ["Point-cloud tile present"], loc="upper left", fontsize=7
    )
    fig.tight_layout()
    fig.savefig(FIGURES / f"{prefix}lidar_coverage.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_classes(
    grid: Grid,
    array: np.ndarray,
    kfc: gpd.GeoDataFrame,
    *,
    title: str,
    labels: list[str],
    colors: list[str],
    filename: str,
    vmax: int | None = None,
) -> None:
    """Draw a categorical raster map."""
    fig, ax = plt.subplots(figsize=(7.2, 7.8))
    cmap = ListedColormap(colors)
    vmax = vmax if vmax is not None else len(colors)
    norm = BoundaryNorm(np.arange(0.5, vmax + 1.5, 1), cmap.N)
    ax.imshow(
        np.where(array > 0, array, np.nan),
        extent=grid.plot_extent,
        cmap=cmap,
        norm=norm,
        interpolation="nearest",
    )
    kfc.boundary.plot(ax=ax, color="black", linewidth=1.0)
    map_setup(ax, grid, title)
    add_scale_and_north(ax, grid)
    handles = [
        Patch(facecolor=color, edgecolor="gray", label=label)
        for color, label in zip(colors, labels, strict=True)
    ]
    ax.legend(handles=handles, loc="upper left", fontsize=5, ncol=2, framealpha=0.8)
    fig.tight_layout()
    fig.savefig(FIGURES / filename, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_three_zones(
    grid: Grid,
    hfi_class: np.ndarray,
    zones: np.ndarray,
    zone_codes: pd.DataFrame,
    kfc: gpd.GeoDataFrame,
) -> None:
    """Draw the three test zones side by side."""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.8))
    cmap = ListedColormap(HFI_COLORS)
    norm = BoundaryNorm(np.arange(0.5, 11.5, 1), cmap.N)
    for ax, zone in zip(axes, ("ICH", "IDF", "PP"), strict=True):
        code = int(zone_codes.loc[zone_codes["zone"] == zone, "code"].iloc[0])
        mask = zones == code
        rows, cols = np.where(mask)
        if len(rows) == 0:
            ax.set_axis_off()
            continue
        pad = 8
        r0, r1 = max(rows.min() - pad, 0), min(rows.max() + pad, grid.height)
        c0, c1 = max(cols.min() - pad, 0), min(cols.max() + pad, grid.width)
        sub = np.where(mask[r0:r1, c0:c1], hfi_class[r0:r1, c0:c1], np.nan)
        left, top = grid.transform * (c0, r0)
        right, bottom = grid.transform * (c1, r1)
        ax.imshow(
            sub, extent=(left, right, bottom, top), cmap=cmap, norm=norm, interpolation="nearest"
        )
        kfc.boundary.plot(ax=ax, color="black", linewidth=0.6)
        ax.set_title(f"{zone} ({int(mask.sum()) * 0.01:,.0f} km²)", fontsize=10, fontweight="bold")
        ax.set_aspect("equal")
        ax.tick_params(labelsize=6)
        ax.set_xlabel("Easting (m)", fontsize=7)
    axes[0].set_ylabel("Northing (m)", fontsize=7)
    handles = [
        Patch(facecolor=color, edgecolor="gray", label=label)
        for color, label in zip(HFI_COLORS, HFI_LABELS, strict=True)
    ]
    fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=6, frameon=False)
    fig.suptitle(
        "Head fire intensity classes (kW/m), provisional 10-class scale",
        fontsize=11,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(FIGURES / "three_zones_hfi.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    """Run all post-processing and write the summary tables and figures."""
    parser = argparse.ArgumentParser(description="Post-process FBP outputs.")
    parser.add_argument("--resolution", type=int, default=200, choices=(100, 200))
    parser.add_argument("--three-zones", action="store_true")
    args = parser.parse_args()
    prefix = "three_zones_" if args.three_zones else "kfc_"

    kfc = gpd.read_file(INTERIM / "kfc.gpkg")
    bec = gpd.read_file(INTERIM / "bec_kfc.gpkg")
    zone_codes = pd.read_csv(INTERIM / "bec_zone_codes.csv")
    fbp_path = (
        PROCESSED / "fbp_three_zones_100m.tif"
        if args.three_zones
        else PROCESSED / f"fbp_{args.resolution}m.tif"
    )
    input_path = (
        PROCESSED / "fbp_inputs_three_zones_100m.tif"
        if args.three_zones
        else PROCESSED / f"fbp_inputs_{args.resolution}m.tif"
    )
    with rasterio.open(fbp_path) as src:
        grid = Grid(transform=src.transform, width=src.width, height=src.height, crs=str(src.crs))
    if args.three_zones:
        kfc_mask, _ = read_raster(INTERIM / "three_zone_mask_100m.tif")
    else:
        kfc_mask = mask_from_polygon(kfc, grid)
    kfc_mask = kfc_mask.astype(bool)
    data, grid = load_fbp(fbp_path, kfc_mask)
    zones = resample_categorical(INTERIM / "bec_zone_100m.tif", grid)
    wui = resample_categorical(INTERIM / "wui_class_100m.tif", grid)
    lidar = resample_categorical(INTERIM / "lidar_coverage_100m.tif", grid)
    fuel, _ = read_raster(input_path)
    hfi = np.where(np.isfinite(data["HFI"]), data["HFI"], 0.0)
    data["FLAME"] = np.where(hfi > 0, 0.0775 * np.power(hfi, 0.46), 0.0)
    hfi_class = classify_hfi(hfi, fuel)
    priority = priority_from_hfi(hfi_class, wui)

    for name, array in (
        ("HFI", hfi),
        ("FLAME", data["FLAME"]),
        ("FD", data["FD"]),
        ("CFB", data["CFB"]),
        ("ROS", data["ROS"]),
        ("TFC", data["TFC"]),
    ):
        write_raster(
            PROCESSED / f"{prefix}{name.lower()}_{args.resolution}m.tif",
            np.where(kfc_mask, array, np.nan),
            grid,
            band_description=name,
        )
    write_raster(
        PROCESSED / f"{prefix}hfi_class_{args.resolution}m.tif",
        hfi_class,
        grid,
        dtype="uint8",
        nodata=0,
    )
    write_raster(
        PROCESSED / f"{prefix}priority_class_{args.resolution}m.tif",
        priority,
        grid,
        dtype="uint8",
        nodata=0,
    )

    cell_area_km2 = (args.resolution / 1000.0) ** 2
    summary = zonal_summary(
        zones,
        zone_codes,
        kfc_mask,
        data,
        fuel,
        wui,
        priority,
        cell_area_km2=cell_area_km2,
    )
    summary.to_csv(TABLES / f"{prefix}fbp_summary_by_bec.csv", index=False)
    fuel_table(fuel, kfc_mask, cell_area_km2=cell_area_km2).to_csv(
        TABLES / f"{prefix}fuel_type_area_kfc.csv", index=False
    )
    print(summary.to_string(index=False))
    print(
        "\nFuel area:\n",
        fuel_table(fuel, kfc_mask, cell_area_km2=cell_area_km2).to_string(index=False),
    )

    plot_bec(grid, zones, kfc, bec, zone_codes, prefix=prefix)
    plot_lidar(grid, lidar, kfc, prefix=prefix)
    plot_classes(
        grid,
        hfi_class,
        kfc,
        title="Head fire intensity classes (kW/m), provisional",
        labels=HFI_LABELS,
        colors=HFI_COLORS,
        filename=f"{prefix}fbp_hfi_classes.png",
    )
    plot_classes(
        grid,
        priority,
        kfc,
        title="Provisional fuel-treatment priority classes (white = outside WUI)",
        labels=[str(i) for i in range(1, 11)],
        colors=HFI_COLORS,
        filename=f"{prefix}priority_classes.png",
        vmax=10,
    )
    fire_type = np.where(
        data["FD"] == 1, 1, np.where(data["FD"] == 2, 2, np.where(data["FD"] == 3, 3, 0))
    )
    plot_classes(
        grid,
        fire_type,
        kfc,
        title="FBP fire type",
        labels=["Surface", "Intermittent crown", "Active crown"],
        colors=["#fee08b", "#f46d43", "#9e0142"],
        filename=f"{prefix}fbp_fire_type.png",
        vmax=3,
    )
    if args.three_zones:
        plot_three_zones(grid, hfi_class, zones, zone_codes, kfc)

    metadata = {
        "hfi_breaks_kw_m": [float(v) for v in HFI_BREAKS.tolist()],
        "hfi_labels": HFI_LABELS,
        "priority_rule": {
            "outside_wui": 0,
            "wui_human_interface_buffer": "ceil(HFI class / 2)",
            "wui_risk_class": "HFI class",
        },
        "flame_length_formula": "0.0775 * HFI^0.46 (Byram 1959)",
    }
    (TABLES / f"{prefix}postprocess_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
