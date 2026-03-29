import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap
from matplotlib.colors import LinearSegmentedColormap
import os
import json
# from matplotlib import colormaps
import re
import io
from datetime import datetime

def _safe_savepath(directory, filename, max_len=259):
    """Return the save path, stripping the leading YYYY-MM-DD_ prefix from the
    filename when the full path would exceed max_len characters which is 260 on Windows (Windows MAX_PATH)."""
    full = os.path.join(directory, filename)
    if len(full) <= max_len:
        return full
    short = re.sub(r'^\d{4}-\d{2}-\d{2}_', '', filename)
    return os.path.join(directory, short)

def folder_main_plot(output_path):
        output_main_plot = os.path.join(output_path, "Main plot")
        os.makedirs(output_main_plot, exist_ok=True)  # Ensure output directory exists
        # Save figure (bbox_inches='tight' ensures everything fits inside)

        


def main_plot(df_fatigue_DHM, df_fatigue_CVM, df_fatigue_PUND, CVM_dataframe,
              metadata_dict_DHM, metadata_dict_CVM, metadata_dict_PUND, 
              metadata_str_DHM, metadata_str_CVM, metadata_str_PUND, 
              output_path, base_name, labelsize):
    
    label_size = labelsize

    # ----------- DHM MEASUREMENT -----------
    if metadata_dict_DHM.get("DHM_present", False):

        dhm_num = metadata_dict_DHM["DHM_number"]

        fig = plt.figure(figsize=(16, 10), facecolor='white')
        fig.suptitle("DHM measurement", fontsize=label_size + 4, fontweight="bold", y=0.98)

        gs = fig.add_gridspec(2, 2, left=0.08, right=0.97, top=0.92, bottom=0.09,
                              wspace=0.25, hspace=0.25)
        ax_pr   = fig.add_subplot(gs[0, :])   # full top row — polarization
        ax_vc   = fig.add_subplot(gs[1, 0])
        ax_meta = fig.add_subplot(gs[1, 1])

        # --- Pr ---
        try:
            ax_pr.plot(df_fatigue_DHM["Cycles [n]"], df_fatigue_DHM[f"{dhm_num}-DHM Pr+ [uC/cm2]"],
                       color=(0.18, 0.45, 0.78), marker='o', markersize=7,
                       linewidth=2.2, label='Pr+')
            ax_pr.plot(df_fatigue_DHM["Cycles [n]"], df_fatigue_DHM[f"{dhm_num}-DHM Pr- [uC/cm2]"],
                       color=(0.13, 0.70, 0.44), marker='s', markersize=7,
                       linewidth=2.2, label='|Pr−|')
        except Exception as e:
            print("Error plotting DHM Pr data:", e)
        ax_pr.set_xlabel("Cycles (n)", fontsize=label_size, fontweight='bold')
        ax_pr.set_ylabel("Pr  (μC cm⁻²)", fontsize=label_size, fontweight='bold')
        ax_pr.set_xscale('log')
        ax_pr.set_title("Remnant polarization vs. fatigue cycles", fontsize=label_size + 1, fontweight='bold', pad=8)
        ax_pr.legend(fontsize=label_size - 1, frameon=True, framealpha=0.9, edgecolor='lightgray')
        ax_pr.tick_params(axis='both', labelsize=label_size, direction='in',
                          which='both', top=True, right=True, length=5, width=1.0)
        ax_pr.set_facecolor('white')
        ax_pr.grid(True, which='major', linestyle='--', linewidth=0.7, color='#cccccc', zorder=0)
        for spine in ax_pr.spines.values():
            spine.set_linewidth(1.0)

        # --- Vc ---
        try:
            ax_vc.plot(df_fatigue_DHM["Cycles [n]"], df_fatigue_DHM["1-DHM Vc+ [V]"],
                       color=(0.18, 0.45, 0.78), marker='o', markersize=7,
                       linewidth=2.2, label='Vc+')
            ax_vc.plot(df_fatigue_DHM["Cycles [n]"], df_fatigue_DHM["1-DHM Vc- [V]"],
                       color=(0.13, 0.70, 0.44), marker='s', markersize=7,
                       linewidth=2.2, label='|Vc−|')
        except Exception as e:
            print("Error plotting DHM Vc data:", e)
        ax_vc.set_xlabel("Cycles (n)", fontsize=label_size, fontweight='bold')
        ax_vc.set_ylabel("Vc  (V)", fontsize=label_size, fontweight='bold')
        ax_vc.set_xscale('log')
        ax_vc.set_title("Coercive voltage vs. fatigue cycles", fontsize=label_size + 1, fontweight='bold', pad=8)
        ax_vc.legend(fontsize=label_size - 1, frameon=True, framealpha=0.9, edgecolor='lightgray')
        ax_vc.tick_params(axis='both', labelsize=label_size, direction='in',
                          which='both', top=True, right=True, length=5, width=1.0)
        ax_vc.set_facecolor('white')
        ax_vc.grid(True, which='major', linestyle='--', linewidth=0.7, color='#cccccc', zorder=0)
        for spine in ax_vc.spines.values():
            spine.set_linewidth(1.0)

        # --- Metadata dashboard ---
        ax_meta.axis('off')
        ax_meta.patch.set_facecolor('#f7f7f7')
        ax_meta.text(0.05, 0.97, metadata_str_DHM,
                     fontsize=14.5, va='top', ha='left',
                     transform=ax_meta.transAxes, family='monospace',
                     linespacing=1.55)
        for spine in ax_meta.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(0.8)
            spine.set_edgecolor('#aaaaaa')

        output_main_plot = os.path.join(output_path, "Main plot")
        os.makedirs(output_main_plot, exist_ok=True)

        #_safe_savepath is a function define at the beginning of this file to avoid Windows MAX_PATH issues by stripping the leading date prefix from the filename if needed
        plt.savefig(
            _safe_savepath(
                output_main_plot,
                f"{metadata_dict_DHM['Measurement_date_iso']}_{base_name}_Fatigue-DHM_Main_Plot.png"
            ),
            dpi=300,
            bbox_inches='tight'
        )

        plt.show()
        plt.close(fig)

    # ----------- CVM MEASUREMENT -----------


    list_memory_window = []
    V_peak_HCS = []
    V_peak_LCS = []

    for df in CVM_dataframe:
        list_memory_window.append(df['Memory_Window'].iloc[0])  # Assuming Memory_Window is constant within each DataFrame
        V_peak_HCS.append(df['V_peak_HCS'].iloc[0])  # Assuming V_peak_HCS is constant within each DataFrame
        V_peak_LCS.append(df['V_peak_LCS'].iloc[0])  # Assuming V_peak_LCS is constant within each DataFrame

    list_memory_window = np.array(list_memory_window)  # Convert to numpy array for easier plotting
    V_peak_HCS = np.array(V_peak_HCS)
    V_peak_LCS = np.array(V_peak_LCS)
        

    if metadata_dict_CVM.get("CVM_present", False):
        cvm_num = metadata_dict_CVM["CVM_number"]

        fig = plt.figure(figsize=(16, 10), facecolor='white')
        fig.suptitle("CVM measurement", fontsize=label_size + 4, fontweight="bold", y=0.98)

        gs = fig.add_gridspec(2, 2, left=0.08, right=0.97, top=0.92, bottom=0.09,
                              wspace=0.25, hspace=0.25)
        ax_mw   = fig.add_subplot(gs[0, :])   # full top row — memory window
        ax_vmax = fig.add_subplot(gs[1, 0])   # bottom left — Vmax peak voltage
        ax_meta = fig.add_subplot(gs[1, 1])   # bottom right — metadata

        # --- Memory window ---
        try:
            ax_mw.plot(df_fatigue_CVM["Cycles [n]"], list_memory_window*1e+12,
                       color=(0.85, 0.35, 0.20), marker='o', markersize=7,
                       linewidth=2.2, label='Memory window')
        except Exception as e:
            print("Error plotting CVM memory window:", e)
        ax_mw.set_xlabel("Cycles (n)", fontsize=label_size, fontweight='bold')
        ax_mw.set_ylabel("Memory window at 0V (pF)", fontsize=label_size, fontweight='bold')
        ax_mw.set_xscale('log')
        ax_mw.set_title("Memory window vs. fatigue cycles", fontsize=label_size + 1, fontweight='bold', pad=8)
        ax_mw.legend(fontsize=label_size - 1, frameon=True, framealpha=0.9, edgecolor='lightgray')
        ax_mw.tick_params(axis='both', labelsize=label_size, direction='in',
                          which='both', top=True, right=True, length=5, width=1.0)
        ax_mw.set_facecolor('white')
        ax_mw.grid(True, which='major', linestyle='--', linewidth=0.7, color='#cccccc', zorder=0)
        for spine in ax_mw.spines.values():
            spine.set_linewidth(1.0)

        # --- Vmax peak voltage ---
        try:
            ax_vmax.plot(df_fatigue_CVM["Cycles [n]"],
                         V_peak_LCS,
                         color="#810303", marker='o', markersize=7,
                         linewidth=2.2, label='V_peak_LCS')
            ax_vmax.plot(df_fatigue_CVM["Cycles [n]"],
                         V_peak_HCS,
                         color="#55037B", marker='s', markersize=7,
                         linewidth=2.2, label='V_peak_HCS')
        except Exception as e:
            print("Error plotting CVM Vmax data:", e)
        ax_vmax.set_xlabel("Cycles (n)", fontsize=label_size, fontweight='bold')
        ax_vmax.set_ylabel("Vmax  (V)", fontsize=label_size, fontweight='bold')
        ax_vmax.set_xscale('log')
        ax_vmax.set_title("Capacitance-peak voltage vs. fatigue cycles", fontsize=label_size + 1, fontweight='bold', pad=8)
        ax_vmax.legend(fontsize=label_size - 1, frameon=True, framealpha=0.9, edgecolor='lightgray')
        ax_vmax.tick_params(axis='both', labelsize=label_size, direction='in',
                            which='both', top=True, right=True, length=5, width=1.0)
        ax_vmax.set_facecolor('white')
        ax_vmax.grid(True, which='major', linestyle='--', linewidth=0.7, color='#cccccc', zorder=0)
        for spine in ax_vmax.spines.values():
            spine.set_linewidth(1.0)

        # --- Metadata panel ---
        ax_meta.axis('off')
        ax_meta.patch.set_facecolor('#f7f7f7')
        ax_meta.text(0.05, 0.97, metadata_str_CVM,
                     fontsize=13.5, va='top', ha='left',
                     transform=ax_meta.transAxes, family='monospace',
                     linespacing=1.55)
        for spine in ax_meta.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(0.8)
            spine.set_edgecolor('#aaaaaa')

        output_main_plot = os.path.join(output_path, "Main plot")
        os.makedirs(output_main_plot, exist_ok=True)

        plt.savefig(
            _safe_savepath(
                output_main_plot,
                f"{metadata_dict_CVM['Measurement_date_iso']}_{base_name}_Fatigue-CVM_Main_Plot.png"
            ),
            dpi=300,
            bbox_inches='tight'
        )

        plt.show()
        plt.close(fig)

    # ----------- PUND MEASUREMENT -----------

    if metadata_dict_PUND.get("PUND_present", False):
        pund_num = metadata_dict_PUND["PUND_number"]

        fig = plt.figure(figsize=(16, 10), facecolor='white')
        fig.suptitle("PUND measurement", fontsize=label_size + 4, fontweight="bold", y=0.98)

        gs = fig.add_gridspec(2, 2, left=0.08, right=0.97, top=0.92, bottom=0.09,
                              wspace=0.25, hspace=0.25)
        ax_pr   = fig.add_subplot(gs[0, :])   # full top row — polarization
        ax_vc   = fig.add_subplot(gs[1, 0])   # bottom left — coercive voltage
        ax_meta = fig.add_subplot(gs[1, 1])   # bottom right — metadata

        # --- Pr ---
        try:
            ax_pr.plot(df_fatigue_PUND["Cycles [n]"],
                       df_fatigue_PUND[f"{pund_num}-PM Pr+ [uC/cm2]"],
                       color="#3A0580", marker='o', markersize=7,
                       linewidth=2.2, label='Pr+')
            ax_pr.plot(df_fatigue_PUND["Cycles [n]"],
                       df_fatigue_PUND[f"{pund_num}-PM Pr- [uC/cm2]"],
                       color="#037421", marker='s', markersize=7,
                       linewidth=2.2, label='|Pr−|')
        except Exception as e:
            print("Error plotting PUND Pr data:", e)
        ax_pr.set_xlabel("Cycles (n)", fontsize=label_size, fontweight='bold')
        ax_pr.set_ylabel("Pr  (μC cm⁻²)", fontsize=label_size, fontweight='bold')
        ax_pr.set_xscale('log')
        ax_pr.set_title("Remnant polarization vs. fatigue cycles", fontsize=label_size + 1, fontweight='bold', pad=8)
        ax_pr.legend(fontsize=label_size - 1, frameon=True, framealpha=0.9, edgecolor='lightgray')
        ax_pr.tick_params(axis='both', labelsize=label_size, direction='in',
                          which='both', top=True, right=True, length=5, width=1.0)
        ax_pr.set_facecolor('white')
        ax_pr.grid(True, which='major', linestyle='--', linewidth=0.7, color='#cccccc', zorder=0)
        for spine in ax_pr.spines.values():
            spine.set_linewidth(1.0)

        # --- Vc (optional — column may be absent in some files) ---
        try:
            ax_vc.plot(df_fatigue_PUND["Cycles [n]"],
                       df_fatigue_PUND[f"{pund_num}-PM Vc+ [V]"],
                       color="#3A0580", marker='o', markersize=7,
                       linewidth=2.2, label='Vc+')
            ax_vc.plot(df_fatigue_PUND["Cycles [n]"],
                       df_fatigue_PUND[f"{pund_num}-PM Vc- [V]"],
                       color="#037421", marker='s', markersize=7,
                       linewidth=2.2, label='|Vc−|')
            ax_vc.set_xlabel("Cycles (n)", fontsize=label_size, fontweight='bold')
            ax_vc.set_ylabel("Vc  (V)", fontsize=label_size, fontweight='bold')
            ax_vc.set_xscale('log')
            ax_vc.set_title("Coercive voltage vs. fatigue cycles", fontsize=label_size + 1, fontweight='bold', pad=8)
            ax_vc.legend(fontsize=label_size - 1, frameon=True, framealpha=0.9, edgecolor='lightgray')
            ax_vc.tick_params(axis='both', labelsize=label_size, direction='in',
                              which='both', top=True, right=True, length=5, width=1.0)
            ax_vc.set_facecolor('white')
            ax_vc.grid(True, which='major', linestyle='--', linewidth=0.7, color='#cccccc', zorder=0)
            for spine in ax_vc.spines.values():
                spine.set_linewidth(1.0)
        except Exception as e:
            print("Vc data not available for PUND — skipping plot:", e)
            ax_vc.axis('off')

        # --- Metadata panel ---
        ax_meta.axis('off')
        ax_meta.patch.set_facecolor('#f7f7f7')
        ax_meta.text(0.05, 0.97, metadata_str_PUND,
                     fontsize=11.5, va='top', ha='left',
                     transform=ax_meta.transAxes, family='monospace',
                     linespacing=1.55)
        for spine in ax_meta.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(0.8)
            spine.set_edgecolor('#aaaaaa')

        output_main_plot = os.path.join(output_path, "Main plot")
        os.makedirs(output_main_plot, exist_ok=True)

        plt.savefig(
            _safe_savepath(
                output_main_plot,
                f"{metadata_dict_PUND['Measurement_date_iso']}_{base_name}_Fatigue-PUND_Main_Plot.png"
            ),
            dpi=300,
            bbox_inches='tight'
        )

        plt.show()
        plt.close(fig)



# ------------------------------------
# ------------------------------------


def _truncate_cmap(cmap, minval=0.3, maxval=0.9, n=256):
    """Évite les zones trop claires du colormap (minval>0)."""
    colors = cmap(np.linspace(minval, maxval, n))
    return ListedColormap(colors)

def Plot_single_DHM(DHM_dataframe, Cycles_total, label_size, output_main_plot, base_name, metadata_dict_DHM):
    if not metadata_dict_DHM.get("DHM_present", False):
        return

    #To remove the breakdown point
    Removal = len(Cycles_total) - len(DHM_dataframe)
    if Removal > 0:
        Cycles_total = Cycles_total[:-Removal]

    legend_threshold = 1
    n_curves = len(DHM_dataframe)
    use_legend = n_curves <= legend_threshold

    # Figure commune aux deux cas
    fig, axs = plt.subplots(1, 2, figsize=(22, 6))
    fig.suptitle(f"DHM - {base_name}", fontsize=label_size + 2, fontweight="bold")

    if use_legend:
        # --------- MODE "PEU DE COURBES" : COULEURS FIXES + ALPHA CROISSANT ---------
        base_color_P = (0.25, 0.85, 0.55)  # vert P–V
        base_color_I = (0.35, 0.65, 0.85)  # bleu I–V
        alpha_list = np.linspace(0.25, 1.0, n_curves)

        for i, cycle in enumerate(Cycles_total):
            df = DHM_dataframe[i]
            alpha = float(alpha_list[i])
            label = f"Cycle {cycle}"

            axs[0].plot(
                df["V+ [V]"],
                df["P1 [uC/cm2]"],
                color=base_color_P,
                alpha=alpha,
                label=label,
            )

            axs[1].plot(
                df["V+ [V]"],
                df["I1 [A]"],
                color=base_color_I,
                alpha=alpha,
                label=label,
            )

        # Styles
        axs[0].set_xlabel("Voltage [V]", fontsize=label_size)
        axs[0].set_ylabel("Polarization (μC/cm²)", fontsize=label_size)
        axs[0].set_title("P–V loop")
        axs[0].grid(True, color="lightgray", linestyle="--", linewidth=0.5)
        axs[0].tick_params(axis="both", labelsize=label_size)

        axs[1].set_xlabel("Voltage [V]", fontsize=label_size)
        axs[1].set_ylabel("Current [A]", fontsize=label_size)
        axs[1].set_title("I–V loop")
        axs[1].grid(True, color="lightgray", linestyle="--", linewidth=0.5)
        axs[1].tick_params(axis="both", labelsize=label_size)

        # Légendes à droite de chaque subplot (sans doublons)
        for ax in axs:
            handles, labels = ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))

            ax.legend(
                handles=list(by_label.values()),
                labels=list(by_label.keys()),
                loc="center left",
                bbox_to_anchor=(1.02, 0.5),
                borderaxespad=0,
                fontsize=label_size - 2,
                title="Cycles",
            )

        fig.subplots_adjust(right=0.85, wspace=0.55)

    else:
        # --------- MODE "GROS DATASET" : COLORMAPS + COLORBARS ---------
        cmap_P = _truncate_cmap(cm.Greens, minval=0.15, maxval=0.95)
        cmap_I = _truncate_cmap(cm.Blues,  minval=0.15, maxval=0.95)

        vmin, vmax = float(np.min(Cycles_total)), float(np.max(Cycles_total))
        norm = mcolors.LogNorm(vmin=max(vmin, 1e-3), vmax=vmax)

        for i, cycle in enumerate(Cycles_total):
            df = DHM_dataframe[i]

            color_P = cmap_P(norm(cycle))
            color_I = cmap_I(norm(cycle))
            alpha = 0.75

            axs[0].plot(
                df["V+ [V]"],
                df["P1 [uC/cm2]"],
                color=color_P,
                alpha=alpha,
            )

            axs[1].plot(
                df["V+ [V]"],
                df["I1 [A]"],
                color=color_I,
                alpha=alpha,
            )

        # Styles
        axs[0].set_xlabel("Voltage [V]", fontsize=label_size)
        axs[0].set_ylabel("Polarization (μC/cm²)", fontsize=label_size)
        axs[0].set_title("P–V loop")
        axs[0].grid(True, color="lightgray", linestyle="--", linewidth=0.5)
        axs[0].tick_params(axis="both", labelsize=label_size)

        axs[1].set_xlabel("Voltage [V]", fontsize=label_size)
        axs[1].set_ylabel("Current [A]", fontsize=label_size)
        axs[1].set_title("I–V loop")
        axs[1].grid(True, color="lightgray", linestyle="--", linewidth=0.5)
        axs[1].tick_params(axis="both", labelsize=label_size)

        # Colorbars
        sm_P = cm.ScalarMappable(cmap=cmap_P, norm=norm)
        sm_P.set_array([])

        sm_I = cm.ScalarMappable(cmap=cmap_I, norm=norm)
        sm_I.set_array([])

        cbar0 = fig.colorbar(sm_P, ax=axs[0], fraction=0.03, pad=0.04)
        cbar0.set_label("Cycle number", fontsize=label_size)

        cbar1 = fig.colorbar(sm_I, ax=axs[1], fraction=0.03, pad=0.04)
        cbar1.set_label("Cycle number", fontsize=label_size)

        fig.subplots_adjust(right=0.90, wspace=0.55)

    # --------- SAUVEGARDE UNIQUE ---------
    filename = f"{metadata_dict_DHM['Measurement_date_iso']}_{base_name}_DHM.png"
    plt.savefig(_safe_savepath(output_main_plot, filename), dpi=300, bbox_inches="tight")
    plt.show()
    plt.close("all")



def Plot_single_CVM(CVM_dataframe, Cycles_total, label_size, output_main_plot, base_name, metadata_dict_CVM):
    if not metadata_dict_CVM.get("CVM_present", False):
        return

    #To remove the breakdown point
    Removal = len(Cycles_total) - len(CVM_dataframe)
    if Removal > 0:
        Cycles_total = Cycles_total[:-Removal]

    legend_threshold = 1
    n_curves = len(CVM_dataframe)
    use_legend = n_curves <= legend_threshold

    # Figure commune aux deux cas
    fig, axs = plt.subplots(1, 2, figsize=(22, 6))
    fig.suptitle(f"CVM - {base_name}", fontsize=label_size + 2, fontweight="bold")

    if use_legend:
        # --------- MODE "PEU DE COURBES" : COULEURS FIXES + ALPHA CROISSANT ---------
        base_color_C = (0.65, 0.35, 0.45)  # vert P–V
        base_color_delta = (0.45, 0.45, 0.15)  # bleu I–V
        alpha_list = np.linspace(0.25, 1.0, n_curves)

        for i, cycle in enumerate(Cycles_total):
            df = CVM_dataframe[i]
            alpha = float(alpha_list[i])
            label = f"Cycle {cycle}"

            axs[0].plot(
                df["Bias [V]"],
                df["C [F]"],
                color=base_color_C,
                alpha=alpha,
                label=label,
            )

            axs[1].plot(
                df["Bias [V]"],
                df["tan(delta) [1]"],
                color=base_color_delta,
                alpha=alpha,
                label=label,
            )

        # Styles
        axs[0].set_xlabel("Voltage [V]", fontsize=label_size)
        axs[0].set_ylabel("C [F]", fontsize=label_size)
        axs[0].set_title("C–V loop")
        axs[0].grid(True, color='lightgray', linestyle='--', linewidth=0.5)
        axs[0].tick_params(axis='both', labelsize=label_size)

        axs[1].set_xlabel("Voltage [V]", fontsize=label_size)
        axs[1].set_ylabel("tan(δ)", fontsize=label_size)
        axs[1].set_title("tan(δ)–V loop")
        axs[1].grid(True, color='lightgray', linestyle='--', linewidth=0.5)
        axs[1].tick_params(axis='both', labelsize=label_size)


        # Légendes à droite de chaque subplot (sans doublons)
        for ax in axs:
            handles, labels = ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))

            ax.legend(
                handles=list(by_label.values()),
                labels=list(by_label.keys()),
                loc="center left",
                bbox_to_anchor=(1.02, 0.5),
                borderaxespad=0,
                fontsize=label_size - 2,
                title="Cycles",
            )

        fig.subplots_adjust(right=0.85, wspace=0.55)

    else:
        # --------- MODE "GROS DATASET" : COLORMAPS + COLORBARS ---------
        cmap_C  = _truncate_cmap(cm.Reds,  minval=0.15, maxval=0.95)
        cmap_td = _truncate_cmap(cm.Greens, minval=0.15, maxval=0.95)

        vmin, vmax = float(np.min(Cycles_total)), float(np.max(Cycles_total))
        norm = mcolors.LogNorm(vmin=max(vmin, 1e-3), vmax=vmax)

        for i, cycle in enumerate(Cycles_total):
            df = CVM_dataframe[i]

            color_C = cmap_C(norm(cycle))
            color_Td = cmap_td(norm(cycle))
            alpha = 0.75

            axs[0].plot(
                df["Bias [V]"],
                df["C [F]"],
                color=color_C,
                alpha=alpha,
            )

            axs[1].plot(
                df["Bias [V]"],
                df["tan(delta) [1]"],
                color=color_Td,
                alpha=alpha,
            )

        # Styles
        axs[0].set_xlabel("Voltage [V]", fontsize=label_size)
        axs[0].set_ylabel("C [F]", fontsize=label_size)
        axs[0].set_title("C–V loop")
        axs[0].grid(True, color='lightgray', linestyle='--', linewidth=0.5)
        axs[0].tick_params(axis='both', labelsize=label_size)

        axs[1].set_xlabel("Voltage [V]", fontsize=label_size)
        axs[1].set_ylabel("tan(δ)", fontsize=label_size)
        axs[1].set_title("tan(δ)–V loop")
        axs[1].grid(True, color='lightgray', linestyle='--', linewidth=0.5)
        axs[1].tick_params(axis='both', labelsize=label_size)


        # Colorbars
        sm_P = cm.ScalarMappable(cmap=cmap_C, norm=norm)
        sm_P.set_array([])

        sm_I = cm.ScalarMappable(cmap=cmap_td, norm=norm)
        sm_I.set_array([])

        cbar0 = fig.colorbar(sm_P, ax=axs[0], fraction=0.03, pad=0.04)
        cbar0.set_label("Cycle number", fontsize=label_size)

        cbar1 = fig.colorbar(sm_I, ax=axs[1], fraction=0.03, pad=0.04)
        cbar1.set_label("Cycle number", fontsize=label_size)

        fig.subplots_adjust(right=0.90, wspace=0.55)

    # --------- SAUVEGARDE UNIQUE ---------
    filename = f"{metadata_dict_CVM['Measurement_date_iso']}_{base_name}_CVM.png"
    plt.savefig(_safe_savepath(output_main_plot, filename), dpi=300, bbox_inches="tight")
    plt.show()
    plt.close("all")


# ------------------------------------------------------------------------------

def Plot_single_PUND(PUND_dataframe, Cycles_total, label_size, output_main_plot, base_name, metadata_dict_PUND):
    if not metadata_dict_PUND.get("PUND_present", False):
        return

    #To remove the breakdown point
    Removal = len(Cycles_total) - len(PUND_dataframe)
    if Removal > 0:
        Cycles_total = Cycles_total[:-Removal]

    legend_threshold = 1
    n_curves = len(PUND_dataframe)
    use_legend = n_curves <= legend_threshold

    # Figure commune aux deux cas
    fig, axs = plt.subplots(1, 2, figsize=(22, 6))
    fig.suptitle(f"PUND - {base_name}", fontsize=label_size + 2, fontweight="bold")


    if use_legend:
        # --------- MODE "PEU DE COURBES" : COULEURS FIXES + ALPHA CROISSANT ---------
        base_color_P = (0.35, 0.75, 0.45)  # vert P–V
        base_color_I = (0.45, 0.45, 0.75)  # bleu I–V
        alpha_list = np.linspace(0.25, 1.0, n_curves)

        for i, cycle in enumerate(Cycles_total):

            df0 = PUND_dataframe[i]
            df_work = df0 if (df0.shape[1] % 4 == 0) else df0.iloc[:, 1:]
            df_list = PUND_collumn_splitter(df_work)

            alpha = float(alpha_list[i])
            label = f"Cycle {cycle}"
            label_for_cycle = f"Cycle {i}"

            first_of_cycle = True
            for w in df_list:
                lbl = label_for_cycle if first_of_cycle else None
                axs[0].plot(w['V'], w['P'], color=base_color_P, alpha=alpha, label=label)
                first_of_cycle = False

            first_of_cycle = True
            for w in df_list:
                lbl = label_for_cycle if first_of_cycle else None
                axs[1].plot(w['V'], w['I'], color=base_color_I, alpha=alpha, label=label)
                first_of_cycle = False


        # --- Styles des axes ---
        axs[0].set_xlabel("Voltage [V]", fontsize=label_size)
        axs[0].set_ylabel("Polarization (μC/cm²)", fontsize=label_size)
        axs[0].set_title("P–V loop")
        axs[0].grid(True, color='lightgray', linestyle='--', linewidth=0.5)
        axs[0].tick_params(axis='both', labelsize=label_size)

        axs[1].set_xlabel("Voltage [V]", fontsize=label_size)
        axs[1].set_ylabel("Current [A]", fontsize=label_size)
        axs[1].set_title("I–V loop")
        axs[1].grid(True, color='lightgray', linestyle='--', linewidth=0.5)
        axs[1].tick_params(axis='both', labelsize=label_size)


        # Légendes à droite de chaque subplot (sans doublons)
        for ax in axs:
            handles, labels = ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))

            ax.legend(
                handles=list(by_label.values()),
                labels=list(by_label.keys()),
                loc="center left",
                bbox_to_anchor=(1.02, 0.5),
                borderaxespad=0,
                fontsize=label_size - 2,
                title="Cycles",
            )

        fig.subplots_adjust(right=0.85, wspace=0.55)

    else:
        # --- Colormaps personnalisés autour de TES couleurs actuelles ---
        # P–V (à gauche) : vert/menthe ~ (0.35, 0.85, 0.65)
        # I–V (à droite) : bleu clair     (0.45, 0.75, 0.85)
        base_P = (0.35, 0.85, 0.65)
        base_I = (0.45, 0.75, 0.85)

        cmap_P = _truncate_cmap(cm.Greens,  minval=0.15, maxval=0.95)
        cmap_I = _truncate_cmap(cm.Purples,  minval=0.15, maxval=0.95)

        # --- Normalisation par numéro de cycle (linéaire; passe à LogNorm si tu veux) ---
        vmin = float(np.min(Cycles_total))
        vmax = float(np.max(Cycles_total))
        norm = mcolors.LogNorm(vmin=max(vmin, 1e-3), vmax=vmax)

        # --- Boucle sur les cycles ---
        for i, j in enumerate(Cycles_total):
            # 1) Récupère le DataFrame du cycle i
            df0 = PUND_dataframe[i]

            # 2) Si nombre de colonnes n'est pas multiple de 4, on retire la 1ʳᵉ (souvent un index importé)
            df_work = df0 if (df0.shape[1] % 4 == 0) else df0.iloc[:, 1:]

            # 3) Split en 5 pulses (ou n pulses) : renvoie une liste de DF avec colonnes ['Time','V','I','P']
            df_list = PUND_collumn_splitter(df_work)

            # 4) Couleurs par cycle (une couleur par axe, mappée via la valeur du cycle j)
            color_P = cmap_P(norm(j))
            color_I = cmap_I(norm(j))

            # 5) Alpha constant (lisible) ; label mis UNE seule fois par cycle
            alpha = 0.75
            label_for_cycle = f"Cycle {j}" if use_legend else None
            first_of_cycle = True

            # 6) Traçage des pulses pour ce cycle (plusieurs curves par cycle)
            for w in df_list:
                lbl = label_for_cycle if first_of_cycle else None
                axs[0].plot(w['V'], w['P'], color=color_P, alpha=alpha, label=lbl)
                first_of_cycle = False

            first_of_cycle = True
            for w in df_list:
                lbl = label_for_cycle if first_of_cycle else None
                axs[1].plot(w['V'], w['I'], color=color_I, alpha=alpha, label=lbl)
                first_of_cycle = False

        # --- Styles des axes ---
        axs[0].set_xlabel("Voltage [V]", fontsize=label_size)
        axs[0].set_ylabel("Polarization (μC/cm²)", fontsize=label_size)
        axs[0].set_title("P–V loop")
        axs[0].grid(True, color='lightgray', linestyle='--', linewidth=0.5)
        axs[0].tick_params(axis='both', labelsize=label_size)

        axs[1].set_xlabel("Voltage [V]", fontsize=label_size)
        axs[1].set_ylabel("Current [A]", fontsize=label_size)
        axs[1].set_title("I–V loop")
        axs[1].grid(True, color='lightgray', linestyle='--', linewidth=0.5)
        axs[1].tick_params(axis='both', labelsize=label_size)

        # Deux colorbars séparées (vert pour P–V, bleu pour I–V)
        sm_P = cm.ScalarMappable(cmap=cmap_P, norm=norm)
        sm_P.set_array([])

        sm_I = cm.ScalarMappable(cmap=cmap_I, norm=norm)
        sm_I.set_array([])

        cbar0 = fig.colorbar(sm_P, ax=axs[0], fraction=0.03, pad=0.04)
        cbar0.set_label('Cycle number', fontsize=label_size)

        cbar1 = fig.colorbar(sm_I, ax=axs[1], fraction=0.03, pad=0.04)
        cbar1.set_label('Cycle number', fontsize=label_size)

        fig.subplots_adjust(right=0.90, wspace=0.55)

    # --------- SAUVEGARDE UNIQUE ---------
    filename = f"{metadata_dict_PUND['Measurement_date_iso']}_{base_name}_PUND.png"
    plt.savefig(_safe_savepath(output_main_plot, filename), dpi=300, bbox_inches="tight")
    plt.show()
    plt.close("all")


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


# ------------------------------------
# ------------------------------------


def Plot_multi_DHM(DHM_dataframe, output_path_02, Cycles_total, label_size, base_name, metadata_dict_DHM):
    if metadata_dict_DHM.get("DHM_present", False) == False:
        return
    else:
        # Trouver le max global
        ymax = max(df['P1 [uC/cm2]'].abs().max() for df in DHM_dataframe)
        ymax = int(np.ceil(ymax / 5.0)) * 5

        output_plot = os.path.join(output_path_02, "DHM plot")
        output_video = os.path.join(output_path_02, "Video")
        os.makedirs(output_plot, exist_ok=True)  # Ensure output directory exists
        os.makedirs(output_video, exist_ok=True)  # Ensure output directory exists

        for i,j in zip(range(len(DHM_dataframe)), Cycles_total):
            
            df = DHM_dataframe[i]

            # Create the figure
            fig, axs = plt.subplots(1, 2, figsize=(14, 5))
            fig.suptitle(f"DHM - {base_name} - cycle {j}", fontsize=label_size + 2, fontweight="bold")
            

            axs[0].plot(df['V+ [V]'], df['P1 [uC/cm2]'], color=(0.25, 0.85, 0.55))
            axs[0].set_xlabel("Voltage [V]", fontsize = label_size)
            axs[0].set_ylabel("Polarization (μC/cm²)", fontsize = label_size)
            axs[0].set_ylim(-ymax, ymax)
            axs[0].set_title(f'Number of cycle {j}')
            axs[0].tick_params(axis='both', labelsize= label_size)
            axs[0].grid(True, color='lightgray', linestyle='--', linewidth=0.5)

            axs[1].plot(df['V+ [V]'], df['I1 [A]'], color=(0.35, 0.65, 0.85))
            axs[1].set_xlabel("Voltage [V]", fontsize = label_size)
            axs[1].set_ylabel("Current [A]", fontsize = label_size)
            axs[1].tick_params(axis='both', labelsize= label_size)
            axs[1].grid(True, color='lightgray', linestyle='--', linewidth=0.5)


            plt.savefig(os.path.join(output_plot, f"{base_name}_DHM_{i}_cycle_{j}.png"), dpi=300)

            plt.close()



def Plot_multi_CVM(CVM_dataframe, output_path_02, Cycles_total, label_size, base_name, metadata_dict_CVM):
    if metadata_dict_CVM.get("CVM_present", False) == False:
        return
    else:

        output_plot = os.path.join(output_path_02, "CVM plot")
        output_video = os.path.join(output_path_02, "Video")
        os.makedirs(output_plot, exist_ok=True)  # Ensure output directory exists
        os.makedirs(output_video, exist_ok=True)  # Ensure output directory exists

        for i,j in zip(range(len(CVM_dataframe)), Cycles_total):
            
            df = CVM_dataframe[i]

            # Create the figure
            fig, axs = plt.subplots(1, 2, figsize=(14, 5))
            fig.suptitle(f"CVM - {base_name} - cycle {j}", fontsize=label_size + 2, fontweight="bold")

            axs[0].plot(df['Bias [V]'], df['C [F]'], color=(0.25, 0.85, 0.55))
            axs[0].set_xlabel("Voltage [V]", fontsize = label_size)
            axs[0].set_ylabel("C [F]", fontsize = label_size)
            axs[0].set_title(f'Number of cycle {j}')
            axs[0].tick_params(axis='both', labelsize= label_size)
            axs[0].grid(True, color='lightgray', linestyle='--', linewidth=0.5)

            axs[1].plot(df['Bias [V]'], df['tan(delta) [1]'], color=(0.35, 0.65, 0.85))
            axs[1].set_xlabel("Voltage [V]", fontsize = label_size)
            axs[1].set_ylabel("tan(delta)", fontsize = label_size)
            axs[1].tick_params(axis='both', labelsize= label_size)
            axs[1].grid(True, color='lightgray', linestyle='--', linewidth=0.5)


            plt.savefig(os.path.join(output_plot, f"{base_name}_CVM_{i}_cycle_{j}.png"), dpi=300)

            plt.close()




def Plot_multi_PUND(PUND_dataframe, output_path_02, Cycles_total, label_size, base_name, metadata_dict_PUND):
    if metadata_dict_PUND.get("PUND_present", False) == False:
        return
    else:
        # Trouver le max global
        ymax = max(df['P [uC/cm2]'].abs().max() for df in PUND_dataframe)
        ymax = int(np.ceil(ymax / 5.0)) * 5

        colors = ["#000000", "#b82e50", "#3cb44b", "#0024a5", "#f58231"]  # X, U, N, D, P
        pulse_labels = [ 'X', 'U', 'N', 'D', 'P']

        output_plot = os.path.join(output_path_02, "PUND plot")
        output_video = os.path.join(output_path_02, "Video")
        os.makedirs(output_plot, exist_ok=True)  # Ensure output directory exists
        os.makedirs(output_video, exist_ok=True)  # Ensure output directory exists

        for i,j in zip(range(len(PUND_dataframe)), Cycles_total):

            fig, axs = plt.subplots(1, 2, figsize=(18, 6))
            fig.suptitle(f"PUND - {base_name} - cycle {j}", fontsize=label_size + 2, fontweight="bold")
            
            df_0 = PUND_dataframe[i]
            df_1 = df_0.iloc[:, 1:]   # Supprime la première colonne inutile
            df = PUND_collumn_splitter(df_1)

            for z, w in enumerate(df):

                label = pulse_labels[z] if z < len(pulse_labels) else f"Pulse {z}"
                axs[0].plot(w['V'], w['P'], color=colors[z % len(colors)], label=label)

            axs[0].set_xlabel("Voltage [V]", fontsize = label_size)
            axs[0].set_ylabel("Polarization (μC/cm²)", fontsize = label_size)
            axs[0].tick_params(axis='both', labelsize= label_size)
            axs[0].set_title(f'P-V loop')
            axs[0].grid(True, color='lightgray', linestyle='--', linewidth=0.5)


            for z, w in enumerate(df):

                label = pulse_labels[z] if z < len(pulse_labels) else f"Pulse {z}"
                axs[1].plot(w['V'], w['I'], color=colors[z % len(colors)], label=label)

            axs[1].set_xlabel("Voltage [V]", fontsize = label_size)
            axs[1].set_ylabel("Current [A]", fontsize = label_size)
            axs[1].tick_params(axis='both', labelsize= label_size)
            axs[1].set_title(f'I-V loop')
            axs[1].grid(True, color='lightgray', linestyle='--', linewidth=0.5)
            axs[1].legend()
            axs[1].legend(loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)


            plt.savefig(os.path.join(output_plot, f"{base_name}_PUND_{i}_cycle_{j}.png"), dpi=300)

            plt.close()