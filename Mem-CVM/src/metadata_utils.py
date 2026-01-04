import io
import pandas as pd
import re
import os
from typing import List, Tuple
from src.file_path import find_seq_file



def seq_file_parsing(path):

    path_seq_file = find_seq_file(path)

    if path_seq_file is None:
        raise FileNotFoundError("Fichier .seq introuvable dans le même dossier que les fichiers CVM.")
    
    with open(path_seq_file, 'r') as f:
        # On utilise splitlines() pour boucler sur chaque ligne du fichier 
        lines = f.read().splitlines()

    # Dictionnaire pour stocker les valeurs propres
    data = {}

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
        if "Name:" in line:
            data["Name"] = clean_val(line)
        elif "Rise time:" in line: 
            data["Rise_time_s"] = clean_val(line)
        elif "Area:" in line: 
            data["Area_um2"] = clean_val(line)
        elif "Thickness:" in line: 
            data["Thickness_nm"] = clean_val(line)
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

    # Création du DataFrame (index [0] car c'est une seule ligne de données)
    df = pd.DataFrame([data])
    
    return df


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



def extract_read_CVM_dataframes(memCVM_files: list) -> list:
    """
    Extrait les dataframes des fichiers memCVM*.dat.
    Retourne une liste de dataframes.
    """

    dataframes = []
    for file in memCVM_files:
        df = extract_CVM_dataframe(file)
        Vw = extract_writing_voltage(file)
        Vw = float(Vw)

        df['Writing_Voltage_V'] = Vw
        dataframes.append(df)

    return dataframes



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




def sort_memcvm_dfs(dfs: List[pd.DataFrame]) -> Tuple[List[pd.DataFrame], List[float]]:
    """
    Trie les DataFrames memCVM selon leur Writing_Voltage_V :

      1) Tous les Vwrite > 0 : triés du plus petit au plus grand
      2) Puis tous les Vwrite < 0 : triés du plus proche de 0 vers le plus négatif

    Retourne (dfs_trié, liste_Vwrite_trié)
    """
    # Construire liste de paires (df, Vwrite)
    pairs = []
    for df in dfs:
        v = get_vwrite_from_df(df)
        pairs.append((df, v))

    pos = [p for p in pairs if p[1] > 0]
    neg = [p for p in pairs if p[1] < 0]

    # Positifs : 0.5 → 2.5
    pos.sort(key=lambda x: x[1])

    # Négatifs : -0.5, -0.833, ..., -2.5  (du plus proche de 0 au plus extrême)
    neg.sort(key=lambda x: abs(x[1]))

    ordered = pos + neg

    dfs_sorted = [p[0] for p in ordered]
    vwrite_sorted = [p[1] for p in ordered]

    return dfs_sorted, vwrite_sorted




def get_capacitance_near_target_bias(df: pd.DataFrame, target: float) -> float:
    """
    Retourne la valeur de la capacitance (C [F]) la plus proche de Bias = target V.
    """
    if "Bias [V]" not in df.columns or "C [F]" not in df.columns:
        raise KeyError("Colonnes 'Bias [V]' ou 'C [F]' absentes du DataFrame.")
    if target > max(df["Bias [V]"]):
        raise ValueError("The target value is higher than the maximum reading bias voltage, decrease the value of the target.")
    if target < min(df["Bias [V]"]):
        raise ValueError("The target value is lower than the minimum reading bias voltage, increase the value of the target.")

    # Trouver l'index où Bias est le plus proche de la target
    idx_closest = (df["Bias [V]"] - target).abs().idxmin()

    capacitance = df.at[idx_closest, "C [F]"]
    return capacitance




def mobile_average(window: int, Dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule la moyenne mobile pour toutes les colonnes numériques du DataFrame.
    """
    # On applique le calcul uniquement sur les colonnes numériques
    # .rolling(window) crée une fenêtre glissante
    # .mean() calcule la moyenne de cette fenêtre
    df_result = Dataframe.rolling(window=window,min_periods=1).mean()
    
    return df_result