"""Tests for Experiment 2 paper-facing analysis."""
import pandas as pd
import pytest

from analysis.analyze_experiment_2 import load_and_audit, targeted_candidates

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


def test_targeted_qem_qed_excludes_trivial_raw_regime():
    wide=pd.DataFrame([
        dict(qubits=2,total_depth=8,noise_probability=1e-4,shots=1024,check_interval=2,
             raw=0.005,zne=0.0010,qed_repeated=0.00101,qed_repeated_zne=0.0005,
             zne_gain_vs_raw=0.004,qed_gain_vs_raw=0.00399,hybrid_gain_vs_raw=0.0045,
             qed_minus_zne=0.00001,hybrid_minus_best_single=-0.0005),
        dict(qubits=4,total_depth=32,noise_probability=3e-4,shots=4096,check_interval=2,
             raw=0.06,zne=0.012,qed_repeated=0.011,qed_repeated_zne=0.004,
             zne_gain_vs_raw=0.048,qed_gain_vs_raw=0.049,hybrid_gain_vs_raw=0.056,
             qed_minus_zne=-0.001,hybrid_minus_best_single=-0.007),
    ])
    agg=pd.DataFrame([
        dict(qubits=2,total_depth=8,noise_probability=1e-4,shots=1024,check_interval=2,
             method="qed_repeated_zne",mean_acceptance=0.99,clipping_fraction=0.0,
             mean_two_qubit_gates=10,mean_depth=10,mean_effective_shots=3072),
        dict(qubits=4,total_depth=32,noise_probability=3e-4,shots=4096,check_interval=2,
             method="qed_repeated_zne",mean_acceptance=0.80,clipping_fraction=0.0,
             mean_two_qubit_gates=100,mean_depth=100,mean_effective_shots=12288),
    ])
    qem_qed,_,_=targeted_candidates(wide,agg)
    assert (qem_qed["raw"]>=0.02).all()
    assert len(qem_qed)==1

def test_targeted_hybrid_penalizes_heavy_clipping():
    wide=pd.DataFrame([
        dict(qubits=4,total_depth=32,noise_probability=1e-3,shots=4096,check_interval=2,
             raw=0.18,zne=0.09,qed_repeated=0.04,qed_repeated_zne=0.039,
             zne_gain_vs_raw=0.09,qed_gain_vs_raw=0.14,hybrid_gain_vs_raw=0.141,
             qed_minus_zne=-0.05,hybrid_minus_best_single=-0.001),
    ])
    agg=pd.DataFrame([
        dict(qubits=4,total_depth=32,noise_probability=1e-3,shots=4096,check_interval=2,
             method="qed_repeated_zne",mean_acceptance=0.60,clipping_fraction=0.60,
             mean_two_qubit_gates=100,mean_depth=100,mean_effective_shots=12288),
    ])
    _,qed_hybrid,_=targeted_candidates(wide,agg)
    assert qed_hybrid.empty
