"""
Experiment Runner
=================

Orchestrates baseline and GWO-optimised DSDV experiments.
Handles:
    - Multi-seed baseline runs
    - GWO optimisation with the Python model backend
    - Paired comparison of default vs optimised parameters
    - CSV output of all results
    - Convergence logging
"""

from __future__ import annotations

import csv
import dataclasses
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np

from optimizer.gwo import GWO, GWOResult
from optimizer.fitness import DSDVFitnessEvaluator, FitnessConfig, FAILURE_PENALTY
from simulator.python_model import PythonMANETSimulator, SimulationConfig, SimulationResult

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class ExperimentScenario:
    """Defines an experimental scenario."""
    name: str
    n_nodes: int = 20
    area_size: float = 500.0
    sim_duration: float = 100.0
    min_speed: float = 1.0
    max_speed: float = 10.0
    n_flows: int = 5
    seeds: list[int] = dataclasses.field(default_factory=lambda: [42, 123, 456, 789, 1024])


# Pre-defined scenarios
SMOKE_TEST = ExperimentScenario(
    name="smoke_test",
    n_nodes=10,
    sim_duration=30.0,
    n_flows=3,
    seeds=[42],
)

SMALL_SCENARIO = ExperimentScenario(
    name="small",
    n_nodes=15,
    sim_duration=60.0,
    n_flows=4,
    seeds=[42, 123, 456],
)

MEDIUM_SCENARIO = ExperimentScenario(
    name="medium",
    n_nodes=20,
    sim_duration=100.0,
    n_flows=5,
    seeds=[42, 123, 456, 789, 1024],
)

HIGH_MOBILITY = ExperimentScenario(
    name="high_mobility",
    n_nodes=20,
    sim_duration=100.0,
    min_speed=5.0,
    max_speed=20.0,
    n_flows=5,
    seeds=[42, 123, 456, 789, 1024],
)

DENSE_NETWORK = ExperimentScenario(
    name="dense",
    n_nodes=30,
    area_size=400.0,
    sim_duration=100.0,
    n_flows=8,
    seeds=[42, 123, 456, 789, 1024],
)


class ExperimentRunner:
    """
    Runs baseline and optimised DSDV experiments.

    Parameters
    ----------
    output_dir : Path
        Directory to store results.
    """

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.raw_dir = self.output_dir / "raw"
        self.processed_dir = self.output_dir / "processed"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def _make_config(self, scenario: ExperimentScenario, seed: int,
                     overrides: Optional[dict] = None) -> SimulationConfig:
        """Create a SimulationConfig from a scenario and seed."""
        cfg = SimulationConfig(
            n_nodes=scenario.n_nodes,
            area_size=scenario.area_size,
            sim_duration=scenario.sim_duration,
            min_speed=scenario.min_speed,
            max_speed=scenario.max_speed,
            n_flows=scenario.n_flows,
            seed=seed,
        )
        if overrides:
            for key, value in overrides.items():
                if hasattr(cfg, key):
                    setattr(cfg, key, value)
        return cfg

    def run_baseline(self, scenario: ExperimentScenario) -> list[SimulationResult]:
        """
        Run baseline DSDV with default parameters across all seeds.

        Returns list of SimulationResult, one per seed.
        """
        logger.info("=== Baseline: %s (%d seeds) ===", scenario.name, len(scenario.seeds))
        results = []

        for seed in scenario.seeds:
            cfg = self._make_config(scenario, seed)
            logger.info("  Seed %d: n_nodes=%d, duration=%.0fs", seed, cfg.n_nodes, cfg.sim_duration)

            sim = PythonMANETSimulator(cfg)
            t0 = time.time()
            result = sim.run()
            elapsed = time.time() - t0

            logger.info(
                "  Seed %d: PDR=%.3f, delay=%.4fs, throughput=%.0f bps, "
                "overhead=%.3f, elapsed=%.2fs, success=%s",
                seed, result.pdr, result.mean_delay, result.throughput,
                result.overhead_ratio, elapsed, result.success,
            )
            results.append(result)

        # Save raw results
        self._save_results(results, scenario.name, "baseline")
        return results

    def run_gwo_optimisation(
        self,
        scenario: ExperimentScenario,
        n_wolves: int = 10,
        n_iterations: int = 15,
        gwo_seed: int = 42,
        fitness_config: Optional[FitnessConfig] = None,
    ) -> tuple[GWOResult, DSDVFitnessEvaluator]:
        """
        Run GWO optimisation to find best DSDV parameters.

        Uses a single tuning seed (first in scenario) for optimisation.
        The remaining seeds are held out for evaluation.

        Returns (GWOResult, evaluator_with_history).
        """
        logger.info("=== GWO Optimisation: %s ===", scenario.name)

        # Use first seed for tuning
        tuning_seed = scenario.seeds[0]
        tuning_config = self._make_config(scenario, tuning_seed)

        if fitness_config is None:
            fitness_config = FitnessConfig(base_config=tuning_config)
        else:
            fitness_config.base_config = tuning_config

        evaluator = DSDVFitnessEvaluator(fitness_config, use_ns3=False)

        lb = fitness_config.get_lb()
        ub = fitness_config.get_ub()

        logger.info("  Search space: %s", list(zip(fitness_config.get_param_names(), lb, ub)))
        logger.info("  Wolves=%d, Iterations=%d, Seed=%d", n_wolves, n_iterations, gwo_seed)

        gwo = GWO(
            fitness_fn=evaluator.evaluate,
            n_wolves=n_wolves,
            n_iterations=n_iterations,
            lb=lb,
            ub=ub,
            seed=gwo_seed,
        )

        t0 = time.time()
        gwo_result = gwo.run()
        elapsed = time.time() - t0

        # Map best position to parameter names
        param_names = fitness_config.get_param_names()
        best_params = dict(zip(param_names, gwo_result.best_position))

        logger.info("  GWO finished in %.2fs, %d evaluations", elapsed, evaluator.eval_count)
        logger.info("  Best fitness: %.6f", gwo_result.best_fitness)
        logger.info("  Best parameters: %s", best_params)

        # Save convergence data
        self._save_convergence(gwo_result, scenario.name)
        self._save_eval_history(evaluator, scenario.name)

        return gwo_result, evaluator

    def run_optimised(
        self,
        scenario: ExperimentScenario,
        best_position: np.ndarray,
        fitness_config: FitnessConfig,
    ) -> list[SimulationResult]:
        """
        Run DSDV with GWO-optimised parameters across all seeds.
        """
        logger.info("=== Optimised: %s (%d seeds) ===", scenario.name, len(scenario.seeds))

        # Build parameter overrides from best position
        overrides = {}
        for i, (name, lb, ub) in enumerate(fitness_config.param_bounds):
            value = float(np.clip(best_position[i], lb, ub))
            if name == "max_queue_len":
                value = int(round(value))
            overrides[name] = value

        logger.info("  Optimised params: %s", overrides)

        results = []
        for seed in scenario.seeds:
            cfg = self._make_config(scenario, seed, overrides=overrides)
            sim = PythonMANETSimulator(cfg)
            t0 = time.time()
            result = sim.run()
            elapsed = time.time() - t0

            logger.info(
                "  Seed %d: PDR=%.3f, delay=%.4fs, throughput=%.0f bps, "
                "overhead=%.3f, elapsed=%.2fs",
                seed, result.pdr, result.mean_delay, result.throughput,
                result.overhead_ratio, elapsed,
            )
            results.append(result)

        self._save_results(results, scenario.name, "optimised")
        return results

    def _save_results(self, results: list[SimulationResult], scenario_name: str, label: str):
        """Save simulation results to CSV."""
        filepath = self.processed_dir / f"{scenario_name}_{label}.csv"
        fieldnames = [
            "scenario", "label", "seed", "n_nodes", "sim_duration",
            "periodic_update_interval", "settling_time", "max_queue_len", "max_queue_time",
            "packets_sent", "packets_received", "packets_dropped",
            "pdr", "mean_delay", "throughput", "overhead_ratio",
            "routing_updates_sent", "success",
        ]

        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                cfg = r.config or SimulationConfig()
                writer.writerow({
                    "scenario": scenario_name,
                    "label": label,
                    "seed": cfg.seed,
                    "n_nodes": cfg.n_nodes,
                    "sim_duration": cfg.sim_duration,
                    "periodic_update_interval": cfg.periodic_update_interval,
                    "settling_time": cfg.settling_time,
                    "max_queue_len": cfg.max_queue_len,
                    "max_queue_time": cfg.max_queue_time,
                    "packets_sent": r.packets_sent,
                    "packets_received": r.packets_received,
                    "packets_dropped": r.packets_dropped,
                    "pdr": f"{r.pdr:.6f}",
                    "mean_delay": f"{r.mean_delay:.6f}",
                    "throughput": f"{r.throughput:.2f}",
                    "overhead_ratio": f"{r.overhead_ratio:.6f}",
                    "routing_updates_sent": r.routing_updates_sent,
                    "success": r.success,
                })

        logger.info("  Results saved to %s", filepath)

    def _save_convergence(self, gwo_result: GWOResult, scenario_name: str):
        """Save GWO convergence curve."""
        filepath = self.raw_dir / f"{scenario_name}_convergence.json"
        data = {
            "best_fitness": gwo_result.best_fitness,
            "best_position": gwo_result.best_position.tolist(),
            "convergence_curve": gwo_result.convergence_curve,
            "n_iterations": gwo_result.n_iterations,
            "n_function_evals": gwo_result.n_function_evals,
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        logger.info("  Convergence saved to %s", filepath)

    def _save_eval_history(self, evaluator: DSDVFitnessEvaluator, scenario_name: str):
        """Save all fitness evaluations."""
        filepath = self.raw_dir / f"{scenario_name}_eval_history.json"
        with open(filepath, "w") as f:
            json.dump(evaluator.eval_history, f, indent=2)
        logger.info("  Eval history saved to %s", filepath)
