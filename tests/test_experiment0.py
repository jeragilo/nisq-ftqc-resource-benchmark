from mitigation.zne import global_fold, linear_zero_noise_extrapolation
from workloads.mirror_circuits import make_mirror_circuit


def test_mirror_circuit_has_measurements():
    qc = make_mirror_circuit(2, 3, 7)
    assert qc.num_qubits == 2
    assert qc.num_clbits == 2


def test_global_fold_increases_depth():
    qc = make_mirror_circuit(2, 3, 7)
    assert global_fold(qc, 3).depth() > global_fold(qc, 1).depth()


def test_linear_zne_intercept():
    estimate = linear_zero_noise_extrapolation([1, 3, 5], [0.9, 0.7, 0.5])
    assert abs(estimate - 1.0) < 1e-10
