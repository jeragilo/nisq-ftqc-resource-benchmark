"""Minimal digital zero-noise extrapolation utilities for Experiment 0."""
from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit


def global_fold(circuit: QuantumCircuit, scale: int) -> QuantumCircuit:
    """Globally fold the unitary portion for odd integer noise scale factors.

    Measurements are removed before folding and restored afterward.
    """
    if scale < 1 or scale % 2 == 0:
        raise ValueError("scale must be a positive odd integer")

    unitary = circuit.remove_final_measurements(inplace=False)
    folded = unitary.copy()
    repetitions = (scale - 1) // 2
    inverse = unitary.inverse()
    for _ in range(repetitions):
        folded = folded.compose(inverse).compose(unitary)
    folded.measure_all()
    return folded


def linear_zero_noise_extrapolation(scales, values) -> float:
    """Return the intercept of a linear fit versus noise scale."""
    x = np.asarray(scales, dtype=float)
    y = np.asarray(values, dtype=float)
    if x.size < 2 or x.size != y.size:
        raise ValueError("scales and values must have equal length >= 2")
    slope, intercept = np.polyfit(x, y, 1)
    return float(intercept)
