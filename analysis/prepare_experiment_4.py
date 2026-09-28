"""Prepare (but do not execute) Experiment 4 realistic-noise cell manifests."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

REQUIRED_SUMMARY={"complete_conditions":9600,"paired_L_invariance":"passed"}
STRATA=("qem_qed","qed_hybrid","acceptance_0.5","acceptance_0.25","acceptance_0.1")

def require_final_e2(summary_path: Path):
    s=json.loads(summary_path.read_text())
    for k,v in REQUIRED_SUMMARY.items():
        if s.get(k)!=v:
            raise ValueError(
                f"Experiment 4 cannot be locked: E2 summary requires {k}={v!r}, "
                f"found {s.get(k)!r}. Finish E2 and rerun analysis with --require-complete."
            )
    return s

def build_manifest(recommended_path: Path, max_per_stratum=4):
    df=pd.read_csv(recommended_path)
    needed={"boundary_type","qubits","total_depth","noise_probability","shots",
            "check_interval","raw","zne","qed_repeated","qed_repeated_zne",
            "mean_acceptance","clipping_fraction","boundary_score"}
    missing=needed-set(df.columns)
    if missing: raise ValueError(f"Missing E3 design columns: {sorted(missing)}")
    parts=[]
    for label in STRATA:
        x=df[df.boundary_type==label].sort_values("boundary_score").copy()
        if len(x):
            parts.append(x.head(max_per_stratum))
    if not parts:
        raise ValueError("No eligible E3 boundary strata found")
    out=pd.concat(parts,ignore_index=True)
    out=out.drop_duplicates(["qubits","total_depth","noise_probability","shots","check_interval"])
    out.insert(0,"e4_cell_id",[f"E4C{i:03d}" for i in range(1,len(out)+1)])
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--e2-summary",default="results/analysis/experiment_2/summary.json")
    p.add_argument("--e3-design",default="results/analysis/experiment_2/experiment_3_recommended_design.csv")
    p.add_argument("--output",default="results/design/experiment_4_cells.csv")
    p.add_argument("--max-per-stratum",type=int,default=4)
    a=p.parse_args()
    require_final_e2(Path(a.e2_summary))
    out=build_manifest(Path(a.e3_design),a.max_per_stratum)
    path=Path(a.output); path.parent.mkdir(parents=True,exist_ok=True)
    out.to_csv(path,index=False)
    print(f"Locked {len(out)} Experiment 4 base cells -> {path}")
    print("Noise parameter scenarios must be locked separately before E4 execution.")

if __name__=="__main__":
    main()
