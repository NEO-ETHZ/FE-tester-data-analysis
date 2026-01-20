

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

    for f in files:
        name = os.path.basename(f)

        if name.endswith(".dat"):
            mem_files.append(f)


    return mem_files










































