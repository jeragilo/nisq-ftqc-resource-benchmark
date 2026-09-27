"""Experiment 0: ideal vs raw depolarizing noise vs digital ZNE."""
from __future__ import annotations

import csv
import time
from pathlib import Path

from qiskit import transpile
from qiskit_aer import AerSimulator

from framework.metrics import ResourceRecord
from framework.noise_models import depolarizing_noise_model
from mitigation.zne import global_fold, linear_zero_noise_extrapolation
from workloads.mirror_circuits import make_mirror_circuit

QUBITS = (2, 4)
DEPTHS = (5, 10, 20)
NOISE = (1e-4, 3e-4, 1e-3, 3e-3, 1e-2)
SHOTS = (1024, 4096, 16384)
SEEDS = tuple(range(10))
ZNE_SCALES = (1, 3, 5)


def success_probability(counts: dict[str, int], num_qubits: int) -> float:
    return counts.get("0" * num_qubits, 0) / sum(counts.values())


def gate_counts(circuit):
    ops = circuit.count_ops()
    one_q = sum(int(ops.get(g, 0)) for g in ("h", "s", "sdg", "x", "sx", "rz"))
    two_q = sum(int(ops.get(g, 0)) for g in ("cx", "cz", "ecr"))
    return one_q, two_q


def execute(circuit, p, shots, seed):
    simulator = AerSimulator(noise_model=depolarizing_noise_model(p))
    tc = transpile(circuit, simulator, optimization_level=0, seed_transpiler=seed)
    start = time.perf_counter()
    counts = simulator.run(tc, shots=shots, seed_simulator=seed).result().get_counts()
    elapsed = time.perf_counter() - start
    return tc, success_probability(counts, circuit.num_qubits), elapsed


def main(output="results/raw/experiment_0.csv"):
    rows = []
    for n in QUBITS:
        for depth in DEPTHS:
            for shots in SHOTS:
                for seed in SEEDS:
                    base = make_mirror_circuit(n, depth, seed)

                    # Ideal reference.
                    tc, ideal, elapsed = execute(base, 0.0, shots, seed)
                    one_q, two_q = gate_counts(tc)
                    rows.append(ResourceRecord(
                        "ideal", n, depth, tc.depth(), one_q, two_q, shots, 0.0,
                        seed, ideal, abs(1.0 - ideal), elapsed
                    ).as_dict())

                    for p in NOISE:
                        tc, raw, elapsed = execute(base, p, shots, seed)
                        one_q, two_q = gate_counts(tc)
                        rows.append(ResourceRecord(
                            "raw", n, depth, tc.depth(), one_q, two_q, shots, p,
                            seed, raw, abs(1.0 - raw), elapsed
                        ).as_dict())

                        folded_values = []
                        total_seconds = 0.0
                        total_one_q = total_two_q = total_depth = 0
                        for scale in ZNE_SCALES:
                            folded = global_fold(base, scale)
                            ftc, value, sec = execute(folded, p, shots, seed)
                            folded_values.append(value)
                            oq, tq = gate_counts(ftc)
                            total_one_q += oq
                            total_two_q += tq
                            total_depth += ftc.depth()
                            total_seconds += sec

                        estimate = min(1.0, max(0.0, linear_zero_noise_extrapolation(
                            ZNE_SCALES, folded_values
                        )))
                        rows.append(ResourceRecord(
                            "zne", n, depth, total_depth, total_one_q, total_two_q,
                            shots * len(ZNE_SCALES), p, seed, estimate,
                            abs(1.0 - estimate), total_seconds
                        ).as_dict())

    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


if __name__ == "__main__":
    main()
