from dataclasses import dataclass, field
import numpy as np

@dataclass
class CrystalFieldParams:
    """
    Full crystal field parameter set for Quanty CTM simulation.
    All energy parameters in eV. Only ten_dq is varied by default —
    all other fields have physically motivated defaults for Co(terpy)2³⁺.
    """


    # --- required fields (no defaults) ---
    ten_dq_i: float
    ten_dq_f: float
    Ds_3d_i: float
    Dt_3d_i: float
    scalef2_3d3d_i: float
    scalef4_3d3d_i: float
    scaleg: float

    # --- initial state ---
    NPsi_i: int = 50
    scale_3dSOC_i: float = 0.8
    U_3d_3d_i: float = 5.0

    # --- final state ---
    NPsi_f: int = 50
    Ds_3d_f: float = None
    Dt_3d_f: float = None
    scalef2_3d3d_f: float = None
    scalef4_3d3d_f: float = None
    scale_3dSOC_f: float = 0.8
    U_3d_3d_f: float = 5.0
    U_2p_3d_f: float = 6.0
    scalef2_2p3d: float = 0.2
    scale_2pSOC: float = 0.8
    E_2p: float = 754.7

    # --- initial state ---
   

    def __post_init__(self):
        if self.Ds_3d_f is None:
            self.Ds_3d_f = self.Ds_3d_i
        if self.Dt_3d_f is None:
            self.Dt_3d_f = self.Dt_3d_i
        if self.scalef2_3d3d_f is None:
            self.scalef2_3d3d_f = self.scalef2_3d3d_i
        if self.scalef4_3d3d_f is None:
            self.scalef4_3d3d_f = self.scalef4_3d3d_i

    def to_dict(self) -> dict:
        return {
        "tenDq_3d_i": self.ten_dq_i,
        "tenDq_3d_f": self.ten_dq_f,
        "Ds_3d_i": self.Ds_3d_i,
        "Dt_3d_i": self.Dt_3d_i,
        "scalef2_3d3d_i": self.scalef2_3d3d_i,
        "scalef4_3d3d_i": self.scalef4_3d3d_i,
        "scaleg": self.scaleg
        }

    def to_array(self) -> np.ndarray:
        return np.array([self.ten_dq_i, 
                         self.ten_dq_f, 
                         self.Ds_3d_i, 
                         self.Dt_3d_i, 
                         self.scalef2_3d3d_i, 
                         self.scalef4_3d3d_i, 
                         self.scaleg])

    @classmethod
    def from_array(cls, arr: np.ndarray) -> "CrystalFieldParams":
        return cls(ten_dq_i=arr[0], 
                   ten_dq_f=arr[1], 
                   Ds_3d_i=arr[2], 
                   Dt_3d_i=arr[3], 
                   scalef2_3d3d_i=arr[4], 
                   scalef4_3d3d_i=arr[5], 
                   scaleg=arr[6])