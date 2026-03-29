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



def Plot_multi_PUND(PUND_dataframe, output_path_02, label_size, base_name, metadata_dict_PUND):

    # Trouver le max global
    ymax = max(df['P [uC/cm2]'].abs().max() for df in PUND_dataframe)
    ymax = int(np.ceil(ymax / 5.0)) * 5

    colors = ["#000000", "#b82e50", "#3cb44b", "#0024a5", "#f58231"]  # X, U, N, D, P
    pulse_labels = [ 'X', 'U', 'N', 'D', 'P']

    output_plot = os.path.join(output_path_02, "PUND plot")
    os.makedirs(output_plot, exist_ok=True)  # Ensure output directory exists

    for i in range(len(PUND_dataframe)):

        fig, axs = plt.subplots(1, 3, figsize=(20, 6),
                                gridspec_kw={'width_ratios': [2, 2, 1]})
        fig.suptitle(f"PUND - {base_name}", fontsize=label_size + 2, fontweight="bold")

        df_0 = PUND_dataframe[i]
        df = PUND_collumn_splitter(df_0)

        for z, w in enumerate(df):
            label = pulse_labels[z] if z < len(pulse_labels) else f"Pulse {z}"
            axs[0].plot(w['V'], w['P'], color=colors[z % len(colors)], label=label)

        axs[0].set_xlabel("Voltage [V]", fontsize=label_size)
        axs[0].set_ylabel("Polarization (μC/cm²)", fontsize=label_size)
        axs[0].tick_params(axis='both', labelsize=label_size)
        axs[0].set_title('P-V loop')
        axs[0].grid(True, color='lightgray', linestyle='--', linewidth=0.5)
        axs[0].legend(fontsize=label_size - 2)

        for z, w in enumerate(df):
            label = pulse_labels[z] if z < len(pulse_labels) else f"Pulse {z}"
            axs[1].plot(w['V'], w['I'], color=colors[z % len(colors)], label=label)

        axs[1].set_xlabel("Voltage [V]", fontsize=label_size)
        axs[1].set_ylabel("Current [A]", fontsize=label_size)
        axs[1].tick_params(axis='both', labelsize=label_size)
        axs[1].set_title('I-V loop')
        axs[1].grid(True, color='lightgray', linestyle='--', linewidth=0.5)
        axs[1].legend(fontsize=label_size - 2)

        # --- Metadata dashboard panel ---
        ax_meta = axs[2]
        ax_meta.axis('off')

        meta_rows = [
            ("Sample",        str(metadata_dict_PUND["SampleName"][i]).split(":")[-1].strip().rstrip("\n")),
            ("Area [mm²]",    str(metadata_dict_PUND["Area_mm2"][i]).split(":")[-1].strip().rstrip("\n")),
            ("",              ""),
            ("PUND amplitude [V]",      str(metadata_dict_PUND["Pund_Amplitude"][i]).split(":")[-1].strip().rstrip("\n")),
            ("PUND frequency [Hz]",     str(metadata_dict_PUND["Pund_Frequency"][i]).split(":")[-1].strip().rstrip("\n")),
            ("",              ""),
            ("Write amplitude [V]",     str(metadata_dict_PUND["Write_Pulse_Amplitude"][i]).split(":")[-1].strip().rstrip("\n")),
            ("Write time [s]",          str(metadata_dict_PUND["Write_Pulse_Time"][i]).split(":")[-1].strip().rstrip("\n")),
            ("Write rise time [s]",     str(metadata_dict_PUND["Write_Pulse_Rise_Time"][i]).split(":")[-1].strip().rstrip("\n")),
            ("Write delay [s]",         str(metadata_dict_PUND["Write_Pulse_Delay"][i]).split(":")[-1].strip().rstrip("\n")),
            ("Read delay [s]",          str(metadata_dict_PUND["Read_Pulse_Delay"][i]).split(":")[-1].strip().rstrip("\n")),
            ("",              ""),
            ("Date",          str(metadata_dict_PUND["Measurement_date"][i]).strip()),
        ]

        y_start = 0.95
        line_h = 0.07
        ax_meta.set_xlim(0, 1)
        ax_meta.set_ylim(0, 1)

        for key, val in meta_rows:
            if key == "":
                y_start -= line_h * 0.4
                continue
            ax_meta.text(0.05, y_start, key, fontsize=11, va='top',
                         fontweight='bold', transform=ax_meta.transAxes)
            ax_meta.text(0.95, y_start, val, fontsize=11, va='top',
                         ha='right', transform=ax_meta.transAxes)
            y_start -= line_h

        # Light box around the metadata panel
        for spine in ax_meta.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor('lightgray')

        plt.tight_layout()
        plt.savefig(os.path.join(output_plot, f"{base_name}_PUND_{i}.png"), dpi=300)
        plt.show()
        plt.close()

























