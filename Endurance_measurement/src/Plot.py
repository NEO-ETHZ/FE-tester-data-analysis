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

def folder_main_plot(output_path):
        output_main_plot = os.path.join(output_path, "Main plot")
        os.makedirs(output_main_plot, exist_ok=True)  # Ensure output directory exists
        # Save figure (bbox_inches='tight' ensures everything fits inside)

def main_plot(df_fatigue_DHM, df_fatigue_CVM, df_fatigue_PUND, metadata_dict_DHM, metadata_dict_CVM, metadata_dict_PUND, metadata_str_DHM, metadata_str_CVM, metadata_str_PUND, output_path, base_name, labelsize):
    import os
    import pandas as pd
    import matplotlib.pyplot as plt

    label_size = labelsize

    if metadata_dict_DHM.get("DHM_present", False):
        # Create the figure
        fig, axs = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle("DHM measurement", fontsize=label_size + 2, fontweight="bold")

        # Plot DHM fatigue data

        axs[0,0].plot(df_fatigue_DHM["Cycles [n]"], df_fatigue_DHM["1-DHM Pr+ [uC/cm2]"], color=(0.25, 0.55, 0.85),marker='o', label ='Pr+')
        axs[0,0].plot(df_fatigue_DHM["Cycles [n]"], abs(df_fatigue_DHM["1-DHM Pr- [uC/cm2]"]), color=(0.25, 0.85, 0.55),marker='o', label ='Pr-')
        axs[0,0].set_xlabel("Cycles [n]", fontsize = label_size)
        axs[0,0].set_ylabel("Pr (μC/cm²)", fontsize = label_size)
        axs[0,0].set_xscale('log')
        axs[0,0].set_title(f"Pr")
        axs[0,0].legend()
        axs[0,0].tick_params(axis='both', labelsize= label_size)

        ax1 = axs[0, 1]
        ax2 = ax1.twinx()  # Second y-axis on the same subplot
        ax1.plot(df_fatigue_DHM["Cycles [n]"], df_fatigue_DHM["1-DHM Ipk+ [A]"]/metadata_dict_DHM["Device_area_um2"], label=f'Jpk +', color=(0.85, 0.55, 0.25), marker='o')
        ax2.plot(df_fatigue_DHM["Cycles [n]"], df_fatigue_DHM["1-DHM Ipk- [A]"]/metadata_dict_DHM["Device_area_um2"], label=f'Jpk -', color=(0.55, 0.25, 0.85), marker='o')
        axs[0,1].set_title("Peak current density Jpk")
        axs[0,1].set_xscale('log')
        axs[0,1].set_xlabel("Cycles [n]", fontsize = label_size)
        ax1.set_ylabel("Jpk + [A/μm²]", color = (0.85, 0.55, 0.25), fontsize = label_size)
        ax2.set_ylabel("Jpk - [A/μm²]", color = (0.55, 0.25, 0.85), fontsize = label_size)
        ax1.tick_params(axis='both', labelsize=label_size)
        ax2.tick_params(axis='both', labelsize=label_size)

        axs[1,0].plot(df_fatigue_DHM["Cycles [n]"], df_fatigue_DHM["1-DHM Vc+ [V]"], color=(0.25, 0.55, 0.85),marker='o', label ='Vc+')
        axs[1,0].plot(df_fatigue_DHM["Cycles [n]"], abs(df_fatigue_DHM["1-DHM Vc- [V]"]), color=(0.25, 0.85, 0.55),marker='o', label ='Vc-')
        axs[1,0].set_xlabel("Cycles [n]", fontsize = label_size)
        axs[1,0].set_ylabel("Vc (V)", fontsize = label_size)
        axs[1,0].set_xscale('log')
        axs[1,0].set_title("Vc")
        axs[1,0].legend()
        axs[1,0].tick_params(axis='both', labelsize=label_size)

        axs[1,1].plot(df_fatigue_DHM["Cycles [n]"], df_fatigue_DHM["1-DHM Wloss [uJ/cm2]"], label=f'Cycle ', color=(0.85, 0.55, 0.25), marker='o')
        axs[1,1].set_xlabel("Cycles [n]", fontsize = label_size)
        axs[1,1].set_ylabel("Wloss (μJ/cm²)", fontsize = label_size)
        axs[1,1].set_xscale('log')
        axs[1,1].set_title("W loss")
        axs[1,1].tick_params(axis='both', labelsize=label_size)


        info_text = metadata_str_DHM

        # Add a text box with device info to the right of the plots
        fig.text(
            0.85,   # X position (shifted further to the right)
            0.5,    # Y position (0=bottom, 1=top)
            info_text,
            fontsize=13,
            va='center',
            bbox=dict(boxstyle="round", facecolor="whitesmoke", edgecolor="gray")
        )

        # Adjust layout to leave more room for the text box
        plt.subplots_adjust(
        left=0.07,    # marge gauche
        right=0.78,   # marge droite (tu l’as déjà à 0.8)
        top=0.92,     # marge supérieure
        bottom=0.08,  # marge inférieure
        wspace=0.3,  # 🔥 espace horizontal entre les colonnes
        hspace=0.25    # 🔥 espace vertical entre les lignes
        )
        

        output_main_plot = os.path.join(output_path, "Main plot")
        os.makedirs(output_main_plot, exist_ok=True)  # Ensure output directory exists
        # Save figure (bbox_inches='tight' ensures everything fits inside)

        plt.savefig(
            os.path.join(output_main_plot, f"{metadata_dict_DHM["Measurement_date_iso"]}_{base_name}_Fatigue-DHM_Main_Plot.png"),
            dpi=300,
            bbox_inches='tight'
        )

        plt.show()
        plt.close(fig)  # Close figure to free memory
    

    # ----------- CVM MEASUREMENT -----------

    if metadata_dict_CVM.get("CVM_present", False):
        # Create the figure
        fig, axs = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle("CV measurement", fontsize=label_size + 2, fontweight="bold")

        # Plot CVM fatigue data

        ax1 = axs[0, 0]
        ax2 = ax1.twinx()  # Second y-axis on the same subplot
        ax1.plot(df_fatigue_CVM["Cycles [n]"], df_fatigue_CVM["2-CVM Cav [F]"]/metadata_dict_CVM["Device_area_um2"], label=f'Cav', color=(0.85, 0.55, 0.25), marker='o')
        ax2.plot(df_fatigue_CVM["Cycles [n]"], df_fatigue_CVM["2-CVM Rav [Ohm]"]/metadata_dict_CVM["Device_area_um2"], label=f'Rav -', color=(0.55, 0.25, 0.85), marker='o')
        axs[0,0].set_title("Capacitance and resistance average")
        axs[0,0].set_xscale('log')
        axs[0,0].set_xlabel("Cycles [n]", fontsize = label_size)
        ax1.set_ylabel("Cav - [F]", color = (0.85, 0.55, 0.25), fontsize = label_size)
        ax2.set_ylabel("Rav - [Ohm]", color = (0.55, 0.25, 0.85), fontsize = label_size)
        ax1.tick_params(axis='both', labelsize=label_size)
        ax2.tick_params(axis='both', labelsize=label_size)
        ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        ax2.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

        ax1 = axs[0, 1]
        ax2 = ax1.twinx()  # Second y-axis on the same subplot
        ax1.plot(df_fatigue_CVM["Cycles [n]"], df_fatigue_CVM["2-CVM TanDmax [1]"]/metadata_dict_CVM["Device_area_um2"], label=f'Tan(TanDmax)', color=(0.85, 0.55, 0.25), marker='o')
        ax2.plot(df_fatigue_CVM["Cycles [n]"], df_fatigue_CVM["2-CVM TanDav [1]"]/metadata_dict_CVM["Device_area_um2"], label=f'TanDav', color=(0.55, 0.25, 0.85), marker='o')
        axs[0,1].set_title("Tan(delta) max and average")
        axs[0,1].set_xscale('log')
        axs[0,1].set_xlabel("Cycles [n]", fontsize = label_size)
        ax1.set_ylabel("Tan(delta)max", color = (0.85, 0.55, 0.25), fontsize = label_size)
        ax2.set_ylabel("Tan(delta)av", color = (0.55, 0.25, 0.85), fontsize = label_size)
        ax1.tick_params(axis='both', labelsize=label_size)
        ax2.tick_params(axis='both', labelsize=label_size)
        ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        ax2.ticklabel_format(style='sci', axis='y', scilimits=(0,0))


        axs[1,0].plot(df_fatigue_CVM["Cycles [n]"], df_fatigue_CVM["2-CVM Cpk+ [F]"], color=(0.25, 0.55, 0.85),marker='o', label ='Cpk+')
        axs[1,0].plot(df_fatigue_CVM["Cycles [n]"], abs(df_fatigue_CVM["2-CVM Cpk- [F]"]), color=(0.25, 0.85, 0.55),marker='o', label ='Cpk-')
        axs[1,0].set_xlabel("Cycles [n]", fontsize = label_size)
        axs[1,0].set_ylabel("Cpk [F]", fontsize = label_size)
        axs[1,0].set_xscale('log')
        axs[1,0].set_title("Capacitance peak")
        axs[1,0].legend()
        axs[1,0].tick_params(axis='both', labelsize=label_size)

        axs[1,1].plot(df_fatigue_CVM["Cycles [n]"], df_fatigue_CVM["2-CVM EpsAv [1]"], label=f'Eps_av', color=(0.85, 0.55, 0.25), marker='o')
        axs[1,1].set_xlabel("Cycles [n]", fontsize = label_size)
        axs[1,1].set_ylabel("Eps_av", fontsize = label_size)
        axs[1,1].set_xscale('log')
        axs[1,1].set_title("Electrical permittivity average")
        axs[1,1].tick_params(axis='both', labelsize=label_size)


        info_text = metadata_str_CVM

        # Add a text box with device info to the right of the plots
        fig.text(
            0.85,   # X position (shifted further to the right)
            0.5,    # Y position (0=bottom, 1=top)
            info_text,
            fontsize=13,
            va='center',
            bbox=dict(boxstyle="round", facecolor="whitesmoke", edgecolor="gray")
        )

        # Adjust layout to leave more room for the text box
        plt.subplots_adjust(
        left=0.07,    # marge gauche
        right=0.78,   # marge droite (tu l’as déjà à 0.8)
        top=0.92,     # marge supérieure
        bottom=0.08,  # marge inférieure
        wspace=0.3,  # 🔥 espace horizontal entre les colonnes
        hspace=0.25    # 🔥 espace vertical entre les lignes
        )

        output_main_plot = os.path.join(output_path, "Main plot")
        os.makedirs(output_main_plot, exist_ok=True)  # Ensure output directory exists
        # Save figure (bbox_inches='tight' ensures everything fits inside)

        plt.savefig(
            os.path.join(output_main_plot, f"{metadata_dict_DHM["Measurement_date_iso"]}_{base_name}_Fatigue_CVM_Main_Plot.png"),
            dpi=300,
            bbox_inches='tight'
        )

        plt.show()
        plt.close(fig)  # Close figure to free memory


    # ----------- PUND MEASUREMENT -----------

    if metadata_dict_PUND.get("PUND_present", False):
        # Create the figure
        fig, axs = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle("PUND measurement", fontsize=label_size + 2, fontweight="bold")

        # Plot DHM fatigue data

        axs[0,0].plot(df_fatigue_PUND["Cycles [n]"], df_fatigue_PUND["3-PM Pr+ [uC/cm2]"], color=(0.25, 0.55, 0.85),marker='o', label ='Pr+')
        axs[0,0].plot(df_fatigue_PUND["Cycles [n]"], abs(df_fatigue_PUND["3-PM Pr- [uC/cm2]"]), color=(0.25, 0.85, 0.55),marker='o', label ='Pr-')
        axs[0,0].set_xlabel("Cycles [n]", fontsize = label_size)
        axs[0,0].set_ylabel("Pr (μC/cm²)", fontsize = label_size)
        axs[0,0].set_xscale('log')
        axs[0,0].set_title(f"Pr")
        axs[0,0].legend()
        axs[0,0].tick_params(axis='both', labelsize= label_size)

        ax1 = axs[0, 1]
        ax2 = ax1.twinx()  # Second y-axis on the same subplot
        ax1.plot(df_fatigue_PUND["Cycles [n]"], df_fatigue_PUND["3-PM Ipk+ [A]"]/metadata_dict_DHM["Device_area_um2"], label=f'Jpk +', color=(0.85, 0.55, 0.25), marker='o')
        ax2.plot(df_fatigue_PUND["Cycles [n]"], df_fatigue_PUND["3-PM Ipk- [A]"]/metadata_dict_DHM["Device_area_um2"], label=f'Jpk -', color=(0.55, 0.25, 0.85), marker='o')
        axs[0,1].set_title("Peak current density Jpk")
        axs[0,1].set_xscale('log')
        axs[0,1].set_xlabel("Cycles [n]", fontsize = label_size)
        ax1.set_ylabel("Jpk + [A/μm²]", color = (0.85, 0.55, 0.25), fontsize = label_size)
        ax2.set_ylabel("Jpk - [A/μm²]", color = (0.55, 0.25, 0.85), fontsize = label_size)
        ax1.tick_params(axis='both', labelsize=label_size)
        ax2.tick_params(axis='both', labelsize=label_size)

        axs[1,0].plot(df_fatigue_PUND["Cycles [n]"], df_fatigue_PUND["3-PM Vc+ [V]"], color=(0.25, 0.55, 0.85),marker='o', label ='Vc+')
        axs[1,0].plot(df_fatigue_PUND["Cycles [n]"], abs(df_fatigue_PUND["3-PM Vc- [V]"]), color=(0.25, 0.85, 0.55),marker='o', label ='Vc-')
        axs[1,0].set_xlabel("Cycles [n]", fontsize = label_size)
        axs[1,0].set_ylabel("Vc (V)", fontsize = label_size)
        axs[1,0].set_xscale('log')
        axs[1,0].set_title("Vc")
        axs[1,0].legend()
        axs[1,0].tick_params(axis='both', labelsize=label_size)

        axs[1,1].plot(df_fatigue_PUND["Cycles [n]"], df_fatigue_PUND["3-PM Psw [uC/cm2]"], label=f'Cycle ', color=(0.85, 0.55, 0.25), marker='o')
        axs[1,1].set_xlabel("Cycles [n]", fontsize = label_size)
        axs[1,1].set_ylabel("Psw [uC/cm2]", fontsize = label_size)
        axs[1,1].set_xscale('log')
        axs[1,1].set_title("Switching polarization Psw")
        axs[1,1].tick_params(axis='both', labelsize=label_size)


        info_text = metadata_str_PUND

        # Add a text box with device info to the right of the plots
        fig.text(
            0.85,   # X position (shifted further to the right)
            0.5,    # Y position (0=bottom, 1=top)
            info_text,
            fontsize=13,
            va='center',
            bbox=dict(boxstyle="round", facecolor="whitesmoke", edgecolor="gray")
        )

        # Adjust layout to leave more room for the text box
        plt.subplots_adjust(
        left=0.07,    # marge gauche
        right=0.78,   # marge droite (tu l’as déjà à 0.8)
        top=0.92,     # marge supérieure
        bottom=0.08,  # marge inférieure
        wspace=0.3,  # 🔥 espace horizontal entre les colonnes
        hspace=0.25    # 🔥 espace vertical entre les lignes
        )
        
        output_main_plot = os.path.join(output_path, "Main plot")
        os.makedirs(output_main_plot, exist_ok=True)  # Ensure output directory exists
        # Save figure (bbox_inches='tight' ensures everything fits inside)

        plt.savefig(
            os.path.join(output_main_plot, f"{metadata_dict_PUND["Measurement_date_iso"]}_{base_name}_Fatigue_PUND_Main_Plot.png"),
            dpi=300,
            bbox_inches='tight'
        )

        plt.show()
        plt.close(fig)  # Close figure to free memory


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
    Cycles_total = Cycles_total[:-Removal]

    legend_threshold = 15
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
    plt.savefig(os.path.join(output_main_plot, filename), dpi=300, bbox_inches="tight")
    plt.show()
    plt.close("all")



def Plot_single_CVM(CVM_dataframe, Cycles_total, label_size, output_main_plot, base_name, metadata_dict_CVM):
    if not metadata_dict_CVM.get("CVM_present", False):
        return

    #To remove the breakdown point
    Removal = len(Cycles_total) - len(CVM_dataframe)
    Cycles_total = Cycles_total[:-Removal]

    legend_threshold = 15
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
    plt.savefig(os.path.join(output_main_plot, filename), dpi=300, bbox_inches="tight")
    plt.show()
    plt.close("all")


# ------------------------------------------------------------------------------

def Plot_single_PUND(PUND_dataframe, Cycles_total, label_size, output_main_plot, base_name, metadata_dict_PUND):
    if not metadata_dict_PUND.get("PUND_present", False):
        return

    #To remove the breakdown point
    Removal = len(Cycles_total) - len(PUND_dataframe)
    Cycles_total = Cycles_total[:-Removal]

    legend_threshold = 15
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
    plt.savefig(os.path.join(output_main_plot, filename), dpi=300, bbox_inches="tight")
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

        colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']  

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

                label = f'Cycle {j}' 
                axs[0].plot(w['V'], w['P'], color=colors[z % len(colors)])

            axs[0].set_xlabel("Voltage [V]", fontsize = label_size)
            axs[0].set_ylabel("Polarization (μC/cm²)", fontsize = label_size)
            axs[0].tick_params(axis='both', labelsize= label_size)
            axs[0].set_title(f'P-V loop')
            axs[0].grid(True, color='lightgray', linestyle='--', linewidth=0.5)
            axs[0].legend()
            axs[0].legend(loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)     # Légendes en dehors des graphes


            for z, w in enumerate(df):

                label = f'Cycle {j}' 
                axs[1].plot(w['V'], w['I'], color=colors[z % len(colors)])

            axs[1].set_xlabel("Voltage [V]", fontsize = label_size)
            axs[1].set_ylabel("Current [A]", fontsize = label_size)
            axs[1].tick_params(axis='both', labelsize= label_size)
            axs[1].set_title(f'I-V loop')
            axs[1].grid(True, color='lightgray', linestyle='--', linewidth=0.5)
            axs[1].legend()
            axs[1].legend(loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)


            plt.savefig(os.path.join(output_plot, f"{base_name}_PUND_{i}_cycle_{j}.png"), dpi=300)

            plt.close()