# Experiment 4 — Realistic-Noise Robustness Protocol

## Purpose

Experiment 4 tests whether the resource-dependent regimes identified by Experiments 2 and 3 persist when the controlled depolarizing-noise model is replaced by more hardware-like noise.

This is a targeted robustness experiment, not a second exhaustive production sweep.

## Dependency and lock rule

The final Experiment 4 cell list MUST NOT be selected until:

1. Experiment 2 reaches 9600/9600 complete matched interval-conditions;
2. the final Experiment 2 analysis is run with `--require-complete`;
3. Experiment 3 refines the relevant check-frequency/crossover boundaries.

Candidate-selection code and the noise machinery may be prepared in advance, but the final E4 conditions are locked only after E2/E3.

## Research question

Do the QEM, repeated-QED, and hybrid QED+ZNE reliability/resource regimes observed under controlled depolarizing noise persist under realistic device-like noise?

## Hypotheses

**H4.1 — Qualitative robustness.** At least some of the QEM↔QED and QED↔Hybrid ordering/crossover structure identified in E2/E3 persists under realistic noise.

**H4.2 — Boundary displacement.** Crossover locations change under heterogeneous noise; the realistic-noise result is not assumed to reproduce the depolarizing thresholds numerically.

**H4.3 — Acceptance sensitivity.** Repeated QED and hybrid strategies become particularly sensitive to two-qubit and relaxation/dephasing errors because syndrome extraction adds gates and time.

**H4.4 — Readout sensitivity.** Readout error can alter both payload estimates and syndrome/postselection decisions; therefore readout noise must be modeled explicitly rather than folded into a single depolarizing probability.

## Methods compared

For every selected workload:

- Raw
- ZNE
- repeated QED
- repeated QED + ZNE

The QED architecture remains the validated reusable-syndrome-ancilla design used by authoritative Experiment 2 v2.

## Realistic noise components

The primary composite model includes:

- amplitude damping / relaxation through T1;
- dephasing through T2;
- one-qubit gate error;
- two-qubit gate error;
- measurement/readout error.

Where supported, gate durations are used so T1/T2 noise is duration-aware.

The first implementation should use documented synthetic parameter sets. A later backend-derived configuration may be instantiated from a saved calibration snapshot. Backend-derived parameters must be archived with timestamp/provenance; results from different calibration snapshots must not be silently pooled.

## Noise scenarios

Use at least three predeclared device-like scenarios:

- **R1 — favorable:** comparatively long coherence and low gate/readout errors;
- **R2 — intermediate:** moderate coherence and gate/readout errors;
- **R3 — stressed:** shorter coherence and higher gate/readout errors.

Exact numerical values are to be locked before execution and recorded in metadata. They must not be tuned after observing method performance.

A fourth backend-derived scenario may be added if hardware calibration data are available.

## Cell-selection strata

E4 deliberately samples conditions from the final E2/E3 results:

1. QEM-favorable / low-overhead regime;
2. QEM↔QED crossover;
3. QED-favorable regime;
4. QED↔Hybrid transition;
5. Hybrid-favorable regime with viable acceptance;
6. acceptance-limited regime.

The final selection should cover multiple widths and depths and should avoid choosing only the most visually dramatic cells.

## Scale

Target approximately 24–40 base workload cells after E2/E3.

For each base cell:

- realistic-noise scenarios: 3 (plus optional backend-derived scenario);
- methods: 4;
- seeds: initially 20;
- principal shot budget: 4096.

This yields a targeted experiment on the order of hundreds to a few thousand method evaluations, not another 9600-condition factorial sweep.

Additional 1024/16384-shot validation is allowed only for selected cells where E2 demonstrated a material shot-budget interaction.

## Controls

For every E4 base workload:

1. retain the corresponding controlled-noise E2/E3 result;
2. use the same underlying seeded workload across methods;
3. preserve paired check-frequency comparisons where applicable;
4. record the complete noise configuration;
5. preserve unclipped ZNE estimates and clipping flags;
6. preserve scale-wise QED acceptance A1, A3, A5.

## Outcomes

Primary:
- absolute error;
- method ordering;
- crossover/regime retention or displacement.

Resource/sampling:
- acceptance probability;
- accepted/rejected shots;
- effective shots;
- one- and two-qubit gate counts;
- aggregate depth;
- physical qubits;
- classical/simulator runtime.

Diagnostics:
- unclipped estimate;
- clipping;
- scale-wise acceptance;
- noise-scenario metadata.

## Statistical analysis

Aggregate over seeds with means and 95% confidence intervals.

For each base workload and realistic-noise scenario:

- compare Raw, ZNE, QED, and Hybrid;
- compare the method ordering with the corresponding controlled-noise result;
- quantify crossover displacement rather than requiring identical thresholds;
- construct reliability/resource Pareto sets;
- report clipping and acceptance-collapse rates.

The primary robustness claim is qualitative/structural: whether the regime framework survives realistic noise. Numerical crossover thresholds are allowed to move.

## Success criteria

E4 supports the paper's robustness claim if:

1. the realistic-noise data exhibit reproducible, statistically supported method/resource differences;
2. crossover or regime structure remains interpretable under at least the intermediate realistic-noise scenario;
3. conclusions are not driven solely by clipped ZNE estimates;
4. QED/Hybrid results are reported jointly with acceptance/resource costs.

A result in which crossover boundaries move substantially is scientifically valid and should be reported. Failure of a regime to survive realistic noise is also a result and must not be hidden.

## Relationship to Experiment 5

E4 is the bridge to hardware validation.

Experiment 5 configurations should be selected from E4 to include:
- at least one prediction that remained robust;
- at least one near-boundary case;
- at least one resource/acceptance-limited case, if hardware feasibility permits.

Thus E5 tests predictions made before hardware execution rather than selecting hardware examples post hoc.

## Reproducibility

The final E4 release must include:
- locked protocol;
- selected-cell manifest;
- noise-parameter manifest;
- raw results;
- metadata/provenance;
- analysis code;
- software versions and random seeds.
