import io
import pandas as pd
import re
import os
from typing import List, Tuple, Optional
from src.file_path import find_seq_file
import numpy as np
import pandas as pd



def seq_file_parsing(path):

    path_seq_file = find_seq_file(path)

    if path_seq_file is None:
        raise FileNotFoundError("Fichier .seq introuvable dans le même dossier que les fichiers CVM.")
    
    with open(path_seq_file, 'r') as f:
        # On utilise splitlines() pour boucler sur chaque ligne du fichier 
        lines = f.read().splitlines()

    # Dictionnaire pour stocker les valeurs propres
    data = {
        # Dates & identification
        'Date': np.nan,
        'Name': np.nan,
        'Device_ID': np.nan,
        
        # Sample parameters
        'Area_um2': np.nan,
        'Thickness_nm': np.nan,
        
        # Writing pulses
        'Rise_time_s': np.nan,
        'PM_Positive_start_V': np.nan,
        'PM_Positive_end_V': np.nan,
        'PM_Positive_steps': np.nan,
        'PM_Negative_start_V': np.nan,
        'PM_Negative_end_V': np.nan,
        'PM_Negative_steps': np.nan,
        
        # CVM Reading parameters
        'Amplitude_V': np.nan,
        'Points': np.nan,
        'Mode': np.nan,
        'Integration': np.nan,
        'Unipolar': np.nan,
        'Prepol': np.nan,
        'Current_range': np.nan,
        'Frequency_Hz': np.nan,
        'SS_Amplitude_V': np.nan,
        'SS_Frequency_Hz': np.nan,
    }

    # Fonction interne pour extraire proprement le nombre ou le texte entre les ":"
    def clean_val(raw_line):
        try:
            # On sépare par ":" et on prend l'élément du milieu (la valeur) 
            val = raw_line.split(':')[1].strip()
            # On essaie de convertir en float si c'est numérique
            return float(val)
        except (ValueError, IndexError):
            # Si échec (ex: "staircase"), on retourne le texte brut nettoyé
            return val if 'val' in locals() else None

    # On parcourt les lignes
    for line in lines:
        if "Date:" in line:
            data['Date'] = clean_val(line)
        elif "Name:" in line:
            data['Name'] = clean_val(line)
        elif "Device ID:" in line:
            data['Device_ID'] = clean_val(line)
        elif "Area:" in line: 
            data["Area_um2"] = clean_val(line)
        elif "Thickness:" in line: 
            data["Thickness_nm"] = clean_val(line)
        # Read CVM metadata
        elif "Small-signal amplitude:" in line: 
            data["SS_Amplitude_V"] = clean_val(line)
        elif "Small-signal frequency:" in line: 
            data["SS_Frequency_Hz"] = clean_val(line)
        elif "Mode:" in line: 
            data["Mode"] = clean_val(line)
        elif "Amplitude:" in line: 
            data["Amplitude_V"] = clean_val(line)
        elif "Points:" in line: 
            data["Points"] = clean_val(line)
        elif "Integration:" in line: 
            data["Integration"] = clean_val(line)
        elif "Unipolar:" in line: 
            data["Unipolar"] = clean_val(line)
        elif "Prepol:" in line: 
            data["Prepol"] = clean_val(line)
        elif "Frequency:" in line: 
            data["Frequency_Hz"] = clean_val(line)
        elif "Current range:" in line:
            data["Current_range"] = clean_val(line)
        # PM Writing pulses 
        elif "Positive start:" in line:
            data["PM_Positive_start_V"] = clean_val(line)
        elif "Positive end:" in line:
            data["PM_Positive_end_V"] = clean_val(line)
        elif "Positive steps:" in line:
            data["PM_Positive_steps"] = clean_val(line)
        elif "Negative start:" in line:
            data["PM_Negative_start_V"] = clean_val(line)
        elif "Negative end:" in line:
            data["PM_Negative_end_V"] = clean_val(line)
        elif "Negative steps:" in line:
            data["PM_Negative_steps"] = clean_val(line)
        elif "Rise time:" in line: 
            data["Rise_time_s"] = clean_val(line)

    # Création du DataFrame (index [0] car c'est une seule ligne de données)
    df = pd.DataFrame([data])
    
    return df

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

def extract_read_CVM_dataframes(memCVM_files: list) -> list:
    """
    Extrait les dataframes des fichiers memCVM*.dat.
    Retourne une liste de dataframes enrichis avec Writing_Voltage_V et Loop.
    """

    dataframes = []

    def extract_loop_number(filepath: str) -> int | None:
        """
        Extrait le numéro de loop à partir d'un nom de fichier de type :
        ..._loop-1.dat

        Retourne un int (ex: 1) ou None si non trouvé.
        """
        filename = os.path.basename(filepath)

        match = re.search(r'loop-(\d+)\.dat$', filename)
        if match:
            return int(match.group(1))
        else:
            return None
        

    def extract_writing_voltage(filepath: str) -> float | None:
        """
        Extrait le writing voltage à partir d'un nom de fichier de type :
        memCVM_-1.5Vwr_2025-12-02_...

        Retourne un float (ex: -1.5) ou None si non trouvé.
        """
        filename = os.path.basename(filepath)

        match = re.search(r'memCVM_([+-]?\d+(?:\.\d+)?)Vwr', filename)
        if match:
            return float(match.group(1))
        else:
            return None
        

    for file in memCVM_files:
        df = extract_CVM_dataframe(file)

        Vw = extract_writing_voltage(file)
        loop_number = extract_loop_number(file)

        if Vw is None:
            raise ValueError(f"Impossible d'extraire le writing voltage depuis : {file}")

        if loop_number is None:
            print(f"Impossible d'extraire le loop number depuis : {file}")
            df["Loop"] = None
        else:
            df["Loop"] = int(loop_number)

        df["Writing_Voltage_V"] = float(Vw)

        dataframes.append(df)

    return dataframes


# ──────────────────────────────────────────────────────────────────────────────
#                          
# ──────────────────────────────────────────────────────────────────────────────


def get_vwrite_from_df(df: pd.DataFrame) -> float:
    """
    Récupère le writing voltage stocké dans la colonne 'Writing_Voltage_V'.
    Suppose que la colonne est constante pour tout le DF.
    """
    if "Writing_Voltage_V" not in df.columns:
        raise KeyError("Colonne 'Writing_Voltage_V' absente du DataFrame.")
    
    # Valeur unique (ou première ligne)
    v = df["Writing_Voltage_V"].iloc[0]
    return float(v)


# ──────────────────────────────────────────────────────────────────────────────
#                          
# ──────────────────────────────────────────────────────────────────────────────


def sort_memcvm_dfs(
    dfs: List[pd.DataFrame]
) -> Tuple[List[pd.DataFrame], List[float], List[Optional[int]]]:
    """
    Trie les DataFrames memCVM selon :
      - Si Loop existe : Loop croissant puis Vwrite (positifs croissants puis négatifs par |V|)
      - Si Loop absent : tri uniquement par Vwrite (même logique)

    Retourne (dfs_sorted, vwrite_sorted, loop_sorted)
    """

    def vwrite_sort_key(v: float) -> tuple:
        # positifs d'abord (croissant), puis négatifs (|v| croissant)
        if v > 0:
            return (0, v)
        if v < 0:
            return (1, abs(v))
        return (0, 0)

    def safe_get_loop(df: pd.DataFrame) -> Optional[int]:
        if "Loop" not in df.columns:
            return None
        val = df["Loop"].iloc[0]
        if pd.isna(val):
            return None
        try:
            return int(val)
        except (TypeError, ValueError):
            return None

    # Construire paires (df, loop, vwrite)
    pairs = []
    for df in dfs:
        v = float(get_vwrite_from_df(df))
        loop = safe_get_loop(df)
        pairs.append((df, loop, v))

    has_loop = any(p[1] is not None for p in pairs)

    if not has_loop:
        # Ancien format : on ignore loop
        pairs_sorted = sorted(pairs, key=lambda x: vwrite_sort_key(x[2]))
    else:
        # Nouveau format : loop d'abord, puis vwrite
        # Les df sans loop (None) seront mis à la fin
        pairs_sorted = sorted(
            pairs,
            key=lambda x: (x[1] is None, x[1] if x[1] is not None else 10**9, vwrite_sort_key(x[2]))
        )

    dfs_sorted = [p[0] for p in pairs_sorted]
    vwrite_sorted = [p[2] for p in pairs_sorted]
    loop_sorted = [p[1] for p in pairs_sorted]

    return dfs_sorted, vwrite_sorted, loop_sorted



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

    bias = df[bias_col].values
    cap = df[cap_col].values

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


def mobile_average(window: int, Dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule la moyenne mobile pour toutes les colonnes numériques du DataFrame.
    """
    # On applique le calcul uniquement sur les colonnes numériques
    # .rolling(window) crée une fenêtre glissante
    # .mean() calcule la moyenne de cette fenêtre
    df_result = Dataframe.rolling(window=window,min_periods=1).mean()
    
    return df_result

# ──────────────────────────────────────────────────────────────────────────────
#                          
# ──────────────────────────────────────────────────────────────────────────────

def build_wide_dataframe_from_list(
    Read_CVM_Dataframe: List[pd.DataFrame],
    Vwrite_list: List[float],
    v_col: str = "V",
    c_col: str = "C",
    vwrite_col_name: str = "Vwrite",
    reset_index: bool = True,
) -> pd.DataFrame:
    """
    Construit un DataFrame large de type :
    [Vwrite_0, V_0, C_0, Vwrite_1, V_1, C_1, ...]
    où Vwrite_list[i] correspond au sous-DataFrame Read_CVM_Dataframe[i].

    - reset_index=True aligne par position (utile si les index diffèrent).
    """

    if len(Read_CVM_Dataframe) != len(Vwrite_list):
        raise ValueError(
            f"Longueurs incohérentes : {len(Read_CVM_Dataframe)=} vs {len(Vwrite_list)=}"
        )

    blocks = []

    for i, (df, vwrite) in enumerate(zip(Read_CVM_Dataframe, Vwrite_list)):

        if not isinstance(df, pd.DataFrame) or df.empty:
            continue

        if v_col not in df.columns or c_col not in df.columns:
            raise KeyError(
                f"Colonnes manquantes dans le sous-DF index {i}: "
                f"attendues '{v_col}' et '{c_col}', trouvées {list(df.columns)}"
            )

        tmp = df[[v_col, c_col]].copy()

        if reset_index:
            tmp = tmp.reset_index(drop=True)

        # Ajouter la colonne Vwrite à gauche
        tmp.insert(0, vwrite_col_name, vwrite)

        # Renommer pour rendre chaque bloc unique
        tmp.columns = [f"{vwrite_col_name}_{i}", f"{v_col}_{i}", f"{c_col}_{i}"]

        blocks.append(tmp)

    if len(blocks) == 0:
        return pd.DataFrame()

    return pd.concat(blocks, axis=1)


# ──────────────────────────────────────────────────────────────────────────────
#                          
# ──────────────────────────────────────────────────────────────────────────────

def get_min_max_Voltage(Read_CVM_Dataframe: List[pd.DataFrame]):

    #Suppose to give the min an the max of the Bias V for the reading pulse.

    Vlistmin = []
    Vlistmax = []

    if not Read_CVM_Dataframe:
            raise ValueError("Empty dataframe for the reading CVM measurement.")

    for df in Read_CVM_Dataframe:
        vmin = df["Bias [V]"].min()
        vmax = df["Bias [V]"].max()
        Vlistmin.append(vmin)
        Vlistmax.append(vmax)
    
    V_min = min(Vlistmin)
    V_max = max(Vlistmax)

    return (V_min, V_max)
    

# ──────────────────────────────────────────────────────────────────────────────
#                          
# ──────────────────────────────────────────────────────────────────────────────

def get_min_max_Capacitance(Main_CVM_Dataframe: pd.DataFrame, Read_CVM_Dataframe: List[pd.DataFrame]):

    
    V_range = get_min_max_Voltage(Read_CVM_Dataframe=Read_CVM_Dataframe)

    mask = (Main_CVM_Dataframe["Bias [V]"] >= V_range[0]) & (Main_CVM_Dataframe["Bias [V]"] <= V_range[1])
    df_main_filtered = Main_CVM_Dataframe["C [F]"][mask]

    #Sanity check
    if df_main_filtered.empty:
        raise ValueError("No data in Main_CVM_Dataframe within voltage range.")

    C_min_main = min(df_main_filtered)
    C_max_main = max(df_main_filtered)

    Clistmin = []
    Clistmax = []

    if not Read_CVM_Dataframe:
            raise ValueError("Empty dataframe for the reading CVM measurement.")

    for df in Read_CVM_Dataframe:
        vmin = df["C [F]"].min()
        vmax = df["C [F]"].max()
        Clistmin.append(vmin)
        Clistmax.append(vmax)
    
    C_min_read = min(Clistmin)
    C_max_read = max(Clistmax)

    C_min = min(C_min_main, C_min_read)
    C_max = max(C_max_main, C_max_read)

    return (float(C_min), float(C_max))




# ──────────────────────────────────────────────────────────────────────────────
#                          
# ──────────────────────────────────────────────────────────────────────────────
def write_csv_with_metadata(
    Output_path: str,
    df_metadata: pd.DataFrame,
    df_data: pd.DataFrame,
    sep: str = "\t"
):
    """
    Écrit un CSV avec :
    - metadata (clé \t valeur)
    - ligne vide
    - dataframe principal
    """

    os.makedirs(Output_path, exist_ok=True)
    csv_name = f"{df_metadata['Date'][0]}_{df_metadata['Name'][0]}_{df_metadata['Device_ID'][0]}_memCVM_READ.csv"
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
