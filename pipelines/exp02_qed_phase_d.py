"""Experiment 2 Phase D: Raw/ZNE/repeated-QED/repeated-QED+ZNE smoke."""
from __future__ import annotations
import argparse, csv, time
from pathlib import Path
from qiskit import transpile
from qiskit_aer import AerSimulator
from framework.noise_models import depolarizing_noise_model
from mitigation.zne import global_fold, linear_zero_noise_extrapolation
from qed.repeated_checks import add_repeated_boundary_parity_checks, split_repeated_counts
from workloads.checkable_mirror_blocks import make_checkable_mirror_blocks, compose_checkable_payload

SCALES=(1,3,5)
FIELDS=[
"qubits","total_depth","check_interval","check_rounds","noise_probability","shots","seed","method",
"absolute_error","estimate","unclipped_estimate","clipped","scale_1","scale_3","scale_5",
"accept_scale_1","accept_scale_3","accept_scale_5","accepted_shots","rejected_shots",
"acceptance_probability","ancilla_qubits","total_physical_qubits","one_qubit_gates",
"two_qubit_gates","aggregate_depth","effective_shots","classical_seconds"]

def gates(c):
    o=c.count_ops()
    return (sum(int(o.get(g,0)) for g in ("h","s","sdg","x","sx","rz")),
            sum(int(o.get(g,0)) for g in ("cx","cz","ecr")))

def execute(c,p,shots,seed):
    sim=AerSimulator(noise_model=depolarizing_noise_model(p))
    tc=transpile(c,sim,optimization_level=0,seed_transpiler=seed)
    t=time.perf_counter()
    counts=sim.run(tc,shots=shots,seed_simulator=seed).result().get_counts()
    return tc,counts,time.perf_counter()-t

def raw(payload,n,d,L,p,shots,seed):
    tc,c,s=execute(payload,p,shots,seed); v=c.get("0"*n,0)/shots; a,b=gates(tc)
    return dict(qubits=n,total_depth=d,check_interval=L,check_rounds=0,noise_probability=p,
      shots=shots,seed=seed,method="raw",absolute_error=abs(1-v),estimate=v,
      unclipped_estimate=v,clipped=0,scale_1=v,scale_3="",scale_5="",
      accept_scale_1=1.0,accept_scale_3="",accept_scale_5="",accepted_shots=shots,
      rejected_shots=0,acceptance_probability=1.0,ancilla_qubits=0,total_physical_qubits=n,
      one_qubit_gates=a,two_qubit_gates=b,aggregate_depth=tc.depth(),effective_shots=shots,
      classical_seconds=s)

def zne(payload,n,d,L,p,shots,seed):
    vals=[]; sec=0; a=b=dep=0
    for scale in SCALES:
        tc,c,t=execute(global_fold(payload,scale),p,shots,seed)
        vals.append(c.get("0"*n,0)/shots); sec+=t
        x,y=gates(tc); a+=x; b+=y; dep+=tc.depth()
    u=linear_zero_noise_extrapolation(SCALES,vals); v=min(1,max(0,u))
    return dict(qubits=n,total_depth=d,check_interval=L,check_rounds=0,noise_probability=p,
      shots=shots,seed=seed,method="zne",absolute_error=abs(1-v),estimate=v,
      unclipped_estimate=u,clipped=int(u!=v),scale_1=vals[0],scale_3=vals[1],scale_5=vals[2],
      accept_scale_1=1.0,accept_scale_3=1.0,accept_scale_5=1.0,accepted_shots=3*shots,
      rejected_shots=0,acceptance_probability=1.0,ancilla_qubits=0,total_physical_qubits=n,
      one_qubit_gates=a,two_qubit_gates=b,aggregate_depth=dep,effective_shots=3*shots,
      classical_seconds=sec)

def checked_at_scale(blocks,scale,p,shots,seed):
    # Fold each ideal-identity block independently so every QED boundary remains valid.
    fb=[global_fold(block,scale) for block in blocks]
    q=add_repeated_boundary_parity_checks(fb)
    tc,c,t=execute(q.circuit,p,shots,seed)
    acc,rej,succ=split_repeated_counts(c)
    cond=succ/acc if acc else 0.0; a,b=gates(tc)
    return dict(v=cond,acc=acc,rej=rej,accept=acc/shots,sec=t,a=a,b=b,dep=tc.depth(),q=q)

def qed(blocks,n,d,L,p,shots,seed):
    r=checked_at_scale(blocks,1,p,shots,seed)
    return dict(qubits=n,total_depth=d,check_interval=L,check_rounds=r["q"].check_rounds,
      noise_probability=p,shots=shots,seed=seed,method="qed_repeated",
      absolute_error=abs(1-r["v"]),estimate=r["v"],unclipped_estimate=r["v"],clipped=0,
      scale_1=r["v"],scale_3="",scale_5="",accept_scale_1=r["accept"],accept_scale_3="",
      accept_scale_5="",accepted_shots=r["acc"],rejected_shots=r["rej"],
      acceptance_probability=r["accept"],ancilla_qubits=r["q"].ancilla_qubits,
      total_physical_qubits=n+r["q"].ancilla_qubits,one_qubit_gates=r["a"],
      two_qubit_gates=r["b"],aggregate_depth=r["dep"],effective_shots=shots,
      classical_seconds=r["sec"])

def hybrid(blocks,n,d,L,p,shots,seed):
    rs=[checked_at_scale(blocks,s,p,shots,seed) for s in SCALES]
    vals=[r["v"] for r in rs]; u=linear_zero_noise_extrapolation(SCALES,vals)
    v=min(1,max(0,u)); acc=sum(r["acc"] for r in rs); rej=sum(r["rej"] for r in rs)
    q=rs[0]["q"]
    return dict(qubits=n,total_depth=d,check_interval=L,check_rounds=q.check_rounds,
      noise_probability=p,shots=shots,seed=seed,method="qed_repeated_zne",
      absolute_error=abs(1-v),estimate=v,unclipped_estimate=u,clipped=int(u!=v),
      scale_1=vals[0],scale_3=vals[1],scale_5=vals[2],
      accept_scale_1=rs[0]["accept"],accept_scale_3=rs[1]["accept"],
      accept_scale_5=rs[2]["accept"],accepted_shots=acc,rejected_shots=rej,
      acceptance_probability=acc/(3*shots),ancilla_qubits=q.ancilla_qubits,
      total_physical_qubits=n+q.ancilla_qubits,one_qubit_gates=sum(r["a"] for r in rs),
      two_qubit_gates=sum(r["b"] for r in rs),aggregate_depth=sum(r["dep"] for r in rs),
      effective_shots=3*shots,classical_seconds=sum(r["sec"] for r in rs))

def run(output):
    rows=[]; grid=[]
    for n in (2,4):
      for d in (8,16):
       for p in (1e-3,1e-2):
        for L in (2,8):
         grid.append((n,d,p,L,1024,0))
    for i,(n,d,p,L,shots,seed) in enumerate(grid,1):
        blocks=make_checkable_mirror_blocks(n,d,L,seed)
        payload=compose_checkable_payload(blocks)
        rr=[raw(payload,n,d,L,p,shots,seed),zne(payload,n,d,L,p,shots,seed),
            qed(blocks,n,d,L,p,shots,seed),hybrid(blocks,n,d,L,p,shots,seed)]
        rows.extend(rr)
        h=rr[3]
        print(f"[{i:>2}/{len(grid)}] q={n} d={d} p={p:g} L={L} | "+
          " ".join(f"{x['method']}={x['absolute_error']:.4f}" for x in rr)+
          f" | hybrid_unclip={h['unclipped_estimate']:.4f} clip={h['clipped']} "+
          f"accepts=({h['accept_scale_1']:.3f},{h['accept_scale_3']:.3f},{h['accept_scale_5']:.3f})",
          flush=True)
    path=Path(output); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",default="results/raw/experiment_2_phase_d.csv")
    a=ap.parse_args(); run(a.output)

if __name__=="__main__":
    main()
