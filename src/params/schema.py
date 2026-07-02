from dataclasses import dataclass, field
import numpy as np

@dataclass
class CrystalFieldParams:
    """
    Full crystal field parameter set for Quanty CTM simulation.
    All energy parameters in eV. Only ten_dq is varied by default —
    all other fields have physically motivated defaults for Co(terpy)2³⁺.
    """

    # --- currently varied parameters ---
    ten_dq_i: float
    ten_dq_f: float

    # --- initial state
    NPsi_i: int = 50
    Ds_3d_i: float = 0.0
    Dt_3d_i: float = 0.0
    scalef2_3d3d_i: float = 0.68
    scalef4_3d3d_i: float = 0.8
    scale_3dSOC_i: float = 0.8
    U_3d_3d_i: float = 0.0

    # --- final state ---
    NPsi_f: int = 50
    Ds_3d_f: float = 0.0
    Dt_3d_f: float = 0.0
    scalef2_3d3d_f: float = 0.68
    scalef4_3d3d_f: float = 0.8
    scale_3dSOC_f: float = 0.8
    U_3d_3d_f: float = 0.0
    U_2p_3d_f: float = 0.0
    scalef2_2p3d: float = 0.2
    scaleg: float = 0.6
    scale_2pSOC: float = 0.8
    E_2p: float = 778.0

    def to_dict(self) -> dict:
        return {
        "tenDq_3d_i": self.ten_dq_i,
        "tenDq_3d_f": self.ten_dq_f,
        }

    def to_array(self) -> np.ndarray:
        return np.array([self.ten_dq_i, self.ten_dq_f])

    @classmethod
    def from_array(cls, arr: np.ndarray) -> "CrystalFieldParams":
        return cls(ten_dq_i=arr[0], ten_dq_f=arr[1])