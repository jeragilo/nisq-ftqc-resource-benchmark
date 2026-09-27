# Experiment 2 Phase D — Repeated QED + ZNE Validation

## Status

**PASS — four-method repeated-QED comparison validated with clipping diagnostics.**

Phase D compared:

1. Raw
2. ZNE
3. repeated QED
4. repeated QED + ZNE

using check-compatible mirror blocks and two representative check intervals, L=2 and L=8.

## Main result

The hybrid method usually produced the lowest reported error, but several low-noise cases
extrapolated above 1 and were clipped to 1. Those zero-error outputs must therefore be
interpreted as estimator-boundary artifacts rather than perfect correction.

Examples of clipped hybrid extrapolations:

- q=2, depth=16, p=1e-3, L=8: unclipped estimate 1.0131
- q=4, depth=8, p=1e-3, L=2: unclipped estimate 1.0076
- q=4, depth=8, p=1e-3, L=8: unclipped estimate 1.0118
- q=4, depth=16, p=1e-3, L=8: unclipped estimate 1.0019

## High-noise resource tradeoff

For q=4, depth=16, p=1e-2:

### L=2

- Raw error: 0.6504
- ZNE error: 0.6139
- repeated-QED error: 0.2480
- repeated-QED+ZNE error: 0.1506
- hybrid unclipped estimate: 0.8494
- acceptance at scales 1/3/5: 0.366 / 0.099 / 0.042

### L=8

- Raw error: 0.6934
- ZNE error: 0.6641
- repeated-QED error: 0.4732
- repeated-QED+ZNE error: 0.4103
- hybrid unclipped estimate: 0.5897
- acceptance at scales 1/3/5: 0.528 / 0.278 / 0.245

The stronger repeated-check configuration substantially improves reliability, but the accepted
sample pool collapses under noise amplification. This is a direct reliability-versus-resource
tradeoff and should be treated explicitly in production analysis.

## Interpretation

Phase D establishes a defensible four-method pipeline:

Raw -> ZNE -> repeated QED(L) -> repeated QED(L)+ZNE

with diagnostics sufficient to distinguish true estimator behavior from clipping artifacts.

The hybrid method cannot be judged solely by its clipped error. Production analysis must
report at least:

- unclipped estimate,
- clipping frequency,
- scale-wise conditional estimates,
- scale-wise acceptance probabilities,
- total executed shots,
- total accepted shots,
- ancilla/qubit overhead,
- two-qubit work,
- aggregate depth work.

## Production-design recommendation

A full Experiment 2 sweep should retain multiple check intervals rather than selecting one
globally. L=2 and L=8 should be retained as representative high-frequency and low-frequency
settings; L=4 may be included if compute budget allows.

Suggested production axes:

- qubits: 2, 4, 6, 8
- total body depth: 8, 16, 32, 64
- p: 1e-4, 3e-4, 1e-3, 3e-3, 1e-2
- shots: 1,024; 4,096; 16,384
- seeds: 20
- check intervals: L=2 and L=8
- methods: Raw, ZNE, repeated QED, repeated QED+ZNE

This is 4*4*5*3*20*2 = 9,600 matched interval-conditions and 38,400 method rows.
Because the hybrid requires three noisy checked executions per condition, local profiling and
checkpoint/resume support should be added before launch.

## Claim boundary

Even after production, these experiments support claims about error detection/postselection,
mitigation, hybrid error management, and resource tradeoffs. They do not establish full QEC,
logical break-even, threshold behavior, or fault tolerance.
