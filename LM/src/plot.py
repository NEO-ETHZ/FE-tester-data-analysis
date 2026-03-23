import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os
# from matplotlib import colormaps
import re
from datetime import datetime
from matplotlib.ticker import AutoMinorLocator
import matplotlib.gridspec as gridspec


"""  
  metadata = {
        "SampleName": SampleName,
        "Area_mm2": Area_mm2,
        "Step_duration": Step_duration,
        "Voltage_step": Voltage_step,
        "Current_range" : Current_range,
        "Measurement_date": Measurement_date
    }
"""

def LM_dashboard(
        LM_dataframe: list[pd.DataFrame],
        metadata_df: pd.DataFrame,
        output_path: str = "",
        base_name: str = "",
        label_size: int = 15,
        tick_size: int = 15,
        color_LM: str = "#282828"
):
    output_path = os.path.join(output_path, "LM_dashboard")
    os.makedirs(output_path, exist_ok=True)

    for i in range(len(LM_dataframe)):
        df = LM_dataframe[i]

        J = np.asarray(df["Leakage Current Density [uA/cm2]"], dtype=float)
        V = np.asarray(df["Voltage [V]"], dtype=float)

        raw_area = metadata_df.loc[i, "Area_mm2"]
        match = re.search(r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)", str(raw_area))
        if match is None:
            raise ValueError(f"Cannot extract area from: {raw_area}")

        area_mm2 = float(match.group(1))
        area_cm2 = area_mm2 * 1e-2

        # ─────────────────────────────────────────────────────────────
        # Layout with GridSpec
        # ─────────────────────────────────────────────────────────────
        fig = plt.figure(figsize=(14, 8))
        gs = gridspec.GridSpec(2, 2, height_ratios=[1, 0.4])

        ax_lin = fig.add_subplot(gs[0, 0])
        ax_log = fig.add_subplot(gs[0, 1])
        ax_text = fig.add_subplot(gs[1, :])

        # ─────────────────────────────────────────────────────────────
        # Linear plot
        # ─────────────────────────────────────────────────────────────
        ax_lin.plot(V, J, color=color_LM)
        ax_lin.set_title("Leakage (linear)", fontsize=label_size)
        ax_lin.set_xlabel("Voltage [V]", fontsize=label_size)
        ax_lin.set_ylabel("Leakage current density [µA/cm²]", fontsize=label_size)

        ax_lin2 = ax_lin.twinx()
        y1_min, y1_max = ax_lin.get_ylim()
        ax_lin2.set_ylim(y1_min * 1e-6 * area_cm2, y1_max * 1e-6 * area_cm2)
        ax_lin2.set_ylabel("Current [A]", fontsize=label_size)

        # ─────────────────────────────────────────────────────────────
        # Log-Y plot (same V, masked J)
        # ─────────────────────────────────────────────────────────────
        J_log = abs(J)

        ax_log.plot(V, J_log, color=color_LM)
        ax_log.set_title("Leakage (log Y)", fontsize=label_size)
        ax_log.set_xlabel("Voltage [V]", fontsize=label_size)
        ax_log.set_ylabel("Leakage current density [µA/cm²]", fontsize=label_size)
        ax_log.set_yscale("log")

        ax_log2 = ax_log.twinx()
        ax_log2.set_yscale("log")
        y1_min, y1_max = ax_log.get_ylim()
        ax_log2.set_ylim(y1_min * 1e-6 * area_cm2, y1_max * 1e-6 * area_cm2)
        ax_log2.set_ylabel("Current [A]", fontsize=label_size)

        # ─────────────────────────────────────────────────────────────
        # Styling (Laura)
        # ─────────────────────────────────────────────────────────────
        def style_axis(ax):
            ax.tick_params(
                axis="both",
                which="both",
                direction="in",
                top=True,
                right=True,
                labelsize=tick_size,
                length=6,
                width=1.2
            )
            ax.xaxis.set_minor_locator(AutoMinorLocator(5))
            ax.grid(True, which="major", linestyle="-", linewidth=0.8, alpha=0.35)
            ax.grid(True, which="minor", linestyle=":", linewidth=0.6, alpha=0.25)

        style_axis(ax_lin)
        style_axis(ax_log)

        ax_lin2.tick_params(axis="y", which="both", direction="in", labelsize=tick_size, length=6, width=1.2)
        ax_log2.tick_params(axis="y", which="both", direction="in", labelsize=tick_size, length=6, width=1.2)

        # ─────────────────────────────────────────────────────────────
        # Text row (no box, just text)
        # ─────────────────────────────────────────────────────────────
        ax_text.axis("off")

        sample_name = metadata_df.loc[i, "SampleName"] if "SampleName" in metadata_df.columns else ""
        step_dur = metadata_df.loc[i, "Step_duration"] if "Step_duration" in metadata_df.columns else ""
        v_step = metadata_df.loc[i, "Voltage_step"] if "Voltage_step" in metadata_df.columns else ""
        i_range = metadata_df.loc[i, "Current_range"] if "Current_range" in metadata_df.columns else ""
        meas_date = metadata_df.loc[i, "Measurement_date"] if "Measurement_date" in metadata_df.columns else ""

        text = (
            f"{sample_name}"
            f"Area: {area_mm2:.4g} mm²\n"
            f"{v_step}"
            f"{step_dur}"
            f"{i_range}\n"
            f"Date: {meas_date}"
        )

        ax_text.text(
            0.01, 0.5,
            text,
            fontsize=13,
            va="center",
            ha="left",
            color="black"
        )

        fig.tight_layout()
        fname = f"{base_name}_{i}.png" if base_name else f"LM_dashboard_{i}.png"
        fig.savefig(os.path.join(output_path, fname), dpi=300, bbox_inches="tight")
        plt.show()
        plt.close(fig)



def LM_plot_linear(
        LM_dataframe: list[pd.DataFrame] | pd.DataFrame,
        metadata_df: pd.DataFrame,
        output_path: str = "",
        base_name: str = "",
        label_size: int = 15,
        tick_size: int = 15,
        color_LM: str = "#282828",
        figsize: tuple[int, int] = (9, 6),
        save: bool = True,
        show: bool = True,
):

    # Output folder
    output_dir = os.path.join(output_path, "LM_plots")
    os.makedirs(output_dir, exist_ok=True)


    # Loop over each measurement
    for i, df in enumerate(LM_dataframe):

        V = np.asarray(df["Voltage [V]"], dtype=float)
        J = np.asarray(df["Leakage Current Density [uA/cm2]"], dtype=float)


        raw_area = metadata_df.loc[i, "Area_mm2"]
        match = re.search(r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)", str(raw_area))
        if match is None:
            raise ValueError(f"Cannot extract area from: {raw_area}")

        area_mm2 = float(match.group(1))
        area_cm2 = area_mm2 * 1e-2

        # ─────────────────────────────────────────────────────────────
        # Figure
        # ─────────────────────────────────────────────────────────────
        fig, ax1 = plt.subplots(figsize=figsize)

        ax1.plot(V, J, color=color_LM, marker = "o", markersize = 2.5)
        ax1.set_xlabel("Voltage [V]", fontsize=label_size)
        ax1.set_ylabel("Leakage current density [µA/cm²]", fontsize=label_size)
        ax1.set_title(f"{base_name} - Leakage", fontsize=label_size)

        # Secondary y-axis (Current)
        ax2 = ax1.twinx()

        y1_min, y1_max = ax1.get_ylim()
        ax2.set_ylim(
            y1_min * 1e-6 * area_cm2,
            y1_max * 1e-6 * area_cm2,
        )
        ax2.set_ylabel("Current [A]", fontsize=label_size)
        

        # ─────────────────────────────────────────────────────────────
        # Styling (Laura-friendly)
        # ─────────────────────────────────────────────────────────────
        ax1.tick_params(
            axis="both",
            which="both",
            direction="in",
            top=True,
            right=True,
            labelsize=tick_size,
            length=6,
            width=1.2,
        )
        ax2.tick_params(
            axis="y",
            which="both",
            direction="in",
            labelsize=tick_size,
            length=6,
            width=1.2,
        )

        ax1.xaxis.set_minor_locator(AutoMinorLocator(5))
        ax1.grid(True, which="major", linestyle="-", linewidth=0.8, alpha=0.35)
        ax1.grid(True, which="minor", linestyle=":", linewidth=0.6, alpha=0.25)

        # ─────────────────────────────────────────────────────────────
        # Save / show / close
        # ─────────────────────────────────────────────────────────────
        if save:
            fname = f"{base_name}_{i}_linear.png" 
            fig.savefig(os.path.join(output_dir, fname), dpi=300, bbox_inches="tight")

        if show:
            plt.show()

        plt.close(fig)










def LM_plot_log(
        LM_dataframe: list[pd.DataFrame] | pd.DataFrame,
        metadata_df: pd.DataFrame,
        output_path: str = "",
        base_name: str = "",
        label_size: int = 15,
        tick_size: int = 15,
        color_LM: str = "#282828",
        figsize: tuple[int, int] = (9, 6),
        save: bool = True,
        show: bool = True,
):

    # Output folder
    output_dir = os.path.join(output_path, "LM_plots")
    os.makedirs(output_dir, exist_ok=True)


    # Loop over each measurement
    for i, df in enumerate(LM_dataframe):

        V = np.asarray(df["Voltage [V]"], dtype=float)
        J = np.asarray(df["Leakage Current Density [uA/cm2]"], dtype=float)
        J_log = abs(J)


        raw_area = metadata_df.loc[i, "Area_mm2"]
        match = re.search(r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)", str(raw_area))
        if match is None:
            raise ValueError(f"Cannot extract area from: {raw_area}")

        area_mm2 = float(match.group(1))
        area_cm2 = area_mm2 * 1e-2

        # ─────────────────────────────────────────────────────────────
        # Figure
        # ─────────────────────────────────────────────────────────────
        fig, ax1 = plt.subplots(figsize=figsize)

        ax1.plot(V, J_log, color=color_LM, marker = "o", markersize = 2.5)
        ax1.set_xlabel("Voltage [V]", fontsize=label_size)
        ax1.set_ylabel("Leakage current density [µA/cm²]", fontsize=label_size)
        ax1.set_yscale("log")
        ax1.set_title(f"{base_name} - Leakage (log)", fontsize=label_size)

        # Secondary y-axis (Current)
        ax2 = ax1.twinx()
        ax2.set_yscale("log")
        y1_min, y1_max = ax1.get_ylim()
        ax2.set_ylim(
            y1_min * 1e-6 * area_cm2,
            y1_max * 1e-6 * area_cm2,
        )
        ax2.set_ylabel("Current [A]", fontsize=label_size)

        # ─────────────────────────────────────────────────────────────
        # Styling (Laura-friendly)
        # ─────────────────────────────────────────────────────────────
        ax1.tick_params(
            axis="both",
            which="both",
            direction="in",
            top=True,
            right=True,
            labelsize=tick_size,
            length=6,
            width=1.2,
        )
        ax2.tick_params(
            axis="y",
            which="both",
            direction="in",
            labelsize=tick_size,
            length=6,
            width=1.2,
        )

        ax1.xaxis.set_minor_locator(AutoMinorLocator(5))
        ax1.grid(True, which="major", linestyle="-", linewidth=0.8, alpha=0.35)
        ax1.grid(True, which="minor", linestyle=":", linewidth=0.6, alpha=0.25)

        # ─────────────────────────────────────────────────────────────
        # Save / show / close
        # ─────────────────────────────────────────────────────────────
        if save:
            fname = f"{base_name}_{i}_log.png"
            fig.savefig(os.path.join(output_dir, fname), dpi=300, bbox_inches="tight")

        if show:
            plt.show()

        plt.close(fig)




