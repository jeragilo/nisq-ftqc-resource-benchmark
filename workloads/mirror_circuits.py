"""Reproducible mirror-style benchmark circuits."""
from __future__ import annotations

import random

from qiskit import QuantumCircuit


def make_mirror_circuit(num_qubits: int, depth: int, seed: int) -> QuantumCircuit:
    """Return a circuit whose ideal output is |0...0>.

    A seeded random Clifford-like body is followed by its inverse. The requested
    depth is a workload-control parameter, not guaranteed to equal transpiled depth.
    """
    if num_qubits < 2:
        raise ValueError("num_qubits must be at least 2")
    if depth < 1:
        raise ValueError("depth must be positive")

    rng = random.Random(seed)
    body = QuantumCircuit(num_qubits)

    for _ in range(depth):
        for q in range(num_qubits):
            gate = rng.choice(("h", "s", "x"))
            getattr(body, gate)(q)
        pairs = list(range(num_qubits - 1))
        rng.shuffle(pairs)
        for q in pairs[::2]:
            body.cx(q, q + 1)

    circuit = body.compose(body.inverse())
    circuit.measure_all()
    return circuit
