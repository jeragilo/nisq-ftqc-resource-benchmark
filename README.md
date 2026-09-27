# NISQ–FTQC Resource Benchmark

Research code for **“Bridging NISQ and Fault-Tolerant Quantum Computing: Resource-Aware Error Mitigation and Quantum Error Correction on Real Hardware.”**

## Research objective

This project studies when resource-efficient quantum error management transitions from raw NISQ execution to quantum error mitigation (QEM), quantum error detection (QED), hybrid protection, and quantum error correction (QEC).

Rather than ranking methods only by output error, experiments jointly track sampling, quantum-hardware, execution-time, and classical-decoding costs.

## Working publication target

**ACM Transactions on Quantum Computing (TQC)**

## Planned experimental progression

1. Experiment 0 — ideal vs. raw noisy vs. zero-noise extrapolation (ZNE)
2. Noise/depth/shot-budget sweeps
3. Quantum error detection and postselection
4. Hybrid QED + QEM
5. Repetition/surface-code QEC with MWPM decoding
6. Classical decoder resource benchmarking
7. IBM Quantum hardware validation
8. Pareto and NISQ-to-FTQC crossover analysis

See `docs/research_spec.md` for the locked scientific specification.

## Status

Research scaffold initialized. Experimental results are not yet available.
