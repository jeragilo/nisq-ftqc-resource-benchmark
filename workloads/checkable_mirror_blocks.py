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

def make_identity_microblocks(num_qubits: int, total_depth: int, seed: int) -> list[QuantumCircuit]:
    """Generate a fixed seeded sequence of unit-depth U U-dagger identity micro-blocks."""
    if num_qubits < 2:
        raise ValueError("num_qubits must be at least 2")
    if total_depth < 1:
        raise ValueError("total_depth must be positive")
    rng = random.Random(seed)
    blocks=[]
    for _ in range(total_depth):
        body=_random_body(num_qubits,1,rng)
        blocks.append(body.compose(body.inverse()))
    return blocks

def group_microblocks(microblocks: list[QuantumCircuit], check_interval: int) -> list[QuantumCircuit]:
    """Group the same underlying micro-block sequence into QED check intervals."""
    if not microblocks:
        raise ValueError("microblocks cannot be empty")
    if check_interval < 1:
        raise ValueError("check_interval must be positive")
    n=microblocks[0].num_qubits
    grouped=[]
    for start in range(0,len(microblocks),check_interval):
        qc=QuantumCircuit(n)
        for block in microblocks[start:start+check_interval]:
            qc.compose(block,inplace=True)
        grouped.append(qc)
    return grouped

def make_checkable_mirror_blocks(num_qubits: int, total_depth: int, check_interval: int, seed: int) -> list[QuantumCircuit]:
    """Compatibility wrapper: fixed micro-workload grouped by requested interval."""
    return group_microblocks(make_identity_microblocks(num_qubits,total_depth,seed),check_interval)

def compose_checkable_payload(blocks: list[QuantumCircuit]) -> QuantumCircuit:
    if not blocks:
        raise ValueError("blocks cannot be empty")
    qc = QuantumCircuit(blocks[0].num_qubits)
    for block in blocks:
        qc.compose(block, inplace=True)
    qc.measure_all()
    return qc
