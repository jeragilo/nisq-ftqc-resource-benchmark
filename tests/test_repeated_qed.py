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

def test_repeated_checks_accept_folded_blocks_with_terminal_measurements():
    from mitigation.zne import global_fold

    blocks = make_checkable_mirror_blocks(2, 8, 2, 7)
    measured_blocks = []
    for block in blocks:
        b = block.copy()
        b.measure_all()
        measured_blocks.append(global_fold(b, 1))

    checked = add_repeated_boundary_parity_checks(measured_blocks)
    sim = AerSimulator()
    tc = transpile(checked.circuit, sim, optimization_level=0, seed_transpiler=7)
    counts = sim.run(tc, shots=64, seed_simulator=7).result().get_counts()
    accepted, rejected, success = split_repeated_counts(counts)
    assert accepted == 64
    assert rejected == 0
    assert success == 64

def test_check_intervals_share_identical_underlying_payload():
    from workloads.checkable_mirror_blocks import make_identity_microblocks, group_microblocks, compose_checkable_payload

    micro = make_identity_microblocks(4, 8, 13)
    p2 = compose_checkable_payload(group_microblocks(micro, 2))
    p8 = compose_checkable_payload(group_microblocks(micro, 8))

    # Ignore register naming; operation sequences on data must be identical.
    ops2 = [(inst.operation.name, [p2.find_bit(q).index for q in inst.qubits]) for inst in p2.data]
    ops8 = [(inst.operation.name, [p8.find_bit(q).index for q in inst.qubits]) for inst in p8.data]
    assert ops2 == ops8

def test_repeated_checks_reuse_single_physical_ancilla():
    blocks = make_checkable_mirror_blocks(2, 64, 2, 0)
    checked = add_repeated_boundary_parity_checks(blocks)
    assert checked.check_rounds == 32
    assert checked.ancilla_qubits == 1
    assert checked.syndrome_bits == 32
    assert checked.circuit.num_qubits == 3


def test_depth64_l2_transpiles_with_reused_ancilla():
    blocks = make_checkable_mirror_blocks(2, 64, 2, 0)
    checked = add_repeated_boundary_parity_checks(blocks)
    sim = AerSimulator()
    tc = transpile(checked.circuit, sim, optimization_level=0, seed_transpiler=0)
    assert tc.num_qubits <= sim.configuration().n_qubits
