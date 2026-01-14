import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from matplotlib.ticker import AutoMinorLocator, NullFormatter

import os

from src.metadata_utils import get_capacitance_near_target_bias, mobile_average, seq_file_parsing



def plot_memCVM_overview_paper(
    Main_CVM_Dataframe: pd.DataFrame,
    Read_CVM_Dataframe: list[pd.DataFrame],
    path_metadata: str,
    Output_dir: str,
    reading_voltage: float,
    Vwrite_list: list[float],
    title: str | None = None,
    filename_suffix: str = "Main-CVM",
):
    """
    Paper-friendly Mem-CVM overview plot:
    - Main CVM curve (smoothed) + read curves colored by Vwrite
    - Paper style: full frame, ticks inward, minor ticks, major+minor grid
    - Colorbar for Vwrite
    - High-res export
    """

    # =========================
    # Metadata
    # =========================
    metadata = seq_file_parsing(path_metadata)
    sample_name = metadata["Name"][0]
    date_str = metadata["Date"][0]
    read_mv = reading_voltage * 1e3

    # =========================
    # Style constants
    # =========================
    FIGSIZE = (9, 6.0)          # paper-like (single panel)
    LINEWIDTH_MAIN = 2.6
    LINEWIDTH_READ = 1.2

    LABEL_FONTSIZE = 18
    TICK_FONTSIZE = 16
    CBAR_FONTSIZE = 16

    color_main_plot = "#000000"
    xlabel = "Bias (V)"
    ylabel = "Capacitance (F)"

    # =========================
    # Figure
    # =========================
    fig, ax = plt.subplots(figsize=FIGSIZE)

    # =========================
    # Main curve (smoothed)
    # =========================
    df_temp = Main_CVM_Dataframe
    df_mobile_average = mobile_average(8, df_temp["C [F]"])

    ax.plot(
        df_temp["Bias [V]"],
        df_mobile_average,
        label="Main CVM",
        linewidth=LINEWIDTH_MAIN,
        color=color_main_plot
    )

    # =========================
    # Read curves colored by Vwrite
    # =========================
    if len(Read_CVM_Dataframe) != len(Vwrite_list):
        raise ValueError("Read_CVM_Dataframe and Vwrite_list must have the same length.")

    vmin = min(Vwrite_list)
    vmax = max(Vwrite_list)

    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.coolwarm

    for df_read, vwrite in zip(Read_CVM_Dataframe, Vwrite_list):
        color = cmap(norm(vwrite))

        ax.plot(
            df_read["Bias [V]"],
            df_read["C [F]"],
            color=color,
            linewidth=LINEWIDTH_READ,
            linestyle="--",
            alpha=0.95
        )

    # Colorbar
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])

    cbar = fig.colorbar(sm, ax=ax, pad=0.015)
    cbar.ax.tick_params(labelsize=CBAR_FONTSIZE, direction="in", length=6, width=1.2)
    cbar.set_label("Writing voltage $V_{write}$ (V)", fontsize=CBAR_FONTSIZE)

    # =========================
    # Paper axis style
    # =========================
    ax.set_xlabel(xlabel, fontsize=LABEL_FONTSIZE)
    ax.set_ylabel(ylabel, fontsize=LABEL_FONTSIZE)

    # --- Zoom sur la zone lecture ---
    ax.set_xlim(0, 0.45)   # <-- à adapter à ta fenêtre de lecture réelle
    ax.set_ylim(2.38e-10, 2.9e-10)  # <-- optionnel, mais rend la lecture ultra lisible


    # ticks inward + top/right
    ax.tick_params(
        axis="both", which="both",
        direction="in", top=True, right=True,
        labelsize=TICK_FONTSIZE,
        length=6, width=1.2
    )
    ax.tick_params(axis="both", which="minor", length=3, width=1.0)

    # minor ticks
    ax.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))
    ax.yaxis.set_minor_formatter(NullFormatter())

    # grid major+minor
    ax.grid(True, which="major", linestyle="-", linewidth=0.8, alpha=0.30)
    ax.grid(True, which="minor", linestyle=":", linewidth=0.6, alpha=0.22)

    # full frame spines
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.2)

    # Legend (boxed, clean)
    leg = ax.legend(loc="best", fontsize=14, frameon=True)
    leg.get_frame().set_linewidth(1.0)
    leg.get_frame().set_alpha(1.0)

    # =========================
    # Export
    # =========================
    os.makedirs(Output_dir, exist_ok=True)

    plot_name = f"{date_str}_{sample_name}_{filename_suffix}.png"
    out_path = os.path.join(Output_dir, plot_name)

    plt.tight_layout()
    fig.savefig(out_path, dpi=600, bbox_inches="tight")
    plt.show()

    return fig, ax, out_path




#----------------------------------------------------------------------
#----------------------------------------------------------------------


def plot_memCVM_Vwrite_paper(
    Read_CVM_Dataframe: list[pd.DataFrame],
    path_metadata: str = "",
    Output_dir: str = "",
    marker_size: int = 40,
    reading_voltage: float = 0.0,
    title: str | None = None,
):
    """
    Paper-friendly plot:
    Memory capacitance (near reading_voltage) vs writing voltage.
    Style matches the other 'paper' functions: full frame, ticks inward, minor ticks,
    major+minor grid, boxed legend, high-res export.
    """

    metadata = seq_file_parsing(path_metadata)
    sample_name = metadata["Name"][0]
    date_str = metadata["Date"][0]

    # =========================
    # Gather values
    # =========================
    Vwrites = []
    Caps = []

    for df in Read_CVM_Dataframe:
        Vw = float(df["Writing_Voltage_V"].iloc[0])
        Cv = float(get_capacitance_near_target_bias(df, target=reading_voltage))
        Vwrites.append(Vw)
        Caps.append(Cv)

    Vwrites = np.asarray(Vwrites, dtype=float)
    Caps = np.asarray(Caps, dtype=float)

    # avoid NaNs/infs
    mask = np.isfinite(Caps) & np.isfinite(Vwrites)
    Vwrites = Vwrites[mask]
    Caps = Caps[mask]

    # =========================
    # Split positive / negative / zero
    # =========================
    pos_mask = Vwrites > 0
    neg_mask = Vwrites < 0
    zero_mask = Vwrites == 0

    POS_COLOR = "#285b96"
    NEG_COLOR = "#8b1010"
    ZERO_COLOR = "0.35"

    # =========================
    # Paper style constants
    # =========================
    FIGSIZE = (9.0, 6.0)
    LINEWIDTH = 5
    LABEL_FONTSIZE = 18
    TICK_FONTSIZE = 16
    LEGEND_FONTSIZE = 14
    TITLE_FONTSIZE = 18

    # markersize in points
    ms = float(marker_size) ** 0.5  # keep your behavior

    fig, ax = plt.subplots(figsize=FIGSIZE)

    # =========================
    # Plot curves
    # =========================
    if np.any(pos_mask):
        idx_sorted = np.argsort(Vwrites[pos_mask])
        ax.plot(
            Vwrites[pos_mask][idx_sorted],
            Caps[pos_mask][idx_sorted]*1e+12,
            linestyle="-",
            marker = 'o',
            markersize=ms,
            linewidth=LINEWIDTH,
            color=POS_COLOR,
            alpha=0.95,
            label="Positive $V_{write}$"
        )

    if np.any(neg_mask):
        # Sort negatives from near 0 to more negative (looks nicer)
        idx_sorted = np.argsort(np.abs(Vwrites[neg_mask]))
        ax.plot(
            Vwrites[neg_mask][idx_sorted],
            Caps[neg_mask][idx_sorted]*1e+12,
            linestyle="-",
            marker = 'o',
            markersize=ms,
            linewidth=LINEWIDTH,
            color=NEG_COLOR,
            alpha=0.95,
            label="Negative $V_{write}$"
        )

    if np.any(zero_mask):
        ax.plot(
            Vwrites[zero_mask],
            Caps[zero_mask],
            linestyle="-",
            markersize=ms + 1.5,
            linewidth=LINEWIDTH,
            color=ZERO_COLOR,
            alpha=1.0,
            label="$V_{write}=0$"
        )

    # =========================
    # Labels / title
    # =========================
    ax.set_xlabel("Writing voltage (V)", fontsize=LABEL_FONTSIZE)
    ax.set_ylabel(
        f"Memory capacitance V (pF)",
        fontsize=LABEL_FONTSIZE
    )

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
    # Legend (boxed, clean)
    # =========================
    leg = ax.legend(loc="best", fontsize=LEGEND_FONTSIZE, frameon=True)
    leg.get_frame().set_linewidth(1.0)
    leg.get_frame().set_alpha(1.0)

    # =========================
    # Export
    # =========================
    os.makedirs(Output_dir, exist_ok=True)
    plot_name = f"{date_str}_{sample_name}_Cmem_vs_Vwrite.png"
    out_path = os.path.join(Output_dir, plot_name)

    plt.tight_layout()
    fig.savefig(out_path, dpi=600, bbox_inches="tight")
    plt.show()

    return fig, ax, out_path


#----------------------------------------------------------------------
#----------------------------------------------------------------------



def plot_memCVM_vs_pulse_number_paper(
    Read_CVM_Dataframe: list[pd.DataFrame],
    path_metadata: str,
    Output_dir: str,
    Vwrite_list: list[float],
    marker_size: int = 40,
    reading_voltage: float = 0.0,
    title: str | None = None,
):
    """
    Paper-friendly plot:
    Memory capacitance (near reading_voltage) vs pulse number,
    colored by sign of Vwrite (pos/neg).
    """

    metadata = seq_file_parsing(path_metadata)
    sample_name = metadata["Name"][0]
    date_str = metadata["Date"][0]

    if len(Read_CVM_Dataframe) == 0:
        raise ValueError("Read_CVM_Dataframe is empty.")
    if len(Read_CVM_Dataframe) != len(Vwrite_list):
        raise ValueError("Read_CVM_Dataframe and Vwrite_list must have the same length.")

    # =========================
    # Build arrays
    # =========================
    pulse_numbers = []
    Cmem_list = []
    Vw_list = []

    for idx, (df, v) in enumerate(zip(Read_CVM_Dataframe, Vwrite_list), start=1):
        Cmem = float(get_capacitance_near_target_bias(df, target=reading_voltage))
        pulse_numbers.append(idx)
        Cmem_list.append(Cmem)
        Vw_list.append(float(v))

    pulse_numbers = np.asarray(pulse_numbers, dtype=float)
    Cmem_list = np.asarray(Cmem_list, dtype=float)
    Vw_list = np.asarray(Vw_list, dtype=float)

    mask = np.isfinite(Cmem_list) & np.isfinite(Vw_list) & np.isfinite(pulse_numbers)
    pulse_numbers = pulse_numbers[mask]
    Cmem_list = Cmem_list[mask]
    Vw_list = Vw_list[mask]

    # Split by sign
    pos_mask = Vw_list > 0
    neg_mask = Vw_list < 0
    zero_mask = Vw_list == 0

    # =========================
    # Paper style
    # =========================
    FIGSIZE = (9.0, 6.0)
    LINEWIDTH = 5
    LABEL_FONTSIZE = 18
    TICK_FONTSIZE = 16
    LEGEND_FONTSIZE = 14
    TITLE_FONTSIZE = 18

    ms = float(marker_size) ** 0.5

    POS_COLOR = "#285b96"
    NEG_COLOR = "#8b1010"
    ZERO_COLOR = "0.35"

    fig, ax = plt.subplots(figsize=FIGSIZE)

    # =========================
    # Plot
    # =========================
    if np.any(pos_mask):
        ax.plot(
            pulse_numbers[pos_mask],
            Cmem_list[pos_mask]*1e+12,
            marker="o",
            linestyle="-",
            linewidth=LINEWIDTH,
            markersize=ms,
            color=POS_COLOR,
            alpha=0.95,
            label="Positive $V_{write}$",
        )

    if np.any(neg_mask):
        ax.plot(
            pulse_numbers[neg_mask],
            Cmem_list[neg_mask]*1e+12,
            marker="o",
            linestyle="-",
            linewidth=LINEWIDTH,
            markersize=ms,
            color=NEG_COLOR,
            alpha=0.95,
            label="Negative $V_{write}$",
        )

    if np.any(zero_mask):
        ax.plot(
            pulse_numbers[zero_mask],
            Cmem_list[zero_mask],
            marker="o",
            linestyle="-",
            linewidth=LINEWIDTH,
            markersize=ms + 1.5,
            color=ZERO_COLOR,
            alpha=1.0,
            label="$V_{write}=0$",
        )

    # =========================
    # Labels / title
    # =========================
    ax.set_xlabel("Pulse number (sequence index)", fontsize=LABEL_FONTSIZE)
    ax.set_ylabel(
        f"Memory capacitance V (pF)",
        fontsize=LABEL_FONTSIZE
    )

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
    # Export
    # =========================
    os.makedirs(Output_dir, exist_ok=True)
    plot_name = f"{date_str}_{sample_name}_Cmem_vs_pulse.png"
    out_path = os.path.join(Output_dir, plot_name)

    plt.tight_layout()
    fig.savefig(out_path, dpi=600, bbox_inches="tight")
    plt.show()

    return fig, ax, out_path



#----------------------------------------------------------------------
#----------------------------------------------------------------------




def Dashboard_memCVM(    
    Main_CVM_Dataframe: pd.DataFrame,
    Read_CVM_Dataframe: List[pd.DataFrame],
    Vwrite_list: list[float],
    reading_voltage: float,
    path_metadata: str = "",
    Output_path: str = "",
    ):

    #Gathering the metadata from the .seq file
    metadata = seq_file_parsing(path_metadata)

    fig = plt.figure(figsize=(15, 11))
    gs = gridspec.GridSpec(3, 2, height_ratios=[1.4, 1.0, 1.0], hspace=0.35, wspace=0.25)

    sample_name = metadata["Name"][0]
    read_mv = reading_voltage * 1e3

    fig.suptitle(
        f"Mem-CVM Dashboard — {sample_name}",
        fontsize=18,
        fontweight="semibold",
        y=0.955,
    )
    fig.subplots_adjust(top=0.925)


    df_temp = Main_CVM_Dataframe

    # =========================
    # Row 1 — full width
    # =========================

    top_font_size = 16
    color_main_plot = "#D11644"
    top_xlabel = "Bias [V]"
    top_ylabel = "Capacitance [F]"

    df_mobile_average = mobile_average(3, df_temp["C [F]"])

    Top_plot = fig.add_subplot(gs[0, :])
    Top_plot.plot(df_temp["Bias [V]"], df_mobile_average, label="Main CVM", linewidth=1.5, color=color_main_plot)

    # === Plotting and colorbar legend ===
    vmin = min(Vwrite_list)
    vmax = max(Vwrite_list)

    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.coolwarm   # très bien pour -V / +V

    for df, v in zip(Read_CVM_Dataframe, Vwrite_list):
        color = cmap(norm(v))

        Top_plot.plot(
            df["Bias [V]"],
            df["C [F]"],
            color=color,
            linewidth=1,
            linestyle="--"
        )

    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])

    cbar = plt.colorbar(sm, ax=Top_plot, pad=0.02)
    cbar.ax.tick_params(labelsize=top_font_size)  # ajuste 14 à la taille souhaitée
    cbar.set_label("Writing voltage Vwrite (V)", fontsize=top_font_size)

    # === Axes & style ===
    Top_plot.grid(True, linestyle=":", linewidth=0.5, alpha=0.35)
    Top_plot.tick_params(labelsize=11)
    Top_plot.axvline(x=reading_voltage, color="#000000", linestyle="--", linewidth=1.0, alpha=0.25, label = f"Vr: {reading_voltage}V") # vertical line at reading voltage

    Top_plot.set_xlabel(top_xlabel, fontsize=top_font_size)
    Top_plot.set_ylabel(top_ylabel, fontsize=top_font_size)
    Top_plot.tick_params(axis="both", labelsize=top_font_size)
    Top_plot.spines["top"].set_visible(False)   #Remove the top border of the plot
    Top_plot.spines["right"].set_visible(False)
    Top_plot.legend(
        loc="upper right",
        frameon=False,
        fontsize=11
    )


    # =========================
    # Rows 2–3 — left (merged)
    # =========================

    left_font_size = 16
    left_xlabel = "Writting Voltage [V]"
    left_ylabel = f"Capacitance near {reading_voltage} V [F]"
    color_left_plot = "#D11644"

    Left_plot = fig.add_subplot(gs[1:, 0])
  

    # --- Récupération des valeurs ---
    Vwrites = []
    Caps = []

    for df in Read_CVM_Dataframe:
        Vw = float(df["Writing_Voltage_V"].iloc[0])
        Cv = float(get_capacitance_near_target_bias(df, target=reading_voltage))

        Vwrites.append(Vw)
        Caps.append(Cv)
    
    Vwrites = np.array(Vwrites)
    Caps = np.array(Caps)

    mask = np.isfinite(Caps) # to avoid plotting NaN values coming through get_capacitance_near_target_bias

    Left_plot.plot(Vwrites[mask], Caps[mask], marker='o', markersize=3, linestyle='-',label = "Mem-CVM", linewidth=1.5, color=color_left_plot, alpha=0.95)
    Left_plot.grid(True, linestyle=":", linewidth=0.5, alpha=0.35)
    Left_plot.tick_params(labelsize=11)

    Left_plot.set_xlabel(left_xlabel, fontsize=left_font_size)
    Left_plot.set_ylabel(left_ylabel, fontsize=left_font_size)
    Left_plot.tick_params(axis="both", labelsize=left_font_size)
    Left_plot.spines["top"].set_visible(False)
    Left_plot.spines["right"].set_visible(False)
    Left_plot.legend(frameon=False)


    # =========================
    # Row 2 — right
    # =========================

    Right_01_plot_xlabel = "Pulse number (sequence index)"
    Right_01_plot_ylabel = f"Capacitance near {reading_voltage} V [F]"
    Right_01_plot_fontsize = 16
    Right_01_plot_poscolor = "#0072B2"
    Right_01_plot_negcolor = "#D55E00"
    Right_01_plot_Markersize = 3

    Right_01_plot = fig.add_subplot(gs[1, 1])

    if len(Read_CVM_Dataframe) == 0:
        raise ValueError("Read_CVM_Dataframe est vide.")

    dfs_sorted = Read_CVM_Dataframe
    vwrite_sorted = Vwrite_list


    # 2) Construire les listes pulse_number, Cmem et Vwrite
    pulse_numbers = []
    Cmem_list = []
    Vwrite_list = []

    for idx, (df, v) in enumerate(zip(dfs_sorted, vwrite_sorted), start=1):
        Cmem = float(get_capacitance_near_target_bias(df,target=reading_voltage))

        pulse_numbers.append(idx)
        Cmem_list.append(Cmem)
        Vwrite_list.append(v)


    mask = np.isfinite(Cmem_list) # to avoid plotting NaN values coming through get_capacitance_near_target_bias

    pulse_numbers = np.array(pulse_numbers)
    pulse_numbers = pulse_numbers[mask]
    Cmem_list = np.array(Cmem_list)
    Cmem_list = Cmem_list[mask]
    Vwrite_list = np.array(Vwrite_list)
    Vwrite_list = Vwrite_list[mask]

    # 3) Séparer positifs / négatifs pour la couleur
    pos_mask = Vwrite_list > 0
    neg_mask = Vwrite_list < 0

    # === Positifs ===
    if np.any(pos_mask):
        Right_01_plot.plot(
            pulse_numbers[pos_mask],
            Cmem_list[pos_mask],
            marker="o",
            linestyle="-",
            linewidth=1.4,
            markersize=Right_01_plot_Markersize,
            color=Right_01_plot_poscolor,
            label="Positive Vwrite",
        )

    # === Négatifs ===
    if np.any(neg_mask):
        Right_01_plot.plot(
            pulse_numbers[neg_mask],
            Cmem_list[neg_mask],
            marker="o",
            linestyle="-",
            linewidth=1.4,
            markersize=Right_01_plot_Markersize,
            color= Right_01_plot_negcolor,
            label="Negative Vwrite",
        )

    # 4) Axes, style, titres
    Right_01_plot.set_xlabel(Right_01_plot_xlabel, fontsize=Right_01_plot_fontsize)
    Right_01_plot.set_ylabel(Right_01_plot_ylabel, fontsize=Right_01_plot_fontsize)
    Right_01_plot.spines["top"].set_visible(False)
    Right_01_plot.spines["right"].set_visible(False)
    Right_01_plot.grid(True, linestyle=":", linewidth=0.5, alpha=0.35)
    Right_01_plot.tick_params(axis="both", labelsize=Right_01_plot_fontsize)

    Right_01_plot.legend(
        loc="best",
        frameon=False,
        fontsize=10,
    )


    # =========================
    # Row 3 — textbox
    # =========================
    Right_02_text = fig.add_subplot(gs[2, 1])
    Right_02_text.axis("off")

    metadata = seq_file_parsing(path_metadata)

    # --- Raccourcis / formatage sûr ---
    mode = metadata["Mode"][0]
    rise_us = float(metadata["Rise_time_s"][0]) * 1e6
    integration = metadata["Integration"][0]
    amp_v = float(metadata["Amplitude_V"][0])
    ss_f = float(metadata["SS_Frequency_Hz"][0])
    ss_a = float(metadata["SS_Amplitude_V"][0])

    read_mv = reading_voltage * 1e3
    n_curves = len(Read_CVM_Dataframe)

    vmin = min(Vwrite_list)
    vmax = max(Vwrite_list)

    bias_vec = Read_CVM_Dataframe[0]["Bias [V]"]
    read_win_min_mv = float(bias_vec.min()) * 1e3
    read_win_max_mv = float(bias_vec.max()) * 1e3
    n_read_pts = len(bias_vec)

    mem_window_pf = (max(Cmem_list) - min(Cmem_list)) * 1e12
    on_off = max(Cmem_list) / min(Cmem_list)

    # --- Texte structuré ---
    text = (
        f"Read voltage          : {read_mv:.1f} mV\n"
        f"Read curves           : {n_curves:d}\n"
        f"Vwrite range          : {vmin:.2f} → {vmax:.2f} V\n"
        f"Pulse width (rise)    : {rise_us:.1f} µs\n"
        f"\n"
        f"Memory window         : {mem_window_pf:.2f} pF\n"
        f"ON/OFF ratio          : {on_off:.3f}\n"
        f"Read window           : {read_win_min_mv:.1f} → {read_win_max_mv:.1f} mV\n"
        f"\n"
        f"Mode                  : {mode}\n"
        f"Read points           : {n_read_pts:d}\n"
        f"Integration           : {integration}\n"
        f"Amplitude             : {amp_v:.2f} V\n"
        f"SS freq / amp         : {ss_f:.0f} Hz / {ss_a:.2f} V"
    )

    # 1) Récupérer la position exacte du plot au-dessus (en coordonnées figure)
    bbox = Right_01_plot.get_position()  # Bbox(x0, y0, x1, y1)

    # 2) Créer un axe texte avec la même largeur (même x0 et même width)
    text_height = 0.24   # ajuste si besoin (0.20–0.28 typiquement)
    gap = 0.055           # petit espace entre plot et box

    text_bottom = bbox.y0 - text_height - gap

    Right_02_text = fig.add_axes([bbox.x0, text_bottom, bbox.width, text_height])
    Right_02_text.axis("off")

    # 3) Mettre le texte dans cet axe (coordonnées axes: 0→1)
    tb_text = Right_02_text.text(
        0.02, 0.98, text,
        transform=Right_02_text.transAxes,
        va="top",
        ha="left",
        family="monospace",
        fontsize=12.5,
        linespacing=1.25,
        bbox=dict(
            boxstyle="round,pad=0.5,rounding_size=0.2",
            facecolor="white",
            edgecolor="0.75",
            linewidth=1.0,
            alpha=0.95
        )
    )

    os.makedirs(Output_path, exist_ok=True)
    plot_name = f"{metadata["Date"][0]}_{metadata["Name"][0]}_Dashboard.png"
    Output_path = os.path.join(Output_path, plot_name)
    plt.savefig(Output_path, dpi=300)
    print(f"Dashboard saved to: {Output_path}")

