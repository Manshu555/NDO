"""
Main entry point for DSDV-GWO Optimisation Project
===================================================

Usage:
    python main.py --mode smoke         # Quick smoke test
    python main.py --mode baseline      # Run baseline experiments
    python main.py --mode optimise      # Run GWO optimisation
    python main.py --mode full          # Full pipeline: baseline + optimise + analyse
    python main.py --mode benchmark     # Validate GWO on benchmark functions
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np

from optimizer.gwo import GWO
from optimizer.benchmarks import sphere, rastrigin
from optimizer.fitness import DSDVFitnessEvaluator, FitnessConfig
from simulator.python_model import PythonMANETSimulator, SimulationConfig
from experiments.runner import (
    ExperimentRunner,
    SMOKE_TEST,
    SMALL_SCENARIO,
    MEDIUM_SCENARIO,
    HIGH_MOBILITY,
    DENSE_NETWORK,
)
from analysis.plots import ResultAnalyser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent
RESULTS_DIR = PROJECT_ROOT / "results"


def run_benchmark_validation(results_dir: Path):
    """Validate GWO on standard benchmark functions."""
    logger.info("=" * 60)
    logger.info("GWO BENCHMARK VALIDATION")
    logger.info("=" * 60)

    plots_dir = results_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Sphere function (5D)
    logger.info("--- Sphere function (5D) ---")
    gwo_sphere = GWO(sphere, n_wolves=20, n_iterations=100, lb=[-100]*5, ub=[100]*5, seed=42)
    sphere_result = gwo_sphere.run()
    logger.info("  Best fitness: %.6e", sphere_result.best_fitness)
    logger.info("  Best position: %s", sphere_result.best_position)
    logger.info("  Expected optimum: 0.0 at origin")

    # Rastrigin function (5D)
    logger.info("--- Rastrigin function (5D) ---")
    gwo_rast = GWO(rastrigin, n_wolves=30, n_iterations=200, lb=[-5.12]*5, ub=[5.12]*5, seed=42)
    rast_result = gwo_rast.run()
    logger.info("  Best fitness: %.6e", rast_result.best_fitness)
    logger.info("  Best position: %s", rast_result.best_position)
    logger.info("  Expected optimum: 0.0 at origin")

    # Determinism test
    logger.info("--- Determinism check ---")
    gwo_check = GWO(sphere, n_wolves=20, n_iterations=100, lb=[-100]*5, ub=[100]*5, seed=42)
    check_result = gwo_check.run()
    match = np.allclose(sphere_result.best_position, check_result.best_position)
    logger.info("  Same seed → same result: %s", match)

    # Plot convergence
    analyser = ResultAnalyser(results_dir, plots_dir)
    analyser.plot_benchmark_validation(
        sphere_result.convergence_curve,
        rast_result.convergence_curve,
    )

    return sphere_result, rast_result


def run_smoke_test(results_dir: Path):
    """Quick smoke test to verify the pipeline works."""
    logger.info("=" * 60)
    logger.info("SMOKE TEST")
    logger.info("=" * 60)

    runner = ExperimentRunner(output_dir=results_dir)

    # Baseline
    baseline = runner.run_baseline(SMOKE_TEST)

    # GWO optimisation (tiny)
    gwo_result, evaluator = runner.run_gwo_optimisation(
        SMOKE_TEST, n_wolves=5, n_iterations=5, gwo_seed=42,
    )

    # Optimised run
    fcfg = FitnessConfig()
    optimised = runner.run_optimised(SMOKE_TEST, gwo_result.best_position, fcfg)

    logger.info("--- Smoke Test Results ---")
    logger.info("  Baseline PDR: %.4f", baseline[0].pdr)
    logger.info("  Optimised PDR: %.4f", optimised[0].pdr)
    logger.info("  GWO best fitness: %.6f", gwo_result.best_fitness)

    return baseline, optimised, gwo_result


def run_full_experiments(results_dir: Path, scenarios=None):
    """Run the full experimental pipeline."""
    logger.info("=" * 60)
    logger.info("FULL EXPERIMENT PIPELINE")
    logger.info("=" * 60)

    if scenarios is None:
        scenarios = [SMALL_SCENARIO, MEDIUM_SCENARIO, HIGH_MOBILITY]

    runner = ExperimentRunner(output_dir=results_dir)
    plots_dir = results_dir / "plots"
    analyser = ResultAnalyser(results_dir, plots_dir)

    all_results = {}

    for scenario in scenarios:
        logger.info("\n" + "=" * 60)
        logger.info("SCENARIO: %s", scenario.name)
        logger.info("=" * 60)

        # 1. Baseline
        baseline_results = runner.run_baseline(scenario)

        # 2. GWO optimisation (using first seed for tuning)
        gwo_result, evaluator = runner.run_gwo_optimisation(
            scenario, n_wolves=10, n_iterations=15, gwo_seed=42,
        )

        # 3. Optimised runs (all seeds including held-out)
        fcfg = FitnessConfig()
        optimised_results = runner.run_optimised(
            scenario, gwo_result.best_position, fcfg,
        )

        # 4. Generate plots
        analyser.plot_convergence(scenario.name)
        analyser.plot_comparison_bars(scenario.name)
        analyser.plot_per_seed_comparison(scenario.name)

        all_results[scenario.name] = {
            "baseline": baseline_results,
            "optimised": optimised_results,
            "gwo_result": gwo_result,
        }

    # 5. Summary statistics
    scenario_names = [s.name for s in scenarios]
    summary_df = analyser.generate_summary_table(scenario_names)

    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)

    for scenario_name in scenario_names:
        stats = analyser.compute_statistics(scenario_name)
        logger.info("\n--- %s ---", scenario_name)
        for metric, data in stats.items():
            b_mean = data.get("baseline_mean", "N/A")
            o_mean = data.get("optimised_mean", "N/A")
            improvement = data.get("improvement_pct", "N/A")
            p_val = data.get("p_value", "N/A")
            logger.info(
                "  %s: baseline=%.4f, optimised=%.4f, improvement=%.1f%%, p=%.4f",
                metric,
                b_mean if isinstance(b_mean, float) else 0,
                o_mean if isinstance(o_mean, float) else 0,
                improvement if isinstance(improvement, float) else 0,
                p_val if isinstance(p_val, float) else 1,
            )

    return all_results


def main():
    parser = argparse.ArgumentParser(description="DSDV-GWO Optimisation Project")
    parser.add_argument(
        "--mode",
        choices=["smoke", "baseline", "optimise", "full", "benchmark"],
        default="smoke",
        help="Execution mode",
    )
    parser.add_argument("--results-dir", type=str, default=str(RESULTS_DIR))

    args = parser.parse_args()
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    logger.info("DSDV-GWO Optimisation Project")
    logger.info("Mode: %s", args.mode)
    logger.info("Results directory: %s", results_dir)
    logger.info("⚠️  Using Python network model (NOT NS-3 packet-level simulation)")

    if args.mode == "benchmark":
        run_benchmark_validation(results_dir)

    elif args.mode == "smoke":
        run_smoke_test(results_dir)

    elif args.mode == "baseline":
        runner = ExperimentRunner(output_dir=results_dir)
        for scenario in [SMALL_SCENARIO, MEDIUM_SCENARIO]:
            runner.run_baseline(scenario)

    elif args.mode == "optimise":
        runner = ExperimentRunner(output_dir=results_dir)
        for scenario in [SMALL_SCENARIO, MEDIUM_SCENARIO]:
            gwo_result, evaluator = runner.run_gwo_optimisation(
                scenario, n_wolves=10, n_iterations=15,
            )
            logger.info("Best params for %s: %s",
                        scenario.name, gwo_result.best_position)

    elif args.mode == "full":
        run_benchmark_validation(results_dir)
        run_full_experiments(results_dir)

    logger.info("\nDone. Results saved to %s", results_dir)


if __name__ == "__main__":
    main()
