from qiskit import transpile
from qiskit_aer import AerSimulator
from qed.repeated_checks import add_repeated_boundary_parity_checks, split_repeated_counts
from workloads.checkable_mirror_blocks import make_checkable_mirror_blocks, compose_checkable_payload

def test_checkable_blocks_preserve_ideal_output():
    blocks = make_checkable_mirror_blocks(2, 8, 2, 7)
    payload = compose_checkable_payload(blocks)
    sim = AerSimulator()
    tc = transpile(payload, sim, optimization_level=0, seed_transpiler=7)
    counts = sim.run(tc, shots=128, seed_simulator=7).result().get_counts()
    assert counts.get("00", 0) == 128

def test_repeated_checks_are_nondestructive_noiseless():
    blocks = make_checkable_mirror_blocks(2, 8, 2, 7)
    checked = add_repeated_boundary_parity_checks(blocks)
    sim = AerSimulator()
    tc = transpile(checked.circuit, sim, optimization_level=0, seed_transpiler=7)
    counts = sim.run(tc, shots=128, seed_simulator=7).result().get_counts()
    accepted, rejected, success = split_repeated_counts(counts)
    assert checked.check_rounds == 4
    assert accepted == 128
    assert rejected == 0
    assert success == 128

def test_check_interval_controls_round_count():
    assert len(make_checkable_mirror_blocks(4, 8, 1, 0)) == 8
    assert len(make_checkable_mirror_blocks(4, 8, 2, 0)) == 4
    assert len(make_checkable_mirror_blocks(4, 8, 4, 0)) == 2
    assert len(make_checkable_mirror_blocks(4, 8, 8, 0)) == 1
