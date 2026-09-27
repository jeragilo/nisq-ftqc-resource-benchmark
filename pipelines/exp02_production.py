"""Experiment 2 production runner: resumable Raw/ZNE/repeated-QED/hybrid sweep."""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import qiskit
import qiskit_aer

from pipelines.exp02_qed_phase_d import FIELDS, hybrid, qed, raw, zne
from workloads.checkable_mirror_blocks import make_checkable_mirror_blocks, compose_checkable_payload

QUBITS=(2,4,6,8)
DEPTHS=(8,16,32,64)
NOISE=(1e-4,3e-4,1e-3,3e-3,1e-2)
SHOTS=(1024,4096,16384)
SEEDS=tuple(range(20))
INTERVALS=(2,8)
METHODS=("raw","zne","qed_repeated","qed_repeated_zne")


def git_commit():
    try:
        return subprocess.check_output(
            ["git","rev-parse","HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def provenance(profile: bool):
    return {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "qiskit_version": qiskit.__version__,
        "qiskit_aer_version": qiskit_aer.__version__,
        "numpy_version": np.__version__,
        "profile": profile,
        "methods": list(METHODS),
    }


def key_from_row(row):
    return (
        int(row["qubits"]), int(row["total_depth"]), float(row["noise_probability"]),
        int(row["shots"]), int(row["seed"]), int(row["check_interval"])
    )


def completed_keys(path: Path):
    if not path.exists() or path.stat().st_size == 0:
        return set()
    methods={}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            methods.setdefault(key_from_row(row),set()).add(row["method"])
    return {k for k,v in methods.items() if set(METHODS) <= v}


def append_four(path: Path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    new=not path.exists() or path.stat().st_size==0
    with path.open("a",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)
        f.flush()
        os.fsync(f.fileno())


def grid(profile: bool):
    if profile:
        # Reduced but deliberately includes a hard/high-overhead condition.
        qs=(2,4)
        ds=(8,16)
        ps=(1e-3,1e-2)
        ss=(1024,)
        seeds=(0,1)
        intervals=(2,8)
    else:
        qs,ds,ps,ss,seeds,intervals=QUBITS,DEPTHS,NOISE,SHOTS,SEEDS,INTERVALS
    return [
        (n,d,p,shots,seed,L)
        for n in qs for d in ds for p in ps for shots in ss for seed in seeds for L in intervals
    ]


def run(output: str, profile=False, resume=False, max_conditions=0):
    path=Path(output)
    meta_path=path.with_suffix(".metadata.json")

    if path.exists() and not resume:
        raise FileExistsError(f"{path} exists; use --resume or choose another output.")

    conditions=grid(profile)
    done=completed_keys(path) if resume else set()
    meta=provenance(profile)
    meta.update({
        "output":str(path),"resume":resume,"conditions_total":len(conditions),
        "conditions_previously_complete":len(done),
        "qubits":sorted({x[0] for x in conditions}),
        "depths":sorted({x[1] for x in conditions}),
        "noise":sorted({x[2] for x in conditions}),
        "shots":sorted({x[3] for x in conditions}),
        "seeds":sorted({x[4] for x in conditions}),
        "check_intervals":sorted({x[5] for x in conditions}),
    })
    meta_path.parent.mkdir(parents=True,exist_ok=True)
    meta_path.write_text(json.dumps(meta,indent=2)+"\n")

    total=len(conditions)
    print(f"Experiment 2: {total} matched interval-conditions / {4*total} method rows")
    print(f"Output: {path}")
    print(f"Already complete: {len(done)}")
    print("Checkpointing after each four-method condition; restart with --resume.")

    start=time.perf_counter()
    completed_this_run=0

    for n,d,p,shots,seed,L in conditions:
        key=(n,d,p,shots,seed,L)
        if key in done:
            continue

        blocks=make_checkable_mirror_blocks(n,d,L,seed)
        payload=compose_checkable_payload(blocks)
        rows=[
            raw(payload,n,d,L,p,shots,seed),
            zne(payload,n,d,L,p,shots,seed),
            qed(blocks,n,d,L,p,shots,seed),
            hybrid(blocks,n,d,L,p,shots,seed),
        ]
        append_four(path,rows)
        done.add(key)
        completed_this_run+=1

        elapsed=time.perf_counter()-start
        rate=completed_this_run/elapsed if elapsed else 0.0
        remaining=total-len(done)
        eta=remaining/rate if rate else float("inf")
        h=rows[3]
        print(
            f"[{len(done):>4}/{total}] q={n} d={d} p={p:g} shots={shots} seed={seed:02d} L={L} "
            f"| raw={rows[0]['absolute_error']:.4f} zne={rows[1]['absolute_error']:.4f} "
            f"qed={rows[2]['absolute_error']:.4f} hybrid={h['absolute_error']:.4f} "
            f"| A=({h['accept_scale_1']:.3f},{h['accept_scale_3']:.3f},{h['accept_scale_5']:.3f}) "
            f"| elapsed={elapsed/60:.1f}m ETA={eta/60:.1f}m",
            flush=True,
        )

    elapsed=time.perf_counter()-start
    meta["completed_utc"]=datetime.now(timezone.utc).isoformat()
    meta["elapsed_seconds_this_run"]=elapsed
    meta["conditions_complete"]=len(done)
    meta_path.write_text(json.dumps(meta,indent=2)+"\n")
    print(f"Complete: {len(done)}/{total} conditions ({4*len(done)} rows)")
    print(f"Elapsed this run: {elapsed/60:.2f} minutes")
    if profile and completed_this_run:
        sec_per=elapsed/completed_this_run
        full_conditions=len(grid(False))
        est=sec_per*full_conditions
        print(f"Profile mean: {sec_per:.3f} s/condition")
        print(f"Naive full-grid estimate at this mean rate: {est/3600:.2f} hours")
        print("Treat this only as a first-order estimate; larger widths/depths may run slower.")
    print(f"Data: {path}")
    print(f"Metadata: {meta_path}")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",default="results/raw/experiment_2_production.csv")
    ap.add_argument("--profile",action="store_true")
    ap.add_argument("--resume",action="store_true")
    a=ap.parse_args()
    run(a.output,profile=a.profile,resume=a.resume,max_conditions=a.max_conditions)


if __name__=="__main__":
    main()
