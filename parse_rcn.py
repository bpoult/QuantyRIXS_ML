import re
from pathlib import Path


# Neutral ground-state electron counts (3d, 4s) for Sc-Zn (Z=21-30).
# Elements with anomalous ground-state configurations (Cr, Cu) are listed
# with their actual configurations, not the [Ar] 3d^n 4s^2 default.
# Ionisation removes 4s electrons first, then 3d electrons.
#
#   Cr: [Ar] 3d5 4s1
#   Cu: [Ar] 3d10 4s1
#
# For example, Co ([Ar] 3d7 4s2) → Co3+: remove 2 from 4s, 1 from 3d → 3d6
#
_VALENCE_NEUTRAL = {
    #         (3d, 4s)
    'Sc': (1,  2),
    'Ti': (2,  2),
    'V':  (3,  2),
    'Cr': (5,  1),   # anomaly: 3d5 4s1
    'Mn': (5,  2),
    'Fe': (6,  2),
    'Co': (7,  2),
    'Ni': (8,  2),
    'Cu': (10, 1),   # anomaly: 3d10 4s1
    'Zn': (10, 2),
}


def _d_count_for_ion(atom: str, charge: str) -> int:
    """Return the number of 3d electrons for a given ion.

    Electrons are removed from 4s first, then from 3d, consistent with
    standard transition-metal ionisation chemistry and the labelling used
    in RCNparameter.txt.

    Parameters
    ----------
    atom   : element symbol, e.g. 'Co'
    charge : charge string, e.g. '3+' or '3'

    Returns
    -------
    int : number of 3d electrons
    """
    atom = atom.strip().capitalize()
    if atom not in _VALENCE_NEUTRAL:
        raise ValueError(
            f"Element '{atom}' is not in the lookup table. "
            f"Supported elements: {list(_VALENCE_NEUTRAL.keys())}"
        )

    # Accept '3+', '+3', '3', 3, etc.
    charge_str = str(charge).strip().replace('+', '').replace('-', '')
    charge_int = int(charge_str)

    d_neutral, s_neutral = _VALENCE_NEUTRAL[atom]

    # Remove from 4s first, then from 3d
    remaining_charge = charge_int
    s_ion = max(0, s_neutral - remaining_charge)
    remaining_charge = max(0, remaining_charge - s_neutral)
    d_ion = max(0, d_neutral - remaining_charge)

    return d_ion


def _parse_rcn_line(line: str) -> dict:
    """Parse a single data line from RCNparameter.txt into a dict of floats.

    Each token has the form  KEY=VALUEeV  (e.g. F2_3d3d=12.66316eV).
    Returns a dict mapping key -> float value.
    """
    result = {}
    # Match patterns like  KEY=1.23456eV  or  KEY=0.000eV
    for match in re.finditer(r'(\w+)=([\d.]+)eV', line):
        key = match.group(1)
        val = float(match.group(2))
        result[key] = val
    return result


def parse_rcn_parameters(atom: str, charge: str, edge: str, rcn_file) -> dict:
    """Look up atomic Hartree-Fock Slater integrals and SOC constants from
    RCNparameter.txt for a given transition-metal ion and absorption edge.

    Parameters
    ----------
    atom     : element symbol, e.g. 'Co'
    charge   : charge string, e.g. '3+'
    edge     : absorption edge, e.g. 'L'  (only 'L' is currently supported)
    rcn_file : path to RCNparameter.txt

    Returns
    -------
    dict with keys:
        F2_3d3d_i_rcn, F4_3d3d_i_rcn, zeta_3d_i_rcn   (from initial-state line)
        F2_3d3d_f_rcn, F4_3d3d_f_rcn,                  (from final-state line)
        F2_2p3d_rcn, G1_2p3d_rcn, G3_2p3d_rcn,         (from final-state line)
        zeta_3d_f_rcn, zeta_2p_rcn                      (from final-state line)

    Raises
    ------
    NotImplementedError  if edge != 'L'
    ValueError           if the required lines are not found in rcn_file
    """
    edge = edge.strip().upper()
    if edge != 'L':
        raise NotImplementedError(
            f"Edge '{edge}' is not implemented yet. "
            "Only 'L' edge is currently supported."
        )

    atom = atom.strip().capitalize()
    # Normalise charge to the form used in the file, e.g. '3+'
    charge_str = str(charge).strip()
    charge_int = int(charge_str.replace('+', '').replace('-', ''))
    charge_label = f"{charge_int}+"   # RCNparameter.txt uses e.g. "Co3+"

    d_count = _d_count_for_ion(atom, charge_str)

    # Build the search strings for the two lines we need.
    # Initial state: full 2p shell (2p06), d_count 3d electrons
    # Final state  : core hole   (2p05), d_count+1 3d electrons
    ion_label = f"{atom}{charge_label}"   # e.g. "Co3+"
    d_i_str   = f"3d{d_count:02d}"        # e.g. "3d06"
    d_f_str   = f"3d{d_count + 1:02d}"   # e.g. "3d07"
    init_tag  = f"2p06 {d_i_str}  {ion_label}"
    final_tag = f"2p05 {d_f_str}  {ion_label}"

    rcn_path = Path(rcn_file)
    if not rcn_path.exists():
        raise FileNotFoundError(f"RCN parameter file not found: {rcn_file}")

    init_line  = None
    final_line = None

    with open(rcn_path, 'r') as fh:
        for line in fh:
            if init_tag in line:
                init_line = line
            if final_tag in line:
                final_line = line
            if init_line and final_line:
                break

    if init_line is None:
        raise ValueError(
            f"Could not find initial-state line for '{ion_label}' L-edge "
            f"(searched for '{init_tag}') in {rcn_file}"
        )
    if final_line is None:
        raise ValueError(
            f"Could not find final-state line for '{ion_label}' L-edge "
            f"(searched for '{final_tag}') in {rcn_file}"
        )

    i_params = _parse_rcn_line(init_line)
    f_params = _parse_rcn_line(final_line)

    def _get(params, key, line_desc):
        if key not in params:
            raise ValueError(
                f"Parameter '{key}' not found in {line_desc} line:\n  {line_desc}"
            )
        return params[key]

    return {
        # --- initial state (2p6 3dN) ---
        'F2_3d3d_i_rcn':  _get(i_params, 'F2_3d3d',  init_tag),
        'F4_3d3d_i_rcn':  _get(i_params, 'F4_3d3d',  init_tag),
        'zeta_3d_i_rcn':  _get(i_params, 'SOC_3d',   init_tag),
        # --- final state (2p5 3d(N+1)) ---
        'F2_3d3d_f_rcn':  _get(f_params, 'F2_3d3d',  final_tag),
        'F4_3d3d_f_rcn':  _get(f_params, 'F4_3d3d',  final_tag),
        'F2_2p3d_rcn':    _get(f_params, 'F2_2p3d',  final_tag),
        'G1_2p3d_rcn':    _get(f_params, 'G1_2p3d',  final_tag),
        'G3_2p3d_rcn':    _get(f_params, 'G3_2p3d',  final_tag),
        'zeta_3d_f_rcn':  _get(f_params, 'SOC_3d',   final_tag),
        'zeta_2p_rcn':    _get(f_params, 'SOC_2p',   final_tag),
    }
