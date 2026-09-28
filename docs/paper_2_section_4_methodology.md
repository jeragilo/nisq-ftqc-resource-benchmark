# Paper 2 Draft — Section 4: Experimental Methodology

> Working manuscript draft grounded in the current implementation. Planned E3–E8 procedures remain prospective until executed.

## 4. Experimental Methodology

### 4.1 Reproducibility, provenance, and execution

The benchmark is implemented in Python using Qiskit and Qiskit Aer. Production runs record execution provenance including the Git commit, Python executable and version, operating platform, machine architecture, CPU count, Qiskit version, Qiskit Aer version, NumPy version, parameter grid, and creation/completion timestamps.

Experiment 2 is checkpointed at the level of a complete matched condition. A condition is identified by

(q, d, p, N, s, L),

where q is data-qubit width, d is the workload-depth parameter, p is the depolarizing-noise probability, N is the nominal shot count, s is the workload/simulator seed, and L is the QED check interval. Raw, ZNE, repeated-QED, and Hybrid rows are generated together and appended as a four-row unit. The file is flushed and synchronized after each condition. Resume logic treats a condition as complete only when all four methods are present.

The authoritative Experiment 2 production grid is

q in {2,4,6,8},
d in {8,16,32,64},
p in {1e-4,3e-4,1e-3,3e-3,1e-2},
N in {1024,4096,16384},
s in {0,...,19},
L in {2,8}.

This yields 9600 matched interval-conditions and 38400 method rows.

### 4.2 Check-compatible paired workloads

Repeated error detection requires intermediate boundaries at which the ideal state satisfies a known check condition. The workload generator therefore constructs seeded identity-preserving mirror micro-blocks.

For each micro-block, a random depth-one body U is generated using single-qubit gates drawn from {H,S,X} and nearest-neighbor CX operations. The block is then composed with its inverse,

U U^dagger,

so that the ideal action of each micro-block is identity.

For fixed (q,d,s), the generator first creates one fixed sequence of d micro-blocks. Check interval L changes only how this same sequence is grouped into larger blocks. Consequently, paired L=2 and L=8 comparisons use the same underlying seeded workload rather than independently generated random circuits.

The production analysis explicitly audits this paired design: Raw and ZNE absolute errors must be invariant across paired L values for the same (q,d,p,N,s) condition.

The complete payload is the composition of all grouped blocks followed by measurement of the data register. Because the ideal mirror workload returns the data register to the all-zero state, the primary success probability is the observed probability of 0^q.

### 4.3 Controlled noise model and execution

The controlled E1/E2 benchmark uses the repository depolarizing-noise model parameterized by p. Each circuit is transpiled for an AerSimulator configured with that noise model, using optimization level 0 and a fixed seed_transpiler equal to the experimental seed. Simulation uses the same seed as seed_simulator.

Optimization level 0 is used to preserve the intended benchmark structure and avoid aggressive compiler transformations becoming an uncontrolled source of variation.

Experiment 4 prospectively replaces this controlled model with composite device-like noise containing T1/T2 effects, one- and two-qubit gate error, and readout error. Those results are not yet available and are not treated as evidence in the present draft.

### 4.4 Raw baseline

For Raw execution, the measured all-zero probability is

y_hat_raw = n(0^q)/N.

Because the ideal target is one, the absolute error is

E_raw = |1-y_hat_raw|.

Raw uses no syndrome ancilla and no postselection.

### 4.5 Zero-noise extrapolation

ZNE uses global circuit folding at noise-scale factors

S={1,3,5}.

For each scale, the folded circuit is independently transpiled and executed under the same controlled physical-noise model. The three measured values are passed to a linear zero-noise extrapolator.

The implementation preserves the extrapolated value before physical clipping,

y_hat_unclipped,

and also reports

y_hat = min(1,max(0,y_hat_unclipped)).

A clipping flag records whether the physical projection changed the extrapolated estimate.

Resource accounting for ZNE sums gate counts, transpiled depth, and execution time across all three scale circuits. Its effective executed sampling is 3N.

### 4.6 Repeated quantum error detection

The authoritative repeated-QED implementation uses one reusable syndrome ancilla rather than allocating one physical ancilla per check round.

For every grouped mirror block:

1. execute the unitary block on the data register;
2. apply CX operations from every data qubit to the syndrome ancilla;
3. measure the ancilla into a distinct classical syndrome bit;
4. reset and reuse the same ancilla before the next block, except after the final syndrome measurement;
5. measure the data register after the final block.

If R is the number of grouped blocks, the circuit stores R syndrome bits but uses only one physical syndrome ancilla.

A shot is accepted only when every recorded syndrome bit is zero. Let N_acc and N_rej denote accepted and rejected shots. Then

A = N_acc/N.

Among accepted shots, the conditional success estimator is

y_hat_QED = N_success/N_acc,

where success requires the measured data register to be all zero. If no shots are accepted, the current implementation assigns the conditional estimator zero; such regimes must therefore be interpreted together with acceptance rather than as ordinary reliability observations.

### 4.7 Hybrid repeated-QED plus ZNE

Hybrid execution applies ZNE to the check-compatible QED workload while preserving valid QED boundaries. Each ideal-identity block is folded independently at scale 1, 3, or 5 before repeated parity checks are inserted.

For each scale k, the experiment records:

- the postselected conditional estimate y_hat_k;
- accepted and rejected shots;
- acceptance A_k;
- gate counts, depth, and runtime.

Linear zero-noise extrapolation is then applied to the three postselected conditional estimates. As with ZNE alone, both unclipped and clipped estimates are retained.

The aggregate Hybrid acceptance reported in the production data is

A_hybrid = (sum_k N_acc,k)/(3N).

This distinction is important because A_1, A_3, and A_5 can differ substantially as folded circuits become noisier.

### 4.8 Check frequency

The check interval L controls how many identity micro-blocks are grouped between syndrome measurements. Smaller L implies more frequent syndrome extraction; larger L reduces checking overhead.

The production benchmark uses L in {2,8}. Experiment 3 prospectively evaluates a denser set L in {1,2,4,8,16} around empirically identified crossover and acceptance boundaries.

Because the underlying micro-block sequence is fixed before grouping, changes with L can be attributed to check placement/frequency rather than a different random workload.

### 4.9 Resource accounting

For every transpiled execution, the implementation records one- and two-qubit gate work using explicit gate-count categories, aggregate transpiled depth, physical-qubit count, effective/executed shots, and classical simulator execution time.

For multi-scale methods, gate work, depth, and runtime are summed across scale circuits.

Raw and ZNE use q physical qubits. Repeated QED and Hybrid use q+1 physical qubits because the syndrome ancilla is reused sequentially.

The benchmark retains both nominal shots and postselection statistics so that conditional accuracy cannot be interpreted independently of discarded sampling work.

### 4.10 Randomization and replication

Experiment 2 uses 20 integer seeds, 0 through 19. The seed controls generation of the underlying mirror micro-workload, transpilation, and simulation. Method comparisons for a matched condition use the same seeded workload.

Seed-level observations are retained in the raw dataset rather than storing only aggregate means.

### 4.11 Statistical aggregation

The analysis first validates schema completeness, rejects duplicate method-condition rows, requires exactly the four expected methods for every completed condition, and audits paired-L invariance for Raw/ZNE.

Results are then aggregated over seeds for each

(q,d,p,N,L,method)

cell. The current analysis records mean error, standard deviation, seed count, mean acceptance, mean accepted shots, mean two-qubit work, mean depth, mean physical qubits, mean effective shots, mean runtime, clipping fraction, mean unclipped estimate, and a 95% confidence interval for mean absolute error.

Experiment 2 is considered final only when all 9600 matched conditions are present and the final analysis is executed with the complete-data requirement.

### 4.12 Boundary selection and prospective follow-up

Experiment 3 candidate selection is algorithmic rather than visual. The analysis separately identifies:

- meaningful QEM-QED boundaries while excluding trivial near-perfect Raw regimes;
- QED-Hybrid boundaries with explicit clipping controls;
- acceptance boundaries near predeclared survival levels.

The final E3 design is not frozen until E2 completes.

Experiments 4 and 5 similarly use gated manifest builders so that realistic-noise and hardware configurations are selected from finalized upstream evidence rather than retrospectively chosen after observing downstream outcomes.

### 4.13 Adaptive-evaluation leakage controls

The adaptive experiments use grouped rather than row-level data splitting. All methods and paired check intervals associated with the same underlying workload unit remain in the same split.

Experiment 6 freezes train, validation, and test groups before policy selection. Experiment 7 uses chronological hardware/calibration windows. Experiment 8 holds out an entire hardware domain for its primary generalization test.

These controls are intended to separate descriptive benchmark performance from genuine out-of-sample decision performance.

### 4.14 Evidence status

At the present manuscript stage, Experiment 1 is complete and Experiment 2 production is in progress. Sections describing Experiments 3-8 specify locked or provisional methodology only. No result from an unexecuted experiment is treated as empirical evidence.
