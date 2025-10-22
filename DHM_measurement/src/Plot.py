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



def DHM_plot(DHM_dataframe, metadata_df, label_size, color_PV, color_IV):


    for i in range(len(DHM_dataframe)):
        # Create the figure
        fig, axs = plt.subplots(1, 2, figsize=(18, 6))
        df = DHM_dataframe[i]

        axs[0].plot(df['V+ [V]'], df['P1 [uC/cm2]'], color=color_PV)
        axs[0].set_xlabel("Voltage [V]", fontsize = label_size)
        axs[0].set_ylabel("Polarization (μC/cm²)", fontsize = label_size)
        axs[0].tick_params(axis='both', labelsize= label_size)
        axs[0].set_title(f'P-V loop')
        axs[0].grid(True, color='lightgray', linestyle='--', linewidth=0.5)

        axs[1].plot(df['V+ [V]'], df['I1 [A]'], color=color_IV)
        axs[1].set_xlabel("Voltage [V]", fontsize = label_size)
        axs[1].set_ylabel("Current [A]", fontsize = label_size)
        axs[1].tick_params(axis='both', labelsize= label_size)
        axs[1].set_title(f'I-V loop')
        axs[1].grid(True, color='lightgray', linestyle='--', linewidth=0.5)

        info_text = f"{metadata_df["SampleName"][i]}"\
                    f"{metadata_df["Area_mm2"][i]}\n"\
                    f"{metadata_df["Hysteresis_Amplitude_V"][i]}"\
                    f"{metadata_df["Hysteresis_Frequence_Hz"][i]}"\
                    f"Date: {metadata_df["Measurement_date"][i]}"\



        # Add a text box with device info to the right of the plots
        fig.text(
            0.925,   # X position (shifted further to the right)
            0.5,    # Y position (0=bottom, 1=top)
            info_text,
            fontsize=13,
            va='center',
            bbox=dict(boxstyle="round", facecolor="whitesmoke", edgecolor="gray")
        )

        plt.show()
        plt.close()




