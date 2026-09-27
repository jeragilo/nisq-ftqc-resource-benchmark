"""Common reliability and resource records for Paper 2 experiments."""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ResourceRecord:
    method: str
    qubits: int
    nominal_depth: int
    transpiled_depth: int
    one_qubit_gates: int
    two_qubit_gates: int
    shots: int
    noise_probability: float
    seed: int
    success_probability: float
    absolute_error: float
    classical_seconds: float

    def as_dict(self) -> dict:
        return asdict(self)
