# Technical Report: DSDV Routing Optimisation Using Grey Wolf Optimisation

## 1. Problem Statement

The Destination-Sequenced Distance-Vector (DSDV) routing protocol is a proactive, table-driven protocol for Mobile Ad Hoc Networks. Its performance depends on configuration parameters that trade off route freshness against control overhead. This project evaluates whether Grey Wolf Optimisation (GWO) can automatically discover DSDV parameter configurations that improve network performance.

> [!IMPORTANT]
> All experimental results in this report were obtained using a **Python network model**, not NS-3 packet-level simulation. A ready-to-compile NS-3 C++ scenario is provided but was not executed due to NS-3 being unavailable on the development system (Windows without WSL).

## 2. GWO Validation on Benchmark Functions

Before applying GWO to DSDV optimisation, we validated the algorithm on standard benchmarks.

| Benchmark | Dimensions | Known Optimum | GWO Result | Iterations |
|-----------|-----------|---------------|------------|------------|
| Sphere | 5 | 0.0 | 3.17 × 10⁻¹⁸ | 100 |
| Rastrigin | 5 | 0.0 | 0.0 (exact) | 200 |

![GWO Benchmark Validation](file:///d:/Github/NDO/results/plots/benchmark_validation.png)

**Determinism check**: Two runs with seed=42 produced identical results ✅

## 3. DSDV Parameters Tuned

We optimise four parameters that NS-3's DSDV implementation exposes as configurable attributes:

| Parameter | Default | Search Range | Unit |
|-----------|---------|-------------|------|
| PeriodicUpdateInterval | 15 | [5, 30] | seconds |
| SettlingTime | 6 | [1, 15] | seconds |
| MaxQueueLen | 64 | [16, 256] | packets |
| MaxQueueTime | 30 | [5, 120] | seconds |

We do **not** modify DSDV's sequence-number and hop-count route-selection rules.

## 4. Experimental Results

### 4.1 GWO-Optimised Parameters Found

| Scenario | UpdateInterval | SettlingTime | QueueLen | QueueTime |
|----------|---------------|-------------|----------|-----------|
| Small | ~5.4s | ~2.5s | ~113 | ~113s |
| Medium | ~5.2s | ~3.5s | ~66 | ~110s |
| High Mobility | ~5.2s | ~3.9s | ~59 | ~111s |

**Key insight**: GWO consistently selects **shorter update intervals** (~5s vs 15s default) and **shorter settling times** (~3s vs 6s default), trading more routing overhead for substantially fresher routes and higher PDR.

### 4.2 Small Scenario (15 nodes, 60s)

| Metric | Default | GWO-Optimised | Change | p-value |
|--------|---------|--------------|--------|---------|
| **PDR** | 0.647 ± 0.082 | **0.840 ± 0.070** | **+29.7%** | 0.038* |
| Mean Delay | 0.0081s ± 0.0019 | 0.0080s ± 0.0016 | −0.5% | 0.979 |
| Throughput | 34,839 bps | **45,193 bps** | **+29.7%** | 0.032* |
| Overhead Ratio | **0.486** | 0.743 | +52.9% | 0.0004* |

### 4.3 Medium Scenario (20 nodes, 100s)

| Metric | Default | GWO-Optimised | Change | p-value |
|--------|---------|--------------|--------|---------|
| **PDR** | 0.615 ± 0.087 | **0.800 ± 0.034** | **+30.1%** | 0.006** |
| Mean Delay | 0.0080s ± 0.0007 | 0.0087s ± 0.0007 | +8.8% | 0.167 |
| Throughput | 40,821 bps | **53,109 bps** | **+30.1%** | 0.007** |
| Overhead Ratio | **0.601** | 0.796 | +32.4% | <0.001** |

![Medium Scenario Comparison](file:///d:/Github/NDO/results/plots/medium_comparison.png)

![Medium Scenario Convergence](file:///d:/Github/NDO/results/plots/medium_convergence.png)

### 4.4 High Mobility Scenario (20 nodes, 5-20 m/s)

| Metric | Default | GWO-Optimised | Change | p-value |
|--------|---------|--------------|--------|---------|
| **PDR** | 0.397 ± 0.032 | **0.631 ± 0.045** | **+58.9%** | <0.001** |
| Mean Delay | 0.0073s ± 0.0011 | 0.0083s ± 0.0006 | +13.0% | 0.138 |
| Throughput | 26,526 bps | **42,131 bps** | **+58.8%** | <0.001** |
| Overhead Ratio | **0.606** | 0.818 | +34.9% | <0.001** |

![High Mobility Comparison](file:///d:/Github/NDO/results/plots/high_mobility_comparison.png)

\* p < 0.05, \** p < 0.01 (Welch's t-test)

## 5. Analysis and Discussion

### 5.1 PDR Improvement Is Consistent and Significant

Across all three scenarios, GWO optimisation improved PDR by **29-59%**, with all improvements statistically significant (p < 0.05). The improvement is **largest in the high-mobility scenario** (58.9%), where fresher routing information is most valuable.

### 5.2 Trade-off: PDR vs Overhead

GWO achieves higher PDR by **reducing the periodic update interval** from 15s to ~5s, which generates substantially more routing control traffic. This is a genuine trade-off, not a free improvement:

- Overhead ratio increases by 33-53%
- The fitness function (w_pdr=0.5, w_delay=0.3, w_overhead=0.2) prioritises PDR, so GWO correctly finds that more frequent updates are worth the overhead cost

### 5.3 Delay Is Largely Unaffected

Mean end-to-end delay shows small, statistically non-significant changes (p > 0.05 in all scenarios). The slight increase in the optimised configuration is likely due to more routing table computation at each node.

### 5.4 GWO Convergence

GWO converges within 7-10 iterations in all scenarios, with most improvement occurring in the first 5 iterations. This suggests the search space is relatively smooth for this problem.

## 6. Test Results

```
49 tests passed, 0 failed
```

| Test Category | Count | Status |
|--------------|-------|--------|
| GWO equations (compute_a, A, C) | 9 | ✅ All pass |
| GWO bounds handling | 3 | ✅ All pass |
| GWO population init | 2 | ✅ All pass |
| GWO convergence (benchmarks) | 3 | ✅ All pass |
| GWO determinism | 2 | ✅ All pass |
| GWO result structure | 1 | ✅ Pass |
| GWO input validation | 4 | ✅ All pass |
| Simulation smoke tests | 3 | ✅ All pass |
| Metric consistency | 5 | ✅ All pass |
| Simulation reproducibility | 2 | ✅ All pass |
| Fitness function | 5 | ✅ All pass |
| Fitness weights | 1 | ✅ Pass |
| SimulationResult.compute_derived | 5 | ✅ All pass |
| End-to-end integration | 3 | ✅ All pass |
| Full pipeline reproducibility | 1 | ✅ Pass |

## 7. Limitations

1. **Python model, not NS-3**: Results are from a simplified Python model. The model does not capture PHY-layer effects, MAC contention, interference, or realistic packet queuing. NS-3 validation is required for publication.

2. **Limited parameter space**: Only 4 of DSDV's parameters are tuned. Other factors (PHY/MAC settings, mobility model, antenna characteristics) are held constant.

3. **Single fitness function weighting**: The results depend on the choice of w_pdr=0.5, w_delay=0.3, w_overhead=0.2. Different weights would yield different "optimal" configurations.

4. **Small GWO population and iterations**: 10 wolves × 15 iterations is computationally cheap but may not find the true optimum. Larger budgets would be advisable with NS-3.

5. **Scenario-specific**: Optimal parameters likely vary with network size, mobility, and traffic load. The optimisation should be repeated for different deployment conditions.

## 8. Reproducibility

```bash
# Install dependencies
pip install numpy scipy matplotlib pandas pytest

# Run tests
python -m pytest tests/ -v

# Reproduce all results
python main.py --mode full
```

All experiments use fixed random seeds. Results are deterministic given the same software versions.

## 9. References

1. S. Mirjalili, S. M. Mirjalili, A. Lewis, "Grey Wolf Optimizer," *Advances in Engineering Software*, vol. 69, pp. 46-61, 2014.
2. C. E. Perkins, P. Bhagwat, "Highly Dynamic Destination-Sequenced Distance-Vector Routing (DSDV) for Mobile Computers," *ACM SIGCOMM*, 1994.
3. NS-3 Consortium, "ns-3 Network Simulator," https://www.nsnam.org/
