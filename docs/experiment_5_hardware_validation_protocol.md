# Experiment 5 — Prospective Real-Quantum-Hardware Validation Protocol

## Purpose

Experiment 5 tests whether selected resource/error-management predictions from Experiments 2–4 survive execution on real quantum hardware.

E5 is deliberately small and prospective. It is not an attempt to reproduce the full simulator benchmark on hardware.

## Scientific role

Experiments 2–4 discover and stress-test regimes in simulation. Experiment 5 asks whether those predictions have external validity on a real processor.

The central principle is:

simulation prediction -> freeze prediction and circuit manifest -> execute hardware -> compare outcome

Hardware examples MUST NOT be selected after inspecting their hardware results.

## Dependencies and lock rule

The final E5 manifest is locked only after:

1. E2 reaches 9600/9600 and passes the final audit;
2. E3 locks/refines the check-frequency boundaries;
3. E4 completes realistic-noise robustness analysis;
4. hardware feasibility is checked for the required dynamic-circuit operations.

The selected hardware backend/device, calibration snapshot, software versions, and submission timestamps must be archived.

## Research question

Do resource-aware QEM/QED/Hybrid regime predictions obtained from controlled and realistic-noise simulations remain predictive on real quantum hardware?

## Hypotheses

**H5.1 — Directional validity.** Selected method-ordering predictions from E2–E4 persist on hardware more often than expected from an unstructured/no-regime baseline.

**H5.2 — Boundary uncertainty.** Near crossover boundaries, hardware may shift the ordering; such shifts are expected and are measured rather than treated as failures to hide.

**H5.3 — Acceptance realism.** Hardware QED/Hybrid performance must be interpreted jointly with syndrome acceptance and executed-shot cost.

**H5.4 — Model gap.** Differences between realistic-noise simulation and hardware quantify a simulation-to-hardware gap useful to later adaptive experiments.

## Methods

Where hardware capability permits, compare:
- Raw
- ZNE
- repeated QED
- repeated QED + ZNE

The repeated-QED implementation should preserve the validated reusable syndrome ancilla architecture.

If a target backend cannot implement the required mid-circuit measurement/reset/dynamic behavior, that backend is not a valid full-method E5 target. A reduced comparison may be reported separately but must not be conflated with the primary E5 validation.

## Prospective strata

Target approximately 20–40 base configurations total, selected before hardware execution from:
1. QEM-favorable regime;
2. QEM↔QED boundary;
3. QED-favorable regime;
4. QED↔Hybrid boundary;
5. Hybrid-favorable but acceptance-viable regime;
6. acceptance-limited/stress regime.

Include multiple widths/depths subject to device feasibility.

## Shot and replication policy

Use a predeclared principal hardware shot budget consistent with provider limits and E2/E4 comparability.

Replicate selected configurations across multiple jobs and, when feasible, multiple calibration windows. Hardware jobs are not interchangeable with random simulator seeds; job/time/calibration identifiers are recorded explicitly.

Do not increase shots selectively after seeing favorable/unfavorable method results unless the additional run is labeled confirmatory follow-up.

## ZNE policy

Noise scaling must use a hardware-valid circuit-folding/noise-scaling procedure declared before execution.

For every ZNE/Hybrid result preserve:
- each scale-level estimate;
- the unclipped extrapolated estimate;
- clipped/physical estimate if used;
- clipping indicator;
- scale-wise executed shots;
- scale-wise QED acceptance for Hybrid.

A clipped value of zero error is not interpreted as exact hardware recovery.

## Hardware metadata

Archive, when available:
- provider and backend identifier;
- job identifiers;
- submission/execution timestamps;
- calibration timestamp;
- qubit mapping/layout;
- T1/T2;
- 1Q and 2Q error estimates;
- readout errors;
- gate durations;
- connectivity/coupling information;
- transpiler settings and seed;
- software/provider package versions.

## Primary outcomes

For each frozen prediction:
- hardware absolute error;
- method ordering;
- prediction agreement/disagreement;
- acceptance probability;
- accepted/effective shots;
- physical-qubit count;
- 1Q/2Q work;
- transpiled depth;
- clipping/unclipped estimator diagnostics.

## Analysis

Report:
1. prediction agreement by regime class;
2. error magnitude and uncertainty;
3. simulator -> realistic-noise -> hardware displacement;
4. acceptance/resource changes;
5. cases where the predicted crossover moves;
6. cases where simulation predictions fail.

No hardware case is removed because it contradicts the simulation.

## Success criteria

E5 is successful as an experiment if it produces a prospectively selected, reproducible hardware test of the framework, regardless of whether every prediction is confirmed.

Support for external validity requires reproducible agreement for a meaningful subset of predeclared regime predictions while transparently reporting disagreement and boundary shifts.

## Relationship to Experiment 6

E5 is held-out evidence for the adaptive-error-management stage.

Experiment 6 must not evaluate an adaptive policy solely on the same conditions used to fit/select it. E5 hardware observations can serve as an external test set or as a separate hardware-validation set, depending on the final E6 protocol.

## Reproducibility artifacts

Release where provider terms permit:
- frozen E5 manifest;
- pre-hardware predictions;
- circuit generation/transpilation settings;
- hardware metadata/calibration snapshots;
- job IDs;
- raw counts;
- postselection records/aggregates;
- analysis scripts.
