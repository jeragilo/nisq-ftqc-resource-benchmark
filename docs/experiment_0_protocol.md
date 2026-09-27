# Experiment 0 Protocol

## Purpose

Validate the complete Paper 2 measurement pipeline before introducing QED or QEC.

## Comparison

Ideal -> raw depolarizing noise -> digital ZNE.

## Initial design

- qubits: 2, 4
- nominal body depths: 5, 10, 20
- depolarizing probabilities: 1e-4, 3e-4, 1e-3, 3e-3, 1e-2
- shot budgets: 1,024; 4,096; 16,384
- seeds: 0-9
- ZNE global-folding scale factors: 1, 3, 5

The mirror body is composed with its inverse, so the ideal target is the all-zero bit string.

## Primary outcome

Success probability relative to the known all-zero ideal output.

## Resource accounting

For each condition record:
- physical qubits
- nominal workload depth
- transpiled/executed depth
- one- and two-qubit gate counts
- effective shots
- noise probability
- seed
- success probability
- absolute error
- classical wall-clock simulation time

For ZNE, resource counts are aggregated across all folded circuits. Its effective shot cost is therefore shots multiplied by the number of scale factors.

## Interpretation guardrail

Experiment 0 is pipeline validation, not evidence of a general NISQ-to-FTQC crossover. Its results determine whether the measurement and resource-accounting infrastructure is trustworthy enough to expand.
