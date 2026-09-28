"""Prepare a prospectively frozen Experiment 5 hardware-validation manifest."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

def require_final(summary: Path, label: str, key: str, value):
    s=json.loads(summary.read_text())
    if s.get(key)!=value:
        raise ValueError(f"{label} not final: expected {key}={value!r}, found {s.get(key)!r}")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--e2-summary",default="results/analysis/experiment_2/summary.json")
    p.add_argument("--e4-summary",default="results/analysis/experiment_4/summary.json")
    p.add_argument("--e4-results",default="results/analysis/experiment_4/regime_validation.csv")
    p.add_argument("--output",default="results/design/experiment_5_hardware_manifest.csv")
    p.add_argument("--max-cells",type=int,default=40)
    a=p.parse_args()

    require_final(Path(a.e2_summary),"Experiment 2","complete_conditions",9600)
    require_final(Path(a.e4_summary),"Experiment 4","status","complete")

    df=pd.read_csv(a.e4_results)
    required={"regime_class","qubits","total_depth","shots","check_interval",
              "predicted_best_method","prediction_confidence"}
    missing=required-set(df.columns)
    if missing: raise ValueError(f"Missing E4 validation columns: {sorted(missing)}")

    # Balanced prospective selection by regime; prefer higher-confidence predictions,
    # while retaining boundary/stress cases represented by their regime labels.
    labels=list(dict.fromkeys(df["regime_class"].tolist()))
    per=max(1,a.max_cells//max(1,len(labels)))
    pieces=[]
    for label in labels:
        x=df[df.regime_class==label].sort_values("prediction_confidence",ascending=False)
        pieces.append(x.head(per))
    out=pd.concat(pieces,ignore_index=True).head(a.max_cells)
    out.insert(0,"e5_case_id",[f"E5C{i:03d}" for i in range(1,len(out)+1)])
    out["hardware_status"]="not_submitted"
    out["prediction_frozen"]=True

    path=Path(a.output); path.parent.mkdir(parents=True,exist_ok=True)
    out.to_csv(path,index=False)
    print(f"Frozen {len(out)} prospective E5 cases -> {path}")
    print("Do not edit predicted outcomes after inspecting hardware results.")

if __name__=="__main__":
    main()
