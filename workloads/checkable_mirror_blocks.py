"""Check-compatible mirror-block workloads for repeated QED."""
from __future__ import annotations
import random
from qiskit import QuantumCircuit

def _random_body(num_qubits: int, depth: int, rng: random.Random) -> QuantumCircuit:
    body = QuantumCircuit(num_qubits)
    for _ in range(depth):
        for q in range(num_qubits):
            getattr(body, rng.choice(("h", "s", "x")))(q)
        pairs = list(range(num_qubits - 1))
        rng.shuffle(pairs)
        for q in pairs[::2]:
            body.cx(q, q + 1)
    return body

def make_checkable_mirror_blocks(num_qubits: int, total_depth: int, check_interval: int, seed: int) -> list[QuantumCircuit]:
    """Build ideal-identity blocks for nondestructive boundary checks."""
    if num_qubits < 2:
        raise ValueError("num_qubits must be at least 2")
    if total_depth < 1 or check_interval < 1:
        raise ValueError("depth and check_interval must be positive")
    rng = random.Random(seed)
    remaining, blocks = total_depth, []
    while remaining > 0:
        d = min(check_interval, remaining)
        body = _random_body(num_qubits, d, rng)
        blocks.append(body.compose(body.inverse()))
        remaining -= d
    return blocks

def compose_checkable_payload(blocks: list[QuantumCircuit]) -> QuantumCircuit:
    if not blocks:
        raise ValueError("blocks cannot be empty")
    qc = QuantumCircuit(blocks[0].num_qubits)
    for block in blocks:
        qc.compose(block, inplace=True)
    qc.measure_all()
    return qc
