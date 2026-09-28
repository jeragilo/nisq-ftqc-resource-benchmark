# Experiment 8 — Cross-Platform Generalization Protocol

## Purpose

Experiment 8 is the capstone generalization test for the unified Paper 2.

Experiments 1–7 establish resource-aware error-management regimes, realistic-noise robustness, hardware validity, static adaptation, and calibration-aware adaptation. E8 asks whether the resulting framework transfers beyond the hardware environment on which it was developed.

## Central research question

Does the resource-aware error-management framework generalize to unseen quantum devices/platforms, even when device-specific crossover thresholds and optimal actions change?

## Key distinction

E8 distinguishes:

1. **framework transfer** — the same inputs/objectives/action formalism remains useful on a new device;
2. **parameter/threshold transfer** — numerical crossover thresholds or policy parameters transfer unchanged.

Framework transfer does NOT require identical thresholds across devices.

## Dependency rule

Primary E8 evaluation begins only after:
- E6 static policy is frozen;
- E7 dynamic/calibration-aware protocol is frozen;
- at least two sufficiently distinct hardware environments are available for comparable execution;
- one target device/platform is designated as held-out before its primary outcomes are inspected.

## Domains

A domain is a device/platform plus its execution/calibration environment.

Prefer diversity in at least one of:
- device generation;
- connectivity/topology;
- native gate characteristics;
- coherence/error profile;
- control/dynamic-circuit behavior;
- provider/platform, when technically feasible.

A comparison of two calibration snapshots of the same device is E7-style temporal validation, not sufficient by itself for E8.

## Workload panel

Use a frozen cross-platform-compatible workload panel spanning:
- QEM-favorable;
- QEM↔QED boundary;
- QED-favorable;
- QED↔Hybrid boundary;
- Hybrid-favorable;
- acceptance-limited/stress cases.

Only circuits implementable with comparable semantics on all primary domains belong in the core cross-platform panel.

Platform-specific supplemental experiments may be reported separately.

## Evaluation modes

### E8-A — Zero-shot transfer

Apply the frozen source-domain E6/E7 policy to the unseen target domain without target-outcome training.

This is the strongest transfer test.

### E8-B — Calibration-feature transfer

Allow target hardware-state/calibration descriptors available before execution, but no labeled target method outcomes.

### E8-C — Few-shot adaptation

Permit a small, predeclared target calibration/probe set, include its quantum-resource cost, adapt the policy, and evaluate on separate target test workloads.

The few-shot adaptation budget must be frozen before target test outcomes are inspected.

## Comparators

On each target domain compare:
- best fixed strategy selected without target test leakage;
- source-domain static E6 policy;
- calibration-aware E7 policy where applicable;
- zero-shot E8 policy;
- few-shot adapted E8 policy;
- target-domain oracle (analysis-only upper bound).

## Domain split

The primary target device/domain is held out at the domain level.

No method outcomes from the held-out target test domain may enter source policy fitting, threshold selection, hyperparameter selection, or feature engineering.

If more than two domains are available, add leave-one-domain-out evaluation.

## Inputs

Use only pre-execution information:
- workload descriptors;
- target reliability/resource budget;
- device/platform descriptors;
- current calibration descriptors where allowed by the evaluation mode.

Provider identity may be included only if justified and ablated; the policy should not merely memorize a device label.

## Outcomes

Primary:
- reliability/resource objective on held-out domain;
- regret relative to target oracle;
- constraint-violation rate;
- improvement versus fixed and source-only policies.

Generalization diagnostics:
- action agreement/disagreement;
- crossover displacement;
- calibration-feature shift;
- acceptance shift;
- clipping rate;
- device-specific resource overhead;
- zero-shot to few-shot improvement.

## Statistical analysis

Preserve workload and hardware-job grouping.

Report uncertainty by domain and regime, not only pooled averages.

Separate:
- interpolation within known domains;
- temporal generalization (E7);
- true held-out-domain generalization (E8).

## Success criteria

Strong support:
- zero-shot or calibration-feature transfer improves the predeclared objective over a fixed/source-only baseline on the held-out domain without unacceptable constraint violations.

Partial support:
- zero-shot transfer degrades, but a small predeclared few-shot adaptation budget recovers meaningful performance.

Negative result:
- substantial target-specific retraining is required. This implies error-management policies are strongly device-specific and is itself scientifically informative.

## Paper-level interpretation

E8 must not claim universal quantum-hardware generalization from a small number of devices.

The defensible claim is limited to the tested domains and asks whether the resource-aware framework transfers while crossover boundaries remain device dependent.

## Reproducibility artifacts

Release where provider terms permit:
- domain definitions;
- frozen source/target designation;
- workload panel;
- zero-shot/few-shot protocol;
- calibration/device descriptors;
- adaptation budget;
- job IDs and timestamps;
- raw counts;
- policy decisions;
- resource accounting;
- held-out-domain evaluation code.
