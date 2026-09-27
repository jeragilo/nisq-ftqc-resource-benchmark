"""Experiment 2 Phase A: QED postselection smoke validation."""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

from qiskit import transpile
from qiskit_aer import AerSimulator

from framework.noise_models import depolarizing_noise_model
from qed.parity_checks import add_global_z_parity_check, split_counts
from workloads.mirror_circuits import make_mirror_circuit


FIELDS = [
    "qubits","nominal_depth","noise_probability","shots","seed","method",
    "success_probability","conditional_success_probability","absolute_error",
    "accepted_shots","rejected_shots","acceptance_probability",
    "data_qubits","ancilla_qubits","total_physical_qubits",
    "one_qubit_gates","two_qubit_gates","circuit_depth","classical_seconds",
]


def gate_counts(circuit):
    ops = circuit.count_ops()
    one_q = sum(int(ops.get(g, 0)) for g in ("h","s","sdg","x","sx","rz"))
    two_q = sum(int(ops.get(g, 0)) for g in ("cx","cz","ecr"))
    return one_q, two_q


def run_once(n, depth, p, shots, seed):
    payload = make_mirror_circuit(n, depth, seed)
    sim = AerSimulator(noise_model=depolarizing_noise_model(p))

    raw_tc = transpile(payload, sim, optimization_level=0, seed_transpiler=seed)
    t0 = time.perf_counter()
    raw_counts = sim.run(raw_tc, shots=shots, seed_simulator=seed).result().get_counts()
    raw_sec = time.perf_counter() - t0
    raw_success = raw_counts.get("0"*n, 0) / shots
    r1, r2 = gate_counts(raw_tc)

    checked = add_global_z_parity_check(payload)
    qed_tc = transpile(checked.circuit, sim, optimization_level=0, seed_transpiler=seed)
    t0 = time.perf_counter()
    qed_counts = sim.run(qed_tc, shots=shots, seed_simulator=seed).result().get_counts()
    qed_sec = time.perf_counter() - t0
    accepted, rejected, success = split_counts(qed_counts)
    acceptance = accepted / shots
    conditional_success = success / accepted if accepted else 0.0
    q1, q2 = gate_counts(qed_tc)

    raw_row = {
        "qubits":n,"nominal_depth":depth,"noise_probability":p,"shots":shots,"seed":seed,
        "method":"raw","success_probability":raw_success,
        "conditional_success_probability":raw_success,"absolute_error":abs(1-raw_success),
        "accepted_shots":shots,"rejected_shots":0,"acceptance_probability":1.0,
        "data_qubits":n,"ancilla_qubits":0,"total_physical_qubits":n,
        "one_qubit_gates":r1,"two_qubit_gates":r2,"circuit_depth":raw_tc.depth(),
        "classical_seconds":raw_sec,
    }
    qed_row = {
        "qubits":n,"nominal_depth":depth,"noise_probability":p,"shots":shots,"seed":seed,
        "method":"qed","success_probability":success/shots,
        "conditional_success_probability":conditional_success,
        "absolute_error":abs(1-conditional_success),
        "accepted_shots":accepted,"rejected_shots":rejected,
        "acceptance_probability":acceptance,
        "data_qubits":n,"ancilla_qubits":1,"total_physical_qubits":n+1,
        "one_qubit_gates":q1,"two_qubit_gates":q2,"circuit_depth":qed_tc.depth(),
        "classical_seconds":qed_sec,
    }
    return raw_row, qed_row


def run_smoke(output):
    grid = {
        "qubits": (2,4),
        "depths": (5,20),
        "noise": (1e-3,1e-2),
        "shots": (1024,),
        "seeds": (0,1),
    }
    rows=[]
    total=2*2*2*1*2
    i=0
    for n in grid["qubits"]:
        for depth in grid["depths"]:
            for p in grid["noise"]:
                for shots in grid["shots"]:
                    for seed in grid["seeds"]:
                        raw,qed=run_once(n,depth,p,shots,seed)
                        rows.extend([raw,qed]); i+=1
                        print(
                            f"[{i:>2}/{total}] q={n} depth={depth} p={p:g} seed={seed} "
                            f"| raw_err={raw['absolute_error']:.4f} "
                            f"| qed_err={qed['absolute_error']:.4f} "
                            f"| accept={qed['acceptance_probability']:.3f}",
                            flush=True,
                        )
    path=Path(output); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="results/raw/experiment_2_phase_a.csv")
    args=parser.parse_args()
    run_smoke(args.output)


if __name__=="__main__":
    main()
