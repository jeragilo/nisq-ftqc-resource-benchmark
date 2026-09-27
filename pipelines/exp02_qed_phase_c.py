"""Experiment 2 Phase C: repeated-check interval smoke study."""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

from qiskit import transpile
from qiskit_aer import AerSimulator

from framework.noise_models import depolarizing_noise_model
from qed.repeated_checks import add_repeated_boundary_parity_checks, split_repeated_counts
from workloads.checkable_mirror_blocks import make_checkable_mirror_blocks, compose_checkable_payload

FIELDS = [
    "qubits","total_depth","check_interval","check_rounds","noise_probability",
    "shots","seed","method","success_probability","conditional_success_probability",
    "absolute_error","accepted_shots","rejected_shots","acceptance_probability",
    "data_qubits","ancilla_qubits","total_physical_qubits","one_qubit_gates",
    "two_qubit_gates","circuit_depth","aggregate_depth","classical_seconds",
]

def gate_counts(circuit):
    ops = circuit.count_ops()
    one_q = sum(int(ops.get(g,0)) for g in ("h","s","sdg","x","sx","rz"))
    two_q = sum(int(ops.get(g,0)) for g in ("cx","cz","ecr"))
    return one_q, two_q

def run_counts(circuit,p,shots,seed):
    sim=AerSimulator(noise_model=depolarizing_noise_model(p))
    tc=transpile(circuit,sim,optimization_level=0,seed_transpiler=seed)
    t0=time.perf_counter()
    counts=sim.run(tc,shots=shots,seed_simulator=seed).result().get_counts()
    return tc,counts,time.perf_counter()-t0

def raw_row(blocks,n,total_depth,L,p,shots,seed):
    payload=compose_checkable_payload(blocks)
    tc,counts,sec=run_counts(payload,p,shots,seed)
    success=counts.get("0"*n,0)/shots
    oq,tq=gate_counts(tc)
    return {
        "qubits":n,"total_depth":total_depth,"check_interval":L,"check_rounds":0,
        "noise_probability":p,"shots":shots,"seed":seed,"method":"raw",
        "success_probability":success,"conditional_success_probability":success,
        "absolute_error":abs(1-success),"accepted_shots":shots,"rejected_shots":0,
        "acceptance_probability":1.0,"data_qubits":n,"ancilla_qubits":0,
        "total_physical_qubits":n,"one_qubit_gates":oq,"two_qubit_gates":tq,
        "circuit_depth":tc.depth(),"aggregate_depth":tc.depth(),
        "classical_seconds":sec,
    }

def qed_row(blocks,n,total_depth,L,p,shots,seed):
    checked=add_repeated_boundary_parity_checks(blocks)
    tc,counts,sec=run_counts(checked.circuit,p,shots,seed)
    accepted,rejected,success=split_repeated_counts(counts)
    cond=success/accepted if accepted else 0.0
    oq,tq=gate_counts(tc)
    return {
        "qubits":n,"total_depth":total_depth,"check_interval":L,
        "check_rounds":checked.check_rounds,"noise_probability":p,"shots":shots,
        "seed":seed,"method":"qed_repeated","success_probability":success/shots,
        "conditional_success_probability":cond,"absolute_error":abs(1-cond),
        "accepted_shots":accepted,"rejected_shots":rejected,
        "acceptance_probability":accepted/shots,"data_qubits":n,
        "ancilla_qubits":checked.ancilla_qubits,
        "total_physical_qubits":n+checked.ancilla_qubits,
        "one_qubit_gates":oq,"two_qubit_gates":tq,"circuit_depth":tc.depth(),
        "aggregate_depth":tc.depth(),"classical_seconds":sec,
    }

def run(output):
    rows=[]
    grid=[]
    for n in (2,4):
        for total_depth in (8,16):
            for p in (1e-3,1e-2):
                for L in (1,2,4,8):
                    if L<=total_depth:
                        grid.append((n,total_depth,p,L,1024,0))
    for i,(n,d,p,L,shots,seed) in enumerate(grid,1):
        blocks=make_checkable_mirror_blocks(n,d,L,seed)
        raw=raw_row(blocks,n,d,L,p,shots,seed)
        qed=qed_row(blocks,n,d,L,p,shots,seed)
        rows.extend([raw,qed])
        print(
            f"[{i:>2}/{len(grid)}] q={n} depth={d} p={p:g} L={L} "
            f"rounds={qed['check_rounds']} | raw_err={raw['absolute_error']:.4f} "
            f"qed_err={qed['absolute_error']:.4f} accept={qed['acceptance_probability']:.3f} "
            f"anc={qed['ancilla_qubits']} 2q={qed['two_qubit_gates']}",
            flush=True,
        )
    path=Path(output); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",default="results/raw/experiment_2_phase_c.csv")
    args=ap.parse_args()
    run(args.output)

if __name__=="__main__":
    main()
