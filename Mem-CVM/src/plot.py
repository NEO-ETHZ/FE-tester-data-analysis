import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import os

from src.metadata_utils import get_capacitance_near_target_bias, mobile_average, seq_file_parsing

def plot_memCVM_overview(
    Main_CVM_Dataframe: pd.DataFrame,
    Read_CVM_Dataframe: list[pd.DataFrame],
    path_metadata: str,
    Output_path: str,
    reading_voltage: float,
    Vwrite_list: list[float],
    title: str | None = None,
):
    #Gathering the metadata from the .seq file
    metadata = seq_file_parsing(path_metadata)

    fig = plt.figure(figsize=(12, 8))

    sample_name = metadata["Name"][0]
    read_mv = reading_voltage * 1e3

    fig.suptitle(
        f"Mem-CVM — {sample_name} | {read_mv:.1f} mV Read",
        fontsize=18,
        fontweight="semibold",
    )
    fig.subplots_adjust(top=0.925)

    df_temp = Main_CVM_Dataframe

    top_font_size = 14
    color_main_plot = "#D11644"
    top_xlabel = "Bias [V]"
    top_ylabel = "Capacitance [F]"

    df_mobile_average = mobile_average(5, df_temp["C [F]"])

    Top_plot = fig.add_subplot()
    Top_plot.plot(df_temp["Bias [V]"], df_mobile_average, label="Main CVM", linewidth=2.5, color=color_main_plot)
    Top_plot.legend(
        loc="upper right",
        frameon=False,
        fontsize=11
    )

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
    cbar.set_label("Writing voltage Vwrite (V)", fontsize=12)

    # === Axes & style ===
    Top_plot.grid(True, linestyle=":", linewidth=0.5, alpha=0.35)
    Top_plot.tick_params(labelsize=11)

    Top_plot.set_xlabel(top_xlabel, fontsize=top_font_size)
    Top_plot.set_ylabel(top_ylabel, fontsize=top_font_size)
    Top_plot.tick_params(axis="both", labelsize=top_font_size)
    Top_plot.spines["top"].set_visible(False)   #Remove the top border of the plot
    Top_plot.spines["right"].set_visible(False)

    os.makedirs(Output_path, exist_ok=True)
    plot_name = f"{metadata["Date"][0]}_{metadata["Name"][0]}_Main-CVM.png"
    Output_path = os.path.join(Output_path, plot_name)
    plt.savefig(Output_path, dpi=300)



#----------------------------------------------------------------------
#----------------------------------------------------------------------


def plot_memCVM_Vwrite(
    Read_CVM_Dataframe: list[pd.DataFrame],
    path_metadata: str = "",
    Output_path: str = "",
    marker_size: int = 80,
    reading_voltage: float = 0,
):
    metadata = seq_file_parsing(path_metadata)

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
    ax.set_ylabel(f"Memory Capacitance near {reading_voltage} V [F]", fontsize=12)

    title = f"Memory Capacitance vs Writing Voltage for Vr: {reading_voltage*1E+3} [mV]"
    ax.set_title(title, fontsize=14, fontweight="bold")

    ax.grid(True, linestyle=":", linewidth=0.7, alpha=0.6)
    ax.tick_params(axis="both", labelsize=11)

    # === Légende ===
    ax.legend(
        loc="best",
        frameon=False,
        fontsize=10,
        title_fontsize=11
    )

    os.makedirs(Output_path, exist_ok=True)
    plot_name = f"{metadata["Date"][0]}_{metadata["Name"][0]}_CrvsVw.png"
    Output_path = os.path.join(Output_path, plot_name)
    plt.savefig(Output_path, dpi=300)




#----------------------------------------------------------------------
#----------------------------------------------------------------------




def plot_memCVM_vs_pulse_number(
    Read_CVM_Dataframe: List[pd.DataFrame],
    path_metadata: str,
    Output_path: str,
    Vwrite_list: list[float],
    marker_size: int = 80,
    reading_voltage: float = 0,
):
    
    metadata = seq_file_parsing(path_metadata)

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
    ax.set_ylabel(f"Memory capacitance near {reading_voltage} V [F]", fontsize=12)

    title = f"Memory Capacitance vs Pulse Number at Vr: {reading_voltage*1E+3} [mV]"
    ax.set_title(title, fontsize=14, fontweight="bold")

    ax.grid(True, linestyle=":", linewidth=0.7, alpha=0.6)
    ax.tick_params(axis="both", labelsize=11)

    ax.legend(
        loc="best",
        frameon=False,
        fontsize=10,
        title_fontsize=11,
    )

    os.makedirs(Output_path, exist_ok=True)
    plot_name = f"{metadata["Date"][0]}_{metadata["Name"][0]}_CrvsPulse.png"
    Output_path = os.path.join(Output_path, plot_name)
    plt.savefig(Output_path, dpi=300)




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
        f"Mem-CVM Dashboard — {sample_name} | {read_mv:.1f} mV Read",
        fontsize=18,
        fontweight="semibold",
        y=0.955,
    )
    fig.subplots_adjust(top=0.925)


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
    Top_plot.plot(df_temp["Bias [V]"], df_mobile_average, label="Main CVM", linewidth=1.5, color=color_main_plot)
    Top_plot.legend(
        loc="upper right",
        frameon=False,
        fontsize=11
    )

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
    cbar.set_label("Writing voltage Vwrite (V)", fontsize=12)

    # === Axes & style ===
    Top_plot.grid(True, linestyle=":", linewidth=0.5, alpha=0.35)
    Top_plot.tick_params(labelsize=11)

    Top_plot.set_xlabel(top_xlabel, fontsize=top_font_size)
    Top_plot.set_ylabel(top_ylabel, fontsize=top_font_size)
    Top_plot.tick_params(axis="both", labelsize=top_font_size)
    Top_plot.spines["top"].set_visible(False)   #Remove the top border of the plot
    Top_plot.spines["right"].set_visible(False)


    # =========================
    # Rows 2–3 — left (merged)
    # =========================

    left_font_size = 14
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

    Left_plot.plot(Vwrites, Caps, marker='o', markersize=3, linestyle='-',label = "Mem-CVM", linewidth=1.5, color=color_left_plot, alpha=0.95)
    Left_plot.grid(True, linestyle=":", linewidth=0.5, alpha=0.35)
    Left_plot.tick_params(labelsize=11)

    Left_plot.set_xlabel(left_xlabel, fontsize=left_font_size)
    Left_plot.set_ylabel(left_ylabel, fontsize=left_font_size)
    Left_plot.tick_params(axis="both", labelsize=top_font_size)
    Left_plot.spines["top"].set_visible(False)
    Left_plot.spines["right"].set_visible(False)
    Left_plot.legend(frameon=False)


    # =========================
    # Row 2 — right
    # =========================

    Right_01_plot_xlabel = "Pulse number (sequence index)"
    Right_01_plot_ylabel = f"Capacitance near {reading_voltage} V [F]"
    Right_01_plot_fontsize = 14
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
    Right_01_plot.tick_params(axis="both", labelsize=11)

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

