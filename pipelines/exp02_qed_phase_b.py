"""Experiment 2 Phase B: matched Raw/ZNE/QED/QED+ZNE smoke comparison."""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

from qiskit import transpile
from qiskit_aer import AerSimulator

from framework.noise_models import depolarizing_noise_model
from mitigation.zne import global_fold, linear_zero_noise_extrapolation
from qed.parity_checks import add_global_z_parity_check, split_counts
from workloads.mirror_circuits import make_mirror_circuit

SCALES = (1, 3, 5)

FIELDS = [
    "qubits","nominal_depth","noise_probability","shots","seed","method",
    "success_probability","conditional_success_probability","absolute_error",
    "unclipped_estimate","clipped","scale_1","scale_3","scale_5",
    "accepted_shots","rejected_shots","acceptance_probability",
    "data_qubits","ancilla_qubits","total_physical_qubits",
    "one_qubit_gates","two_qubit_gates","circuit_depth","aggregate_depth",
    "effective_shots","classical_seconds",
]


def gate_counts(circuit):
    ops = circuit.count_ops()
    one_q = sum(int(ops.get(g, 0)) for g in ("h","s","sdg","x","sx","rz"))
    two_q = sum(int(ops.get(g, 0)) for g in ("cx","cz","ecr"))
    return one_q, two_q


def run_counts(circuit, p, shots, seed):
    sim = AerSimulator(noise_model=depolarizing_noise_model(p))
    tc = transpile(circuit, sim, optimization_level=0, seed_transpiler=seed)
    t0 = time.perf_counter()
    counts = sim.run(tc, shots=shots, seed_simulator=seed).result().get_counts()
    return tc, counts, time.perf_counter() - t0


def raw_row(payload, n, depth, p, shots, seed):
    tc, counts, sec = run_counts(payload, p, shots, seed)
    success = counts.get("0"*n, 0) / shots
    oq,tq=gate_counts(tc)
    return {
        "qubits":n,"nominal_depth":depth,"noise_probability":p,"shots":shots,"seed":seed,
        "method":"raw","success_probability":success,
        "conditional_success_probability":success,"absolute_error":abs(1-success),
        "unclipped_estimate":success,"clipped":0,"scale_1":success,"scale_3":"","scale_5":"",
        "accepted_shots":shots,"rejected_shots":0,"acceptance_probability":1.0,
        "data_qubits":n,"ancilla_qubits":0,"total_physical_qubits":n,
        "one_qubit_gates":oq,"two_qubit_gates":tq,"circuit_depth":tc.depth(),
        "aggregate_depth":tc.depth(),"effective_shots":shots,"classical_seconds":sec,
    }


def zne_row(payload, n, depth, p, shots, seed):
    vals=[]; total_sec=0.0; oq=tq=agg_depth=0
    for scale in SCALES:
        folded=global_fold(payload, scale)
        tc,counts,sec=run_counts(folded,p,shots,seed)
        vals.append(counts.get("0"*n,0)/shots)
        total_sec+=sec
        a,b=gate_counts(tc); oq+=a; tq+=b; agg_depth+=tc.depth()
    unclip=linear_zero_noise_extrapolation(SCALES,vals)
    clipped=min(1.0,max(0.0,unclip))
    return {
        "qubits":n,"nominal_depth":depth,"noise_probability":p,"shots":shots,"seed":seed,
        "method":"zne","success_probability":clipped,
        "conditional_success_probability":clipped,"absolute_error":abs(1-clipped),
        "unclipped_estimate":unclip,"clipped":int(unclip!=clipped),
        "scale_1":vals[0],"scale_3":vals[1],"scale_5":vals[2],
        "accepted_shots":shots*3,"rejected_shots":0,"acceptance_probability":1.0,
        "data_qubits":n,"ancilla_qubits":0,"total_physical_qubits":n,
        "one_qubit_gates":oq,"two_qubit_gates":tq,"circuit_depth":"","aggregate_depth":agg_depth,
        "effective_shots":shots*3,"classical_seconds":total_sec,
    }


def qed_scale(payload, scale, p, shots, seed):
    folded=global_fold(payload, scale)
    checked=add_global_z_parity_check(folded)
    tc,counts,sec=run_counts(checked.circuit,p,shots,seed)
    accepted,rejected,success=split_counts(counts)
    cond=success/accepted if accepted else 0.0
    oq,tq=gate_counts(tc)
    return {
        "cond":cond,"accepted":accepted,"rejected":rejected,
        "acceptance":accepted/shots,"tc":tc,"sec":sec,"oq":oq,"tq":tq
    }


def qed_row(payload,n,depth,p,shots,seed):
    r=qed_scale(payload,1,p,shots,seed)
    return {
        "qubits":n,"nominal_depth":depth,"noise_probability":p,"shots":shots,"seed":seed,
        "method":"qed","success_probability":r["cond"],
        "conditional_success_probability":r["cond"],"absolute_error":abs(1-r["cond"]),
        "unclipped_estimate":r["cond"],"clipped":0,"scale_1":r["cond"],"scale_3":"","scale_5":"",
        "accepted_shots":r["accepted"],"rejected_shots":r["rejected"],
        "acceptance_probability":r["acceptance"],
        "data_qubits":n,"ancilla_qubits":1,"total_physical_qubits":n+1,
        "one_qubit_gates":r["oq"],"two_qubit_gates":r["tq"],
        "circuit_depth":r["tc"].depth(),"aggregate_depth":r["tc"].depth(),
        "effective_shots":shots,"classical_seconds":r["sec"],
    }


def hybrid_row(payload,n,depth,p,shots,seed):
    rs=[qed_scale(payload,s,p,shots,seed) for s in SCALES]
    vals=[r["cond"] for r in rs]
    unclip=linear_zero_noise_extrapolation(SCALES,vals)
    clipped=min(1.0,max(0.0,unclip))
    total_acc=sum(r["accepted"] for r in rs)
    total_rej=sum(r["rejected"] for r in rs)
    return {
        "qubits":n,"nominal_depth":depth,"noise_probability":p,"shots":shots,"seed":seed,
        "method":"qed_zne","success_probability":clipped,
        "conditional_success_probability":clipped,"absolute_error":abs(1-clipped),
        "unclipped_estimate":unclip,"clipped":int(unclip!=clipped),
        "scale_1":vals[0],"scale_3":vals[1],"scale_5":vals[2],
        "accepted_shots":total_acc,"rejected_shots":total_rej,
        "acceptance_probability":total_acc/(shots*3),
        "data_qubits":n,"ancilla_qubits":1,"total_physical_qubits":n+1,
        "one_qubit_gates":sum(r["oq"] for r in rs),
        "two_qubit_gates":sum(r["tq"] for r in rs),
        "circuit_depth":"","aggregate_depth":sum(r["tc"].depth() for r in rs),
        "effective_shots":shots*3,"classical_seconds":sum(r["sec"] for r in rs),
    }


def run(output):
    rows=[]
    grid=[(2,5,1e-3,1024,0),(2,5,1e-2,1024,0),
          (2,20,1e-3,1024,0),(2,20,1e-2,1024,0),
          (4,5,1e-3,1024,0),(4,5,1e-2,1024,0),
          (4,20,1e-3,1024,0),(4,20,1e-2,1024,0)]
    for i,(n,d,p,s,seed) in enumerate(grid,1):
        payload=make_mirror_circuit(n,d,seed)
        methods=[
            raw_row(payload,n,d,p,s,seed),
            zne_row(payload,n,d,p,s,seed),
            qed_row(payload,n,d,p,s,seed),
            hybrid_row(payload,n,d,p,s,seed),
        ]
        rows.extend(methods)
        print(
            f"[{i}/8] q={n} depth={d} p={p:g} | "
            + " ".join(f"{r['method']}={r['absolute_error']:.4f}" for r in methods)
            + f" | qed_accept={methods[2]['acceptance_probability']:.3f} "
              f"hybrid_accept={methods[3]['acceptance_probability']:.3f}",
            flush=True,
        )
    path=Path(output); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",default="results/raw/experiment_2_phase_b.csv")
    args=ap.parse_args()
    run(args.output)


if __name__=="__main__":
    main()
