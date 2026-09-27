from qiskit_aer import AerSimulator
from qiskit import transpile

from qed.parity_checks import add_global_z_parity_check, split_counts
from workloads.mirror_circuits import make_mirror_circuit


def test_qed_noiseless_preserves_ideal_output():
    payload = make_mirror_circuit(2, 5, 0)
    checked = add_global_z_parity_check(payload)
    sim = AerSimulator()
    tc = transpile(checked.circuit, sim, optimization_level=0, seed_transpiler=0)
    counts = sim.run(tc, shots=256, seed_simulator=0).result().get_counts()
    accepted, rejected, success = split_counts(counts)
    assert accepted == 256
    assert rejected == 0
    assert success == 256


def test_qed_adds_one_ancilla():
    payload = make_mirror_circuit(4, 5, 0)
    checked = add_global_z_parity_check(payload)
    assert checked.data_qubits == 4
    assert checked.ancilla_qubits == 1
    assert checked.circuit.num_qubits == 5
