"""Analyze Experiment 2 Phase C check-interval resource frontier."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

def analyze(path: Path, out: Path):
    df=pd.read_csv(path)
    q=df[df.method=="qed_repeated"].copy()
    r=df[df.method=="raw"].copy()
    keys=["qubits","total_depth","check_interval","noise_probability","shots","seed"]
    m=q.merge(r,on=keys,suffixes=("_qed","_raw"))
    m["error_improvement"]=m.absolute_error_raw-m.absolute_error_qed
    m["acceptance_cost"]=1-m.acceptance_probability_qed
    m["accepted_sample_overhead"]=1/m.acceptance_probability_qed
    m["twoq_ratio"]=m.two_qubit_gates_qed/m.two_qubit_gates_raw
    m["qubit_ratio"]=m.total_physical_qubits_qed/m.total_physical_qubits_raw

    # Pareto efficiency within each physical condition for error, rejection,
    # physical qubits, and 2Q work. A point is dominated only if another interval
    # is no worse in all four dimensions and strictly better in at least one.
    m["pareto_efficient"]=False
    group=["qubits","total_depth","noise_probability","shots","seed"]
    for _,idx in m.groupby(group).groups.items():
        ids=list(idx)
        for i in ids:
            a=m.loc[i]
            dominated=False
            for j in ids:
                if i==j: continue
                b=m.loc[j]
                no_worse=(
                    b.absolute_error_qed<=a.absolute_error_qed and
                    b.acceptance_cost<=a.acceptance_cost and
                    b.total_physical_qubits_qed<=a.total_physical_qubits_qed and
                    b.two_qubit_gates_qed<=a.two_qubit_gates_qed
                )
                strictly=(
                    b.absolute_error_qed<a.absolute_error_qed or
                    b.acceptance_cost<a.acceptance_cost or
                    b.total_physical_qubits_qed<a.total_physical_qubits_qed or
                    b.two_qubit_gates_qed<a.two_qubit_gates_qed
                )
                if no_worse and strictly:
                    dominated=True; break
            m.loc[i,"pareto_efficient"]=not dominated

    out.mkdir(parents=True,exist_ok=True)
    m.to_csv(out/"phase_c_matched_analysis.csv",index=False)
    summary=m.groupby(["qubits","total_depth","noise_probability","check_interval"]).agg(
        raw_error=("absolute_error_raw","mean"),
        qed_error=("absolute_error_qed","mean"),
        error_improvement=("error_improvement","mean"),
        acceptance=("acceptance_probability_qed","mean"),
        ancillas=("ancilla_qubits_qed","mean"),
        twoq=("two_qubit_gates_qed","mean"),
        pareto=("pareto_efficient","all"),
    ).reset_index()
    summary.to_csv(out/"phase_c_interval_summary.csv",index=False)
    print(summary.to_string(index=False))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",default="results/raw/experiment_2_phase_c.csv")
    ap.add_argument("--output-dir",default="results/analysis/experiment_2_phase_c")
    a=ap.parse_args()
    analyze(Path(a.input),Path(a.output_dir))

if __name__=="__main__":
    main()
