import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List


from src.metadata_utils import get_capacitance_near_zero_bias

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



def plot_memCVM_Vwrite(
    Read_CVM_Dataframe: list[pd.DataFrame],
    title: str | None = "Memory Capacitance vs Writing Voltage",
    marker_size: int = 80
):

    # --- Récupération des valeurs ---
    Vwrites = []
    Caps = []

    for df in Read_CVM_Dataframe:
        Vw = float(df["Writing_Voltage_V"].iloc[0])
        Cv = float(get_capacitance_near_zero_bias(df))

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

    if title:
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





def plot_memCVM_vs_pulse_number(
    Read_CVM_Dataframe: List[pd.DataFrame],
    Vwrite_list: list[float],
    title: str | None = "Memory Capacitance vs Pulse Number",
    marker_size: int = 80,
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
        Cmem = float(get_capacitance_near_zero_bias(df))

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

    if title:
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

            
