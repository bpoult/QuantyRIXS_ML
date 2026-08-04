from dataclasses import dataclass
import numpy as np

@dataclass
class CrystalFieldParams:
    """
    Full crystal field + charge transfer parameter set for Quanty CTM simulation.
    All energy parameters in eV.
    
    Required fields must be specified. Optional fields have physically motivated 
    defaults for Co(terpy)2³⁺. CT parameters default to 0 (pure CF mode).
    Final state parameters are derived from initial state in __post_init__ if not specified.
    """

    # ── Required CF parameters (no defaults, must be specified) ──────────────
    ten_dq_i: float
    ten_dq_f: float
    Ds_3d_i: float
    Dt_3d_i: float
    scalef2_3d3d_i: float
    scalef4_3d3d_i: float
    scaleg: float

    # ── CF initial state fixed defaults ──────────────────────────────────────
    NPsi_i: int = 50
    scale_3dSOC_i: float = 0.8
    U_3d_3d_i: float = 5.0

    # ── CF final state (derived from initial in __post_init__ if None) ────────
    NPsi_f: int = 50
    Ds_3d_f: float = None
    Dt_3d_f: float = None
    scalef2_3d3d_f: float = None
    scalef4_3d3d_f: float = None
    scale_3dSOC_f: float = 0.8
    scale_2pSOC: float = 0.8
    scalef2_2p3d: float = 0.2
    U_3d_3d_f: float = 5.0
    U_2p_3d_f: float = 6.0
    E_2p: float = None                  # set per-complex in config JSON

    # ── CT initial state (freely sampled, default 0 = pure CF mode) ──────────
    Delta_3d_L1_i: float = 0.0         # range [-4, 4]
    Veg_3d_L1_i: float = 0.0           # range [0, 4]
    Vt2g_3d_L1_i: float = 0.0          # range [0, 2]
    Delta_3d_L2_i: float = 0.0         # range [0, 5]
    Vt2g_3d_L2_i: float = 0.0          # range [0, 3]

    # ── CT final state (derived from initial in __post_init__ if None) ────────
    Delta_3d_L1_f: float = None        # Delta_3d_L1_i + offset [-2, 0]
    Veg_3d_L1_f: float = None          # Veg_3d_L1_i * reduction [0.75, 1.0]
    Vt2g_3d_L1_f: float = None         # Vt2g_3d_L1_i * reduction [0.75, 1.0]
    Delta_3d_L2_f: float = None        # Delta_3d_L2_i + offset [0, 2]
    Vt2g_3d_L2_f: float = None         # Vt2g_3d_L2_i * reduction [0.75, 1.0]

    # ── Fixed at 0 — never varied ─────────────────────────────────────────────
    ten_dq_L1_i: float = 0.0
    ten_dq_L2_i: float = 0.0
    ten_dq_L1_f: float = 0.0
    ten_dq_L2_f: float = 0.0
    Veg_3d_L2_i: float = 0.0
    Veg_3d_L2_f: float = 0.0

    def __post_init__(self):
        # CF final state defaults to initial state values
        if self.Ds_3d_f is None:
            self.Ds_3d_f = self.Ds_3d_i
        if self.Dt_3d_f is None:
            self.Dt_3d_f = self.Dt_3d_i
        if self.scalef2_3d3d_f is None:
            self.scalef2_3d3d_f = self.scalef2_3d3d_i
        if self.scalef4_3d3d_f is None:
            self.scalef4_3d3d_f = self.scalef4_3d3d_i

        # CT final state defaults to initial state values
        # Offsets and reductions are applied during sampling in generate_dataset.py
        if self.Delta_3d_L1_f is None:
            self.Delta_3d_L1_f = self.Delta_3d_L1_i
        if self.Veg_3d_L1_f is None:
            self.Veg_3d_L1_f = self.Veg_3d_L1_i
        if self.Vt2g_3d_L1_f is None:
            self.Vt2g_3d_L1_f = self.Vt2g_3d_L1_i
        if self.Delta_3d_L2_f is None:
            self.Delta_3d_L2_f = self.Delta_3d_L2_i
        if self.Vt2g_3d_L2_f is None:
            self.Vt2g_3d_L2_f = self.Vt2g_3d_L2_i

    def to_dict(self) -> dict:
        """Convert to dict with Quanty-expected key names."""
        return {
            "tenDq_3d_i": self.ten_dq_i,
            "tenDq_3d_f": self.ten_dq_f,
            "Ds_3d_i": self.Ds_3d_i,
            "Dt_3d_i": self.Dt_3d_i,
            "scalef2_3d3d_i": self.scalef2_3d3d_i,
            "scalef4_3d3d_i": self.scalef4_3d3d_i,
            "scaleg": self.scaleg,
            "Delta_3d_L1_i": self.Delta_3d_L1_i,
            "Veg_3d_L1_i": self.Veg_3d_L1_i,
            "Vt2g_3d_L1_i": self.Vt2g_3d_L1_i,
            "Delta_3d_L2_i": self.Delta_3d_L2_i,
            "Vt2g_3d_L2_i": self.Vt2g_3d_L2_i,
        }

    def to_array(self) -> np.ndarray:
        """
        Convert varied parameters to numpy array for ML model.
        Order: [CF params (7), CT initial params (5)] = 12 total
        """
        return np.array([
            # CF parameters
            self.ten_dq_i,
            self.ten_dq_f,
            self.Ds_3d_i,
            self.Dt_3d_i,
            self.scalef2_3d3d_i,
            self.scalef4_3d3d_i,
            self.scaleg,
            # CT parameters
            self.Delta_3d_L1_i,
            self.Veg_3d_L1_i,
            self.Vt2g_3d_L1_i,
            self.Delta_3d_L2_i,
            self.Vt2g_3d_L2_i,
        ])

    @classmethod
    def from_array(cls, arr: np.ndarray) -> "CrystalFieldParams":
        """Reconstruct from ML model output array."""
        return cls(
            # CF parameters
            ten_dq_i=arr[0],
            ten_dq_f=arr[1],
            Ds_3d_i=arr[2],
            Dt_3d_i=arr[3],
            scalef2_3d3d_i=arr[4],
            scalef4_3d3d_i=arr[5],
            scaleg=arr[6],
            # CT parameters
            Delta_3d_L1_i=arr[7],
            Veg_3d_L1_i=arr[8],
            Vt2g_3d_L1_i=arr[9],
            Delta_3d_L2_i=arr[10],
            Vt2g_3d_L2_i=arr[11],
        )