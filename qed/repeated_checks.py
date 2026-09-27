"""Repeated boundary QED for check-compatible mirror blocks."""
from __future__ import annotations
from dataclasses import dataclass
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

@dataclass
class RepeatedQEDCircuit:
    circuit: QuantumCircuit
    data_qubits: int
    ancilla_qubits: int
    syndrome_bits: int
    check_rounds: int

def add_repeated_boundary_parity_checks(blocks: list[QuantumCircuit]) -> RepeatedQEDCircuit:
    """Insert a fresh ancilla parity check after each ideal-identity mirror block."""
    if not blocks:
        raise ValueError("blocks cannot be empty")
    n, rounds = blocks[0].num_qubits, len(blocks)
    data = QuantumRegister(n, "data")
    anc = QuantumRegister(rounds, "anc")
    data_c = ClassicalRegister(n, "data_c")
    syn_c = ClassicalRegister(rounds, "syn_c")
    qc = QuantumCircuit(data, anc, data_c, syn_c)
    for r, block in enumerate(blocks):
        if block.num_qubits != n:
            raise ValueError("all blocks must have the same width")
        for inst in block.data:
            qargs = [data[block.find_bit(q).index] for q in inst.qubits]
            qc.append(inst.operation, qargs, [])
        for q in data:
            qc.cx(q, anc[r])
        qc.measure(anc[r], syn_c[r])
    qc.measure(data, data_c)
    return RepeatedQEDCircuit(qc, n, rounds, rounds, rounds)

def split_repeated_counts(counts: dict[str, int]) -> tuple[int, int, int]:
    """Accept only shots with an all-zero multi-round syndrome."""
    accepted = rejected = success = 0
    for key, count in counts.items():
        parts = key.split()
        if len(parts) != 2:
            raise ValueError(f"Unexpected repeated-QED key: {key!r}")
        syndrome, data_bits = parts
        if set(syndrome) <= {"0"}:
            accepted += count
            if set(data_bits) <= {"0"}:
                success += count
        else:
            rejected += count
    return accepted, rejected, success
