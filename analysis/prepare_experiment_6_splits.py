"""Create a leakage-safe grouped split manifest for Experiment 6."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import pandas as pd

GROUP=["qubits","total_depth","noise_probability","shots","seed"]

def stable_bucket(values, salt):
    s="|".join(map(str,values))+"|"+salt
    return int(hashlib.sha256(s.encode()).hexdigest()[:12],16)%10000

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",default="results/raw/experiment_2_production_v2.csv")
    p.add_argument("--e2-summary",default="results/analysis/experiment_2/summary.json")
    p.add_argument("--output",default="results/design/experiment_6_split_manifest.csv")
    p.add_argument("--salt",default="paper2-e6-v1")
    a=p.parse_args()

    summary=json.loads(Path(a.e2_summary).read_text())
    if summary.get("complete_conditions")!=9600 or summary.get("paired_L_invariance")!="passed":
        raise ValueError("E6 split cannot be frozen until final E2=9600 and paired-L audit passes.")

    df=pd.read_csv(a.input)
    missing=set(GROUP)-set(df.columns)
    if missing: raise ValueError(f"Missing grouping columns: {sorted(missing)}")

    groups=df[GROUP].drop_duplicates().copy()
    groups["split_bucket"]=[stable_bucket(row,a.salt) for row in groups[GROUP].itertuples(index=False,name=None)]
    # 70/15/15 deterministic grouped split.
    groups["split"]=groups["split_bucket"].map(
        lambda x:"train" if x<7000 else ("validation" if x<8500 else "test")
    )
    groups["split_salt"]=a.salt

    path=Path(a.output); path.parent.mkdir(parents=True,exist_ok=True)
    groups.to_csv(path,index=False)
    counts=groups["split"].value_counts().to_dict()
    print(json.dumps({"groups":len(groups),"split_counts":counts,"output":str(path)},indent=2))
    print("Freeze this manifest before E6 model/hyperparameter selection.")

if __name__=="__main__":
    main()
