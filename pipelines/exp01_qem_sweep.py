"""Experiment 1: resource-aware QEM sweep."""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

from qiskit import transpile
from qiskit_aer import AerSimulator

from framework.noise_models import depolarizing_noise_model
from mitigation.zne import global_fold, linear_zero_noise_extrapolation
from workloads.mirror_circuits import make_mirror_circuit

QUBITS = (2, 4, 6, 8)
DEPTHS = (5, 10, 20, 40, 80)
NOISE = (1e-4, 3e-4, 1e-3, 3e-3, 1e-2)
SHOTS = (1024, 4096, 16384)
SEEDS = tuple(range(20))
ZNE_SCALES = (1, 3, 5)


def success_probability(counts, n):
    return counts.get("0" * n, 0) / sum(counts.values())


def gate_counts(circuit):
    ops = circuit.count_ops()
    one_q = sum(int(ops.get(g, 0)) for g in ("h", "s", "sdg", "x", "sx", "rz"))
    two_q = sum(int(ops.get(g, 0)) for g in ("cx", "cz", "ecr"))
    return one_q, two_q


def prepare_circuits(n, depth, seed):
    """Transpile base and folded circuits once for reuse across p/shots."""
    base = make_mirror_circuit(n, depth, seed)
    ideal_sim = AerSimulator()
    prepared = {}
    for scale in ZNE_SCALES:
        folded = global_fold(base, scale)
        prepared[scale] = transpile(
            folded, ideal_sim, optimization_level=0, seed_transpiler=seed
        )
    return prepared


def run_prepared(circuit, p, shots, seed):
    sim = AerSimulator(noise_model=depolarizing_noise_model(p))
    start = time.perf_counter()
    counts = sim.run(circuit, shots=shots, seed_simulator=seed).result().get_counts()
    return success_probability(counts, circuit.num_qubits), time.perf_counter() - start


def run_sweep(output, quick=False):
    qubits = (2, 4) if quick else QUBITS
    depths = (5, 20) if quick else DEPTHS
    noise = (1e-3, 1e-2) if quick else NOISE
    shots_grid = (1024,) if quick else SHOTS
    seeds = (0, 1) if quick else SEEDS

    rows = []
    for n in qubits:
        for depth in depths:
            for seed in seeds:
                prepared = prepare_circuits(n, depth, seed)
                base_tc = prepared[1]
                raw_1q, raw_2q = gate_counts(base_tc)
                raw_depth = base_tc.depth()

                zne_1q = zne_2q = zne_depth = 0
                for tc in prepared.values():
                    oq, tq = gate_counts(tc)
                    zne_1q += oq
                    zne_2q += tq
                    zne_depth += tc.depth()

                for p in noise:
                    for shots in shots_grid:
                        raw, raw_sec = run_prepared(base_tc, p, shots, seed)

                        scale_values = []
                        zne_sec = 0.0
                        for scale, tc in prepared.items():
                            value, sec = run_prepared(tc, p, shots, seed)
                            scale_values.append(value)
                            zne_sec += sec

                        unclip = linear_zero_noise_extrapolation(ZNE_SCALES, scale_values)
                        clipped = min(1.0, max(0.0, unclip))
                        clipped_flag = int(clipped != unclip)

                        raw_error = abs(1.0 - raw)
                        zne_error = abs(1.0 - clipped)
                        improvement = raw_error - zne_error
                        extra_shots = shots * (len(ZNE_SCALES) - 1)

                        common = {
                            "qubits": n, "nominal_depth": depth, "noise_probability": p,
                            "nominal_shots": shots, "seed": seed,
                        }
                        rows.append({
                            **common, "method": "raw", "success_probability": raw,
                            "absolute_error": raw_error, "unclipped_estimate": raw,
                            "clipped": 0, "scale_1": raw, "scale_3": "",
                            "scale_5": "", "effective_shots": shots,
                            "one_qubit_gates": raw_1q, "two_qubit_gates": raw_2q,
                            "aggregate_depth": raw_depth, "classical_seconds": raw_sec,
                            "improvement_vs_raw": 0.0, "sampling_overhead_ratio": 1.0,
                            "gate2_work_ratio": 1.0, "depth_work_ratio": 1.0,
                            "runtime_ratio": 1.0, "improvement_per_extra_shot": 0.0,
                        })
                        rows.append({
                            **common, "method": "zne", "success_probability": clipped,
                            "absolute_error": zne_error, "unclipped_estimate": unclip,
                            "clipped": clipped_flag, "scale_1": scale_values[0],
                            "scale_3": scale_values[1], "scale_5": scale_values[2],
                            "effective_shots": shots * len(ZNE_SCALES),
                            "one_qubit_gates": zne_1q, "two_qubit_gates": zne_2q,
                            "aggregate_depth": zne_depth, "classical_seconds": zne_sec,
                            "improvement_vs_raw": improvement,
                            "sampling_overhead_ratio": float(len(ZNE_SCALES)),
                            "gate2_work_ratio": zne_2q / raw_2q if raw_2q else 0.0,
                            "depth_work_ratio": zne_depth / raw_depth if raw_depth else 0.0,
                            "runtime_ratio": zne_sec / raw_sec if raw_sec else 0.0,
                            "improvement_per_extra_shot": improvement / extra_shots,
                        })

    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--output", default="results/raw/experiment_1.csv")
    args = parser.parse_args()
    run_sweep(args.output, quick=args.quick)


if __name__ == "__main__":
    main()
