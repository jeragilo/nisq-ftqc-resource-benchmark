# Experiment 2 Phase C — Repeated-Check Validation

## Status

**PASS — repeated nondestructive QED produces a structured reliability/resource frontier.**

Phase C replaces the one-time terminal parity detector with check-compatible mirror blocks.
Each block is an ideal identity U U-dagger, so global Z parity is known at each check boundary.
This permits repeated parity checks without intentionally disturbing the ideal computation.

## Smoke design

- data qubits: 2, 4
- total nominal body depth: 8, 16
- depolarizing probability: 1e-3, 1e-2
- check interval L: 1, 2, 4, 8
- shots: 1,024
- seed: 0
- methods: matched Raw and repeated-QED

32 matched configurations / 64 rows.

## Main finding

More frequent checking generally improves conditional reliability, especially in the
high-noise/deeper regime, but spends substantial physical resources and rejects more shots.

Representative hard condition: q=4, depth=16, p=1e-2

| L | rounds | QED error | acceptance | ancillas | 2Q gates |
|---:|---:|---:|---:|---:|---:|
| 1 | 16 | 0.1692 | 0.260 | 16 | 128 |
| 2 | 8 | 0.2480 | 0.366 | 8 | 96 |
| 4 | 4 | 0.3747 | 0.456 | 4 | 80 |
| 8 | 2 | 0.4732 | 0.528 | 2 | 72 |

This is a clear reliability/resource tradeoff rather than a single dominant operating point.

## Low-noise nuance

At p=1e-3, the smallest interval is not universally the lowest-error choice. Sampling
variation and additional noisy check operations can make intermediate intervals competitive
or slightly better in some smoke cells.

Therefore the production study must not assume L=1 is optimal. Check interval must remain an
experimental/resource variable.

## Interpretation

Phase C establishes a defensible QED resource axis:

- smaller L -> more detection opportunities,
- smaller L -> more check rounds,
- more ancillas in this transparent fresh-ancilla implementation,
- more 2Q gates/depth,
- lower acceptance,
- usually lower conditional error in difficult regimes.

The relevant question for Paper 2 is therefore not "does repeated QED help?" but:

> Which check interval lies on the Pareto-efficient frontier for a specified reliability target and resource constraint?

## Next step

Phase D should combine the repeated-check architecture with the four-method comparison:

Raw -> ZNE -> repeated QED(L) -> repeated QED(L)+ZNE

while preserving unclipped hybrid estimates and scale-wise acceptance diagnostics.

Production scale should be frozen only after that smoke comparison is validated.
