# Experiment 6 — Adaptive Resource-Aware Error Management Protocol

## Purpose

Experiment 6 converts the descriptive regime structure established in Experiments 1–5 into an adaptive decision method.

Given a workload, noise/hardware state, resource budget, and reliability target, the policy selects an error-management action rather than applying one fixed strategy everywhere.

## Central research question

Can an adaptive resource-aware policy outperform fixed Raw, ZNE, QED, and Hybrid policies under equal resource budgets or equal reliability targets?

## Action space

The policy may select:

- Raw
- ZNE
- QED(L)
- Hybrid QED+ZNE(L)

where L is restricted to check intervals validated by Experiment 3 and feasible for the target hardware/workload.

## Inputs

Candidate policy features include only information available before executing the selected method:

- circuit width;
- circuit depth / structural workload descriptors;
- hardware/noise descriptors;
- requested shot budget;
- resource budget;
- target error/reliability;
- device/calibration descriptors when available.

Post-outcome quantities such as realized method error, realized postselection acceptance, or realized clipping MUST NOT be used as decision-time features unless they arise from a separately declared calibration/probing stage whose cost is included.

## Objectives

Evaluate at least two decision formulations.

### Reliability-constrained cost minimization

minimize C(a | x)
subject to E(a | x) <= epsilon

### Budget-constrained error minimization

minimize E(a | x)
subject to C(a | x) <= B

Cost C must be reported transparently and may include separate resource dimensions rather than hiding them in one arbitrary scalar:
- executed shots;
- accepted/effective shots;
- 2Q work;
- depth;
- physical qubits;
- runtime where relevant.

Any scalarized cost function must be predeclared and sensitivity-tested.

## Baselines

Compare the adaptive policy against:

1. Always Raw
2. Always ZNE
3. Always QED with each validated fixed L
4. Always Hybrid with each validated fixed L
5. Best single fixed policy chosen using training/validation data only
6. Oracle policy (analysis-only upper bound using test outcomes; never deployable)

The oracle is not a fair operational baseline; it quantifies headroom.

## Data provenance

E2 provides broad controlled-noise coverage.
E3 provides refined check-frequency/crossover evidence.
E4 provides realistic-noise robustness data.
E5 remains an external hardware validation source unless a later protocol explicitly allocates a disjoint hardware-training subset.

Rows from the same underlying seeded workload or paired L comparison must not leak across train/test partitions.

## Split policy

Split by grouped workload/noise units, not random method rows.

At minimum create:
- training set;
- validation set;
- locked test set.

All methods/actions for a given underlying workload condition belong to the same split.

The split manifest is frozen before model/hyperparameter selection.

A second out-of-distribution test should hold out at least one structured region (for example a width, depth band, noise scenario, or later device) when sufficient data exist.

## Policy families

Start with interpretable baselines before complex ML:

- lookup/regime rules derived only from training data;
- multinomial/logistic decision model;
- shallow decision tree or constrained tree;
- simple probabilistic performance/cost surrogate + optimizer.

More complex ML is justified only if it materially improves locked validation performance and retains reproducibility/interpretability.

## Labels / optimal actions

For each training condition, feasible actions are evaluated under the declared objective.

Ties must use a deterministic rule declared before test evaluation, favoring lower resource cost when reliability is statistically indistinguishable.

Uncertainty in seed-aggregated estimates must be retained; labels near unresolved boundaries may be marked ambiguous rather than forced into a false exact class.

## Primary metrics

For budget-constrained evaluation:
- achieved absolute error;
- constraint-violation rate;
- regret relative to oracle;
- improvement versus best fixed policy.

For reliability-constrained evaluation:
- resource cost to achieve target;
- target-success rate;
- resource regret relative to oracle;
- savings versus best fixed policy.

Also report action-selection frequency and performance by regime class.

## Statistical evaluation

Use the locked test set exactly once for the primary final evaluation.

Report confidence intervals via grouped bootstrap or another predeclared method respecting workload grouping.

Do not report only overall accuracy of action labels. The scientifically relevant outcome is realized reliability/resource performance.

## Leakage controls

Forbidden:
- random row-level split across methods from the same condition;
- using test outcomes to set crossover thresholds;
- selecting cost weights after inspecting test results;
- using E5 hardware outcomes both to train and claim independent hardware validation;
- treating clipped ZNE/Hybrid boundary values as exact ground truth without diagnostics.

## Ablations

Evaluate the contribution of:
- noise descriptors;
- resource-budget input;
- target reliability input;
- check-frequency choice;
- realistic-noise training data;
- calibration/device features when available.

## Success criteria

E6 supports the adaptive-method claim if, on locked held-out conditions, the policy provides a reproducible advantage over the best fixed policy under at least one predeclared resource/reliability formulation without unacceptable constraint violations.

A null result is valid: if a fixed policy is effectively dominant, the adaptive hypothesis is rejected for the tested regime.

## Relationship to E7 and E8

E7 introduces time-varying calibration/device state and tests whether the policy should adapt over time.

E8 tests transfer/generalization across held-out devices/platforms.

E6 therefore establishes the static adaptive policy before dynamic and cross-platform claims are attempted.

## Reproducibility artifacts

Release:
- frozen split manifest;
- feature schema;
- objective/cost definitions;
- training/validation/test IDs;
- policy code and hyperparameters;
- fixed-policy baselines;
- oracle calculation;
- predictions on locked test data;
- evaluation script and confidence intervals.
