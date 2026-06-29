from dataclasses import dataclass, field
import numpy as np

@dataclass
class CrystalFieldParams:
    """
    Crystal field parameters for Quanty CTM simulation.
    All energy parameters in eV.
    """

    ten_dq: float
    scale_dd: float = 0.8
    scale_pd: float = 0.8
    gamma_lorentz: float = 0.2

    def to_dict(self) -> dict:
        return {
            "10Dq": self.ten_dq,
            "scale_dd": self.scale_dd,
            "scale_pd": self.scale_pd,
            "Gamma": self.gamma_lorentz
        }
    
    def to_array(self) -> np.ndarray:
        return np.array([self.ten_dq, self.scale_dd, self.scale_pd, self.gamma_lorentz])
    
    @classmethod
    def from_array(cls, arr: np.ndarray) -> "CrystalFieldParams":
        return cls(ten_dq=arr[0], scale_dd=arr[1], scale_pd=arr[2], gamma_lorentz=arr[3])