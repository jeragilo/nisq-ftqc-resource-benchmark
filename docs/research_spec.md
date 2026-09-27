# Paper 2 Research Specification v1.0

## Working title

**Bridging NISQ and Fault-Tolerant Quantum Computing: Resource-Aware Error Mitigation and Quantum Error Correction on Real Hardware**

## Publication target

ACM Transactions on Quantum Computing (TQC).

## Central thesis

Error management across the NISQ-to-FTQC transition should not be evaluated solely by error reduction. QEM, QED, and QEC exchange different resources for reliability, so practical utility should be evaluated jointly across sampling, quantum-hardware, execution-time, and classical-decoding costs.

## Research questions and hypotheses

### RQ1 — Reliability
How does reliability achieved by raw NISQ execution, QEM, QED, hybrid mitigation/detection, and QEC vary with physical noise strength and circuit complexity?

**H1.** Error-management strategies will exhibit different reliability regimes as physical noise and circuit complexity increase.

### RQ2 — Resource efficiency
How do the quantum and classical resource costs required to achieve a target reliability differ across QEM, QED, hybrid error management, and QEC?

**H2.** No single strategy will dominate all resource dimensions; QEM preferentially exchanges sampling/execution cost for reliability, while QED/QEC increasingly exchange physical-qubit, circuit, and decoding resources for reliability.

### RQ3 — Error-management crossover
Under what combinations of noise, circuit complexity, and resource availability does the resource-efficient strategy transition among raw NISQ execution, QEM, QED/hybrid protection, and QEC?

**H3.** Distinct crossover regions will emerge in which the Pareto-efficient strategy changes with noise, circuit complexity, and available resources.

### RQ4 — Classical decoding
How does classical decoder capability and computational cost affect the resource-performance tradeoff of error-corrected quantum computation?

**H4.** Increased decoder sophistication can reduce logical error under appropriate noise conditions, but improvement must be evaluated against decoder latency and computational overhead.

### RQ5 — Real hardware
To what extent do crossover and resource-efficiency conclusions obtained under controlled simulation persist on real quantum hardware under temporally varying device conditions?

**H5.** Hardware variability will shift quantitative crossover points relative to stationary-noise simulations, while sufficiently robust qualitative trends may remain observable across repeated executions.

## Target contributions

- **C1 — Unified error-management framework:** common experimental framework spanning raw NISQ, QEM, QED, hybrid error management, and QEC.
- **C2 — Multi-resource accounting:** jointly track sampling, physical-qubit, ancilla, gate, depth, QPU-time, postselection, and classical-decoding costs.
- **C3 — Crossover/Pareto characterization:** empirically identify Pareto-efficient regimes and crossover regions without collapsing resources into an arbitrary weighted scalar.
- **C4 — Real-hardware validation:** validate selected tradeoffs on physical quantum hardware while recording calibration/execution conditions.
- **C5 — Quantum-classical systems analysis:** treat classical decoding latency and compute requirements as explicit FTQC resource costs.

These are target contributions until supported by experimental evidence.

## Core resource vector

For method m:

R_m = [N_q, N_a, N_s, N_reject, N_1q, N_2q, D, T_QPU, T_decode, T_post]

where:
- N_q: physical qubits
- N_a: ancillas
- N_s: shots
- N_reject: rejected/postselected shots
- N_1q: one-qubit gates
- N_2q: two-qubit gates
- D: transpiled circuit depth
- T_QPU: QPU execution time
- T_decode: decoder latency/time
- T_post: classical post-processing time

## Error-management continuum

RAW -> QEM -> QED -> QED+QEM -> QEC

This ordering is a conceptual continuum, not a claim that empirical crossover regions must appear in this order.

## Planned experiments

### Experiment 0 — Raw vs ZNE
Small reproducible Clifford/mirror-style circuits under depolarizing noise:
- qubits: {2, 4}
- nominal depths: {5, 10, 20}
- initial physical error probabilities: {1e-4, 3e-4, 1e-3, 3e-3, 1e-2}
- shot budgets: {1024, 4096, 16384}
- conditions: ideal, raw noisy, ZNE
- record reliability and resource metrics

### Experiment 1
Noise x depth x shot-budget QEM sweep.

### Experiment 2
QED/postselection with controlled detection intervals.

### Experiment 3
Hybrid QED + QEM.

### Experiment 4
Repetition/surface-code QEC with MWPM/PyMatching.

### Experiment 5
Decoder accuracy/latency/resource benchmark; learned/soft-information decoder only if scientifically justified.

### Experiment 6
IBM Quantum hardware validation with backend and calibration metadata.

### Experiment 7
Pareto and crossover synthesis.

## Statistical protocol

- repeated seeded simulation trials
- controlled shot budgets
- means, standard deviations, and 95% confidence intervals
- paired/matched comparisons where appropriate
- effect sizes
- multiple-comparison correction where required
- hardware execution batch/calibration treated as experimental context

## Manuscript target

Approximate main-text budget: 11,400 words plus ~225-word abstract.

1. Introduction — 1,150
2. Background and Related Work — 1,600
3. Resource-Aware NISQ-to-FTQC Framework — 1,600
4. Experimental Methodology — 1,700
5. Error-Management Performance — 1,650
6. Resource-Crossover Analysis — 1,400
7. Real-Hardware Evaluation — 1,050
8. Discussion — 900
9. Conclusion — 350

## Scientific guardrails

- Do not claim that QEM+QEC, QED+QEM, real-hardware QEC, or resource-aware QEM are novel by themselves.
- Do not claim a universal crossover law unless evidence supports generalization.
- Keep simulation and real-hardware evidence explicitly separated.
- Preserve raw experimental outputs and metadata.
- Treat contribution statements as provisional until results support them.
