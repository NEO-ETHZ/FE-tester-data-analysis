

import os

def list_files_in_folder(folder_path: str) -> list:
    """
    Returns a list of all files (with full paths) inside the given folder.
    """
    files = []
    for fname in os.listdir(folder_path):
        full_path = os.path.join(folder_path, fname)
        if os.path.isfile(full_path):
            files.append(full_path)
    return files



def filter_cvm_files(files: list) -> dict:
    """
    Filters files into two categories:
      - memCVM*.dat
      - mainCVM*.dat

    """
    mem_files = []
    main_files = None

    for f in files:
        name = os.path.basename(f)

        if name.startswith("memCVM") and name.endswith(".dat"):
            mem_files.append(f)

        if name.startswith("mainCVM") and name.endswith(".dat"):
            main_files = f

    return mem_files, main_files


def find_seq_file(path):
    """
    Trouve le fichier .seq dans le même dossier que le fichier CVM donné.
    Retourne le chemin complet du fichier .seq ou None si non trouvé.
    """
    for file in os.listdir(path):
        if file.endswith('.seq'):
            return os.path.join(path, file)
    return None




















