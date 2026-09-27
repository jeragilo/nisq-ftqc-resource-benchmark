# Experiment 0 Validation Report

## Status

**PASS — pipeline validation complete.**

Experiment 0 completed successfully in GitHub Actions after the test suite passed. The run generated 1,980 records:

- 180 ideal-reference records
- 900 raw-noise records
- 900 ZNE records

The analysis below is descriptive validation of the pipeline, not a final Paper 2 inferential result.

## Aggregate Raw vs ZNE result

Across 900 matched raw/ZNE conditions:

- mean raw absolute error: **0.13338**
- mean ZNE absolute error: **0.09393**
- mean absolute improvement: **0.03946**
- relative reduction in mean absolute error: **29.6%**
- ZNE had lower absolute error in **900/900 matched records**
- all **90 seed-aggregated experimental cells** also favored ZNE

A paired comparison across the 900 records gives a large standardized paired difference (Cohen-style dz ≈ **1.28**). This statistic is diagnostic only: the final manuscript analysis must respect the hierarchical/repeated experimental design rather than treat every record as an independent scientific replicate.

## Improvement by depolarizing-noise probability

| p | Raw mean error | ZNE mean error | Mean improvement |
|---:|---:|---:|---:|
| 0.0001 | 0.00699 | 0.00113 | 0.00586 |
| 0.0003 | 0.01993 | 0.00318 | 0.01675 |
| 0.0010 | 0.06213 | 0.01781 | 0.04432 |
| 0.0030 | 0.16680 | 0.09453 | 0.07227 |
| 0.0100 | 0.41107 | 0.35299 | 0.05808 |

The absolute ZNE benefit grows through the intermediate-noise regime and then contracts at the highest tested noise level. This is consistent with the intended Experiment 0 role: identify a regime in which mitigation helps and a regime in which its leverage begins to saturate.

For the hardest tested aggregate condition (4 qubits, nominal depth 20, p=0.01), mean raw absolute error was approximately **0.7622**, versus **0.7454** after ZNE. The mitigation benefit is therefore small once the circuit is already strongly degraded.

## Resource cost

Relative to a matched raw execution, the current three-scale ZNE implementation incurs:

- **3.0x effective shots**
- **9.0x aggregate one-qubit gate executions**
- **9.0x aggregate two-qubit gate executions**
- approximately **8.85x aggregate transpiled-depth work**
- approximately **4.74x mean measured simulator wall time**

The gate/depth factors arise because scale factors 1, 3, and 5 are all executed and their circuit work is aggregated. These are intentionally reported as resource costs rather than hidden implementation details.

## Shot-budget observation

Mean absolute improvement was nearly unchanged across nominal shot budgets:

- 1,024 shots: 0.03930
- 4,096 shots: 0.03949
- 16,384 shots: 0.03958

Experiment 0 is not sufficient to conclude that shot budget is unimportant. It indicates that, for this simple deterministic mirror workload and tested budgets, systematic mitigation benefit dominates changes in sampling variance.

## Interpretation

Experiment 0 validates the central measurement philosophy of Paper 2:

> error reduction alone is incomplete; the same improvement must be reported together with the resources used to obtain it.

ZNE clearly improves this controlled benchmark, but the improvement is purchased with additional sampling, circuit work, and runtime. At high noise/depth, the marginal reliability benefit contracts.

## Limitations

- depolarizing noise only
- 2- and 4-qubit mirror-style circuits only
- linear ZNE with integer global-folding scales 1, 3, 5
- simulator execution only
- simulator wall time is not QPU execution time
- current gate/depth resource totals are aggregate executed work across folded circuits, not critical-path QPU latency
- clipping extrapolated success probability to [0,1] can bias boundary cases and should be reported/diagnosed explicitly in later experiments
- no QED or QEC is included yet
- inferential statistics for the final paper require a hierarchical design that accounts for seeds, circuits, and repeated conditions

## Decision

Experiment 0 has fulfilled its purpose as a pipeline-validation experiment. The branch is suitable to merge after preserving this report. Experiment 1 should retain the same resource schema while expanding the QEM sweep and adding diagnostics for extrapolation/clipping and uncertainty.
