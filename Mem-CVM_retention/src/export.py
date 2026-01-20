import io
import pandas as pd
import re
import os
from typing import List, Tuple, Optional
import numpy as np
import pandas as pd



# ──────────────────────────────────────────────────────────────────────────────
#                          
# ──────────────────────────────────────────────────────────────────────────────
def write_csv_with_metadata(
    Output_path: str,
    df_metadata: pd.DataFrame,
    df_data: pd.DataFrame,
    Reading_voltage: float,
    sep: str = "\t"
):
    """
    Écrit un CSV avec :
    - metadata (clé \t valeur)
    - ligne vide
    - dataframe principal
    """

    os.makedirs(Output_path, exist_ok=True)
    csv_name = f"Vr-{Reading_voltage}_memCVM_READ.csv"
    Output_path = os.path.join(Output_path, csv_name)
    

    if df_metadata.shape[0] != 1:
        raise ValueError("df_metadata doit contenir exactement une ligne")

    with open(Output_path, "w", encoding="utf-8", newline="") as f:


        # --- 1) Écriture des metadata ---
        for key, value in df_metadata.iloc[0].items():
            if pd.isna(value):
                f.write(f"{key}{sep}\n")
            else:
                f.write(f"{key}{sep}{value}\n")

        # --- 2) Ligne vide de séparation ---
        f.write("\n")

        # --- 3) Écriture du DataFrame principal ---
        df_data.to_csv(
            f,
            sep=sep,
            index=False
        )

