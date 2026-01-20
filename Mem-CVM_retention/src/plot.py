import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
from matplotlib.ticker import AutoMinorLocator, NullFormatter
import matplotlib.cm as cm
import os

from src.metadata_utils import get_capacitance_near_target_bias, compute_elapsed_time_seconds








def plot_memCVM_retention_vs_time(
    DF_CVM: list,                  # list[pd.DataFrame]
    Timestamps: list[str],          # list of strings like "01/19/2026 17:41:53"
    Output_dir: str | None = None,
    reading_voltage: float = 0.0,
    time_unit: str = "s",           # "s", "h", "days"
    marker_size: int = 40,
    title: str | None = None,
    filename: str | None = None,
):
    """
    Paper-friendly plot:
    Memory capacitance (near reading_voltage) vs time.

    - DF_CVM: list of CVM DataFrames (one per read)
    - Timestamps: same length as DF_CVM
    - time_unit: "s", "h", or "days"
    """

    if len(DF_CVM) == 0:
        raise ValueError("DF_CVM is empty.")
    if len(DF_CVM) != len(Timestamps):
        raise ValueError("DF_CVM and Timestamps must have the same length.")

    # =========================
    # Build arrays
    # =========================
    Caps = []
    for df in DF_CVM:
        c = float(get_capacitance_near_target_bias(df=df, target=reading_voltage))
        Caps.append(c)

    time_s = compute_elapsed_time_seconds(Timestamps)

    Caps = np.asarray(Caps, dtype=float)
    time_s = np.asarray(time_s, dtype=float)

    mask = np.isfinite(Caps) & np.isfinite(time_s)
    Caps = Caps[mask]
    time_s = time_s[mask]

    # Conversion in pF
    Caps_pF = Caps * 1e12

    # Time unit conversion
    if time_unit == "s":
        time_x = time_s
        xlabel = "Time (s)"
    elif time_unit == "h":
        time_x = time_s / 3600.0
        xlabel = "Time (h)"
    elif time_unit == "days":
        time_x = time_s / (3600.0 * 24.0)
        xlabel = "Time (days)"
    else:
        raise ValueError("time_unit must be 's', 'h', or 'days'.")
    
    # For dataframe extraction
    time_h = time_s/3600.0
    time_d = time_s/(3600.0 * 24.0)

    # =========================
    # Paper style (same as your other function)
    # =========================
    FIGSIZE = (9.0, 6.0)
    LABEL_FONTSIZE = 18
    TICK_FONTSIZE = 16
    LEGEND_FONTSIZE = 14
    TITLE_FONTSIZE = 18

    LINE_COLOR = "#000000"
    POINT_COLOR = "#285b96"   # same blue vibe as POS_COLOR
    LINEWIDTH = 0.8
    ms = float(marker_size) ** 0.5

    fig, ax = plt.subplots(figsize=FIGSIZE)

    # =========================
    # Plot
    # =========================
    ax.plot(
        time_x,
        Caps_pF,
        color=LINE_COLOR,
        alpha=0.65,
        linewidth=LINEWIDTH,
        zorder=1
    )

    ax.scatter(
        time_x,
        Caps_pF,
        marker="o",
        s=marker_size,
        color=POINT_COLOR,
        label="Retention read",
        zorder=10
    )

    # =========================
    # Labels / title
    # =========================
    ax.set_xlabel(xlabel, fontsize=LABEL_FONTSIZE)
    ax.set_ylabel(f"Capacitance near {reading_voltage} V (pF)", fontsize=LABEL_FONTSIZE)

    if title is not None:
        ax.set_title(title, fontsize=TITLE_FONTSIZE)

    # =========================
    # Paper ticks + grid
    # =========================
    ax.tick_params(
        axis="both",
        which="both",
        direction="in",
        top=True,
        right=True,
        labelsize=TICK_FONTSIZE,
        length=6,
        width=1.2
    )
    ax.tick_params(axis="both", which="minor", length=3, width=1.0)

    ax.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))
    ax.yaxis.set_minor_formatter(NullFormatter())

    ax.grid(True, which="major", linestyle="-", linewidth=0.8, alpha=0.30)
    ax.grid(True, which="minor", linestyle=":", linewidth=0.6, alpha=0.22)

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.2)

    # =========================
    # Export (optional)
    # =========================
    out_path = None
    if Output_dir is not None:
        os.makedirs(Output_dir, exist_ok=True)

        if filename is None:
            filename = f"Cmem_retention_vs_time_{time_unit}.png"

        out_path = os.path.join(Output_dir, filename)

        plt.tight_layout()
        fig.savefig(out_path, dpi=600, bbox_inches="tight")

    plt.show()

    df = pd.DataFrame({
    "time_s": time_s,
    "time_h": time_h,
    "time_d": time_d,
    "C_pF": Caps
    })

    return df


# ──────────────────────────────────────────────────────────────────────────────
#                         
# ──────────────────────────────────────────────────────────────────────────────


def plot_memCVM_retention_overview(
    DF_CVM: list,                     # list[pd.DataFrame]
    Timestamps: list[str],             # list[str] e.g. "01/19/2026 17:41:53"
    Output_dir: str,
    reading_voltage: float = 0.0,      # only for ylabel text (optional)
    time_unit: str = "h",              # "s", "h", "days"
    title: str | None = None,
    filename_suffix: str = "Retention-CVM",
    linewidth: float = 1.2,
    cmap_name: str = "viridis",
):
    """
    Paper-friendly retention CVM overview plot:
    - Plot each CVM curve (Bias vs Capacitance) for different retention times
    - Curves are colored by elapsed time (from Timestamps)
    - Paper style: full frame, ticks inward, minor ticks, major+minor grid
    - Colorbar for elapsed time
    - High-res export (600 dpi)
    """

    # =========================
    # Checks
    # =========================
    if len(DF_CVM) == 0:
        raise ValueError("DF_CVM is empty.")
    if len(DF_CVM) != len(Timestamps):
        raise ValueError("DF_CVM and Timestamps must have the same length.")

    # =========================
    # Build elapsed time
    # =========================
    time_s = compute_elapsed_time_seconds(Timestamps)
    time_s = np.asarray(time_s, dtype=float)

    if time_unit == "s":
        time_vals = time_s
        cbar_label = "Elapsed time (s)"
    elif time_unit == "h":
        time_vals = time_s / 3600.0
        cbar_label = "Elapsed time (h)"
    elif time_unit == "days":
        time_vals = time_s / (3600.0 * 24.0)
        cbar_label = "Elapsed time (days)"
    else:
        raise ValueError("time_unit must be 's', 'h', or 'days'.")

    # =========================
    # Style constants (match overview)
    # =========================
    FIGSIZE = (9, 6.0)
    LABEL_FONTSIZE = 18
    TICK_FONTSIZE = 16
    CBAR_FONTSIZE = 16

    xlabel = "Bias (V)"
    ylabel = "Capacitance (pF)"

    # =========================
    # Figure
    # =========================
    fig, ax = plt.subplots(figsize=FIGSIZE)

    # =========================
    # Colormap setup
    # =========================
    finite_mask = np.isfinite(time_vals)
    if not np.any(finite_mask):
        raise ValueError("Elapsed time array contains no finite values.")

    vmin = float(np.nanmin(time_vals[finite_mask]))
    vmax = float(np.nanmax(time_vals[finite_mask]))

    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap(cmap_name)

    # =========================
    # Plot each CVM curve (colored by time)
    # =========================
    for df, t in zip(DF_CVM, time_vals):
        if not np.isfinite(t):
            continue

        color = cmap(norm(t))

        ax.plot(
            df["Bias [V]"],
            df["C [F]"] * 1e12,
            color=color,
            linewidth=linewidth,
            alpha=0.95
        )

    # =========================
    # Colorbar
    # =========================
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])

    cbar = fig.colorbar(sm, ax=ax, pad=0.015)
    cbar.ax.tick_params(labelsize=CBAR_FONTSIZE, direction="in", length=6, width=1.2)
    cbar.set_label(cbar_label, fontsize=CBAR_FONTSIZE)

    # =========================
    # Labels / title
    # =========================
    ax.set_xlabel(xlabel, fontsize=LABEL_FONTSIZE)
    ax.set_ylabel(ylabel, fontsize=LABEL_FONTSIZE)

    if title is not None:
        ax.set_title(title, fontsize=LABEL_FONTSIZE)


    # =========================
    # Paper axis style
    # =========================
    ax.tick_params(
        axis="both", which="both",
        direction="in", top=True, right=True,
        labelsize=TICK_FONTSIZE,
        length=6, width=1.2
    )
    ax.tick_params(axis="both", which="minor", length=3, width=1.0)

    ax.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))
    ax.yaxis.set_minor_formatter(NullFormatter())


    ax.grid(True, which="major", linestyle="-", linewidth=0.8, alpha=0.30)
    ax.grid(True, which="minor", linestyle=":", linewidth=0.6, alpha=0.22)

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.2)

    # =========================
    # Export
    # =========================
    os.makedirs(Output_dir, exist_ok=True)

    plot_name = f"{filename_suffix}.png"
    out_path = os.path.join(Output_dir, plot_name)

    plt.tight_layout()
    fig.savefig(out_path, dpi=600, bbox_inches="tight")
    plt.show()

    return fig, ax, out_path
