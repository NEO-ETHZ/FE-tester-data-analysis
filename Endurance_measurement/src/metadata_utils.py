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

    DHM_present = False
    CVM_present = False
    PUND_present = False

    DHM_number = None
    CVM_number = None
    PUND_number = None

    Fatigue_Amplitude_V = None
    Fatigue_Offset_V = None
    Fatigue_Frequency_Hz = None
    Total_Cycles = None
    PtsPerDecade = None

    DHM_Frequency_Hz = None
    DHM_Amplitude_V = None

    CVM_Voltage = None
    CVM_Base_Frequency_Hz = None
    CVM_ss_Frequency_Hz = None
    CVM_ss_amplitude_V = None
    CVM_datapoints = None

    PUND_Write_Amplitude_V = None
    PUND_Pulse_time_s = None
    PUND_Pulse_rise_time_s = None
    PUND_Frequency_Hz = None
    PUND_Amplitude_V = None
    PUND_Write_delay_s = None
    PUND_Read_delay_s = None
    PUND_Pulse_points = None

    # --- Indexing the measurement parameters lines ---

    for line in data_lines:
        if "Data Measurement Parameters" in line:
            params_start_index = data_lines.index(line)
            break
    data_lines_02 = data_lines[params_start_index:]

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
        if "Timestamp:" in line and Measurement_date is None:
            # ex: "... Timestamp: 03/15/2025 14:22:11"
            Measurement_date = line.strip().split("Timestamp:", 1)[1].strip()

        if "Hysteresis Amplitude [V]" in line and DHM_Amplitude_V is None:
            DHM_Amplitude_V = line.strip()
        if "Hysteresis Frequency [Hz]" in line and DHM_Frequency_Hz is None:
            DHM_Frequency_Hz = line.strip()

        if "Max. Voltage [V]:" in line and CVM_Voltage is None:
            CVM_Voltage = line.split("Max. Voltage [V]:", 1)[-1].strip()
            CVM_Voltage = "Max. Voltage [V]: " + CVM_Voltage
        if "BaseFreq [Hz]:" in line and CVM_Base_Frequency_Hz is None:
            CVM_Base_Frequency_Hz = line.split("BaseFreq [Hz]:", 1)[-1].strip()
            CVM_Base_Frequency_Hz = "BaseFreq [Hz]: " + CVM_Base_Frequency_Hz
        if "SsFrequency [Hz]" in line and CVM_ss_Frequency_Hz is None:
            CVM_ss_Frequency_Hz = line.split("SsFrequency [Hz]", 1)[-1].strip()
            CVM_ss_Frequency_Hz = "SsFrequency [Hz]: " + CVM_ss_Frequency_Hz
        if "SsAmplitude [V]:" in line and CVM_ss_amplitude_V is None:
            CVM_ss_amplitude_V = line.split("SsAmplitude [V]:", 1)[-1].strip()
            CVM_ss_amplitude_V = "SsAmplitude [V]: " + CVM_ss_amplitude_V
        if "Repetitions:" in line and CVM_datapoints is None:
            CVM_datapoints = line.split("Repetitions:", 1)[-1].strip()
            CVM_datapoints = "Repetitions: " + CVM_datapoints

        if "Write Pulse Amplitude [V]:" in line and PUND_Write_Amplitude_V is None:
            PUND_Write_Amplitude_V = line.split("Write Pulse Amplitude [V]:", 1)[-1].strip()
            PUND_Write_Amplitude_V = "Write Pulse Amplitude [V]: " + PUND_Write_Amplitude_V
        if "Write Pulse Time [s]:" in line and PUND_Pulse_time_s is None:
            PUND_Pulse_time_s = line.split("Write Pulse Time [s]:", 1)[-1].strip()
            PUND_Pulse_time_s = "Write Pulse Time [s]: " + PUND_Pulse_time_s
        if "Write Pulse Rise Time [s]:" in line and PUND_Pulse_rise_time_s is None:
            PUND_Pulse_rise_time_s = line.split("Write Pulse Rise Time [s]:", 1)[-1].strip()
            PUND_Pulse_rise_time_s = "Write Pulse Rise Time [s]: " + PUND_Pulse_rise_time_s
        if "Pund Frequency [Hz]:" in line and PUND_Frequency_Hz is None:
            PUND_Frequency_Hz = line.split("Pund Frequency [Hz]:", 1)[-1].strip()
            PUND_Frequency_Hz = "Pund Frequency [Hz]: " + PUND_Frequency_Hz
        if "Pund Amplitude [V]:" in line and PUND_Amplitude_V is None:
            PUND_Amplitude_V = line.split("Pund Amplitude [V]:", 1)[-1].strip()
            PUND_Amplitude_V = "Pund Amplitude [V]: " + PUND_Amplitude_V
        if "Write Pulse Delay [s]:" in line and PUND_Write_delay_s is None:
            PUND_Write_delay_s = line.split("Write Pulse Delay [s]:", 1)[-1].strip()
            PUND_Write_delay_s = "Write Pulse Delay [s]: " + PUND_Write_delay_s
        if "Read Pulse Delay [s]:" in line and PUND_Read_delay_s is None:
            PUND_Read_delay_s = line.split("Read Pulse Delay [s]:", 1)[-1].strip()
            PUND_Read_delay_s = "Read Pulse Delay [s]: " + PUND_Read_delay_s
        if "Pulse Points:" in line and PUND_Pulse_points is None:
            PUND_Pulse_points = line.split("Pulse Points:", 1)[-1].strip()
            PUND_Pulse_points = "Pulse Points: " + PUND_Pulse_points
    
    for line in data_lines_02:

        if "-DHM" in line and DHM_present is False:
            DHM_present = True
            DHM_number = line.split("-DHM")[0].strip()
            print(f"DHM is present:{DHM_present}, number : {DHM_number}")
        if "-CVM" in line and CVM_present is False:
            CVM_present = True
            CVM_number = line.split("-CVM")[0].strip()
            print(f"CVM is present: {CVM_present}, number : {CVM_number}")
        if "-PM" in line and PUND_present is False:
            PUND_present = True
            PUND_number = line.split("-PM")[0].strip()
            print(f"PUND is present: {PUND_present}, number : {PUND_number}")



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
    if DHM_Amplitude_V and keyword in DHM_Amplitude_V:
        DHM_Amplitude_V = keyword + DHM_Amplitude_V.split(keyword, 1)[1]
    if DHM_Frequency_Hz and keyword in DHM_Frequency_Hz:
        DHM_Frequency_Hz = keyword + DHM_Frequency_Hz.split(keyword, 1)[1]

    # --- Dictionnaire de sortie (utile si tu veux logguer/exporter) ---
    metadata_DHM = {
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
        "DHM_Amplitude_V": DHM_Amplitude_V,
        "DHM_Frequency_Hz": DHM_Frequency_Hz,
        "Number_of_breakdown": point_removal,
        "DHM_present": DHM_present,
        "DHM_number": DHM_number,
    }

    metadata_CVM = {
        "CVM_Voltage": CVM_Voltage,
        "CVM_Base_Frequency_Hz": CVM_Base_Frequency_Hz,
        "CVM_ss_Frequency_Hz": CVM_ss_Frequency_Hz,
        "CVM_ss_amplitude_V": CVM_ss_amplitude_V,
        "CVM_datapoints": CVM_datapoints,
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
        "Number_of_breakdown": point_removal,
        "CVM_present": CVM_present,
        "CVM_number": CVM_number,
    }

    metadata_PUND = {
        "PUND_Write_Amplitude_V": PUND_Write_Amplitude_V,
        "PUND_Pulse_time_s": PUND_Pulse_time_s,
        "PUND_Pulse_rise_time_s": PUND_Pulse_rise_time_s,
        "PUND_Frequency_Hz": PUND_Frequency_Hz,
        "PUND_Amplitude_V": PUND_Amplitude_V,
        "PUND_Write_delay_s": PUND_Write_delay_s,
        "PUND_Read_delay_s": PUND_Read_delay_s,
        "PUND_Pulse_points": PUND_Pulse_points,
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
        "Number_of_breakdown": point_removal,
        "PUND_present": PUND_present,
        "PUND_number": PUND_number,
    }

    # --- Construction de la chaîne info_text pour le plot ---
    def _nz(x: Optional[str], default="N/A"):   #If None the value is gonna be N/A
        return x if x not in (None, "") else default

    info_text_DHM = (
        f"{_nz(SampleName)}\n"
        f"{_nz(Area_mm2)}\n\n"
        f"{_nz(Fatigue_Amplitude_V)}\n"
        f"{_nz(Fatigue_Offset_V)}\n"
        f"{_nz(Fatigue_Frequency_Hz)}\n"
        f"{_nz(Total_Cycles)}\n"
        f"{_nz(PtsPerDecade)}\n"
        f"Number of breakdown:{point_removal}\n\n"
        f"{_nz(DHM_Amplitude_V)}\n"
        f"{_nz(DHM_Frequency_Hz)}"
    )

    info_text_CVM = (
        f"{_nz(SampleName)}\n"
        f"{_nz(Area_mm2)}\n\n"
        f"{_nz(Fatigue_Amplitude_V)}\n"
        f"{_nz(Fatigue_Offset_V)}\n"
        f"{_nz(Fatigue_Frequency_Hz)}\n"
        f"{_nz(Total_Cycles)}\n"
        f"{_nz(PtsPerDecade)}\n"
        f"Number of breakdown:{point_removal}\n\n"
        f"{_nz(CVM_Voltage)}\n"
        f"{_nz(CVM_Base_Frequency_Hz)}\n"
        f"{_nz(CVM_ss_Frequency_Hz)}\n"
        f"{_nz(CVM_ss_amplitude_V)}\n"
        f"{_nz(CVM_datapoints)}"
    )

    info_text_PUND = (
        f"{_nz(SampleName)}\n"
        f"{_nz(Area_mm2)}\n\n"
        f"{_nz(Fatigue_Amplitude_V)}\n"
        f"{_nz(Fatigue_Offset_V)}\n"
        f"{_nz(Fatigue_Frequency_Hz)}\n"
        f"{_nz(Total_Cycles)}\n"
        f"{_nz(PtsPerDecade)}\n"
        f"Number of breakdown:{point_removal}\n\n"
        f"{_nz(PUND_Write_Amplitude_V)}\n"
        f"{_nz(PUND_Pulse_time_s)}\n"
        f"{_nz(PUND_Pulse_rise_time_s)}\n"
        f"{_nz(PUND_Frequency_Hz)}\n"
        f"{_nz(PUND_Amplitude_V)}\n"
        f"{_nz(PUND_Write_delay_s)}\n"
        f"{_nz(PUND_Read_delay_s)}\n"
        f"{_nz(PUND_Pulse_points)}"
    )

    return metadata_DHM, metadata_CVM, metadata_PUND, info_text_DHM, info_text_CVM, info_text_PUND




# ---------------------------------------------------
# ---------------------------------------------------


def fatigue_dataframe_extraction(data_lines_complete_fatigue, point_removal, metadata_dict_DHM, metadata_dict_CVM, metadata_dict_PUND):
    
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
    
    cols_DHM = [
        'Cycles [n]',
        f'{metadata_dict_DHM["DHM_number"]}-DHM Pr+ [uC/cm2]',
        f'{metadata_dict_DHM["DHM_number"]}-DHM Pr- [uC/cm2]',
        f'{metadata_dict_DHM["DHM_number"]}-DHM Vc+ [V]',
        f'{metadata_dict_DHM["DHM_number"]}-DHM Vc- [V]',
        f'{metadata_dict_DHM["DHM_number"]}-DHM Wloss [uJ/cm2]',
        f'{metadata_dict_DHM["DHM_number"]}-DHM Ipk+ [A]',
        f'{metadata_dict_DHM["DHM_number"]}-DHM Ipk- [A]',
    ]

    cols_CVM = [
        'Cycles [n]',
        f'{metadata_dict_CVM["CVM_number"]}-CVM Cav [F]',
        f'{metadata_dict_CVM["CVM_number"]}-CVM Rav [Ohm]',
        f'{metadata_dict_CVM["CVM_number"]}-CVM TanDmax [1]',
        f'{metadata_dict_CVM["CVM_number"]}-CVM TanDav [1]',
        f'{metadata_dict_CVM["CVM_number"]}-CVM Vav [V]',
        f'{metadata_dict_CVM["CVM_number"]}-CVM Iav [A]',
        f'{metadata_dict_CVM["CVM_number"]}-CVM EpsAv [1]',
        f'{metadata_dict_CVM["CVM_number"]}-CVM Cpk+ [F]',
        f'{metadata_dict_CVM["CVM_number"]}-CVM Cpk- [F]',
    ]

    cols_PUND = [
        'Cycles [n]',
        f'{metadata_dict_PUND["PUND_number"]}-PM Psw [uC/cm2]',
        f'{metadata_dict_PUND["PUND_number"]}-PM Ipk+ [A]',
        f'{metadata_dict_PUND["PUND_number"]}-PM Ipk- [A]',
        f'{metadata_dict_PUND["PUND_number"]}-PM Vc+ [V]',
        f'{metadata_dict_PUND["PUND_number"]}-PM Vc- [V]',
        f'{metadata_dict_PUND["PUND_number"]}-PM Pr+ [uC/cm2]',
        f'{metadata_dict_PUND["PUND_number"]}-PM Pr- [uC/cm2]',
    ]


    if metadata_dict_DHM["DHM_present"] is True:
        df_fatigue_DHM = data_frame_fatigue[cols_DHM].copy()
        if point_removal > 0:
            df_fatigue_DHM = df_fatigue_DHM.iloc[:-point_removal]
    else:
        df_fatigue_DHM = pd.DataFrame()  # empty DataFrame if DHM not present

    if metadata_dict_CVM["CVM_present"] is True:
        df_fatigue_CVM = data_frame_fatigue[cols_CVM].copy()
        if point_removal > 0:
            df_fatigue_CVM = df_fatigue_CVM.iloc[:-point_removal]
    else:
        df_fatigue_CVM = pd.DataFrame()  # empty DataFrame if CVM not present

    if metadata_dict_PUND["PUND_present"] is True:
        df_fatigue_PUND = data_frame_fatigue[cols_PUND].copy()
        if point_removal > 0:
            df_fatigue_PUND = df_fatigue_PUND.iloc[:-point_removal]
    else:
        df_fatigue_PUND = pd.DataFrame()  # empty DataFrame if PUND not present

    
    return df_fatigue_DHM, df_fatigue_CVM, df_fatigue_PUND, Cycles_total



# ---------------------------------------------------
# ---------------------------------------------------



def DHM_data_extraction(full_path, Cycles_total, point_removal, df_fatigue_DHM, metadata_dict_DHM):
    
    if metadata_dict_DHM["DHM_present"] is False:
        return []  # Return an empty list if DHM data is not present
    else:
        # Read all lines once we know the indices so we can slice them.
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        # Depends how we measure on the FE tester, DHM might not be in Table number 1
        index_table = []
        DHM_Table_check = "Data Table [" + metadata_dict_DHM["DHM_number"] + ","

        for i, str in enumerate(lines):
            if DHM_Table_check in str:
                index_table.append(i)

        #DHM is metadate + dataframe of every DHM loop
        DHM = []
        for i, index in enumerate(index_table):

            if i < len(Cycles_total) - 1:
                DHM.append(lines[index:index_table[i+1]])
            if i == len(Cycles_total) - 1:
                Delta = index - index_table[i-1]
                DHM.append(lines[index:index + Delta])


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

        print(len(DHM_dataframe), "DHM dataframe loaded.")

        # Add a column with the cycle number to each DataFrame
        for i, (df, cycle) in enumerate(zip(DHM_dataframe, df_fatigue_DHM["Cycles [n]"])):
            df.insert(0, "Cycle", cycle)  # Add a column at the first position with the cycle number

        return DHM_dataframe




def CVM_data_extraction(full_path, Cycles_total, point_removal, df_fatigue_CVM, metadata_dict_CVM):
    if metadata_dict_CVM["CVM_present"] is False:
        return []  # Return an empty list if CVM data is not present   
    else:
        # Read all lines once we know the indices so we can slice them.
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        # Depends how we measure on the FE tester, CVM might not be in Table number 1
        index_table = []
        CVM_Table_check = "Data Table [" + metadata_dict_CVM["CVM_number"] + ","

        for i, str in enumerate(lines):
            if CVM_Table_check in str:
                index_table.append(i)

        #CVM is metadate + dataframe of every CVM loop
        CVM = []
        for i, index in enumerate(index_table):

            if i < len(Cycles_total) - 1:
                CVM.append(lines[index:index_table[i+1]])
            if i == len(Cycles_total) - 1:
                Delta = index - index_table[i-1]
                CVM.append(lines[index:index + Delta])


        #CVM_dataframe is only the data without metadata
        CVM_dataframe=[]
        header_index = None


        for i, loop in enumerate(CVM):
            header_index = None

            for idx, line in enumerate(loop):
                if line.count('\t') > 5 and header_index is None:
                    header_index = idx
                    break
            if header_index is not None:
                data_block = loop[header_index:]
                df = pd.read_csv(io.StringIO(''.join(data_block)), sep='\t', engine='python')
                CVM_dataframe.append(df)

        if point_removal > 0:
                CVM_dataframe = CVM_dataframe[:-point_removal]

        print(len(CVM_dataframe), "CVM dataframe loaded.")

        # Add a column with the cycle number to each DataFrame
        for i, (df, cycle) in enumerate(zip(CVM_dataframe, df_fatigue_CVM["Cycles [n]"])):
            df.insert(0, "Cycle", cycle)  # Add a column at the first position with the cycle number

        return CVM_dataframe


def PUND_data_extraction(full_path, Cycles_total, point_removal, df_fatigue_PUND, metadata_dict_PUND):
    if metadata_dict_PUND["PUND_present"] is False:
        return []  # Return an empty list if PUND data is not present   
    else:
        # Read all lines once we know the indices so we can slice them.
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        # Depends how we measure on the FE tester, PUND might not be in Table number 1
        index_table = []
        PUND_Table_check = "Data Table [" + metadata_dict_PUND["PUND_number"] + ","

        for i, str in enumerate(lines):
            if PUND_Table_check in str:
                index_table.append(i)

        #PUND is metadate + dataframe of every PUND loop
        PUND = []
        for i, index in enumerate(index_table):

            if i < len(Cycles_total) - 1:
                PUND.append(lines[index:index_table[i+1]])
            if i == len(Cycles_total) - 1:
                Delta = index - index_table[i-1]
                PUND.append(lines[index:index + Delta])


        #PUND_dataframe is only the data without metadata
        PUND_dataframe=[]
        header_index = None


        for i, loop in enumerate(PUND):
            header_index = None

            for idx, line in enumerate(loop):
                if line.count('\t') > 5 and header_index is None:
                    header_index = idx
                    break
            if header_index is not None:
                data_block = loop[header_index:]
                df = pd.read_csv(io.StringIO(''.join(data_block)), sep='\t', engine='python')
                PUND_dataframe.append(df)

        if point_removal > 0:
                PUND_dataframe = PUND_dataframe[:-point_removal]

        print(len(PUND_dataframe), "PUND dataframe loaded.")

        # Add a column with the cycle number to each DataFrame
        for i, (df, cycle) in enumerate(zip(PUND_dataframe, df_fatigue_PUND["Cycles [n]"])):
            df.insert(0, "Cycle", cycle)  # Add a column at the first position with the cycle number

        return PUND_dataframe















