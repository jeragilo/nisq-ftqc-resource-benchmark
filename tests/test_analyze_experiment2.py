"""Tests for Experiment 2 paper-facing analysis."""
import pandas as pd
import pytest

from analysis.analyze_experiment_2 import load_and_audit

BASE={
    "qubits":2,"total_depth":8,"noise_probability":0.001,"shots":1024,"seed":0,
    "absolute_error":0.1,"estimate":0.9,"unclipped_estimate":0.9,"clipped":0,
    "accept_scale_1":1.0,"accept_scale_3":1.0,"accept_scale_5":1.0,
    "accepted_shots":1024,"rejected_shots":0,"acceptance_probability":1.0,
    "ancilla_qubits":0,"total_physical_qubits":2,"one_qubit_gates":1,
    "two_qubit_gates":1,"aggregate_depth":1,"effective_shots":1024,
    "classical_seconds":0.01,
}

def make_rows():
    rows=[]
    for L in (2,8):
        for method in ("raw","zne","qed_repeated","qed_repeated_zne"):
            r=dict(BASE,check_interval=L,method=method)
            if method.startswith("qed"):
                r["ancilla_qubits"]=1
                r["total_physical_qubits"]=3
            rows.append(r)
    return rows

def test_analysis_accepts_paired_intervals(tmp_path):
    p=tmp_path/"x.csv"
    pd.DataFrame(make_rows()).to_csv(p,index=False)
    _,n=load_and_audit(p)
    assert n==2

def test_analysis_rejects_incomplete_condition(tmp_path):
    rows=make_rows()
    rows.pop()
    p=tmp_path/"x.csv"
    pd.DataFrame(rows).to_csv(p,index=False)
    with pytest.raises(ValueError,match="four methods"):
        load_and_audit(p)

def test_analysis_rejects_raw_change_across_L(tmp_path):
    rows=make_rows()
    for r in rows:
        if r["method"]=="raw" and r["check_interval"]==8:
            r["absolute_error"]=0.2
    p=tmp_path/"x.csv"
    pd.DataFrame(rows).to_csv(p,index=False)
    with pytest.raises(ValueError,match="Paired-L invariant"):
        load_and_audit(p)
