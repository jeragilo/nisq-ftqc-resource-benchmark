# Experiment 2 Protocol — Quantum Error Detection and Postselection

## Purpose

Experiment 2 introduces quantum error detection (QED) into the same resource-aware benchmarking framework used in Experiment 1.

The immediate scientific comparison is:

**Raw -> ZNE -> QED -> QED+ZNE**

The goal is not merely to show that postselection can improve fidelity. The goal is to quantify when QED trades qubit/gate/depth/rejection overhead for reliability more efficiently than ZNE trades sampling/execution overhead.

This experiment addresses RQ1, RQ2, and the first direct crossover component of RQ3.

## Scientific questions

### E2-RQ1 — Reliability
How does QED/postselection change reliability as physical noise and circuit depth increase?

### E2-RQ2 — Resource efficiency
How much reliability gain is purchased by:
- ancilla/qubit overhead,
- additional 1Q/2Q gates,
- additional depth,
- shot rejection/postselection,
- increased effective sampling cost?

### E2-RQ3 — QEM vs QED crossover
Under what noise/depth regimes does QED become more resource-efficient than ZNE under the common resource accounting framework?

### E2-RQ4 — Hybrid QED+ZNE
Can QED reduce the residual noise seen by ZNE enough that the combined method produces a favorable reliability/resource tradeoff relative to either method alone?

## Hypotheses

H2.1: QED will improve conditional reliability over raw execution across a broad region, but its acceptance probability will decrease as noise and circuit complexity rise.

H2.2: ZNE and QED will occupy different resource regimes: ZNE primarily spends repeated execution/sampling while QED spends qubits, gates, depth, and rejected shots.

H2.3: A crossover region will emerge where QED offers a better reliability gain per accepted sample or per aggregate quantum work than ZNE.

H2.4: QED+ZNE may outperform either technique alone in some intermediate regimes, but the hybrid will not necessarily dominate after full resource accounting.

## Scope

Experiment 2 is intentionally a QED/postselection study. It is **not yet full QEC**.

We do not claim:
- fault-tolerant logical computation,
- active correction,
- below-threshold logical scaling,
- a QEC threshold,
- logical error suppression with increasing code distance.

Those belong to later QEC experiments.

## Workload continuity

Use the same seeded mirror/Clifford benchmark family from Experiment 1 wherever possible so Raw and ZNE baselines remain directly comparable.

Ideal target remains the all-zero output after a circuit body followed by its inverse.

Primary dimensions:

- data qubits: 2, 4, 6, 8 where feasible
- nominal depths: 5, 10, 20, 40, 80
- physical depolarizing probability: 1e-4, 3e-4, 1e-3, 3e-3, 1e-2
- nominal shot budgets: 1,024; 4,096; 16,384
- seeded circuit instances: 20 for production

## QED mechanism

### Initial implementation

Use low-overhead parity/stabilizer-style checks with ancilla-assisted detection and postselection.

The implementation must satisfy:

1. The check circuit leaves the intended logical action of the payload unchanged in the ideal/noiseless case.
2. Ancilla/check measurements generate an error-detection syndrome.
3. A shot is **accepted** only when all configured checks pass.
4. Reliability is evaluated both:
   - conditionally on accepted shots, and
   - in conjunction with the acceptance/rejection cost.

The first implementation should prioritize transparency and reproducibility over maximal code sophistication.

### Check interval

Treat detection frequency as an experimental variable.

Initial candidate intervals:

- L = 1
- L = 2
- L = 4
- L = 8

Interpretation: insert a detection/check layer every L payload layers/blocks, subject to circuit-structure feasibility.

If implementation details require a different exact unit than a nominal payload layer, document the mapping explicitly.

## Compared methods

Minimum production comparison:

1. Raw
2. ZNE
3. QED
4. QED+ZNE

For QED+ZNE, postselection must be applied consistently at each ZNE noise-amplification scale, and the resulting estimator construction must be documented.

## Reliability metrics

Primary:

- success probability
- absolute error relative to ideal target
- conditional accepted-shot success probability

QED-specific:

- acceptance probability
- rejection probability
- accepted shots
- rejected shots

For hybrid QED+ZNE:

- unclipped extrapolated estimate
- clipped estimate
- clipping flag
- scale-wise accepted-shot estimates
- scale-wise acceptance probabilities

## Resource metrics

Retain the Paper 2 resource vector:

R_m = [N_q, N_a, N_s, N_reject, N_1q, N_2q, D, T_QPU, T_decode, T_post]

For Experiment 2 record at minimum:

- data qubits
- ancilla/check qubits
- total physical qubits
- nominal shots
- executed shots
- accepted shots
- rejected shots
- acceptance probability
- 1Q gates
- 2Q gates
- circuit depth
- aggregate depth work
- classical postselection time
- total simulator execution time

Derived resource ratios relative to matched Raw:

- sampling/execution overhead
- accepted-sample overhead
- 2Q gate-work ratio
- depth-work ratio
- physical-qubit ratio
- runtime ratio

## Resource-efficiency analysis

Do not collapse all resources into a single arbitrary weighted utility score.

Analyze Pareto-style tradeoffs separately, including:

- absolute error vs executed shots
- absolute error vs accepted shots
- absolute error vs total physical qubits
- absolute error vs aggregate 2Q gate work
- absolute error vs aggregate depth work
- absolute error vs runtime

Candidate crossover definitions should be based on target reliability and explicit resource dimensions rather than a universal scalar score.

## Experimental phases

### Phase A — invariant and smoke validation

Small grid:
- qubits: 2, 4
- depths: 5, 20
- noise: 1e-3, 1e-2
- shots: 1,024
- seeds: 0, 1
- check intervals: selected subset, initially L = 2 and 4

Required invariants:
- noiseless checked circuit preserves all-zero ideal output
- acceptance probability is 1 or near 1 under noiseless ideal checks
- injected noise increases detected-syndrome/rejection rate
- accepted-shot conditional error differs from unconditioned/raw behavior
- resource accounting increases consistently with inserted checks

### Phase B — implementation validation

Compare:
- Raw
- QED
- ZNE
- QED+ZNE

Verify:
- matched seeds/workloads
- schema completeness
- no duplicate condition/method rows
- checkpoint/resume behavior
- deterministic seeded smoke reproducibility

### Phase C — production sweep

Only after Phase A/B pass.

Production dimensions may be reduced if QED interval creates a combinatorial explosion, but any reduction must be documented before the run.

Default target:
- 4 widths
- 5 depths
- 5 noise levels
- 3 shot budgets
- 20 seeds
- multiple QED intervals
- 4 methods

This could substantially exceed Experiment 1 compute, so production design should be profiled locally before launch.

## Statistical protocol

Primary inference unit should respect the repeated seeded design.

Use:
- paired Raw/QED/ZNE/QED+ZNE comparisons within matched seed-condition cells
- seed-aggregated cell summaries
- 95% confidence intervals across seed-level or cell-level matched effects
- explicit reporting of ties/failures/saturation
- no treatment of all CSV rows as independent replicates

Later, mixed-effects or hierarchical modeling may be added if needed.

## Interpretation guardrails

Experiment 2 may support claims about:
- error detection,
- postselection,
- conditional reliability,
- resource overhead,
- QEM-vs-QED tradeoffs,
- hybrid QED+QEM tradeoffs.

Experiment 2 must **not** be described as demonstrating:
- full quantum error correction,
- fault tolerance,
- logical break-even,
- code-distance scaling,
- below-threshold QEC.

## Decision criterion for moving to Experiment 3

Proceed to full QEC only after Experiment 2 establishes:

1. a validated QED/postselection implementation,
2. reliable resource accounting,
3. at least one clearly characterized regime where QED behaves differently from ZNE,
4. a stable comparison pipeline that can be extended to repetition/surface-code QEC.

