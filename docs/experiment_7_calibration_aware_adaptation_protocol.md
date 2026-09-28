# Experiment 7 — Calibration-Aware Dynamic Error Management Protocol

## Purpose

Experiment 7 extends the static adaptive policy of Experiment 6 to nonstationary quantum hardware.

Real quantum processors drift over time. Coherence, gate errors, readout errors, calibration state, queue/execution timing, and effective circuit performance may change. E7 tests whether updating the error-management decision from current hardware state improves reliability/resource performance relative to a static policy.

## Central research question

Does calibration-aware adaptation outperform a static resource-aware error-management policy when hardware/noise conditions vary over time?

## Dependency rule

E7 begins only after:
1. E6 has a frozen static policy and locked evaluation protocol;
2. E5 establishes a feasible hardware execution path;
3. time-stamped calibration/device metadata can be collected consistently.

E7 must not be used to retroactively tune E6 test results.

## Dynamic policy

The static E6 policy is:

pi(x, B, epsilon)

E7 extends it to:

pi(x, h_t, B, epsilon)

where h_t is hardware state available before execution at time t.

Candidate h_t features include:
- T1/T2 summaries for mapped qubits;
- 1Q/2Q gate-error estimates;
- readout-error estimates;
- gate durations;
- connectivity/layout descriptors;
- calibration age;
- backend/device identifier;
- recent declared probe/calibration measurements, if their execution cost is included.

Future calibration information is forbidden.

## Comparators

Evaluate:
1. best fixed error-management strategy;
2. frozen static E6 policy without time-varying calibration features;
3. calibration-aware E7 policy;
4. stale-calibration policy using an older snapshot;
5. oracle with contemporaneous outcomes (analysis-only upper bound).

## Temporal data collection

Collect repeated evaluations of a fixed panel of representative workloads across multiple hardware/calibration windows.

The panel should contain:
- QEM-favorable cases;
- crossover cases;
- QED-favorable cases;
- Hybrid-favorable cases;
- acceptance-sensitive cases.

Do not change the workload panel simply because a later hardware window produces inconvenient results.

## Chronological split

Primary evaluation MUST be chronological.

Example:
- early windows: training;
- subsequent windows: validation;
- latest untouched windows: test.

Randomly mixing observations from the same calibration period across train and test is prohibited.

A leave-one-calibration-window-out analysis may be added as a secondary robustness test.

## Drift definition

Before primary analysis, define measurable hardware-state change using calibration variables and/or a predeclared distance/statistical criterion.

Separate:
- calibration drift;
- sampling variation;
- job-to-job stochastic variation.

Do not label every performance change as drift.

## Adaptation mechanisms

Start with interpretable mechanisms:
- recalculation of E6 surrogate predictions from current calibration features;
- threshold/rule updates;
- lightweight online recalibration of performance models;
- constrained contextual decision policy.

Fully online reinforcement learning is out of scope unless later evidence shows it is necessary and safe to evaluate rigorously.

## Resource accounting

Any probing used to estimate current state is part of the cost.

Total adaptive cost includes:
- calibration/probe executions attributable to the method;
- method shots;
- rejected/postselected shots;
- ZNE scale overhead;
- QED gate/depth overhead;
- physical qubits;
- classical decision overhead when material.

## Primary outcomes

Under fixed reliability target:
- total resource cost;
- target-success rate;
- regret vs oracle;
- savings vs static E6.

Under fixed resource budget:
- achieved error;
- violation rate;
- regret vs oracle;
- improvement vs static E6.

Also report:
- strategy-switch frequency;
- relationship between measured drift and policy changes;
- false/unnecessary switches;
- missed beneficial switches.

## Statistical analysis

Use time-aware uncertainty estimates and preserve calibration-window grouping.

Report performance per window as well as aggregate performance.

Test whether gains are concentrated only in extreme drift windows or persist across ordinary calibration variation.

## Success criteria

E7 supports dynamic adaptation if the calibration-aware policy improves a predeclared resource/reliability objective over the frozen static E6 policy on chronologically held-out hardware windows, after including adaptation/probing costs.

A finding that calibration-aware adaptation offers negligible benefit is valid and implies that the static E6 policy is sufficiently robust over the tested timescale.

## Relationship to E8

E7 asks whether the policy adapts across time on a hardware environment.

E8 asks whether the framework generalizes across different devices/platforms.

E7 therefore isolates temporal nonstationarity before E8 tests device/domain shift.

## Reproducibility artifacts

Release where provider terms permit:
- workload panel;
- chronological split manifest;
- timestamps and job IDs;
- calibration snapshots;
- hardware-state feature table;
- policy decisions before each execution;
- probe/adaptation costs;
- raw counts/results;
- static and dynamic predictions;
- evaluation code.
