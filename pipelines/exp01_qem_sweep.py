"""Experiment 1: resumable resource-aware QEM sweep."""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import qiskit
import qiskit_aer
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

FIELDS = (
    "qubits", "nominal_depth", "noise_probability", "nominal_shots", "seed",
    "method", "success_probability", "absolute_error", "unclipped_estimate",
    "clipped", "scale_1", "scale_3", "scale_5", "effective_shots",
    "one_qubit_gates", "two_qubit_gates", "aggregate_depth",
    "classical_seconds", "improvement_vs_raw", "sampling_overhead_ratio",
    "gate2_work_ratio", "depth_work_ratio", "runtime_ratio",
    "improvement_per_extra_shot",
)


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
    simulator = AerSimulator()
    prepared = {}
    for scale in ZNE_SCALES:
        folded = global_fold(base, scale)
        prepared[scale] = transpile(
            folded, simulator, optimization_level=0, seed_transpiler=seed
        )
    return prepared


def run_prepared(circuit, p, shots, seed):
    simulator = AerSimulator(noise_model=depolarizing_noise_model(p))
    start = time.perf_counter()
    counts = simulator.run(
        circuit, shots=shots, seed_simulator=seed
    ).result().get_counts()
    return success_probability(counts, circuit.num_qubits), time.perf_counter() - start


def git_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def provenance(quick):
    return {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "qiskit_version": qiskit.__version__,
        "qiskit_aer_version": qiskit_aer.__version__,
        "numpy_version": np.__version__,
        "quick": quick,
        "zne_scales": list(ZNE_SCALES),
    }


def completed_keys(path):
    """Return matched condition keys already containing both raw and ZNE rows."""
    if not path.exists() or path.stat().st_size == 0:
        return set()
    methods = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            key = (
                int(row["qubits"]), int(row["nominal_depth"]),
                float(row["noise_probability"]), int(row["nominal_shots"]),
                int(row["seed"]),
            )
            methods.setdefault(key, set()).add(row["method"])
    return {k for k, v in methods.items() if {"raw", "zne"} <= v}


def append_pair(path, raw_row, zne_row):
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(raw_row)
        writer.writerow(zne_row)
        f.flush()
        os.fsync(f.fileno())


def run_sweep(output, quick=False, resume=False):
    qubits = (2, 4) if quick else QUBITS
    depths = (5, 20) if quick else DEPTHS
    noise = (1e-3, 1e-2) if quick else NOISE
    shots_grid = (1024,) if quick else SHOTS
    seeds = (0, 1) if quick else SEEDS

    path = Path(output)
    metadata_path = path.with_suffix(".metadata.json")
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists() and not resume:
        raise FileExistsError(
            f"{path} already exists. Use --resume to continue it or choose a new output."
        )

    done = completed_keys(path) if resume else set()
    total = len(qubits) * len(depths) * len(noise) * len(shots_grid) * len(seeds)
    start_run = time.perf_counter()
    completed_this_run = 0

    meta = provenance(quick)
    meta.update({
        "output": str(path),
        "resume": resume,
        "conditions_total": total,
        "conditions_previously_complete": len(done),
        "qubits": list(qubits),
        "depths": list(depths),
        "noise": list(noise),
        "shots": list(shots_grid),
        "seeds": list(seeds),
    })
    metadata_path.write_text(json.dumps(meta, indent=2) + "\n")

    print(f"Experiment 1: {total} matched conditions / {2 * total} CSV rows")
    print(f"Output: {path}")
    print(f"Already complete: {len(done)} conditions")
    print(f"Python: {sys.executable}")
    print(f"Git commit: {meta['git_commit']}")
    print("Checkpointing after every Raw/ZNE pair. Ctrl+C is safe; restart with --resume.")

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
                        key = (n, depth, p, shots, seed)
                        if key in done:
                            continue

                        raw, raw_sec = run_prepared(base_tc, p, shots, seed)
                        scale_values, zne_sec = [], 0.0
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
                            "qubits": n, "nominal_depth": depth,
                            "noise_probability": p, "nominal_shots": shots, "seed": seed,
                        }
                        raw_row = {
                            **common, "method": "raw", "success_probability": raw,
                            "absolute_error": raw_error, "unclipped_estimate": raw,
                            "clipped": 0, "scale_1": raw, "scale_3": "", "scale_5": "",
                            "effective_shots": shots, "one_qubit_gates": raw_1q,
                            "two_qubit_gates": raw_2q, "aggregate_depth": raw_depth,
                            "classical_seconds": raw_sec, "improvement_vs_raw": 0.0,
                            "sampling_overhead_ratio": 1.0, "gate2_work_ratio": 1.0,
                            "depth_work_ratio": 1.0, "runtime_ratio": 1.0,
                            "improvement_per_extra_shot": 0.0,
                        }
                        zne_row = {
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
                        }
                        append_pair(path, raw_row, zne_row)
                        done.add(key)
                        completed_this_run += 1

                        elapsed = time.perf_counter() - start_run
                        rate = completed_this_run / elapsed if elapsed else 0.0
                        remaining = total - len(done)
                        eta = remaining / rate if rate else float("inf")
                        print(
                            f"[{len(done):>4}/{total}] q={n} depth={depth} seed={seed:02d} "
                            f"p={p:g} shots={shots} | Δerr={improvement:+.6f} "
                            f"| elapsed={elapsed/60:.1f}m ETA={eta/60:.1f}m",
                            flush=True,
                        )

    elapsed = time.perf_counter() - start_run
    meta["completed_utc"] = datetime.now(timezone.utc).isoformat()
    meta["elapsed_seconds_this_run"] = elapsed
    meta["conditions_complete"] = len(done)
    metadata_path.write_text(json.dumps(meta, indent=2) + "\n")
    print(f"Complete: {len(done)}/{total} conditions ({2 * len(done)} rows)")
    print(f"Elapsed this run: {elapsed/60:.2f} minutes")
    print(f"Data: {path}")
    print(f"Metadata: {metadata_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--output", default="results/raw/experiment_1.csv")
    args = parser.parse_args()
    run_sweep(args.output, quick=args.quick, resume=args.resume)


if __name__ == "__main__":
    main()
