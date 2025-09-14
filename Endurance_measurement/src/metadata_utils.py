import pandas as pd
import io
from datetime import datetime
from typing import Dict, Tuple, Optional
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

def fatigue_data_extraction(full_path, ):

    # --- Fatigue .dat → structured DataFrame (user‑friendly commented version) ---
    # This script locates and parses the "Result Table" block from a FE tester .dat file.
    # Steps:
    # 1) Scan the file to find the first "Result Table" (start of the block) and the first
    #    "Data Table" (end of the block).
    # 2) Slice the file lines to keep only the metadata + data for that fatigue block.
    # 3) Extract key metadata values (sample name, area, fatigue/hysteresis parameters).


    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:

        for i, line in enumerate(f):
            # Find the first occurrence of a "Result Table" header → just after it starts the block.
            if "Result Table" in line:
                print(f"Found the start of the table block at line {i+1}: {line.strip()}")
                start_index = i + 1  # exclude the marker line itself

            # Find the first occurrence of a "Data Table" header → this marks the end of the block.
            if "Data Table" in line:
                print(f"Found the end of the table block at line {i}: {line.strip()}")
                end_index = i  # exclude the end marker line
                break  # stop scanning once the first block is delimited

    # Read all lines once we know the indices so we can slice them.
    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()


    # Keep only the lines within the block [start_index:end_index].
    data_lines_complete_fatigue = lines[start_index:end_index]
    # Free memory for large files.
    del start_index, end_index, lines

    return data_lines_complete_fatigue


# ---------------------------------------------------
# ---------------------------------------------------


# --- Return a string object and a dict with metadata fields ---

def extract_metadata(
    data_lines,
    point_removal: int = 0,
    keyword: str = "Hysteresis",
) -> Tuple[Dict[str, Optional[str]], str]:
    """
    Parse les métadonnées d'un bloc texte (liste de lignes) et construit
    un dict + une chaîne 'info_text' prête pour l'affichage sur un plot.

    Parameters
    ----------
    data_lines : Iterable[str]
        Lignes de texte contenant les métadonnées.
    point_removal : int, optional
        Nombre de breakdowns (pour l'affichage), by default 0.
    keyword : str, optional
        Mot-clé pour tronquer les lignes d'hystérésis, by default "Hysteresis".

    Returns
    -------
    metadata : dict
        Dictionnaire contenant les champs bruts + champs dérivés.
    info_text : str
        Chaîne multi-ligne prête à être utilisée dans un plot.
    """

    # --- Placeholders ---
    Measurement_date = None
    SampleName = None
    Area_mm2 = None

    Fatigue_Amplitude_V = None
    Fatigue_Offset_V = None
    Fatigue_Frequency_Hz = None
    Total_Cycles = None
    PtsPerDecade = None

    Hysteresis_Frequence_Hz = None
    Hysteresis_Amplitude_V = None

    # --- Parse: première occurrence uniquement ---
    for line in data_lines:
        if "Fatigue Amplitude [V]" in line and Fatigue_Amplitude_V is None:
            Fatigue_Amplitude_V = line.strip()
        if "Fatigue Offset [V]" in line and Fatigue_Offset_V is None:
            Fatigue_Offset_V = line.strip()
        if "Fatigue Frequency [Hz]" in line and Fatigue_Frequency_Hz is None:
            Fatigue_Frequency_Hz = line.strip()
        if "Total Cycles" in line and Total_Cycles is None:
            Total_Cycles = line.strip()
        if "PtsPerDecade" in line and PtsPerDecade is None:
            PtsPerDecade = line.strip()
        if "SampleName" in line and SampleName is None:
            SampleName = line.strip()
        if "Area [mm2]" in line and Area_mm2 is None:
            Area_mm2 = line.strip()
        if "Hysteresis Amplitude [V]" in line and Hysteresis_Amplitude_V is None:
            Hysteresis_Amplitude_V = line.strip()
        if "Hysteresis Frequency [Hz]" in line and Hysteresis_Frequence_Hz is None:
            Hysteresis_Frequence_Hz = line.strip()
        if "Timestamp:" in line and Measurement_date is None:
            # ex: "... Timestamp: 03/15/2025 14:22:11"
            Measurement_date = line.strip().split("Timestamp:", 1)[1].strip()

    # --- Conversion d'aire mm² -> µm² ---
    Device_area_um2 = None
    if Area_mm2:
        try:
            # on prend la partie après ":", ex: "Area [mm2]: 3.2"
            area_num = float(Area_mm2.split(":", 1)[1].strip())
            Device_area_um2 = area_num * 1e6  # mm² → µm²
        except Exception:
            Device_area_um2 = None  # si parsing impossible

    # --- Normalisation de la date ---
    Measurement_date_iso = "Unknown"
    if Measurement_date:
        # tente plusieurs formats courants, sinon laisse "Unknown"
        parsed = None
        for fmt in ("%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
            try:
                parsed = datetime.strptime(Measurement_date, fmt)
                break
            except ValueError:
                pass
        if parsed:
            Measurement_date_iso = parsed.strftime("%Y-%m-%d")

    # --- Nettoyage (tronquer depuis le mot-clé "Hysteresis") ---
    if Hysteresis_Amplitude_V and keyword in Hysteresis_Amplitude_V:
        Hysteresis_Amplitude_V = keyword + Hysteresis_Amplitude_V.split(keyword, 1)[1]
    if Hysteresis_Frequence_Hz and keyword in Hysteresis_Frequence_Hz:
        Hysteresis_Frequence_Hz = keyword + Hysteresis_Frequence_Hz.split(keyword, 1)[1]

    # --- Dictionnaire de sortie (utile si tu veux logguer/exporter) ---
    metadata = {
        "Measurement_date_raw": Measurement_date,
        "Measurement_date_iso": Measurement_date_iso,
        "SampleName": SampleName,
        "Area_mm2": Area_mm2,
        "Device_area_um2": Device_area_um2,
        "Fatigue_Amplitude_V": Fatigue_Amplitude_V,
        "Fatigue_Offset_V": Fatigue_Offset_V,
        "Fatigue_Frequency_Hz": Fatigue_Frequency_Hz,
        "Total_Cycles": Total_Cycles,
        "PtsPerDecade": PtsPerDecade,
        "Hysteresis_Amplitude_V": Hysteresis_Amplitude_V,
        "Hysteresis_Frequence_Hz": Hysteresis_Frequence_Hz,
        "Number_of_breakdown": point_removal,
    }

    # --- Construction de la chaîne info_text pour le plot ---
    def _nz(x: Optional[str], default="N/A"):
        return x if x not in (None, "") else default

    info_text = (
        f"{_nz(SampleName)}\n"
        f"{_nz(Area_mm2)}\n\n"
        f"{_nz(Fatigue_Amplitude_V)}\n"
        f"{_nz(Fatigue_Offset_V)}\n"
        f"{_nz(Fatigue_Frequency_Hz)}\n"
        f"{_nz(Total_Cycles)}\n"
        f"{_nz(PtsPerDecade)}\n"
        f"Number of breakdown:{point_removal}\n\n"
        f"{_nz(Hysteresis_Amplitude_V)}\n"
        f"{_nz(Hysteresis_Frequence_Hz)}"
    )

    return metadata, info_text


# ---------------------------------------------------
# ---------------------------------------------------


def fatigue_dataframe_extraction(data_lines_complete_fatigue, point_removal):
    
    # --- Locate the tabular data region ---
    # We consider the first line that contains many tabs as the header (column names),
    # then we stop when reaching the "Data Measurement Parameters" section.
    header_index = None
    ender_index = None
    for idx, line in enumerate(data_lines_complete_fatigue):
        if line.count('\t') > 5 and header_index is None:
            header_index = idx  # likely the header row of the data table
        if "Data Measurement Parameters" in line and ender_index is None:
            ender_index = idx   # end of the data table block
            break

    # Extract only the data table (including the header row)
    data_frame_fatigue = data_lines_complete_fatigue[header_index:ender_index]
    print(f"Data header found at relative line {header_index}, end marker at {ender_index}")

    # --- Load the table into a DataFrame ---
    # The FE tester exports tab‑delimited text. We pass it directly to pandas.
    data_frame_fatigue = pd.read_csv(io.StringIO(''.join(data_frame_fatigue)), sep='\t', engine='python')

    # --- Select columns of interest (adjust names if your tester uses a different locale) ---
    Cycles_total = data_frame_fatigue['Cycles [n]']

    cols = [
        'Cycles [n]',
        '1-DHM Pr+ [uC/cm2]',
        '1-DHM Pr- [uC/cm2]',
        '1-DHM Vc+ [V]',
        '1-DHM Vc- [V]',
        '1-DHM Wloss [uJ/cm2]',
        '1-DHM Ipk+ [A]',
        '1-DHM Ipk- [A]',
    ]

    # si tu es sûr que toutes existent :
    df_fatigue = data_frame_fatigue[cols].copy()

    # coupe les point_removal dernières lignes pour TOUTES les colonnes
    if point_removal > 0:
        df_fatigue = df_fatigue.iloc[:-point_removal]
    
    return df_fatigue, Cycles_total



# ---------------------------------------------------
# ---------------------------------------------------



def DHM_data_extraction(full_path, Cycles_total, point_removal, df_fatigue):
        # Read all lines once we know the indices so we can slice them.
    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    index_table = []

    for i, str in enumerate(lines):
        if f"Data Table [1," in str:
            index_table.append(i)

    #DHM is metadate + data of every DHM loop
    DHM = []
    for i, index in enumerate(index_table):  

        if i < len(Cycles_total) - 1:
            DHM.append(lines[index:index_table[i+1]])
        if i == len(Cycles_total) - 1:
            DHM.append(lines[index:])


    #DHM_dataframe is only the data without metadata
    DHM_dataframe=[]
    header_index = None

    for i, loop in enumerate(DHM):
        header_index = None
        for idx, line in enumerate(loop):
            if line.count('\t') > 5 and header_index is None:
                header_index = idx
                break
        if header_index is not None:
            data_block = loop[header_index:]
            df = pd.read_csv(io.StringIO(''.join(data_block)), sep='\t', engine='python')
            DHM_dataframe.append(df)

    if point_removal > 0:
            DHM_dataframe = DHM_dataframe[:-point_removal]

    print(len(DHM_dataframe), "P-V loops loaded.")

    # Add a column with the cycle number to each DataFrame
    for i, (df, cycle) in enumerate(zip(DHM_dataframe, df_fatigue["Cycles [n]"])):
        df.insert(0, "Cycle", cycle)  # Add a column at the first position with the cycle number

    return DHM_dataframe






















