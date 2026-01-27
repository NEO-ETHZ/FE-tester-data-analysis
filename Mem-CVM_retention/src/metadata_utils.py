import io
import pandas as pd
import re
import os
from typing import List, Tuple, Optional
import numpy as np
import pandas as pd
from datetime import datetime





def extract_read_CVM_dataframes(memCVM_files: list) -> list:
    """
    Extrait les dataframes des fichiers memCVM*.dat.
    Retourne une liste de dataframes enrichis avec Writing_Voltage_V et Loop.
    """

    dataframes = []
    Timestamps = []

    for file in memCVM_files:
        df = extract_CVM_dataframe(file)
        time = extract_first_timestamp(file)

        dataframes.append(df)
        Timestamps.append(time)

    return dataframes, Timestamps


# ──────────────────────────────────────────────────────────────────────────────
#                          
# ──────────────────────────────────────────────────────────────────────────────


def extract_CVM_dataframe(CVM_file: str) -> pd.DataFrame:
    """
    Extrait le tableau Bias-C-tan(delta) du fichier CVM .dat.
    Ignore :
      - le bloc CVResult
      - les métadonnées
    Ne garde que le tableau qui suit le bloc 'CV'.
    """

    with open(CVM_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    # 1) Trouver le début du bloc 'CV'
    cv_block_start = None
    for i, line in enumerate(lines):
        if line.strip() == "CV":
            cv_block_start = i
            break

    if cv_block_start is None:
        raise ValueError("Bloc 'CV' introuvable dans le fichier (pas de ligne 'CV').")

    # 2) À partir du bloc 'CV', trouver la première ligne tabulée = header du 2e tableau
    table_header_idx = None
    for i in range(cv_block_start, len(lines)):
        line = lines[i]
        if line.count('\t') >= 2 and line.strip() != "":
            table_header_idx = i
            break

    if table_header_idx is None:
        raise ValueError("Impossible de trouver le header du tableau Bias–C après le bloc 'CV'.")

    # 3) Garder uniquement le 2e tableau (header + data)
    table_text = "".join(lines[table_header_idx:])

    # 4) Lecture avec pandas
    df = pd.read_csv(
        io.StringIO(table_text),
        sep="\t",
        engine="python"
    )

    return df


# ──────────────────────────────────────────────────────────────────────────────
#                          
# ──────────────────────────────────────────────────────────────────────────────


def get_capacitance_near_target_bias(
    df: pd.DataFrame,
    target: float,
    bias_col: str = "Bias [V]",
    cap_col: str = "C [F]",
) -> float:
    """
    Retourne la capacitance la plus proche de Bias = target.
    Si la lecture CVM est incomplète, retourne np.nan.
    """

    # Colonnes manquantes = bug de code → exception
    if bias_col not in df.columns or cap_col not in df.columns:
        raise KeyError(f"Colonnes '{bias_col}' ou '{cap_col}' absentes du DataFrame.")

    bias = df[bias_col]
    cap = df[cap_col]

    # DataFrame vide ou trop court
    if len(bias) == 0:
        return np.nan



    # Target hors plage → mesure incomplète → NaN
    if target > np.nanmax(bias) or target < np.nanmin(bias):
        return np.nan

    # Trouver le point le plus proche
    idx_closest = np.nanargmin(np.abs(bias - target))

    value = cap[idx_closest]

    # Si la cap est NaN → on propage
    return float(value) if np.isfinite(value) else np.nan


# ──────────────────────────────────────────────────────────────────────────────
#                          
# ──────────────────────────────────────────────────────────────────────────────


def extract_first_timestamp(dat_path: str) -> datetime:
    """
    Extrait le premier TimeStamp d'un fichier .dat
    Format attendu: TimeStamp: MM/DD/YYYY HH:MM:SS
    """
    with open(dat_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("TimeStamp:"):
                ts_str = line.replace("TimeStamp:", "").strip()
                return datetime.strptime(ts_str, "%m/%d/%Y %H:%M:%S")

    raise ValueError("Aucun 'TimeStamp:' trouvé dans le fichier.")


def compute_elapsed_time_seconds(timestamp_list: list[str]) -> list[float]:
    """
    Retourne le temps écoulé (en secondes) depuis le premier timestamp.
    """

    t0 = timestamp_list[0]
    
    elapsed_s = []
    for dt in timestamp_list:
        elapsed_s.append((dt - t0).total_seconds())

    return elapsed_s


# ──────────────────────────────────────────────────────────────────────────────
#                          
# ──────────────────────────────────────────────────────────────────────────────

def metadata_extraction(CVM_file: str):

    with open(CVM_file, 'r') as f:
        # On utilise splitlines() pour boucler sur chaque ligne du fichier 
        lines = f.read().splitlines()

    # Dictionnaire pour stocker les valeurs propres
    data = {
        # Dates & identification
        'Date': np.nan,        
        # Sample parameters
        'Area_mm2': np.nan,
        'Thickness_nm': np.nan,
        
        # CVM Reading parameters
        'Amplitude_V': np.nan,
        'Points': np.nan,
        'Integration': np.nan,
        'Current_range': np.nan,
        'SS_Amplitude_V': np.nan,
        'SS_Frequency_Hz': np.nan,
    }

    def clean_val(raw_line):
        try:
            # On sépare par ":" et on prend l'élément du milieu (la valeur) 
            val = raw_line.split(':')[1].strip()
            # On essaie de convertir en float si c'est numérique
            return float(val)
        except (ValueError, IndexError):
            # Si échec (ex: "staircase"), on retourne le texte brut nettoyé
            return val if 'val' in locals() else None

    for line in lines:
        line = line.strip()
        if "Timestamp:" in line:
            data["Date"] = line.strip().split("Timestamp:", 1)[1].strip()
        if "Area [mm2]:" in line:
            data["Area_mm2"] = clean_val(line)
        if "Thickness [nm]:" in line:
            data["Thickness_nm"] = clean_val(line)
        if "Current Range:" in line:
            data["Current_range"] = clean_val(line)
        if "SsFrequency [Hz]:" in line:
            data["SS_Frequency_Hz"] = clean_val(line)
        if "SsAmplitude [V]:" in line:
            data["SS_Amplitude_V"] = clean_val(line)
        if "Max. Voltage [V]:" in line:
            data["Amplitude_V"] = clean_val(line)
        if "Integration Mode:" in line:
            data["Integration"] = clean_val(line)
    
    # Création du DataFrame (index [0] car c'est une seule ligne de données)
    df = pd.DataFrame([data])
    
    return df


# ──────────────────────────────────────────────────────────────────────────────
#                          
# ──────────────────────────────────────────────────────────────────────────────


def extract_index(path: str) -> int:
    """
    Extrait le nombre après 'NegBias' dans le filepath.
    Exemple: ...NegBias17.dat -> 17
    """
    m = re.search(r"(\d+)\.dat$", path)
    if m is None:
        raise ValueError(f"Index introuvable dans: {path}")
    return int(m.group(1))


# ──────────────────────────────────────────────────────────────────────────────
#                          
# ──────────────────────────────────────────────────────────────────────────────


def extract_CVM_Average(memCVM_files: list) -> pd.DataFrame:
    """
    Extrait le tableau Bias-C-tan(delta) du fichier CVM .dat.
    Ignore :
      - le bloc CVResult
      - les métadonnées
    Ne garde que le tableau qui suit le bloc 'CV'.
    """

    MEAN_DATAFRAME = []

    for file in memCVM_files:
    
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        # 1) Trouver le début du bloc 'CV'
        cv_block_start = None
        for i, line in enumerate(lines):
            if line.strip() == "CV":
                cv_block_start = i
                break

        if cv_block_start is None:
            raise ValueError("Bloc 'CV' introuvable dans le fichier (pas de ligne 'CV').")

        # 2) À partir du bloc 'CV', trouver la première ligne tabulée = header du 2e tableau
        table_header_idx = None
        for i, line in enumerate(lines):
        
            if line.count('\t') >= 2 and line.strip() != "":
                table_header_idx = i
                break

        if table_header_idx is None:
            raise ValueError("Impossible de trouver le header du tableau Bias–C après le bloc 'CV'.")

        # 3) Garder uniquement le 2e tableau (header + data)
        table_text = "".join(lines[table_header_idx:(cv_block_start-1)])

        # 4) Lecture avec pandas
        df = pd.read_csv(
            io.StringIO(table_text),
            sep="\t",
            engine="python"
        )

        C_av = df["Cav [F]"][0]

        MEAN_DATAFRAME.append(C_av)
    

    return MEAN_DATAFRAME







