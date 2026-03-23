import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, NullFormatter
import os
import json
# from matplotlib import colormaps
import re
import io
from datetime import datetime




def PUND_collumn_splitter(df):
    
        # T,V,I,P repeated 5 times
        num_sets = 5
        columns_per_set = 4  # Time, V, I, P
        sets = []

        for i in range(num_sets):
            start_col = i * columns_per_set
            end_col = start_col + columns_per_set
            set_df = df.iloc[:, start_col:end_col].copy()
            set_df.columns = ['Time', 'V', 'I', 'P']
            
            # --- Converti in numerico per sicurezza ---
            set_df['Time'] = pd.to_numeric(set_df['Time'], errors='coerce')
            set_df['V'] = pd.to_numeric(set_df['V'], errors='coerce')
            set_df['I'] = pd.to_numeric(set_df['I'], errors='coerce')
            set_df['P'] = pd.to_numeric(set_df['P'], errors='coerce')
            
            sets.append(set_df)              

        return sets







def plot_PVIV_DHM(
    df,
    x_col="V+ [V]",
    y1_col="P1 [uC/cm2]",
    y2_col="I1 [A]",
    color_y1="#289E46",
    color_y2="#461172",
    xlabel="Voltage (V)",
    ylabel_y1="Polarization (uC/cm²)",
    ylabel_y2="Current (µA)",
):
    # =========================
    # Style paper / doctoral plan
    # =========================
    FIGSIZE = (9, 6)
    LINEWIDTH = 3
    LABEL_FONTSIZE = 20
    TICK_FONTSIZE = 20
    LEGEND_FONTSIZE = 15
    MARKER_SIZE = 4

    fig, ax1 = plt.subplots(figsize=FIGSIZE)

    # =========================
    # Courbe axe Y1 (gauche)
    # =========================
    l1 = ax1.plot(
        df[x_col],
        df[y1_col],
        linewidth=LINEWIDTH,
        color=color_y1,
        label=y1_col,
    )

    ax1.set_xlabel(xlabel, fontsize=LABEL_FONTSIZE)
    ax1.set_ylabel(ylabel_y1, fontsize=LABEL_FONTSIZE)
    ax1.set_ylim(-30, 30)


    # =========================
    # Courbe axe Y2 (droite)
    # =========================
    ax2 = ax1.twinx()
    l2 = ax2.plot(
        df[x_col],
        df[y2_col]*1e6,  # Convert A to µA for better readability
        linewidth=LINEWIDTH,
        color=color_y2,
        label=y2_col,
    )
    ax2.set_ylabel(ylabel_y2, fontsize=LABEL_FONTSIZE)
    ax2.set_ylim(-500, 500)

    # =========================
    # Ticks inward + minor + top/right
    # =========================
    # ax1 : gauche + haut (PAS droite)
    ax1.tick_params(
        axis="both", which="both",
        direction="in", top=True, right=False,
        labelsize=TICK_FONTSIZE, length=6, width=1.2
    )
    ax1.tick_params(axis="both", which="minor", length=3, width=1.0)

    # ax2 : droite + haut (PAS gauche)
    ax2.tick_params(
        axis="both", which="both",
        direction="in", top=True, right=True, left=False,
        labelsize=TICK_FONTSIZE, length=6, width=1.2
    )
    ax2.tick_params(axis="both", which="minor", length=3, width=1.0)


    # Minor ticks (X + Y)
    ax1.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax1.yaxis.set_minor_locator(AutoMinorLocator(5))
    ax2.yaxis.set_minor_locator(AutoMinorLocator(5))

    ax1.tick_params(axis="y", colors=color_y1)
    ax1.yaxis.label.set_color(color_y1)

    ax2.tick_params(axis="y", colors=color_y2)
    ax2.yaxis.label.set_color(color_y2)


    # (Optionnel) si tu veux pas voir les labels des minor ticks sur Y
    ax1.yaxis.set_minor_formatter(NullFormatter())
    ax2.yaxis.set_minor_formatter(NullFormatter())
    

    # =========================
    # Grid (major + minor) -> seulement sur ax1 pour éviter le bazar
    # =========================
    ax1.grid(True, which="major", linestyle="-", linewidth=0.8, alpha=0.35)
    ax1.grid(True, which="minor", linestyle=":", linewidth=0.6, alpha=0.25)

    # =========================
    # Spines (cadre complet)
    # =========================
    for spine in ax1.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.2)
    # Sur ax2, on touche surtout la spine droite
    ax2.spines["right"].set_linewidth(1.2)
    ax2.spines["top"].set_linewidth(1.2)

    # =========================
    # Légende commune (ax1 + ax2)
    # =========================

    plt.tight_layout()
    plt.show()







def PUND_collumn_splitter(df):
    
        # T,V,I,P repeated 5 times
        num_sets = 5
        columns_per_set = 4  # Time, V, I, P
        sets = []

        for i in range(num_sets):
            start_col = i * columns_per_set
            end_col = start_col + columns_per_set
            set_df = df.iloc[:, start_col:end_col].copy()
            set_df.columns = ['Time', 'V', 'I', 'P']
            
            # --- Converti in numerico per sicurezza ---
            set_df['Time'] = pd.to_numeric(set_df['Time'], errors='coerce')
            set_df['V'] = pd.to_numeric(set_df['V'], errors='coerce')
            set_df['I'] = pd.to_numeric(set_df['I'], errors='coerce')
            set_df['P'] = pd.to_numeric(set_df['P'], errors='coerce')
            
            sets.append(set_df)              

        return sets





import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, NullFormatter


def plot_PVIV_PUND(
    df,
    x_col="V+ [V]",
    y1_col="P1 [uC/cm2]",
    y2_col="I1 [A]",
    color_y1="#289E46",
    color_y2="#461172",
    xlabel="Voltage [V]",
    ylabel_y1="Polarization [µC/cm²]",
    ylabel_y2="Current [µA]",
):
    # =========================
    # Style paper / doctoral plan
    # =========================
    FIGSIZE = (8, 6)
    LINEWIDTH = 3
    LABEL_FONTSIZE = 20
    TICK_FONTSIZE = 20

    fig, ax1 = plt.subplots(figsize=FIGSIZE)

    df0 = df
    df_work = df0 if (df0.shape[1] % 4 == 0) else df0.iloc[:, 1:]
    df_list = PUND_collumn_splitter(df_work)

    # ==========================================================
    # AXIS 1 — Polarization
    # ==========================================================
    for w in df_list:
        ax1.plot(w['V'], w['P'], color=color_y1, linewidth=LINEWIDTH)

    ax1.set_xlabel(xlabel, fontsize=LABEL_FONTSIZE)
    ax1.set_ylabel(ylabel_y1, fontsize=LABEL_FONTSIZE, color=color_y1)
    ax1.set_ylim(-35, 35)

    # ==========================================================
    # AXIS 2 — Current
    # ==========================================================
    ax2 = ax1.twinx()

    for w in df_list:
        ax2.plot(w['V'], w['I'] * 1e6, color=color_y2, linewidth=LINEWIDTH)

    ax2.set_ylabel(ylabel_y2, fontsize=LABEL_FONTSIZE, color=color_y2)

    # ==========================================================
    # Make left axis visually on top (important for twin axis)
    # ==========================================================
    ax1.set_zorder(2)
    ax2.set_zorder(1)
    ax1.patch.set_visible(False)

    # ==========================================================
    # Ticks inward + minor
    # ==========================================================
    ax1.tick_params(
        axis="both", which="both",
        direction="in", top=True, right=False,
        labelsize=TICK_FONTSIZE, length=6, width=1.2,
        colors=color_y1
    )

    ax2.tick_params(
        axis="both", which="both",
        direction="in", top=True, right=True, left=False,
        labelsize=TICK_FONTSIZE, length=6, width=1.2,
        colors=color_y2
    )

    ax1.tick_params(axis="both", which="minor", length=3, width=1.0)
    ax2.tick_params(axis="both", which="minor", length=3, width=1.0)

    ax1.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax1.yaxis.set_minor_locator(AutoMinorLocator(5))
    ax2.yaxis.set_minor_locator(AutoMinorLocator(5))

    ax1.yaxis.set_minor_formatter(NullFormatter())
    ax2.yaxis.set_minor_formatter(NullFormatter())

    # ==========================================================
    # Grid (only ax1 to avoid chaos)
    # ==========================================================
    ax1.grid(True, which="major", linestyle="-", linewidth=0.8, alpha=0.35)
    ax1.grid(True, which="minor", linestyle=":", linewidth=0.6, alpha=0.25)

    # ==========================================================
    # Spines (full frame Laura style)
    # ==========================================================
    for spine in ax1.spines.values():
        spine.set_linewidth(1.2)

    ax2.spines["right"].set_linewidth(1.2)
    ax2.spines["top"].set_linewidth(1.2)

    plt.tight_layout()
    plt.show()

    return fig, ax1, ax2







def plot_PVIV_PUND_triptych(
    dfs,
    titles=None,
    panel_labels=None,
    color_y1="#289E46",
    color_y2="#461172",
    xlabel="Voltage (V)",
    ylabel_y1="Polarization (µC/cm²)",
    ylabel_y2="Current (µA)",
    Label_size : int = 20,
    Tick_size: int = 18,
    y1_lim=(-35, 35),
    y2_lim=(-16, 12.5),
):
    LINEWIDTH = 3
    LABEL_FONTSIZE = Label_size
    TICK_FONTSIZE = Tick_size
    TITLE_FONTSIZE = 18

    if not isinstance(dfs, (list, tuple)) or len(dfs) < 1:
        raise ValueError("dfs must be a non-empty list/tuple of dataframes.")

    n = len(dfs)

    # Auto figsize: 4.5 inches per panel
    FIGSIZE = (18, 6)

    if titles is None:
        titles = [""] * n
    if len(titles) != n:
        raise ValueError(f"titles must have length {n} (or be None).")

    if panel_labels is None:
        panel_labels = [""] * n
    if len(panel_labels) != n:
        raise ValueError(f"panel_labels must have length {n} (or be None).")

    fig, axes = plt.subplots(
        nrows=1,
        ncols=n,
        figsize=FIGSIZE,
        sharex=True,
        sharey=True,
        gridspec_kw={"wspace": 0.0}
    )

    # Si n==1, matplotlib renvoie un seul Axes, pas une liste
    if n == 1:
        axes = [axes]

    ax2_list = []

    for i, (ax1, df, title) in enumerate(zip(axes, dfs, titles)):
        df0 = df
        df_work = df0 if (df0.shape[1] % 4 == 0) else df0.iloc[:, 1:]
        df_list = PUND_collumn_splitter(df_work)

        # Y1 (P)
        for w in df_list:
            ax1.plot(w["V"], w["P"], color=color_y1, linewidth=LINEWIDTH)
        ax1.set_ylim(*y1_lim)

        # Y2 (I)
        ax2 = ax1.twinx()
        for w in df_list:
            ax2.plot(w["V"], w["I"] * 1e6, color=color_y2, linewidth=LINEWIDTH)
        ax2.set_ylim(*y2_lim)
        ax2_list.append(ax2)

        # Ticks style
        ax1.tick_params(axis="both", which="both", direction="in", top=True, right=False,
                        labelsize=TICK_FONTSIZE, length=6, width=1.2)
        ax1.tick_params(axis="both", which="minor", length=3, width=1.0)

        ax2.tick_params(axis="both", which="both", direction="in", top=True, right=True, left=False,
                        labelsize=TICK_FONTSIZE, length=6, width=1.2)
        ax2.tick_params(axis="both", which="minor", length=3, width=1.0)

        # Minor ticks
        ax1.xaxis.set_minor_locator(AutoMinorLocator(5))
        ax1.yaxis.set_minor_locator(AutoMinorLocator(5))
        ax2.yaxis.set_minor_locator(AutoMinorLocator(5))
        ax1.yaxis.set_minor_formatter(NullFormatter())
        ax2.yaxis.set_minor_formatter(NullFormatter())

        ax1.tick_params(axis="y", colors=color_y1)
        ax2.tick_params(axis="y", colors=color_y2)

        # Grid only on ax1
        ax1.grid(True, which="major", linestyle="-", linewidth=0.8, alpha=0.35)
        ax1.grid(True, which="minor", linestyle=":", linewidth=0.6, alpha=0.25)

        # Spines
        for spine in ax1.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(1.2)
        ax2.spines["right"].set_linewidth(1.2)
        ax2.spines["top"].set_linewidth(1.2)

        # Title
        if title:
            ax1.set_title(title, fontsize=TITLE_FONTSIZE, pad=10)

        # Only left labels on first, only right labels on last
        if i == 0:
            ax1.tick_params(axis="y", labelleft=True)
            ax2.tick_params(axis="y", labelright=False)
        elif i == n - 1:
            ax1.tick_params(axis="y", labelleft=False)
            ax2.tick_params(axis="y", labelright=True)
        else:
            ax1.tick_params(axis="y", labelleft=False)
            ax2.tick_params(axis="y", labelright=False)

        # Panel label
        if panel_labels[i]:
            ax1.text(
                0.02, 0.97,
                panel_labels[i],
                transform=ax1.transAxes,
                fontsize=18,
                fontweight="bold",
                va="top",
                ha="left",
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.75, pad=2)
            )

    # Global labels
    fig.supxlabel(xlabel, fontsize=LABEL_FONTSIZE)
    axes[0].set_ylabel(ylabel_y1, fontsize=LABEL_FONTSIZE, color=color_y1)
    ax2_list[-1].set_ylabel(ylabel_y2, fontsize=LABEL_FONTSIZE, color=color_y2)

    plt.subplots_adjust(wspace=0.0)
    plt.tight_layout()
    plt.show()

    return fig, axes, ax2_list
