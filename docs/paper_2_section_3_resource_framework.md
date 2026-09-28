# Paper 2 Draft — Section 3: Resource-Aware Error-Management Framework

> Manuscript working draft. Mathematical notation may be converted to ACM LaTeX after the experimental notation is frozen.

## 3. Resource-Aware Error-Management Framework

This work evaluates quantum error-management strategies as joint reliability-resource decisions rather than ranking methods solely by their observed output error. The central premise is that an error-management method is operationally useful only when its reliability gain is interpreted together with the quantum and sampling resources required to obtain that gain. This distinction is particularly important when comparing error mitigation with postselection-based error detection: mitigation can amplify circuit-execution cost, while detection can discard an increasing fraction of executed shots as noise and circuit complexity increase.

### 3.1 Workload and operating condition

Let an experimental workload be described by an operating condition

x = (q, d, n, N, L),

where q denotes the number of data qubits, d denotes the workload-depth parameter, n denotes the physical-noise specification, N denotes the nominal shot budget, and L denotes the interval between repeated error-detection checks when QED is used.

For methods that do not use repeated QED, L is not a physical control variable. In paired comparisons, however, Raw and ZNE observations are retained alongside each L condition so that all four methods are evaluated against the same underlying seeded workload. The analysis audits that Raw and ZNE outcomes remain invariant across paired L values.

The available action set is

A = {Raw, ZNE, QED(L), Hybrid(L)},

where Hybrid denotes repeated QED followed by ZNE using the postselected estimates at each noise scale.

### 3.2 Reliability

For a known ideal target y*, the primary reliability metric is absolute estimation error

E(a,x) = | y_hat(a,x) - y* |,

for method a under condition x.

Lower E indicates greater reliability. Error is aggregated over independent seeded workloads, and uncertainty is reported using seed-level variation and confidence intervals.

Reliability alone is not treated as sufficient evidence that one method dominates another. A method with lower conditional error may require substantially more executed shots, greater circuit depth, additional entangling gates, or severe postselection.

### 3.3 Sampling and postselection cost

For QED-based methods, let A denote the acceptance probability of the postselection rule. If N_exec shots are executed, the accepted sample count is

N_acc = A N_exec.

Equivalently, obtaining a target accepted sample count N_target requires an expected executed-shot cost

N_exec approximately N_target / A.

As A approaches zero, the sampling cost of postselection diverges even when the conditional estimate among accepted shots remains accurate.

For Hybrid QED+ZNE, acceptance is recorded independently at each ZNE scale s:

A_s, s in S,

with the current ZNE scale set S={1,3,5}. This is necessary because noise amplification can reduce acceptance at the same time that extrapolation attempts to infer the zero-noise value. A low-error extrapolated estimate is therefore interpreted jointly with A_1, A_3, and A_5.

### 3.4 Gate, depth, and physical-qubit cost

For every method, the benchmark records at least:

- one-qubit gate work G_1;
- two-qubit gate work G_2;
- aggregate depth D;
- physical qubit count Q_phys;
- executed/effective shots;
- classical/simulator runtime where applicable.

Two-qubit work is emphasized because entangling operations are typically among the most consequential noisy resources in the benchmarked circuits, while depth captures additional exposure to decoherence and accumulated control error.

The authoritative repeated-QED architecture uses one reusable syndrome ancilla. Intermediate syndrome information is measured into classical storage and the ancilla is reset and reused. Consequently, increasing check frequency primarily changes temporal/gate/sampling overhead rather than allocating one new physical ancilla for every check.

### 3.5 ZNE extrapolation and clipping diagnostics

ZNE can produce an extrapolated estimate outside the physical range of the measured observable/probability. Therefore the benchmark preserves both

y_hat_unclipped

and, where a physical-range projection is used,

y_hat_clipped.

A binary clipping indicator is recorded for every extrapolated result. Apparent boundary performance after clipping is not interpreted as exact recovery unless supported by the unclipped estimator and uncertainty.

This diagnostic is particularly important for Hybrid QED+ZNE, where postselection can alter the scale-wise estimator before extrapolation.

### 3.6 Resource vectors and Pareto efficiency

Rather than assuming a single universal resource price, define a resource vector

C(a,x) = (N_exec, N_eff, G_2, D, Q_phys, T),

where T denotes runtime when relevant.

Method a dominates method b under condition x only if it is no worse in reliability and no more costly in every resource dimension considered, with at least one strict improvement.

The Pareto set is therefore

P(x) = {a in A : no b in A dominates a}.

This representation allows the analysis to identify strategies that remain rational choices under different resource preferences without imposing an arbitrary scalar cost prematurely.

### 3.7 Crossover regimes

A reliability crossover between two strategies a and b occurs near conditions where

E(a,x) approximately E(b,x),

while their resource vectors differ materially.

The paper distinguishes at least three empirically relevant boundaries:

1. QEM <-> QED: where mitigation and repeated detection provide comparable reliability;
2. QED <-> Hybrid: where adding ZNE to QED provides diminishing or meaningful incremental benefit;
3. Hybrid <-> sampling-limited: where conditional reliability remains attractive but postselection acceptance makes the strategy operationally expensive.

Experiment 3 refines these boundaries by varying QED check interval L.

A crossover is not defined solely by an exact equality of sample means. Statistical uncertainty, resource cost, and neighboring operating conditions are considered when interpreting a boundary.

### 3.8 Reliability-constrained and budget-constrained decision problems

The later adaptive stage uses the benchmark to formulate two operational decision problems.

For a target reliability epsilon, choose the least costly feasible action:

minimize_a C(a,x)
subject to E(a,x) <= epsilon.

Because C may be multidimensional, the optimization can be evaluated under individual resource constraints, Pareto ordering, or predeclared scalarizations.

Conversely, under resource budget B, choose the most reliable feasible action:

minimize_a E(a,x)
subject to C(a,x) <= B.

These formulations distinguish the paper's adaptive objective from ordinary method classification. The goal is not merely to predict which method has the smallest historical error, but to select an error-management strategy that satisfies an explicit reliability-resource objective.

### 3.9 Framework interpretation

The framework therefore treats error management as a resource-allocation problem:

workload + hardware/noise state + reliability target + resource budget
-> error-management action.

Experiments 1–3 characterize the controlled resource landscape, Experiments 4–5 test its robustness and hardware relevance, and Experiments 6–8 evaluate whether the resulting structure can support adaptive decisions under held-out workloads, temporal calibration drift, and hardware-domain shift.
