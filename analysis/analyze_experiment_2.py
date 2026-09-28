"""Analyze Experiment 2 production data and select crossover cells for Experiment 3."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

METHODS=("raw","zne","qed_repeated","qed_repeated_zne")
KEY=["qubits","total_depth","noise_probability","shots","seed","check_interval"]
CELL=["qubits","total_depth","noise_probability","shots","check_interval"]

def ci95(x):
    x=np.asarray(x,dtype=float)
    if len(x)<2: return float("nan")
    return float(1.96*x.std(ddof=1)/np.sqrt(len(x)))

def load_and_audit(path: Path, require_complete=False):
    df=pd.read_csv(path)
    required=set(KEY+[
        "method","absolute_error","estimate","unclipped_estimate","clipped",
        "accept_scale_1","accept_scale_3","accept_scale_5","accepted_shots",
        "rejected_shots","acceptance_probability","ancilla_qubits",
        "total_physical_qubits","one_qubit_gates","two_qubit_gates",
        "aggregate_depth","effective_shots","classical_seconds",
    ])
    missing=required-set(df.columns)
    if missing: raise ValueError(f"Missing columns: {sorted(missing)}")
    if df.duplicated(KEY+["method"]).any():
        raise ValueError("Duplicate method-condition rows detected")

    counts=df.groupby(KEY)["method"].agg(lambda s:set(s))
    bad=counts[counts.apply(lambda s:set(METHODS)!=s)]
    if len(bad):
        raise ValueError(f"{len(bad)} conditions do not contain exactly the four methods")

    n_conditions=len(counts)
    if require_complete and n_conditions!=9600:
        raise ValueError(f"Expected 9600 complete conditions, found {n_conditions}")

    # Paired-design audit: Raw and ZNE must not depend on check interval.
    pair=["qubits","total_depth","noise_probability","shots","seed","method"]
    base=df[df.method.isin(["raw","zne"])]
    nunique=base.groupby(pair)["absolute_error"].nunique(dropna=False)
    if (nunique>1).any():
        raise ValueError(f"Paired-L invariant failed for {(nunique>1).sum()} Raw/ZNE pairs")

    return df,n_conditions

def aggregate(df):
    agg=df.groupby(CELL+["method"]).agg(
        mean_error=("absolute_error","mean"),
        std_error=("absolute_error","std"),
        n_seeds=("absolute_error","size"),
        mean_acceptance=("acceptance_probability","mean"),
        mean_accepted_shots=("accepted_shots","mean"),
        mean_two_qubit_gates=("two_qubit_gates","mean"),
        mean_depth=("aggregate_depth","mean"),
        mean_physical_qubits=("total_physical_qubits","mean"),
        mean_effective_shots=("effective_shots","mean"),
        mean_seconds=("classical_seconds","mean"),
        clipping_fraction=("clipped","mean"),
        mean_unclipped=("unclipped_estimate","mean"),
    ).reset_index()
    agg["error_ci95"]=agg.groupby(CELL+["method"])["mean_error"].transform(lambda _: np.nan)
    # one row per cell/method: compute CI directly from raw seeds
    cis=df.groupby(CELL+["method"])["absolute_error"].apply(ci95).rename("error_ci95").reset_index()
    agg=agg.drop(columns=["error_ci95"]).merge(cis,on=CELL+["method"],how="left")
    return agg

def method_wide(agg):
    w=agg.pivot(index=CELL,columns="method",values="mean_error").reset_index()
    w.columns=[c if isinstance(c,str) else c for c in w.columns]
    w["zne_gain_vs_raw"]=w["raw"]-w["zne"]
    w["qed_gain_vs_raw"]=w["raw"]-w["qed_repeated"]
    w["hybrid_gain_vs_raw"]=w["raw"]-w["qed_repeated_zne"]
    w["qed_minus_zne"]=w["qed_repeated"]-w["zne"]
    w["hybrid_minus_best_single"]=w["qed_repeated_zne"]-w[["zne","qed_repeated"]].min(axis=1)
    return w

def crossover_candidates(wide, agg, top_n=60):
    # Small |QED-ZNE| = empirical crossover neighborhood.
    c=wide.copy()
    c["qem_qed_gap"]=c["qed_minus_zne"].abs()
    # Add hybrid acceptance/clipping diagnostics.
    h=agg[agg.method=="qed_repeated_zne"][CELL+[
        "mean_acceptance","clipping_fraction","mean_two_qubit_gates",
        "mean_depth","mean_effective_shots"
    ]]
    c=c.merge(h,on=CELL,how="left")
    c["acceptance_penalty"]=1-c["mean_acceptance"]
    c["candidate_score"]=(
        c["qem_qed_gap"]
        +0.02*c["clipping_fraction"]
    )
    # Preserve regime diversity instead of selecting only easy low-noise cells.
    ranked=c.sort_values(["candidate_score","noise_probability","total_depth"],ascending=[True,False,False])
    return ranked.head(top_n)

def l_comparison(agg):
    q=agg[agg.method.isin(["qed_repeated","qed_repeated_zne"])].copy()
    idx=["qubits","total_depth","noise_probability","shots","method"]
    e=q.pivot(index=idx,columns="check_interval",values="mean_error").reset_index()
    a=q.pivot(index=idx,columns="check_interval",values="mean_acceptance").reset_index()
    if 2 in e.columns and 8 in e.columns:
        e["error_L2_minus_L8"]=e[2]-e[8]
    if 2 in a.columns and 8 in a.columns:
        a["accept_L2_minus_L8"]=a[2]-a[8]
    return e,a

def analyze(input_path: Path, output_dir: Path, require_complete=False):
    output_dir.mkdir(parents=True,exist_ok=True)
    df,n_conditions=load_and_audit(input_path,require_complete=require_complete)
    agg=aggregate(df)
    wide=method_wide(agg)
    candidates=crossover_candidates(wide,agg)
    lerr,lacc=l_comparison(agg)

    hybrid=df[df.method=="qed_repeated_zne"]
    summary={
        "rows":int(len(df)),
        "complete_conditions":int(n_conditions),
        "completion_fraction":float(n_conditions/9600),
        "seed_aggregated_method_cells":int(len(agg)),
        "hybrid_clipping_fraction":float(hybrid.clipped.mean()),
        "hybrid_mean_acceptance":float(hybrid.acceptance_probability.mean()),
        "raw_mean_error":float(df[df.method=="raw"].absolute_error.mean()),
        "zne_mean_error":float(df[df.method=="zne"].absolute_error.mean()),
        "qed_mean_error":float(df[df.method=="qed_repeated"].absolute_error.mean()),
        "hybrid_mean_error":float(hybrid.absolute_error.mean()),
        "qem_qed_crossover_candidates_written":int(len(candidates)),
        "paired_L_invariance":"passed",
    }
    (output_dir/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    agg.to_csv(output_dir/"seed_aggregated_method_cells.csv",index=False)
    wide.to_csv(output_dir/"method_comparison_cells.csv",index=False)
    candidates.to_csv(output_dir/"experiment_3_crossover_candidates.csv",index=False)
    lerr.to_csv(output_dir/"check_interval_error_comparison.csv",index=False)
    lacc.to_csv(output_dir/"check_interval_acceptance_comparison.csv",index=False)

    # Regime table: which method has lowest conditional error (descriptive, not cost-optimal).
    method_cols=["raw","zne","qed_repeated","qed_repeated_zne"]
    regime=wide[CELL+method_cols].copy()
    regime["lowest_error_method"]=regime[method_cols].idxmin(axis=1)
    regime.to_csv(output_dir/"lowest_error_regimes.csv",index=False)

    print(json.dumps(summary,indent=2))
    print(f"Experiment 3 candidates: {output_dir/'experiment_3_crossover_candidates.csv'}")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",default="results/raw/experiment_2_production_v2.csv")
    p.add_argument("--output-dir",default="results/analysis/experiment_2")
    p.add_argument("--require-complete",action="store_true",
                   help="Require all 9600 production conditions; omit during an in-progress run.")
    a=p.parse_args()
    analyze(Path(a.input),Path(a.output_dir),require_complete=a.require_complete)

if __name__=="__main__":
    main()
