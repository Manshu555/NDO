# DSDV Routing Optimisation Using Grey Wolf Optimisation (GWO)

An academic project evaluating whether Grey Wolf Optimisation can improve the
performance of the DSDV routing protocol in a Mobile Ad Hoc Network (MANET).

> **⚠️ Simulation Backend**: This project includes two simulation backends:
> 1. **Python Network Model** — a simplified DSDV MANET simulator (used for
>    the experiments presented here)
> 2. **NS-3 C++ Scenario** — ready-to-compile code for NS-3 packet-level
>    simulation (requires a working NS-3 installation)
>
> All experimental results in this repository were produced using the **Python
> model**, not NS-3. They demonstrate the optimisation framework but are not
> publication-quality packet-level simulation results.

## Project Structure

```
NDO/
├── main.py                    # Main entry point (CLI)
├── optimizer/
│   ├── gwo.py                 # Grey Wolf Optimisation algorithm
│   ├── benchmarks.py          # Sphere, Rastrigin, etc.
│   └── fitness.py             # DSDV fitness evaluator
├── simulator/
│   ├── python_model.py        # Python MANET simulation model
│   ├── ns3_runner.py          # NS-3 subprocess interface
│   └── ns3_dsdv_scenario.cc   # NS-3 C++ scenario
├── experiments/
│   └── runner.py              # Experiment orchestration
├── analysis/
│   └── plots.py               # Statistical analysis & plotting
├── results/
│   ├── raw/                   # Raw simulation outputs
│   ├── processed/             # CSV summaries
│   └── plots/                 # Generated figures
├── tests/
│   ├── test_gwo.py            # GWO unit tests
│   ├── test_simulator.py      # Simulator & fitness tests
│   └── test_integration.py    # End-to-end tests
└── docs/
    ├── setup_guide.md
    ├── methodology.md
    └── ns3_dsdv_parameters.md
```

## Quick Start

### Prerequisites

- Python 3.10+
- numpy, scipy, matplotlib, pandas, pytest

```bash
pip install numpy scipy matplotlib pandas pytest
```

### Run Tests

```bash
python -m pytest tests/ -v
```

### Run Experiments

```bash
# GWO benchmark validation
python main.py --mode benchmark

# Quick smoke test (< 10 seconds)
python main.py --mode smoke

# Full experiment pipeline (baseline + GWO + analysis)
python main.py --mode full
```

### Reproduce Results

```bash
# 1. Run all tests to verify correctness
python -m pytest tests/ -v

# 2. Run benchmark validation
python main.py --mode benchmark

# 3. Run full experiments
python main.py --mode full

# Results will be in results/processed/ and results/plots/
```

## GWO Algorithm

Implements the standard Grey Wolf Optimiser (Mirjalili et al., 2014):
- Population of search agents modelling wolf pack hierarchy (α, β, δ, ω)
- Linear decrease of exploration coefficient `a` from 2 to 0
- Position update guided by α, β, δ leaders
- Validated on Sphere (unimodal) and Rastrigin (multimodal) benchmarks

## DSDV Parameters Tuned

The following DSDV parameters are optimised by GWO:

| Parameter | NS-3 Attribute | Default | Range | Effect |
|-----------|---------------|---------|-------|--------|
| Periodic Update Interval | `PeriodicUpdateInterval` | 15 s | 5–30 s | Route freshness vs overhead |
| Settling Time | `SettlingTime` | 6 s | 1–15 s | Stability vs adaptation speed |
| Max Queue Length | `MaxQueueLen` | 64 | 16–256 | Buffer size |
| Max Queue Time | `MaxQueueTime` | 30 s | 5–120 s | Buffer timeout |

These are actual NS-3 DSDV attributes. The project does **not** modify DSDV's
sequence-number and hop-count route-selection rules.

## Fitness Function

```
fitness = w_pdr * (1 - PDR) + w_delay * norm_delay + w_overhead * overhead_ratio
```

Default weights: `w_pdr=0.5, w_delay=0.3, w_overhead=0.2`

All components normalised to [0, 1]. Failed simulations receive a penalty of 10.0.

## Using NS-3 (If Available)

```bash
# Copy scenario to NS-3 scratch directory
cp simulator/ns3_dsdv_scenario.cc /path/to/ns-3/scratch/dsdv-manet-gwo.cc

# Build
cd /path/to/ns-3
./ns3 build

# Run standalone
./ns3 run "scratch/dsdv-manet-gwo --nNodes=20 --simDuration=100 --seed=42"

# Run through the project's NS-3 runner
NS3_DIR=/path/to/ns-3 python main.py --mode full
```

## References

1. S. Mirjalili, S. M. Mirjalili, A. Lewis, "Grey Wolf Optimizer,"
   *Advances in Engineering Software*, vol. 69, pp. 46-61, 2014.
2. C. E. Perkins, P. Bhagwat, "Highly Dynamic Destination-Sequenced
   Distance-Vector Routing (DSDV) for Mobile Computers," *ACM SIGCOMM*, 1994.
3. NS-3 Consortium, "ns-3 Network Simulator," https://www.nsnam.org/

## License

Academic use only. This is a research prototype.
