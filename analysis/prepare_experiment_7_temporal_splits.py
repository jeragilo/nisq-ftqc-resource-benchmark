"""Create chronological train/validation/test windows for Experiment 7."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,help="CSV with calibration_window_id and timestamp")
    p.add_argument("--output",default="results/design/experiment_7_temporal_split.csv")
    p.add_argument("--train-frac",type=float,default=0.60)
    p.add_argument("--validation-frac",type=float,default=0.20)
    a=p.parse_args()

    if a.train_frac<=0 or a.validation_frac<=0 or a.train_frac+a.validation_frac>=1:
        raise ValueError("Need positive train/validation fractions with nonempty test fraction.")

    df=pd.read_csv(a.input)
    required={"calibration_window_id","timestamp"}
    missing=required-set(df.columns)
    if missing: raise ValueError(f"Missing temporal columns: {sorted(missing)}")
    df["timestamp"]=pd.to_datetime(df["timestamp"],utc=True,errors="raise")

    windows=(df.groupby("calibration_window_id",as_index=False)["timestamp"]
             .min().rename(columns={"timestamp":"window_start"})
             .sort_values("window_start").reset_index(drop=True))
    n=len(windows)
    if n<5: raise ValueError("At least 5 distinct chronological calibration windows are required.")

    n_train=max(1,int(n*a.train_frac))
    n_val=max(1,int(n*a.validation_frac))
    if n_train+n_val>=n:
        n_val=max(1,n-n_train-1)

    windows["split"]="test"
    windows.loc[:n_train-1,"split"]="train"
    windows.loc[n_train:n_train+n_val-1,"split"]="validation"
    windows["chronological_order"]=range(1,n+1)

    path=Path(a.output); path.parent.mkdir(parents=True,exist_ok=True)
    windows.to_csv(path,index=False)
    print(windows.groupby("split").size().to_string())
    print(f"Chronological E7 split -> {path}")
    print("Do not reshuffle windows after inspecting held-out outcomes.")

if __name__=="__main__":
    main()
