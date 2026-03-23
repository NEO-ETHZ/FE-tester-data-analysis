import io
import pandas as pd
import re
import os
from typing import List, Tuple, Optional
from src.file_path import find_seq_file
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from collections import defaultdict




def ensure_ndarrays(
    V_write: np.ndarray | List[float],
    C_array: np.ndarray | List[float],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Ensure ndarray for the analysis.
    """
    Vw = np.asarray(V_write, dtype=float)
    C = np.asarray(C_array, dtype=float)


    return Vw, C




def round_vwrite_to_step(
    Vw: np.ndarray,
    round_by: float,
) -> np.ndarray:
    """
    Yooow this is is simply cut the data into bins of voltage like the following exemple :

    | Vw original | Vw / step | round | Vw_round |
    | ----------- | --------- | ----- | -------- |
    | 0.12        | 2.40      | 2     | 0.10     |
    | 0.13        | 2.60      | 3     | 0.15     |
    | 0.14        | 2.80      | 3     | 0.15     |
    | 0.16        | 3.20      | 3     | 0.15     |
    | 0.17        | 3.40      | 3     | 0.15     |
    | 0.18        | 3.60      | 4     | 0.20     |

    And in the rest of the analysis we will use Vw_round
    """
    step = float(round_by)

    if step <= 0:
        raise ValueError("round_by used as step must be > 0")

    Vw_round = np.round(Vw / step) * step

    # remove tiny floating-point noise
    if step < 1:
        decimals = max(0, int(np.ceil(-np.log10(step))) + 6)
    else:
        decimals = 6

    Vw_round = np.round(Vw_round, decimals)

    print(f"Here is the list of the rounded voltage use for the analysis :{np.unique(Vw_round)}")

    return Vw_round





def select_indices_from_vwrite_direction(
    Vw: np.ndarray,
    Vw_round: np.ndarray,
    vwrite_threshold_pos: float,
    vwrite_threshold_neg: float,
) -> np.ndarray:
    """
    a) np.diff(Vw, prepend=Vw[0])

    np.diff(Vw) calcule :

    Vw[i]−Vw[i−1]

    prepend=Vw[0] sert à garder la même longueur que Vw

    This part of the code is mainly to simply select the datapoint that have interest in the LTP-LTD.
    We remove the point to close to zero and the point that makes no sens
    (like noisy one where dV change sign frequently)
    Cool but not obvious
    """
    dV = np.sign(np.diff(Vw, prepend=Vw[0]))

    sel_pos = (Vw_round > vwrite_threshold_pos) & (dV > 0)
    sel_neg = (Vw_round < -vwrite_threshold_neg) & (dV < 0)

    sel = sel_pos | sel_neg

    selected_idx = np.flatnonzero(sel)

    return selected_idx




def group_by_rounded_voltage(
    Vw_round: np.ndarray,
    Y: np.ndarray,
    selected_idx: np.ndarray,
) -> Dict[float, np.ndarray]:
    """
    Yooow this is a hard cookie as well, so basically we regroupe every resistance for the same rounded voltage

    C_grouped_by_V = {
        0.15: [2.1e7, 2.0e7, 2.2e7, ...],
        0.20: [1.9e7, 2.05e7, 2.1e7, ...],
        0.25: [2.3e7, 2.4e7, ...],
        ...
    }
    """
    C_grouped_by_V = defaultdict(list)

    for v, r in zip(Vw_round[selected_idx], Y[selected_idx]):
        C_grouped_by_V[v].append(r)

    # convert each list to ndarray (expanded form, no one-liner dict comprehension)
    """
    Okay now he converts the list into array cause histogram in the plot need array instead of list !
    I'm talking about the list within the dictionary maboi. array is a numpy object, list is not.
    """
    C_grouped_by_V_arrays: Dict[float, np.ndarray] = {}

    for key in C_grouped_by_V:
        values_list = C_grouped_by_V[key]
        values_array = np.asarray(values_list)
        C_grouped_by_V_arrays[key] = values_array

    C_grouped_by_V_final = C_grouped_by_V_arrays

    return C_grouped_by_V_final
    #What are you doing so deep in my code ? 




def build_common_hist_bins(
    C_grouped_by_V: Dict[float, np.ndarray],
    n_bins: int = 100,
) -> np.ndarray:
    """
    Okay so here we put every resistance together and we do that so we can construct easily an histogram.
    It's simply because the histogram function needs a big array with every resistance in the same bag.
    Until now we had a dictionary of array.

    -> But to be honest I just realized this function is useless lmao, We could have just give the R["R_pos_ohm"] column
    to the onstruction of bins.
    """
    if len(C_grouped_by_V) == 0:
        all_R = np.array([])
    else:
        all_values = []

        for k in C_grouped_by_V:
            vs = C_grouped_by_V[k]
            if len(vs) > 0:
                all_values.append(vs)

        if len(all_values) == 0:
            all_R = np.array([])
        else:
            all_R = np.concatenate(all_values)

    if all_R.size == 0:
        raise ValueError("No data after selection; check thresholds.")

    """
    Popopopoooo maboi here the bins are constructed in a linear way !
    Apparently we can also construct the bins in a logarithmic way. need to investigate that shit maboi

    np.histogram_bin_edges(all_R, bins=100)
    [min(R) -------------------- max(R)]
        |--|--|--|--|--|--|  ← 100 bins
    """
    bins = np.histogram_bin_edges(all_R, bins=n_bins)

    return bins