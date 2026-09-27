from qiskit import transpile
from qiskit_aer import AerSimulator

from framework.noise_models import depolarizing_noise_model
from mitigation.zne import global_fold, linear_zero_noise_extrapolation
from workloads.mirror_circuits import make_mirror_circuit


def _success(qc, p, shots=20000, seed=17):
    sim = AerSimulator(noise_model=depolarizing_noise_model(p))
    tqc = transpile(qc, sim, optimization_level=0, seed_transpiler=seed)
    counts = sim.run(tqc, shots=shots, seed_simulator=seed).result().get_counts()
    return counts.get("0" * qc.num_qubits, 0) / shots


def test_mirror_circuit_has_measurements():
    qc = make_mirror_circuit(2, 3, 7)
    assert qc.num_qubits == 2
    assert qc.num_clbits == 2


def test_mirror_circuit_returns_zero_ideally():
    qc = make_mirror_circuit(4, 5, 7)
    assert _success(qc, 0.0, shots=1024) == 1.0


def test_depolarizing_noise_reduces_success():
    qc = make_mirror_circuit(4, 20, 7)
    ideal = _success(qc, 0.0)
    noisy = _success(qc, 0.01)
    assert ideal == 1.0
    assert noisy < ideal


def test_global_fold_increases_depth():
    qc = make_mirror_circuit(2, 3, 7)
    assert global_fold(qc, 3).depth() > global_fold(qc, 1).depth()


def test_linear_zne_intercept():
    estimate = linear_zero_noise_extrapolation([1, 3, 5], [0.9, 0.7, 0.5])
    assert abs(estimate - 1.0) < 1e-10
