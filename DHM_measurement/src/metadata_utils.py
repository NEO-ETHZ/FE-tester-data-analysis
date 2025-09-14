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





def Extract_data_and_metadata(full_path):
    
    # Read all lines once we know the indices so we can slice them.
    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    header_start_index = None
    header_end_index = None

    for i, str in enumerate(lines):
        if f"DynamicHysteresisResult" in str:
            header_start_index = i
        if "TfaVersion" in str:
            header_end_index = i
            break

    header_DHM = lines[header_start_index:header_end_index]

    lines = lines[header_end_index:]
    index_table = []

    Number_of_dataframe = 0
    for i, str in enumerate(lines):
        if "Table " in str:
            Number_of_dataframe += 1
            index_table.append(i+1)

    del str, i

    #DHM is metadate + data of every DHM loop
    DHM = []
    for i, index in enumerate(index_table):  

        if i < Number_of_dataframe - 1:
            DHM.append(lines[index:index_table[i+1]])
        if i == Number_of_dataframe - 1:
            DHM.append(lines[index:])


    # --- Initialize variables to store metadata ---

    SampleName = []
    Area_mm2 = []
    Hysteresis_Amplitude_V = []
    Hysteresis_Frequence_Hz = []
    Measurement_date = []


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


    # --- Initialize variables to store metadata ---

    SampleName = []
    Area_mm2 = []
    Hysteresis_Amplitude_V = []
    Hysteresis_Frequence_Hz = []
    Measurement_date = []


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

        # --- Parse: première occurrence uniquement ---
        for metadata in loop:
            if "SampleName" in metadata:
                SampleName.append(metadata)
            if "Area [mm2]" in metadata:
                Area_mm2.append(metadata)
            if "Hysteresis Amplitude [V]" in metadata:
                Hysteresis_Amplitude_V.append(metadata)
            if "Hysteresis Frequency [Hz]" in metadata:
                Hysteresis_Frequence_Hz.append(metadata)
            if "Timestamp:" in metadata:
                # ex: "... Timestamp: 03/15/2025 14:22:11"
                Measurement_date.append(metadata.split("Timestamp:")[-1].strip())

    del metadata, line, data_block, df, header_index, i, idx

    # On crée un dictionnaire
    metadata = {
        "SampleName": SampleName,
        "Area_mm2": Area_mm2,
        "Hysteresis_Amplitude_V": Hysteresis_Amplitude_V,
        "Hysteresis_Frequence_Hz": Hysteresis_Frequence_Hz,
        "Measurement_date": Measurement_date
    }

    metadata_df = pd.DataFrame(metadata)

    print(len(DHM_dataframe), "P-V loops loaded.")

    return DHM_dataframe, metadata_df















