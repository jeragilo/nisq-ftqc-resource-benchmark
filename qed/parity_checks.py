"""Simple ancilla-assisted parity-check QED utilities for Experiment 2 Phase A."""
from __future__ import annotations

from dataclasses import dataclass

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister


@dataclass
class QEDCheckedCircuit:
    circuit: QuantumCircuit
    data_qubits: int
    ancilla_qubits: int
    syndrome_bits: int


def add_global_z_parity_check(payload: QuantumCircuit) -> QEDCheckedCircuit:
    """
    Append one ancilla that measures global Z parity of the data register.

    This is a deliberately simple Phase-A detector. It is intended to validate
    the postselection/resource pipeline, not to represent full QEC.
    """
    n = payload.num_qubits
    data = QuantumRegister(n, "data")
    anc = QuantumRegister(1, "anc")
    data_c = ClassicalRegister(n, "data_c")
    syn_c = ClassicalRegister(1, "syn_c")
    qc = QuantumCircuit(data, anc, data_c, syn_c)

    # Rebuild payload instructions onto data qubits.
    for inst in payload.data:
        qargs = [data[payload.find_bit(q).index] for q in inst.qubits]
        qc.append(inst.operation, qargs, [])

    # Global Z parity check: ancilla starts |0>, receives CNOTs from data.
    for q in data:
        qc.cx(q, anc[0])
    qc.measure(anc[0], syn_c[0])
    qc.measure(data, data_c)
    return QEDCheckedCircuit(qc, n, 1, 1)


def split_counts(counts: dict[str, int]) -> tuple[int, int, int]:
    """
    Return accepted shots, rejected shots, accepted all-zero-data shots.

    Qiskit prints classical registers in reverse register order. With registers
    (data_c, syn_c), count keys are expected as "syn data".
    """
    accepted = rejected = success = 0
    for key, count in counts.items():
        parts = key.replace(" ", " ").split()
        if len(parts) != 2:
            raise ValueError(f"Unexpected QED count key format: {key!r}")
        syndrome, data_bits = parts[0], parts[1]
        if syndrome == "0":
            accepted += count
            if set(data_bits) <= {"0"}:
                success += count
        else:
            rejected += count
    return accepted, rejected, success
