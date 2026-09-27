"""Analyze Experiment 1 production data and generate paper-facing outputs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load_and_audit(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(path)
    expected = {
        "qubits", "nominal_depth", "noise_probability", "nominal_shots", "seed",
        "method", "absolute_error", "improvement_vs_raw", "clipped",
        "sampling_overhead_ratio", "gate2_work_ratio", "depth_work_ratio",
        "classical_seconds",
    }
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    key = ["qubits", "nominal_depth", "noise_probability", "nominal_shots", "seed"]
    if len(df) != 12000:
        raise ValueError(f"Expected 12000 rows, found {len(df)}")
    if df.duplicated(key + ["method"]).any():
        raise ValueError("Duplicate method-condition rows detected")

    counts = df.groupby(key)["method"].nunique()
    if not (counts == 2).all():
        raise ValueError("Not every condition has both raw and ZNE rows")

    zne = df[df["method"] == "zne"].copy()
    return df, zne


def ci95(values):
    x = np.asarray(values, dtype=float)
    return 1.96 * x.std(ddof=1) / np.sqrt(len(x))


def save_heatmap(table: pd.DataFrame, output: Path):
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    im = ax.imshow(table.values, aspect="auto")
    ax.set_xticks(range(len(table.columns)), [f"{x:g}" for x in table.columns])
    ax.set_yticks(range(len(table.index)), [str(x) for x in table.index])
    ax.set_xlabel("Depolarizing-noise probability")
    ax.set_ylabel("Nominal circuit depth")
    ax.set_title("Mean ZNE absolute-error improvement")
    for i in range(table.shape[0]):
        for j in range(table.shape[1]):
            ax.text(j, i, f"{table.iloc[i, j]:.3f}", ha="center", va="center")
    fig.colorbar(im, ax=ax, label="Raw error - ZNE error")
    fig.tight_layout()
    fig.savefig(output, dpi=300)
    plt.close(fig)


def save_noise_curves(zne: pd.DataFrame, output: Path):
    g = zne.groupby(["nominal_depth", "noise_probability"])["improvement_vs_raw"].agg(
        ["mean", "std", "count"]
    ).reset_index()
    g["ci95"] = 1.96 * g["std"] / np.sqrt(g["count"])
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for depth, part in g.groupby("nominal_depth"):
        ax.errorbar(
            part["noise_probability"], part["mean"], yerr=part["ci95"],
            marker="o", label=f"Depth {depth}",
        )
    ax.set_xscale("log")
    ax.set_xlabel("Depolarizing-noise probability")
    ax.set_ylabel("Mean absolute-error improvement")
    ax.set_title("ZNE benefit shifts and collapses with circuit depth")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=300)
    plt.close(fig)


def analyze(input_path: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    df, zne = load_and_audit(input_path)

    raw = df[df["method"] == "raw"]
    raw_mean = raw["absolute_error"].mean()
    zne_mean = zne["absolute_error"].mean()
    improvement = zne["improvement_vs_raw"]

    cell_keys = ["qubits", "nominal_depth", "noise_probability", "nominal_shots"]
    cells = zne.groupby(cell_keys)["improvement_vs_raw"].mean().reset_index()
    cell_mean = cells["improvement_vs_raw"].mean()
    cell_ci = ci95(cells["improvement_vs_raw"])

    summary = {
        "rows": int(len(df)),
        "matched_conditions": int(len(zne)),
        "raw_mean_absolute_error": float(raw_mean),
        "zne_mean_absolute_error": float(zne_mean),
        "mean_absolute_improvement": float(improvement.mean()),
        "relative_mean_error_reduction": float(improvement.mean() / raw_mean),
        "individual_improved_fraction": float((improvement > 0).mean()),
        "individual_tied_fraction": float((improvement == 0).mean()),
        "individual_worse_fraction": float((improvement < 0).mean()),
        "seed_aggregated_cells": int(len(cells)),
        "cells_improved": int((cells["improvement_vs_raw"] > 0).sum()),
        "cells_tied": int((cells["improvement_vs_raw"] == 0).sum()),
        "cell_mean_improvement": float(cell_mean),
        "cell_mean_improvement_ci95": [float(cell_mean - cell_ci), float(cell_mean + cell_ci)],
        "zne_clipped_count": int(zne["clipped"].sum()),
        "zne_clipped_fraction": float(zne["clipped"].mean()),
        "raw_total_simulator_seconds": float(raw["classical_seconds"].sum()),
        "zne_total_simulator_seconds": float(zne["classical_seconds"].sum()),
        "runtime_ratio_total": float(
            zne["classical_seconds"].sum() / raw["classical_seconds"].sum()
        ),
        "sampling_overhead_ratio": float(zne["sampling_overhead_ratio"].mean()),
        "two_qubit_gate_work_ratio": float(zne["gate2_work_ratio"].mean()),
        "depth_work_ratio": float(zne["depth_work_ratio"].mean()),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    heat = zne.pivot_table(
        index="nominal_depth", columns="noise_probability",
        values="improvement_vs_raw", aggfunc="mean"
    )
    heat.to_csv(output_dir / "improvement_depth_noise.csv")

    shots = zne.groupby("nominal_shots")["improvement_vs_raw"].agg(
        ["mean", "std", "count"]
    )
    shots["ci95"] = 1.96 * shots["std"] / np.sqrt(shots["count"])
    shots.to_csv(output_dir / "improvement_by_shots.csv")

    clipping = zne.groupby(["nominal_depth", "noise_probability"])["clipped"].agg(
        ["sum", "mean", "count"]
    )
    clipping.to_csv(output_dir / "clipping_depth_noise.csv")

    cells.to_csv(output_dir / "seed_aggregated_cells.csv", index=False)
    save_heatmap(heat, output_dir / "figure_qem_improvement_heatmap.png")
    save_noise_curves(zne, output_dir / "figure_qem_noise_depth_curves.png")

    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="results/raw/experiment_1_local.csv")
    parser.add_argument("--output-dir", default="results/analysis/experiment_1")
    args = parser.parse_args()
    analyze(Path(args.input), Path(args.output_dir))


if __name__ == "__main__":
    main()
