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
        if f"LeakageResult" in str:
            header_start_index = i
        if "TfaVersion" in str:
            header_end_index = i
            break

    header_LM = lines[header_start_index:header_end_index]

    lines = lines[header_end_index:]
    index_table = []

    Number_of_dataframe = 0
    for i, str in enumerate(lines):
        if "Table " in str:
            Number_of_dataframe += 1
            index_table.append(i+1)

    del str, i

    #LM is metadate + data of every LM loop
    LM = []
    for i, index in enumerate(index_table):  

        if i < Number_of_dataframe - 1:
            LM.append(lines[index:index_table[i+1]])
        if i == Number_of_dataframe - 1:
            LM.append(lines[index:])


    # --- Initialize variables to store metadata ---

    SampleName = []
    Area_mm2 = []
    Step_duration = []
    Voltage_step = []
    Current_range = []
    Measurement_date = []


    #LM_dataframe is only the data without metadata
    LM_dataframe=[]
    header_index = None

    for i, loop in enumerate(LM):
        header_index = None
        for idx, line in enumerate(loop):
            if line.count('\t') > 3 and header_index is None:
                header_index = idx
                break
        if header_index is not None:
            data_block = loop[header_index:]
            df = pd.read_csv(io.StringIO(''.join(data_block)), sep='\t', engine='python')
            LM_dataframe.append(df)

        # --- Parse: première occurrence uniquement --- retrive metadata
        for metadata in loop:
            if "Current Range: " in metadata:
                Current_range.append(metadata)
            elif "Settings:  DR O2 MON PSW LF" in metadata:
                Current_range.append("Current Range: Auto")
            if "SampleName" in metadata:
                SampleName.append(metadata)
            if "Area [mm2]" in metadata:
                Area_mm2.append(metadata)
            if "Step Duration" in metadata:
                Step_duration.append(metadata)
            if "Voltage Step" in metadata:
                Voltage_step.append(metadata)
            if "Timestamp:" in metadata:
                # ex: "... Timestamp: 03/15/2025 14:22:11"
                Measurement_date.append(metadata.split("Timestamp:")[-1].strip())
                


    # On crée un dictionnaire
    metadata = {
        "SampleName": SampleName,
        "Area_mm2": Area_mm2,
        "Step_duration": Step_duration,
        "Voltage_step": Voltage_step,
        "Current_range" : Current_range,
        "Measurement_date": Measurement_date
    }

    metadata_df = pd.DataFrame(metadata)

    print(len(LM_dataframe), "LM loaded.")

    return LM_dataframe, metadata_df















