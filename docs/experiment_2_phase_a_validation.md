# Experiment 2 Phase A Validation

## Status

**PASS — QED smoke mechanics validated.**

Phase A used a simple ancilla-assisted global Z-parity check to validate syndrome generation,
postselection, conditional reliability, and resource accounting before implementing a more
substantive QED design.

## Test status

All repository tests pass after fixing terminal-measurement handling in the QED wrapper:

- 8 passed
- no Experiment 2 test failures

The regression test now verifies that the QED wrapper strips the mirror circuit's existing
terminal measurements before inserting syndrome and final data measurements.

## Smoke grid

The Phase A smoke run evaluated:

- data qubits: 2, 4
- nominal depths: 5, 20
- depolarizing probability: 1e-3, 1e-2
- shots: 1,024
- seeds: 0, 1
- methods: Raw and QED

Total: 16 matched conditions / 32 rows.

## Observed behavior

QED conditional error was lower than Raw error in all 16 matched smoke conditions.

Representative cases:

| q | depth | p | seed | Raw error | QED conditional error | Acceptance |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 5 | 1e-3 | 0 | 0.0146 | 0.0049 | 0.988 |
| 2 | 5 | 1e-2 | 1 | 0.1455 | 0.0376 | 0.883 |
| 2 | 20 | 1e-2 | 0 | 0.4541 | 0.2396 | 0.705 |
| 4 | 5 | 1e-2 | 0 | 0.2803 | 0.1509 | 0.828 |
| 4 | 20 | 1e-3 | 1 | 0.1455 | 0.0632 | 0.912 |
| 4 | 20 | 1e-2 | 1 | 0.7900 | 0.6414 | 0.566 |

The expected tradeoff appears clearly:

- conditional reliability improves under postselection,
- acceptance probability decreases with increasing noise/circuit complexity,
- stronger raw degradation corresponds to a larger rejected-shot burden.

## Interpretation

Phase A validates the mechanics of the Experiment 2 pipeline.

It does **not** establish a paper-level QED result because the current global parity detector is
deliberately minimal and is used only to validate the framework.

The next step is Phase B:

**Raw -> ZNE -> QED -> QED+ZNE**

on matched conditions with common resource accounting.

Only after Phase B is stable should the detector architecture be upgraded and production-scale
QED experiments be launched.
