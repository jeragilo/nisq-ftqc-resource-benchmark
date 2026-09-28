"""Freeze source/held-out target domains for Experiment 8."""
from __future__ import annotations
import argparse, hashlib
from pathlib import Path
import pandas as pd

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,help="CSV with domain_id and optional provider/device metadata")
    p.add_argument("--output",default="results/design/experiment_8_domain_split.csv")
    p.add_argument("--target-domain",default=None,
                   help="Predeclared held-out target. If omitted, deterministic hash selection is used.")
    p.add_argument("--salt",default="paper2-e8-v1")
    a=p.parse_args()

    df=pd.read_csv(a.input)
    if "domain_id" not in df.columns:
        raise ValueError("Input requires domain_id.")
    domains=df.drop_duplicates("domain_id").copy()
    if len(domains)<2:
        raise ValueError("E8 requires at least two distinct hardware domains.")

    ids=sorted(domains.domain_id.astype(str).tolist())
    if a.target_domain is not None:
        if a.target_domain not in ids:
            raise ValueError(f"Unknown target domain: {a.target_domain}")
        target=a.target_domain
    else:
        scored=[(hashlib.sha256((x+"|"+a.salt).encode()).hexdigest(),x) for x in ids]
        target=sorted(scored)[0][1]

    domains["e8_role"]=domains.domain_id.astype(str).map(
        lambda x:"heldout_target" if x==target else "source"
    )
    domains["split_salt"]=a.salt
    path=Path(a.output); path.parent.mkdir(parents=True,exist_ok=True)
    domains.to_csv(path,index=False)
    print(f"Held-out E8 target domain: {target}")
    print(f"Frozen domain split -> {path}")
    print("Do not move the target domain after inspecting target outcomes.")

if __name__=="__main__":
    main()
