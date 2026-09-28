# Experiment 2 Phase B Validation

## Status

**PASS FOR FRAMEWORK VALIDATION — NOT YET PRODUCTION READY.**

Phase B compared four matched methods on a small smoke grid:

1. Raw
2. ZNE
3. QED
4. QED+ZNE

The purpose was to validate the combined estimator/resource pipeline before committing to a stronger paper-level QED architecture.

## Smoke grid

Eight matched conditions were evaluated:

- data qubits: 2, 4
- nominal depths: 5, 20
- physical depolarizing probability: 1e-3, 1e-2
- shots: 1,024
- seed: 0

Each condition produced four method rows, for 32 rows total.

## Observed matched errors

| q | depth | p | Raw | ZNE | QED | QED+ZNE | QED accept | Hybrid accept |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 5 | 1e-3 | 0.0146 | 0.0023 | 0.0049 | 0.0000 | 0.988 | 0.968 |
| 2 | 5 | 1e-2 | 0.1191 | 0.0418 | 0.0463 | 0.0000 | 0.907 | 0.792 |
| 2 | 20 | 1e-3 | 0.0645 | 0.0129 | 0.0194 | 0.0000 | 0.954 | 0.890 |
| 2 | 20 | 1e-2 | 0.4541 | 0.4172 | 0.2396 | 0.1993 | 0.705 | 0.577 |
| 4 | 5 | 1e-3 | 0.0391 | 0.0147 | 0.0151 | 0.0044 | 0.973 | 0.941 |
| 4 | 5 | 1e-2 | 0.2803 | 0.1908 | 0.1509 | 0.0588 | 0.828 | 0.674 |
| 4 | 20 | 1e-3 | 0.1279 | 0.0357 | 0.0502 | 0.0000 | 0.915 | 0.800 |
| 4 | 20 | 1e-2 | 0.7734 | 0.7562 | 0.6114 | 0.5823 | 0.565 | 0.517 |

## What Phase B validates

The four-method pipeline behaves qualitatively as expected:

- QED improves conditional reliability relative to Raw in all smoke conditions.
- ZNE improves reliability in all smoke conditions.
- QED+ZNE frequently produces the lowest reported error.
- Postselection cost increases as noise and circuit complexity increase.
- Hybrid postselection acceptance is lower than QED-only acceptance because checks are evaluated at all three ZNE scales.

## Important warning

Several QED+ZNE cases report zero error after clipping.

This is not sufficient evidence that the hybrid perfectly restores the ideal result.

The hybrid estimator combines:
- conditional postselected estimates,
- scale-dependent acceptance,
- linear zero-noise extrapolation,
- clipping to [0,1].

The interaction can create extrapolated values above 1 that are clipped to 1, yielding reported absolute error 0.

Therefore production work must preserve and analyze:

- unclipped hybrid estimate,
- clipping flag,
- scale-1/3/5 conditional estimates,
- scale-1/3/5 acceptance probabilities,
- accepted/rejected shots by scale.

No paper claim should rely on clipped zero-error values without reporting these diagnostics.

## Decision

Phase B validates the software path but does not justify a full-grid production run with the current minimal global-parity detector.

Before production:

1. add hybrid extrapolation/acceptance diagnostics,
2. strengthen the QED architecture beyond one terminal global parity check,
3. introduce repeated/interleaved checks with an explicit check interval,
4. validate ideal invariance and detection behavior for the stronger detector,
5. rerun a matched four-method smoke study.

Only then should Experiment 2 production scale be frozen.
