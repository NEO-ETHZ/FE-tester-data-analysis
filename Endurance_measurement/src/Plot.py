import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os
import json
# from matplotlib import colormaps
import re
import io
from datetime import datetime


def main_plot(df_fatigue_DHM, df_fatigue_CVM, df_fatigue_PUND, metadata_dict_DHM, metadata_dict_CVM, metadata_dict_PUND, metadata_str_DHM, metadata_str_CVM, metadata_str_PUND, output_path, base_name, labelsize):
    import os
    import pandas as pd
    import matplotlib.pyplot as plt

    label_size = labelsize

    if metadata_dict_DHM.get("DHM_present", False):
        # Create the figure
        fig, axs = plt.subplots(2, 2, figsize=(16, 10))

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
        
        output_path_02 = os.path.join(output_path, base_name)
        os.makedirs(output_path_02, exist_ok=True)  # Ensure output directory exists
        output_main_plot = os.path.join(output_path_02, "Main plot")
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

        
        output_path_02 = os.path.join(output_path, base_name)
        os.makedirs(output_path_02, exist_ok=True)  # Ensure output directory exists
        output_main_plot = os.path.join(output_path_02, "Main plot")
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
        
        output_path_02 = os.path.join(output_path, base_name)
        os.makedirs(output_path_02, exist_ok=True)  # Ensure output directory exists
        output_main_plot = os.path.join(output_path_02, "Main plot")
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


def Plot_single_DHM(DHM_dataframe, Cycles_total, label_size, output_main_plot, base_name, metadata_dict_DHM):
    # Création du colormap (dégradé de bleu clair à bleu foncé)
    cmap = plt.cm.Blues
    colors = [cmap(i / (len(DHM_dataframe)-1)) for i in range(len(DHM_dataframe))]


    # Create the figure
    fig, axs = plt.subplots(1, 2, figsize=(18, 6))

    for i,j in zip(range(len(DHM_dataframe)), Cycles_total):
        
        df = DHM_dataframe[i]
        alpha = 0.3 + 0.7 * (i / (len(DHM_dataframe)-1))   # alpha de 0.3 → 1.0

        axs[0].plot(df['V+ [V]'], df['P1 [uC/cm2]'], color=(0.25, 0.85, 0.55), alpha=alpha, label=f'Cycle {j}')
        axs[0].set_xlabel("Voltage [V]", fontsize = label_size)
        axs[0].set_ylabel("Polarization (μC/cm²)", fontsize = label_size)
        axs[0].tick_params(axis='both', labelsize= label_size)
        axs[0].set_title(f'P-V loop')
        axs[0].grid(True, color='lightgray', linestyle='--', linewidth=0.5)
        axs[0].legend()
        axs[0].legend(loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)     # Légendes en dehors des graphes

        axs[1].plot(df['V+ [V]'], df['I1 [A]'], color=(0.35, 0.65, 0.85), alpha=alpha, label=f'Cycle {j}')
        axs[1].set_xlabel("Voltage [V]", fontsize = label_size)
        axs[1].set_ylabel("Current [A]", fontsize = label_size)
        axs[1].tick_params(axis='both', labelsize= label_size)
        axs[1].set_title(f'I-V loop')
        axs[1].grid(True, color='lightgray', linestyle='--', linewidth=0.5)
        axs[1].legend()
        axs[1].legend(loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)

    # Ajustement pour laisser de la place à droite
    fig.subplots_adjust(right=0.9, wspace=0.55)
    plt.savefig(os.path.join(output_main_plot, f"{metadata_dict_DHM["Measurement_date_iso"]}_{base_name}_DHM.png"), dpi=300)
    plt.show()
    plt.close()




# ------------------------------------
# ------------------------------------


def Plot_multi_DHM(DHM_dataframe, output_path_02, Cycles_total, label_size, base_name):

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

        plt.show()
        plt.close()



