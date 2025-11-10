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

    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']  

    output_plot = os.path.join(output_path_02, "PUND plot")
    os.makedirs(output_plot, exist_ok=True)  # Ensure output directory exists

    for i in range(len(PUND_dataframe)):

        fig, axs = plt.subplots(1, 2, figsize=(18, 6))
        fig.suptitle(f"PUND - {base_name}", fontsize=label_size + 2, fontweight="bold")
        
        df_0 = PUND_dataframe[i]
        df = PUND_collumn_splitter(df_0)

        for z, w in enumerate(df): 
            axs[0].plot(w['V'], w['P'], color=colors[z % len(colors)])

        axs[0].set_xlabel("Voltage [V]", fontsize = label_size)
        axs[0].set_ylabel("Polarization (μC/cm²)", fontsize = label_size)
        axs[0].tick_params(axis='both', labelsize= label_size)
        axs[0].set_title(f'P-V loop')
        axs[0].grid(True, color='lightgray', linestyle='--', linewidth=0.5)    


        for z, w in enumerate(df):
            axs[1].plot(w['V'], w['I'], color=colors[z % len(colors)])

        axs[1].set_xlabel("Voltage [V]", fontsize = label_size)
        axs[1].set_ylabel("Current [A]", fontsize = label_size)
        axs[1].tick_params(axis='both', labelsize= label_size)
        axs[1].set_title(f'I-V loop')
        axs[1].grid(True, color='lightgray', linestyle='--', linewidth=0.5)


        info_text = f"{metadata_dict_PUND["SampleName"][i]}"\
                    f"{metadata_dict_PUND["Area_mm2"][i]}\n"\
                    f"{metadata_dict_PUND["Pund_Amplitude"][i]}"\
                    f"{metadata_dict_PUND["Pund_Frequency"][i]}"\
                    f"{metadata_dict_PUND["Write_Pulse_Amplitude"][i]}"\
                    f"{metadata_dict_PUND["Write_Pulse_Time"][i]}"\
                    f"{metadata_dict_PUND["Write_Pulse_Rise_Time"][i]}"\
                    f"{metadata_dict_PUND["Read_Pulse_Delay"][i]}"\
                    f"{metadata_dict_PUND["Write_Pulse_Delay"][i]}"\
                    f"Date: {metadata_dict_PUND["Measurement_date"][i]}"\

        # Add a text box with device info to the right of the plots
        fig.text(
            0.925,   # X position (shifted further to the right)
            0.5,    # Y position (0=bottom, 1=top)
            info_text,
            fontsize=13,
            va='center',
            bbox=dict(boxstyle="round", facecolor="whitesmoke", edgecolor="gray")
        )


        plt.savefig(os.path.join(output_plot, f"{base_name}_PUND_{i}.png"), dpi=300)
        plt.show()
        plt.close()

























