# Paper 2 — Unified Manuscript Architecture

## Provisional title

**Bridging NISQ and Fault-Tolerant Quantum Computing: Resource-Aware and Adaptive Quantum Error Management**

The title remains provisional until Experiments 6–8 establish whether the adaptive/generalization claims are supported.

## Central thesis

Quantum error management should be evaluated and selected jointly with its resource cost. The paper studies when resources should be allocated to mitigation, detection, or hybrid strategies; tests whether those regimes survive realistic noise and hardware; and, conditionally on the empirical evidence, evaluates adaptive selection under resource and reliability constraints.

## Evidence-status rule

- E1: completed evidence.
- E2: production in progress; partial checkpoint results are exploratory only.
- E3: protocol/selection methodology prepared; final design depends on completed E2.
- E4: protocol prepared; execution depends on E2/E3.
- E5: protocol prepared; execution depends on E4 and hardware feasibility.
- E6: protocol prepared; execution depends on finalized upstream datasets and frozen splits.
- E7: protocol prepared; execution depends on E5/E6 and longitudinal hardware data.
- E8: protocol prepared; execution depends on multiple hardware domains.

No planned experiment may be described in manuscript prose as a completed result.

## Research questions

**RQ1.** How do QEM, QED, and hybrid error-management strategies trade reliability against quantum-resource consumption across circuit width, depth, noise, and sampling regimes?

**RQ2.** Where do statistically identifiable resource-dependent crossover regimes occur between QEM, QED, and hybrid error management?

**RQ3.** How does error-detection frequency alter reliability, postselection acceptance, and resource Pareto efficiency?

**RQ4.** Do the identified resource/crossover regimes persist under realistic device noise and real quantum hardware?

**RQ5.** Can an adaptive resource-aware policy outperform fixed error-management strategies under equal resource budgets or equal reliability targets?

**RQ6.** Does adaptive error management remain effective under calibration drift and across held-out quantum hardware environments?

## Intended contributions

C1. A resource-aware characterization of ZNE that reports reliability improvement jointly with sampling, gate, depth, and runtime overhead.

C2. A matched Raw/ZNE/repeated-QED/Hybrid benchmark across workload, noise, shot-budget, seed, and check-frequency dimensions.

C3. A crossover-oriented analysis that treats QED check frequency as a controllable resource variable and explicitly models acceptance/postselection cost.

C4. Targeted robustness validation under realistic composite noise and prospectively selected hardware tests.

C5. Conditional on E6 results, an adaptive policy formulation for choosing method and check interval under reliability/resource constraints.

C6. Conditional on E7/E8 results, evaluation under temporal calibration drift and held-out hardware-domain shift.

## Manuscript structure

### Abstract
Write last. State only completed findings.

### 1. Introduction
1.1 Reliability bottleneck in noisy quantum computation  
1.2 QEM, QED, and the transition toward fault tolerance  
1.3 Why error reduction alone is an incomplete objective  
1.4 Resource-aware crossover problem  
1.5 Research questions and contributions  

### 2. Background and Related Work
2.1 Quantum error mitigation and zero-noise extrapolation  
2.2 Sampling overhead and limitations of mitigation  
2.3 Quantum error detection and postselection  
2.4 Error correction and fault-tolerant transition  
2.5 Hybrid mitigation/detection strategies  
2.6 Quantum benchmarking and resource estimation  
2.7 Adaptive/hardware-aware quantum execution  

### 3. Resource-Aware Error-Management Framework
3.1 Workload and noise notation  
3.2 Reliability metrics  
3.3 Sampling and postselection cost  
3.4 Gate, depth, and physical-qubit cost  
3.5 ZNE clipping/unclipped-estimator diagnostics  
3.6 Pareto efficiency  
3.7 Crossover definitions  
3.8 Reliability-constrained and budget-constrained objectives  

### 4. Experimental Methodology
4.1 Reproducibility and software environment  
4.2 Workload construction and paired-design controls  
4.3 Noise models  
4.4 ZNE implementation  
4.5 Reusable-ancilla repeated QED  
4.6 Hybrid QED+ZNE  
4.7 Statistical aggregation and confidence intervals  
4.8 Leakage controls and prospective validation principles  

### 5. Phase I — Characterize
#### 5.1 Experiment 1: QEM/ZNE Resource Scaling
5.1.1 Design  
5.1.2 Reliability results  
5.1.3 Sampling/gate/depth/runtime overhead  
5.1.4 Interpretation  

#### 5.2 Experiment 2: QEM vs QED vs Hybrid Resource Benchmark
5.2.1 Production grid  
5.2.2 Method comparison  
5.2.3 Width/depth/noise scaling  
5.2.4 Shot-budget effects  
5.2.5 Acceptance and clipping  
5.2.6 Resource Pareto frontiers  
5.2.7 QEM↔QED and QED↔Hybrid crossover structure  

#### 5.3 Experiment 3: Check-Frequency and Boundary Validation
5.3.1 Empirical boundary selection  
5.3.2 L={1,2,4,8,16} design  
5.3.3 Reliability/acceptance tradeoff  
5.3.4 Optimal/Pareto-efficient check intervals  
5.3.5 Implications for adaptive selection  

### 6. Phase II — Validate
#### 6.1 Experiment 4: Realistic-Noise Robustness
6.1.1 Composite T1/T2 + gate + readout noise  
6.1.2 Predeclared device-like scenarios  
6.1.3 Regime retention/displacement  
6.1.4 Simulation-model limitations  

#### 6.2 Experiment 5: Prospective Hardware Validation
6.2.1 Frozen predictions and hardware manifest  
6.2.2 Hardware execution and metadata  
6.2.3 Prediction agreement/disagreement  
6.2.4 Simulator-to-hardware displacement  
6.2.5 Hardware resource/acceptance behavior  

### 7. Phase III — Adapt
#### 7.1 Experiment 6: Adaptive Resource-Aware Error Management
7.1.1 Decision problem  
7.1.2 Leakage-safe grouped splits  
7.1.3 Fixed-strategy and oracle baselines  
7.1.4 Reliability-constrained optimization  
7.1.5 Budget-constrained optimization  
7.1.6 Held-out performance and regret  
7.1.7 Ablations  

#### 7.2 Experiment 7: Calibration-Aware Dynamic Adaptation
7.2.1 Hardware-state features  
7.2.2 Chronological evaluation  
7.2.3 Static vs calibration-aware policy  
7.2.4 Switching behavior and adaptation cost  

#### 7.3 Experiment 8: Cross-Platform Generalization
7.3.1 Held-out hardware domains  
7.3.2 Zero-shot transfer  
7.3.3 Calibration-feature transfer  
7.3.4 Few-shot adaptation  
7.3.5 Framework transfer vs threshold transfer  

### 8. Integrated Discussion
8.1 What resources should be spent on mitigation versus detection?  
8.2 Where hybrid strategies are useful and where acceptance collapses  
8.3 From static crossover maps to adaptive error management  
8.4 Implications for NISQ-to-FTQC system design  
8.5 External validity and hardware dependence  
8.6 Limitations and threats to validity  

### 9. Conclusion

### Appendices / Supplement
A. Complete parameter grids  
B. Additional confidence intervals and seed distributions  
C. Resource accounting definitions  
D. Full Pareto/crossover maps  
E. Noise manifests  
F. Hardware manifests and calibration metadata  
G. Adaptive-policy feature/split manifests  
H. Additional ablations and negative results  

## Current confirmed Experiment 1 result block

The completed Experiment 1 dataset contains 6000 matched conditions / 12000 method rows.

Current aggregate values from the authoritative analysis:
- Raw mean absolute error: 0.2965122986
- ZNE mean absolute error: 0.2526226976
- mean absolute improvement: 0.0438896010
- relative mean error reduction: 0.1480194959 (~14.8%)
- individual improved fraction: 0.9783333333
- individual tied fraction: 0.0216666667
- individual worse fraction: 0.0
- seed-aggregated cells: 300
- cells improved: 295
- cells tied: 5
- cell mean improvement 95% CI: [0.0401222503, 0.0476569517]
- ZNE clipping fraction: 0.079
- total simulator runtime ratio: 8.8762288673
- sampling overhead ratio: 3.0
- two-qubit gate-work ratio: 9.0
- depth-work ratio: 8.9091503072

These values may be used in the manuscript. E2 checkpoint aggregates must not be presented as final global results until 9600/9600 completes.

## Immediate writing order

1. Section 3 — Resource-Aware Error-Management Framework.
2. Section 4 — Experimental Methodology.
3. Section 5.1 — completed Experiment 1.
4. Introduction, once the technical framing is stable.
5. Related Work after literature/citation audit.
6. E2–E8 Results only as each experiment completes.
