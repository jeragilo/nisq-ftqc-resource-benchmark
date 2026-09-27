"""Noise models used by Experiment 0."""
from qiskit_aer.noise import NoiseModel, depolarizing_error


def depolarizing_noise_model(p: float) -> NoiseModel:
    if not 0.0 <= p < 1.0:
        raise ValueError("p must satisfy 0 <= p < 1")

    model = NoiseModel()
    if p == 0:
        return model

    model.add_all_qubit_quantum_error(depolarizing_error(p, 1), ["h", "s", "x"])
    model.add_all_qubit_quantum_error(depolarizing_error(p, 2), ["cx"])
    return model
