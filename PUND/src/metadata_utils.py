


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
        if f"PulseResult" in str:
            header_start_index = i
        if "TfaVersion" in str:
            header_end_index = i
            break

    header_PUND = lines[header_start_index:header_end_index]

    lines = lines[header_end_index:]
    index_table = []

    Number_of_dataframe = 0
    for i, str in enumerate(lines):
        if "Table " in str:
            Number_of_dataframe += 1
            index_table.append(i+1)

    del str, i

    #PUND is metadate + data of every PUND loop
    PUND = []
    for i, index in enumerate(index_table):  

        if i < Number_of_dataframe - 1:
            PUND.append(lines[index:index_table[i+1]])
        if i == Number_of_dataframe - 1:
            PUND.append(lines[index:])


    # --- Initialize variables to store metadata ---
    SampleName = []
    Area_mm2 = []
    Current_Range = []
    Pund_Frequency = []
    Pund_Amplitude = []
    Write_Pulse_Time = []
    Write_Pulse_Rise_Time = []
    Write_Pulse_Amplitude = []
    Read_Pulse_Delay = []
    Write_Pulse_Delay = []
    Measurement_date = []

    #PUND_dataframe is only the data without metadata
    PUND_dataframe = []


    header_index = None

    for i, loop in enumerate(PUND):
        header_index = None
        data_start = None
        
        # Find the line with column headers (it has many tabs)
        for idx, line in enumerate(loop):
            if line.count('\t') > 5:
                header_index = idx
                data_start = idx
                break
                
        if header_index is not None:
            # Get the data block (everything after the header)
            data_block = loop[data_start:]
            # Create dataframe from the data block
            try:
                df = pd.read_csv(io.StringIO(''.join(data_block)), sep='\t', engine='python')
                PUND_dataframe.append(df)
            except pd.errors.EmptyDataError:
                print(f"Warning: Empty data block in measurement {i+1}")
                continue

        # --- Parse: première occurrence uniquement ---
        for metadata in loop:
            if "SampleName" in metadata:
                SampleName.append(metadata)
            if "Area [mm2]" in metadata:
                Area_mm2.append(metadata)
            if "Current Range:" in metadata:
                Current_Range.append(metadata)
            if "Pund Frequency [Hz]:" in metadata:
                Pund_Frequency.append(metadata)
            if "Pund Amplitude [V]:" in metadata:
                Pund_Amplitude.append(metadata)
            if "Write Pulse Amplitude [V]:" in metadata:
                Write_Pulse_Amplitude.append(metadata)
            if "Write Pulse Time [s]:" in metadata:
                Write_Pulse_Time.append(metadata)
            if "Write Pulse Rise Time [s]:" in metadata:
                Write_Pulse_Rise_Time.append(metadata)
            if "Read Pulse Delay [s]:" in metadata:
                Read_Pulse_Delay.append(metadata)
            if "Write Pulse Delay [s]:" in metadata:
                Write_Pulse_Delay.append(metadata)            
            if "Timestamp:" in metadata:
                # ex: "... Timestamp: 03/15/2025 14:22:11"
                Measurement_date.append(metadata.split("Timestamp:")[-1].strip())


    del metadata, line, data_block, df, header_index, i, idx

    # On crée un dictionnaire
    metadata = {
        "SampleName": SampleName,
        "Area_mm2": Area_mm2,
        "Current_Range": Current_Range,
        "Pund_Frequency": Pund_Frequency,
        "Pund_Amplitude": Pund_Amplitude,
        "Write_Pulse_Amplitude": Write_Pulse_Amplitude,
        "Write_Pulse_Time": Write_Pulse_Time,
        "Write_Pulse_Rise_Time": Write_Pulse_Rise_Time,
        "Read_Pulse_Delay": Read_Pulse_Delay,
        "Write_Pulse_Delay": Write_Pulse_Delay,
        "Measurement_date": Measurement_date
    }

    metadata_df = pd.DataFrame(metadata)

    print(len(PUND_dataframe), "P-V loops loaded.")

    return PUND_dataframe, metadata_df




























