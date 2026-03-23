import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
from matplotlib.ticker import AutoMinorLocator, NullFormatter
from matplotlib.colors import ListedColormap
from scipy.stats import norm

import matplotlib.cm as cm
import os
from typing import Dict, List, Tuple






# ──────────────────────────────────────────────────────────────────────────────
#                       Plot mean - Vwrite
# ──────────────────────────────────────────────────────────────────────────────


def plot_mean_vwrite(
    DF_MEAN: pd.DataFrame,
    metadata, 
    Output_dir: str = "",
    marker_size: int = 40,
    Label_size: int = 18,
    tick_size: int = 16,
    legend_size: int = 14,
    reading_voltage: float = 0.0
):
    

    
    Vwrites = []
    Caps = []

    for v in DF_MEAN["Vwrite"]:
        Vwrites.append(v)

    for c in DF_MEAN["Cmem"]:
        Caps.append(c)


    # To close the hysteresis maboi.
    # What are you doing so deep in my code ? 
    Vwrites.append(Vwrites[0])
    Caps.append(Caps[0])

    Vwrites = np.asarray(Vwrites, dtype = float)
    Caps = np.asanyarray(Caps, dtype = float)

    
    # Conversion in pF
    Caps = Caps*1e+12

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
    LABEL_FONTSIZE = Label_size
    TICK_FONTSIZE = tick_size
    LEGEND_FONTSIZE = legend_size
    TITLE_FONTSIZE = 18

    # markersize in points
    ms = float(marker_size) ** 0.5  # keep your behavior

    fig, ax = plt.subplots(figsize=FIGSIZE)

    # =========================
    # Plot curves
    # =========================
    ax.plot(
        Vwrites, 
        Caps, 
        linestyle='-',
        linewidth=0.8, 
        color="#000000", 
        alpha=0.65
        )
    ax.scatter(
        Vwrites[pos_mask],
        Caps[pos_mask],
        marker="o",
        s = marker_size,   # ajuste la taille visuelle
        color=POS_COLOR,
        label="Positive Vwrite",
        zorder=10
        )
    ax.scatter(
        Vwrites[neg_mask],
        Caps[neg_mask],
        marker="o",
        s = marker_size,   # ajuste la taille visuelle
        color=NEG_COLOR,
        label="Negative Vwrite",
        zorder=10
        )

    # =========================
    # Labels / title
    # =========================
    ax.set_xlabel("Writing voltage (V)", fontsize=LABEL_FONTSIZE)
    ax.set_ylabel(
        f"Average Capacitance near {reading_voltage} V (pF)",
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
    plot_name = f"{metadata['Date'][0]}_{metadata['Name'][0]}_{metadata['Device_ID'][0]}_AVERAGE_Cmem_vs_Vwrite.png"
    out_path = os.path.join(Output_dir, plot_name)

    plt.tight_layout()
    fig.savefig(out_path, dpi=600, bbox_inches="tight")
    plt.show()

    return fig, ax, out_path



# ──────────────────────────────────────────────────────────────────────────────
#                       Plot mean - Pulse index
# ──────────────────────────────────────────────────────────────────────────────


def plot_mean_index(
    DF_MEAN: pd.DataFrame,
    metadata, 
    Output_dir: str = "",
    marker_size: int = 40,
    Label_size: int = 18,
    tick_size: int = 16,
    legend_size: int = 14,
    reading_voltage: float = 0.0
):
    

    
    Vwrites = []
    Caps = []
    Index = []

    for v in DF_MEAN["Vwrite"]:
        Vwrites.append(v)

    for i,c in enumerate(DF_MEAN["Cmem"], start=1):
        Caps.append(c)
        Index.append(i)

    Vwrites = np.asarray(Vwrites, dtype=float)
    Index = np.asarray(Index, dtype = float)
    Caps = np.asanyarray(Caps, dtype = float)

    
    # Conversion in pF
    Caps = Caps*1e+12

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
    LABEL_FONTSIZE = Label_size
    TICK_FONTSIZE = tick_size
    LEGEND_FONTSIZE = legend_size
    TITLE_FONTSIZE = 18

    # markersize in points
    ms = float(marker_size) ** 0.5  # keep your behavior

    fig, ax = plt.subplots(figsize=FIGSIZE)

    # =========================
    # Plot curves
    # =========================
    ax.plot(
        Index, 
        Caps, 
        linestyle='-',
        linewidth=0.8, 
        color="#000000", 
        alpha=0.65
        )
    ax.scatter(
        Index[pos_mask],
        Caps[pos_mask],
        marker="o",
        s = marker_size,   # ajuste la taille visuelle
        color=POS_COLOR,
        label="Positive Vwrite",
        zorder=10
        )
    ax.scatter(
        Index[neg_mask],
        Caps[neg_mask],
        marker="o",
        s = marker_size,   # ajuste la taille visuelle
        color=NEG_COLOR,
        label="Negative Vwrite",
        zorder=10
        )

    # =========================
    # Labels / title
    # =========================
    ax.set_xlabel("Pulse Index", fontsize=LABEL_FONTSIZE)
    ax.set_ylabel(
        f"Average Capacitance near {reading_voltage} V (pF)",
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
    plot_name = f"{metadata['Date'][0]}_{metadata['Name'][0]}_{metadata['Device_ID'][0]}_AVERAGE_Cmem_vs_Index.png"
    out_path = os.path.join(Output_dir, plot_name)

    plt.tight_layout()
    fig.savefig(out_path, dpi=600, bbox_inches="tight")
    plt.show()

    return fig, ax, out_path




# ──────────────────────────────────────────────────────────────────────────────
#                           Plots   
# ──────────────────────────────────────────────────────────────────────────────


def plot_hist_panel(
    C_grouped_by_V: Dict[float, np.ndarray],
    bins: np.ndarray,
    round_by: float,
    vwrite_threshold_pos: float,
    vwrite_threshold_neg: float,
    sign: str = "pos",
    title: str = "",
    output_dir: str = "plots",
    Label: str = "Resistance (Ohm)",
    figsize = (6,3)
) -> str | None:
    """
    sign:
      - 'LTD' -> plot groups with V > +threshold (LTD)
      - 'LTP' -> plot groups with V < -threshold (LTP)
    """
    

    statistics_array = []

    if sign == "LTD":
        keys = []
        for k in C_grouped_by_V:
            if k > vwrite_threshold_pos:
                keys.append(k)

        keys = sorted(keys)
        cmap_base = plt.get_cmap("Blues")

    elif sign == "LTP":
        keys = []
        for k in C_grouped_by_V:
            if k < -vwrite_threshold_neg:
                keys.append(k)

        keys = sorted(keys)
        cmap_base = plt.get_cmap("Reds")
    
    else:
        print("sign must be either LTP or LTD")

    if len(keys) == 0:
        print(f"No groups to plot for sign={sign}")
        return None

    cmap_values = cmap_base(np.linspace(0.3, 0.9, len(keys)))
    cmap = ListedColormap(cmap_values)

    plt.figure(figsize=(6, 3))
    ax = plt.gca()

    for i, v in enumerate(keys):
        data = C_grouped_by_V[v]

        if data.size == 0:
            continue

        # histogram counts
        counts, _ = np.histogram(data, bins=bins)

        bin_centers = 0.5 * (bins[:-1] + bins[1:])
        bin_widths = np.diff(bins)

        ax.bar(
            bin_centers,
            counts,
            width=bin_widths,
            alpha=0.4,
            color=cmap(i % cmap.N),
            align="center",
            label=f"Vprog={v} V",
        )

        # gaussian fit scaled to counts
        mu, std = norm.fit(data)

        rsd_percent = std / mu * 100
        statistics_array.append([v, mu, std, rsd_percent])
        statistics_Dataframe = pd.DataFrame(statistics_array, columns = ["Vw", "mu", "std", "rsd percent"])

        x = np.linspace(mu - 3 * std, mu + 3 * std, 200)
        p = norm.pdf(x, mu, std)

        scale = data.size * np.diff(bins)[0]

        ax.plot(
            x,
            p * scale,
            color=cmap(i % cmap.N),
            linewidth=2,
        )

    ax.set_xlabel(Label)
    ax.set_ylabel("Count")
    ax.set_title(title)

    # colorbar reflecting V values in this panel
    sm = plt.cm.ScalarMappable(
        cmap=cmap,
        norm=plt.Normalize(vmin=min(keys), vmax=max(keys)),
    )
    sm.set_array([])

    cbar = plt.colorbar(sm, ax=ax, pad=0.01)
    cbar.set_label("Vprog (V)")

    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"hist_C_grouped_by_V_{sign}_roundby{round_by}.svg")
    #plt.savefig(out_path)

    return statistics_Dataframe



# ──────────────────────────────────────────────────────────────────────────────
#                           Plots  LTP-LTD for conductance and weight 
# ──────────────────────────────────────────────────────────────────────────────

def plot_hist_analysis(
    C_sorted,
    bins,
    round_by: float = 0.05,
    vwrite_threshold_pos: float = 0.1,
    vwrite_threshold_neg: float = 0.1,
    Label: str = "Resistance (Ohm)",
    figsize = (9,6),
    output_dir: str = "plots",
) -> dict:
    """
    Convenience wrapper to run the whole workflow (same as notebook sequence).
    Returns paths + arrays for further use in a notebook.
    """

    statistics_df_LTD = plot_hist_panel(
        C_grouped_by_V= C_sorted,
        bins=bins,
        round_by=round_by,
        vwrite_threshold_pos=vwrite_threshold_pos,
        vwrite_threshold_neg=vwrite_threshold_neg,
        sign="LTD",
        title="Depression",
        Label=Label,
        figsize=figsize
        )

    statistics_df_LTP = plot_hist_panel(
        C_grouped_by_V= C_sorted,
        bins=bins,
        round_by=round_by,
        vwrite_threshold_pos=vwrite_threshold_pos,
        vwrite_threshold_neg=vwrite_threshold_neg,
        sign="LTP",
        title="Potentiation",
        Label=Label,
        figsize=figsize
        )
    
    return statistics_df_LTD, statistics_df_LTP





# ──────────────────────────────────────────────────────────────────────────────
#                           Plots  k-factor 
# ──────────────────────────────────────────────────────────────────────────────

def count_distinct_states(df, k=2.0):
    """
    Count the number of statistically distinguishable states
    using |mu_i - mu_j| > k (std_i + std_j)
    """
    mus = df["mu"].values
    stds = df["std"].values

    count = 1  # at least one state
    last_mu = mus[0]
    last_std = stds[0]

    for mu, std in zip(mus[1:], stds[1:]):
        if abs(mu - last_mu) > k * (std + last_std):
            count += 1
            last_mu = mu
            last_std = std

    return count


def k_list(statistics_df):
    """
    Help to plot the change of the number of state depending on k
    """

    k_range = [1.0, 1.5, 2.0, 2.5, 3.0]
    nbr_state_list = []

    for k in k_range:
        nbr_state_list.append(count_distinct_states(statistics_df, k=k))
    
    k_stats = pd.DataFrame({
        "k": k_range,
        "Nbr_state": nbr_state_list
    })

    return k_stats



def plot_k(
    statistics_df_LTD: pd.DataFrame,
    statistics_df_LTP: pd.DataFrame,
    LTD_COLOR: str = "#285b96",
    LTP_COLOR: str  = "#C20000FF"
):

    k_stats_LTD = k_list(statistics_df_LTD)
    k_stats_LTP = k_list(statistics_df_LTP)



    plt.figure(figsize=(6, 4))

    # ---------- LTD ----------
    plt.scatter(
        k_stats_LTD["k"],
        k_stats_LTD["Nbr_state"],
        color=LTD_COLOR,
        s=45,
        label="Depression",
        zorder=3,
    )

    plt.plot(
        k_stats_LTD["k"],
        k_stats_LTD["Nbr_state"],
        color="gray",
        linewidth=0.75,
        alpha=0.5,
        zorder=2,
    )

    # value labels LTD
    for x, y in zip(k_stats_LTD["k"], k_stats_LTD["Nbr_state"]):
        plt.text(
            x,
            y + 0.25,
            f"{y}",
            color=LTD_COLOR,
            fontsize=10,
            ha="center",
        )

    # ---------- LTP ----------
    plt.scatter(
        k_stats_LTP["k"],
        k_stats_LTP["Nbr_state"],
        color=LTP_COLOR,
        s=45,
        label="Potentiation",
        zorder=3,
    )

    plt.plot(
        k_stats_LTP["k"],
        k_stats_LTP["Nbr_state"],
        color="gray",
        linewidth=0.75,
        alpha=0.5,
        zorder=2,
    )

    # value labels LTP
    for x, y in zip(k_stats_LTP["k"], k_stats_LTP["Nbr_state"]):
        plt.text(
            x,
            y - 0.4,
            f"{y}",
            color=LTP_COLOR,
            fontsize=10,
            ha="center",
        )

    plt.xlabel("k factor")
    plt.ylabel("Number of distinct states")
    plt.title("Distinct states vs separability factor k")

    # plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.show()
