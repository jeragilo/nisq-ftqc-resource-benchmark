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

def _unitary_block(block: QuantumCircuit) -> QuantumCircuit:
    """Return a block with terminal measurements removed defensively."""
    try:
        return block.remove_final_measurements(inplace=False)
    except AttributeError:
        qc = block.copy()
        while qc.data and qc.data[-1].operation.name == "measure":
            qc.data.pop()
        return qc

def add_repeated_boundary_parity_checks(blocks: list[QuantumCircuit]) -> RepeatedQEDCircuit:
    """
    Insert repeated boundary parity checks using one reusable ancilla.

    Each check writes to a distinct classical syndrome bit, then resets the same
    ancilla before the next block. This models sequential syndrome extraction
    without allocating one physical ancilla per check round.
    """
    if not blocks:
        raise ValueError("blocks cannot be empty")

    clean_blocks = [_unitary_block(block) for block in blocks]
    n, rounds = clean_blocks[0].num_qubits, len(clean_blocks)
    data = QuantumRegister(n, "data")
    anc = QuantumRegister(1, "anc")
    data_c = ClassicalRegister(n, "data_c")
    syn_c = ClassicalRegister(rounds, "syn_c")
    qc = QuantumCircuit(data, anc, data_c, syn_c)

    for r, block in enumerate(clean_blocks):
        if block.num_qubits != n:
            raise ValueError("all blocks must have the same width")
        for inst in block.data:
            if inst.operation.name == "measure":
                raise ValueError("internal measurement found inside a QED unitary block")
            qargs = [data[block.find_bit(q).index] for q in inst.qubits]
            qc.append(inst.operation, qargs, [])
        for q in data:
            qc.cx(q, anc[0])
        qc.measure(anc[0], syn_c[r])
        if r != rounds - 1:
            qc.reset(anc[0])

    qc.measure(data, data_c)
    return RepeatedQEDCircuit(qc, n, 1, rounds, rounds)

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
