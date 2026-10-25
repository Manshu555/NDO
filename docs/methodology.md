# Methodology

## 1. Problem Statement

The Destination-Sequenced Distance-Vector (DSDV) routing protocol maintains
routing tables at every node through periodic exchanges. Its performance
depends on configuration parameters that trade off route freshness against
control overhead. This project investigates whether the Grey Wolf Optimiser
(GWO) can automatically find DSDV parameter configurations that improve
network performance metrics.

## 2. DSDV Protocol Overview

DSDV (Perkins & Bhagwat, 1994) is a proactive, table-driven routing protocol:
- Each node maintains a routing table with entries for all known destinations
- Routes are selected by: (1) highest sequence number, (2) lowest hop count
- Full routing table dumps are broadcast at each `PeriodicUpdateInterval`
- Route changes are delayed by `SettlingTime` to reduce oscillation
- Packets waiting for routes are buffered (bounded by `MaxQueueLen` and `MaxQueueTime`)

### Parameters Being Optimised

| Parameter | Description | Trade-off |
|-----------|-------------|-----------|
| `PeriodicUpdateInterval` | Interval between full routing table broadcasts | Lower → fresher routes but more overhead |
| `SettlingTime` | Delay before accepting route updates | Lower → faster adaptation but risk of oscillation |
| `MaxQueueLen` | Maximum packets in the send buffer | Higher → fewer drops but more memory |
| `MaxQueueTime` | Maximum time a packet waits in the send buffer | Higher → more chances for route discovery |

### What We Do NOT Modify

We preserve DSDV's fundamental route-selection rules:
- Sequence-number-based route preference (higher is fresher)
- Hop-count-based tie-breaking (lower is shorter)

Modifying these rules would change DSDV's correctness guarantees and is
beyond the scope of this parameter tuning study.

## 3. Grey Wolf Optimisation

GWO (Mirjalili et al., 2014) models the hunting behaviour of grey wolves:

### Social Hierarchy
- **Alpha (α)**: Best solution found (pack leader)
- **Beta (β)**: Second-best solution (advisor)
- **Delta (δ)**: Third-best solution (subordinate leader)
- **Omega (ω)**: Remaining candidates (followers)

### Key Equations

**Linearly decreasing coefficient:**
```
a = 2 - 2 × (t / T)
```

**Coefficient vectors:**
```
A = 2a × r₁ - a       where r₁ ∈ [0,1]
C = 2 × r₂             where r₂ ∈ [0,1]
```

**Distance and position update (for each leader L ∈ {α, β, δ}):**
```
D_L = |C_L × X_L - X|
X_L' = X_L - A_L × D_L
```

**Final position:**
```
X(t+1) = (X_α' + X_β' + X_δ') / 3
```

### Exploration vs Exploitation
- When |A| > 1: exploration (wolves search widely)
- When |A| < 1: exploitation (wolves converge on prey)
- `a` linearly decreases from 2 to 0, shifting from exploration to exploitation

## 4. Fitness Function

The fitness function combines three network performance metrics:

```
fitness = (w_pdr × (1 - PDR) + w_delay × norm_delay + w_overhead × overhead) / Σw
```

| Component | Direction | Normalisation |
|-----------|-----------|--------------|
| `1 - PDR` | Lower is better | PDR ∈ [0,1] by definition |
| `norm_delay` | Lower is better | Clipped to [0, delay_max] then scaled |
| `overhead` | Lower is better | Routing updates / total packets |

Default weights: `w_pdr = 0.5`, `w_delay = 0.3`, `w_overhead = 0.2`

**PDR dominates** because packet delivery is the primary objective.

Failed simulations receive a penalty fitness of 10.0 (well above the valid range [0,1]).

## 5. Experimental Design

### Data Leakage Prevention
- **Tuning seed**: First seed in each scenario used for GWO optimisation
- **Held-out seeds**: Remaining seeds used only for final evaluation
- Identical traffic patterns and mobility across baseline and optimised runs

### Scenarios

| Scenario | Nodes | Area | Duration | Speed | Flows | Seeds |
|----------|-------|------|----------|-------|-------|-------|
| Small | 15 | 500m | 60s | 1-10 m/s | 4 | 3 |
| Medium | 20 | 500m | 100s | 1-10 m/s | 5 | 5 |
| High Mobility | 20 | 500m | 100s | 5-20 m/s | 5 | 5 |

### Statistical Analysis
- Mean ± standard deviation across seeds
- 95% confidence intervals (where n ≥ 2)
- Welch's t-test for baseline vs optimised comparison
- Convergence curves for GWO optimisation progress

## 6. Limitations

1. **Python model is approximate**: The Python network model simplifies many
   aspects of real wireless communication (no PHY layer modelling, simplified
   MAC, no interference modelling). Results demonstrate the framework but
   should be validated with NS-3.

2. **Parameter space is limited**: Only 4 DSDV parameters are tuned. Other
   factors (PHY/MAC parameters, mobility model) are held constant.

3. **GWO is a metaheuristic**: No guarantee of finding the global optimum.
   Results depend on population size, iterations, and random initialisation.

4. **Scenario-specific tuning**: Optimal parameters may differ for different
   network sizes, mobility patterns, and traffic loads.

## 7. References

1. S. Mirjalili, S. M. Mirjalili, A. Lewis, "Grey Wolf Optimizer,"
   *Advances in Engineering Software*, vol. 69, pp. 46-61, 2014.

2. C. E. Perkins, P. Bhagwat, "Highly Dynamic Destination-Sequenced
   Distance-Vector Routing (DSDV) for Mobile Computers," *ACM SIGCOMM*, 1994.

3. NS-3 Consortium, "ns-3 Network Simulator," https://www.nsnam.org/

4. NS-3 DSDV Module Documentation,
   https://www.nsnam.org/docs/models/html/dsdv.html
