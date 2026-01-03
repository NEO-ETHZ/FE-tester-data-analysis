import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
import matplotlib.cm as cm

from src.metadata_utils import get_capacitance_near_target_bias, mobile_average, seq_file_parsing

def plot_memCVM_overview(
    Main_CVM_Dataframe: pd.DataFrame,
    Read_CVM_Dataframes: list[pd.DataFrame],
    Vwrite_list: list[float],
    title: str | None = None,
):



    fig, ax = plt.subplots(figsize=(9, 6))

    # === Courbe principale ===
    ax.plot(
        Main_CVM_Dataframe["Bias [V]"],
        Main_CVM_Dataframe["C [F]"],
        label="Main CVM",
        linewidth=2.5,
        color=(0.95,0.25,0.35)
    )

    # === Séparation POSITIFS / NÉGATIFS ===
    pos_pairs = [(df, v) for df, v in zip(Read_CVM_Dataframes, Vwrite_list) if v > 0]
    neg_pairs = [(df, v) for df, v in zip(Read_CVM_Dataframes, Vwrite_list) if v < 0]

    # Couleurs fixes
    POS_COLOR = "#0072B2"   # bleu
    NEG_COLOR = "#D55E00"   # orange

    # === PLOT POSITIFS ===
    if len(pos_pairs) > 0:
        n_pos = len(pos_pairs)
        # alpha va de 0.25 à 1.0
        alphas_pos = np.linspace(0.25, 1.0, n_pos)

        for (df, v), alpha in zip(pos_pairs, alphas_pos):
            ax.plot(
                df["Bias [V]"],
                df["C [F]"],
                color=POS_COLOR,
                alpha=alpha,
                linestyle="--",
                linewidth=1.8,
                label=f"memCVM | {v:.3g}"
            )

    # === PLOT NÉGATIFS ===
    if len(neg_pairs) > 0:
        n_neg = len(neg_pairs)
        alphas_neg = np.linspace(0.25, 1.0, n_neg)

        for (df, v), alpha in zip(neg_pairs, alphas_neg):
            ax.plot(
                df["Bias [V]"],
                df["C [F]"],
                color=NEG_COLOR,
                alpha=alpha,
                linestyle="--",
                linewidth=1.8,
                label=f"memCVM | {v:.3g}"
            )

    # === Axes & style ===
    ax.set_xlabel("Bias [V]", fontsize=12)
    ax.set_ylabel("Capacitance [F]", fontsize=12)

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold")

    ax.grid(True, linestyle=":", linewidth=0.7, alpha=0.5)
    ax.tick_params(labelsize=11)

    # === Légende à droite ===
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.78, box.height])

    ax.legend(
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        fontsize=10,
        frameon=True,
        title="Curves",
        title_fontsize=11
    )

    plt.tight_layout()
    plt.show()
    plt.close(fig)



#----------------------------------------------------------------------
#----------------------------------------------------------------------


def plot_memCVM_Vwrite(
    Read_CVM_Dataframe: list[pd.DataFrame],
    marker_size: int = 80,
    reading_voltage: float = 0,
):

    # --- Récupération des valeurs ---
    Vwrites = []
    Caps = []

    for df in Read_CVM_Dataframe:
        Vw = float(df["Writing_Voltage_V"].iloc[0])
        Cv = float(get_capacitance_near_target_bias(df,target=reading_voltage))

        Vwrites.append(Vw)
        Caps.append(Cv)

    # --- Conversion en numpy ---
    Vwrites = np.array(Vwrites)
    Caps = np.array(Caps)

    # --- Séparation des points ---
    pos_mask = Vwrites > 0
    neg_mask = Vwrites < 0
    zero_mask = Vwrites == 0   # on sait jamais

    # Couleurs
    POS_COLOR = "#0072B2"  # Bleu
    NEG_COLOR = "#D55E00"  # Orange
    ZERO_COLOR = "gray"

    fig, ax = plt.subplots(figsize=(9, 6))

    # === Courbe des Vwrite positifs ===
    if np.any(pos_mask):
        # Tri pour que la courbe soit dans le bon ordre croissant
        idx_sorted = np.argsort(Vwrites[pos_mask])

        ax.plot(
            Vwrites[pos_mask][idx_sorted],
            Caps[pos_mask][idx_sorted],
            linestyle='-',
            marker='o',
            markersize=marker_size**0.5,
            linewidth=2.0,
            color=POS_COLOR,
            alpha=0.95,
            label="Positive Vwrite"
        )

    # === Courbe des Vwrite négatifs ===
    if np.any(neg_mask):
        # Tri des négatifs (du plus proche de 0 vers le plus extrême)
        idx_sorted = np.argsort(np.abs(Vwrites[neg_mask]))

        ax.plot(
            Vwrites[neg_mask][idx_sorted],
            Caps[neg_mask][idx_sorted],
            linestyle='-',
            marker='o',
            markersize=marker_size**0.5,
            linewidth=2.0,
            color=NEG_COLOR,
            alpha=0.95,
            label="Negative Vwrite"
        )

    # === Courbe pour Vwrite = 0 (si jamais) ===
    if np.any(zero_mask):
        ax.plot(
            Vwrites[zero_mask],
            Caps[zero_mask],
            linestyle='-',
            marker='o',
            markersize=marker_size**0.5 + 2,
            linewidth=2.0,
            color=ZERO_COLOR,
            alpha=1.0,
            label="Vwrite = 0"
        )


    # === Style des axes ===
    ax.set_xlabel("Writing Voltage [V]", fontsize=12)
    ax.set_ylabel("Memory Capacitance near 0V [F]", fontsize=12)

    title = f"Memory Capacitance vs Writing Voltage for Vr: {reading_voltage*1E+3} [mV]"
    ax.set_title(title, fontsize=14, fontweight="bold")

    ax.grid(True, linestyle=":", linewidth=0.7, alpha=0.6)
    ax.tick_params(axis="both", labelsize=11)

    # === Légende ===
    ax.legend(
        loc="best",
        frameon=True,
        fontsize=10,
        title="Groups",
        title_fontsize=11
    )

    # === Layout propre ===
    plt.tight_layout()
    plt.show()
    plt.close(fig)


#----------------------------------------------------------------------
#----------------------------------------------------------------------


def plot_memCVM_vs_pulse_number(
    Read_CVM_Dataframe: List[pd.DataFrame],
    Vwrite_list: list[float],
    marker_size: int = 80,
    reading_voltage: float = 0,
):

    if len(Read_CVM_Dataframe) == 0:
        raise ValueError("Read_CVM_Dataframe est vide.")

    dfs_sorted = Read_CVM_Dataframe
    vwrite_sorted = Vwrite_list


    # 2) Construire les listes pulse_number, Cmem et Vwrite
    pulse_numbers = []
    Cmem_list = []
    Vwrite_list = []

    for idx, (df, v) in enumerate(zip(dfs_sorted, vwrite_sorted), start=1):
        Cmem = float(get_capacitance_near_target_bias(df, reading_voltage))

        pulse_numbers.append(idx)
        Cmem_list.append(Cmem)
        Vwrite_list.append(v)

    pulse_numbers = np.array(pulse_numbers)
    Cmem_list = np.array(Cmem_list)
    Vwrite_list = np.array(Vwrite_list)

    # 3) Séparer positifs / négatifs pour la couleur
    pos_mask = Vwrite_list > 0
    neg_mask = Vwrite_list < 0

    POS_COLOR = "#0072B2"   # bleu
    NEG_COLOR = "#D55E00"   # orange

    fig, ax = plt.subplots(figsize=(9, 6))

    # === Positifs ===
    if np.any(pos_mask):
        ax.plot(
            pulse_numbers[pos_mask],
            Cmem_list[pos_mask],
            marker="o",
            linestyle="-",
            linewidth=1.8,
            markersize=marker_size ** 0.5,
            color=POS_COLOR,
            label="Positive Vwrite",
        )

    # === Négatifs ===
    if np.any(neg_mask):
        ax.plot(
            pulse_numbers[neg_mask],
            Cmem_list[neg_mask],
            marker="o",
            linestyle="-",
            linewidth=1.8,
            markersize=marker_size ** 0.5,
            color=NEG_COLOR,
            label="Negative Vwrite",
        )

    # 4) Axes, style, titres
    ax.set_xlabel("Pulse number (sequence index)", fontsize=12)
    ax.set_ylabel("Memory capacitance near 0 V [F]", fontsize=12)

    title = f"Memory Capacitance vs Pulse Number at Vr: {reading_voltage*1E+3} [mV]"
    ax.set_title(title, fontsize=14, fontweight="bold")

    ax.grid(True, linestyle=":", linewidth=0.7, alpha=0.6)
    ax.tick_params(axis="both", labelsize=11)

    ax.legend(
        loc="best",
        frameon=True,
        fontsize=10,
        title="Pulse group",
        title_fontsize=11,
    )

    plt.tight_layout()
    plt.show()
    plt.close(fig)

            
#----------------------------------------------------------------------
#----------------------------------------------------------------------


def Dashboard_memCVM(    
    Main_CVM_Dataframe: pd.DataFrame,
    Read_CVM_Dataframe: List[pd.DataFrame],
    Vwrite_list: list[float],
    reading_voltage: float,
    path_metadata: str = "",
    ):

    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(3, 2, height_ratios=[1.4, 1.0, 1.0], hspace=0.35, wspace=0.25)

    df_temp = Main_CVM_Dataframe

    # =========================
    # Row 1 — full width
    # =========================

    top_font_size = 14
    color_main_plot = "#D11644"
    top_xlabel = "Bias [V]"
    top_ylabel = "Capacitance [F]"

    df_mobile_average = mobile_average(3, df_temp["C [F]"])

    Top_plot = fig.add_subplot(gs[0, :])
    Top_plot.plot(df_temp["Bias [V]"], df_mobile_average, label="Main CVM", linewidth=2.5, color=color_main_plot)

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
            linewidth=1.8,
            linestyle="--"
        )

    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])

    cbar = plt.colorbar(sm, ax=Top_plot, pad=0.02)
    cbar.set_label("Writing voltage Vwrite (V)", fontsize=12)

    # === Axes & style ===
    Top_plot.grid(True, linestyle=":", linewidth=0.7, alpha=0.5)
    Top_plot.tick_params(labelsize=11)

    Top_plot.set_xlabel(top_xlabel, fontsize=top_font_size)
    Top_plot.set_ylabel(top_ylabel, fontsize=top_font_size)
    Top_plot.tick_params(axis="both", labelsize=top_font_size)
    Top_plot.grid(True)
    Top_plot.legend()


    # =========================
    # Rows 2–3 — left (merged)
    # =========================

    left_font_size = 14
    left_xlabel = "Writting Voltage [V]"
    left_ylabel = "Capacitance near 0 V [F]"
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

    Left_plot.plot(Vwrites, Caps, marker='o', markersize=8, linestyle='-',label = "Mem-CVM", linewidth=2.0, color=color_left_plot, alpha=0.95)
    Left_plot.grid(True, linestyle=":", linewidth=0.7, alpha=0.5)
    Left_plot.tick_params(labelsize=11)

    Left_plot.set_xlabel(left_xlabel, fontsize=left_font_size)
    Left_plot.set_ylabel(left_ylabel, fontsize=left_font_size)
    Left_plot.tick_params(axis="both", labelsize=top_font_size)
    Left_plot.grid(True)
    Left_plot.legend()


    # =========================
    # Row 2 — right
    # =========================

    Right_01_plot_xlabel = "Pulse number (sequence index)"
    Right_01_plot_ylabel = "Capacitance near 0 V [F]"
    Right_01_plot_fontsize = 14
    Right_01_plot_poscolor = "#0072B2"
    Right_01_plot_negcolor = "#D55E00"
    Right_01_plot_Markersize = 4

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

    pulse_numbers = np.array(pulse_numbers)
    Cmem_list = np.array(Cmem_list)
    Vwrite_list = np.array(Vwrite_list)

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
            linewidth=1.8,
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
            linewidth=1.8,
            markersize=Right_01_plot_Markersize,
            color= Right_01_plot_negcolor,
            label="Negative Vwrite",
        )

    # 4) Axes, style, titres
    Right_01_plot.set_xlabel(Right_01_plot_xlabel, fontsize=Right_01_plot_fontsize)
    Right_01_plot.set_ylabel(Right_01_plot_ylabel, fontsize=Right_01_plot_fontsize)

    Right_01_plot.grid(True, linestyle=":", linewidth=0.7, alpha=0.6)
    Right_01_plot.tick_params(axis="both", labelsize=11)

    Right_01_plot.legend(
        loc="best",
        frameon=True,
        fontsize=10,
    )


    # =========================
    # Row 3 — textbox
    # =========================
    Right_02_text = fig.add_subplot(gs[2, 1])
    Right_02_text.axis("off")
    metadata = seq_file_parsing(path_metadata)

    text = (
        f"Reading Voltage: {reading_voltage*1E+3} [mV]\n"
        f"Number of memCVM read curves: {len(Read_CVM_Dataframe)}\n"
        f"Writing Voltages range: {min(Vwrite_list):.3g} V to {max(Vwrite_list):.3g} V\n"
        f"\n"
        f"Memory Capacitance window: {((max(Cmem_list) - min(Cmem_list))*1E+12):.4g} [pF] \n"
        f"ON/OFF ratio: {(max(Cmem_list)/min(Cmem_list)):.3g}\n"
        f"Reading Voltage window: {((min(Read_CVM_Dataframe[0]["Bias [V]"]))*1E+3):.4g} --> {((max(Read_CVM_Dataframe[0]["Bias [V]"]))*1E+3):.4g} [mV]\n"
        f"Reading point: {len(Read_CVM_Dataframe[0]["Bias [V]"])}\n"
        f"Small signal frequency: {metadata["SS_Frequency_Hz"][0]} [Hz]\n"
    )

    tb_text = Right_02_text.text(
        0.02, 0.98, text,
        va="top",
        ha="left",
        family="monospace",
        fontsize=10
    )
