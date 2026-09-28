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


def _payload_without_final_measurements(payload: QuantumCircuit) -> QuantumCircuit:
    """
    Return the payload with final measurements removed.

    Experiment-0/1 mirror circuits include terminal measurements. QED must insert
    the syndrome check before the final data readout, so those terminal
    measurements cannot be copied into the checked circuit.
    """
    try:
        return payload.remove_final_measurements(inplace=False)
    except AttributeError:
        qc = payload.copy()
        while qc.data and qc.data[-1].operation.name == "measure":
            qc.data.pop()
        return qc


def add_global_z_parity_check(payload: QuantumCircuit) -> QEDCheckedCircuit:
    """
    Append one ancilla that measures global Z parity of the data register.

    This is a deliberately simple Phase-A detector. It is intended to validate
    the postselection/resource pipeline, not to represent full QEC.
    """
    unitary_payload = _payload_without_final_measurements(payload)
    n = unitary_payload.num_qubits

    data = QuantumRegister(n, "data")
    anc = QuantumRegister(1, "anc")
    data_c = ClassicalRegister(n, "data_c")
    syn_c = ClassicalRegister(1, "syn_c")
    qc = QuantumCircuit(data, anc, data_c, syn_c)

    for inst in unitary_payload.data:
        qargs = [data[unitary_payload.find_bit(q).index] for q in inst.qubits]
        cargs = []
        if inst.clbits:
            cargs = [data_c[unitary_payload.find_bit(c).index] for c in inst.clbits]
        qc.append(inst.operation, qargs, cargs)

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
        parts = key.split()
        if len(parts) != 2:
            raise ValueError(f"Unexpected QED count key format: {key!r}")
        syndrome, data_bits = parts
        if syndrome == "0":
            accepted += count
            if set(data_bits) <= {"0"}:
                success += count
        else:
            rejected += count
    return accepted, rejected, success
