"""
End-to-End Integration Tests
=============================

Tests the full pipeline: GWO optimisation → simulation → fitness → results.
Uses small scenarios to keep runtime manageable.
"""

import json
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pytest

from optimizer.gwo import GWO
from optimizer.fitness import DSDVFitnessEvaluator, FitnessConfig, FAILURE_PENALTY
from simulator.python_model import PythonMANETSimulator, SimulationConfig
from experiments.runner import ExperimentRunner, SMOKE_TEST


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_gwo_with_dsdv_fitness(self):
        """GWO should be able to optimise DSDV parameters via fitness function."""
        base_cfg = SimulationConfig(n_nodes=8, sim_duration=15.0, n_flows=2, seed=42)
        fcfg = FitnessConfig(base_config=base_cfg)
        evaluator = DSDVFitnessEvaluator(fcfg)

        gwo = GWO(
            fitness_fn=evaluator.evaluate,
            n_wolves=5,
            n_iterations=3,
            lb=fcfg.get_lb(),
            ub=fcfg.get_ub(),
            seed=42,
        )

        result = gwo.run()

        assert result.best_fitness < FAILURE_PENALTY
        assert len(result.convergence_curve) == 4  # initial + 3 iters
        assert evaluator.eval_count > 0
        assert len(evaluator.eval_history) > 0

    def test_experiment_runner_smoke(self):
        """ExperimentRunner should complete a smoke test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = ExperimentRunner(output_dir=Path(tmpdir))

            # Run baseline
            baseline_results = runner.run_baseline(SMOKE_TEST)
            assert len(baseline_results) == 1
            assert baseline_results[0].success

            # Run GWO
            gwo_result, evaluator = runner.run_gwo_optimisation(
                SMOKE_TEST, n_wolves=5, n_iterations=3, gwo_seed=42,
            )
            assert gwo_result.best_fitness < FAILURE_PENALTY

            # Run optimised
            fcfg = FitnessConfig()
            optimised_results = runner.run_optimised(
                SMOKE_TEST, gwo_result.best_position, fcfg,
            )
            assert len(optimised_results) == 1
            assert optimised_results[0].success

            # Check that files were created
            processed = Path(tmpdir) / "processed"
            assert (processed / "smoke_test_baseline.csv").exists()
            assert (processed / "smoke_test_optimised.csv").exists()

            raw = Path(tmpdir) / "raw"
            assert (raw / "smoke_test_convergence.json").exists()

    def test_optimised_parameters_differ_from_default(self):
        """GWO-found parameters should differ from defaults in most cases."""
        base_cfg = SimulationConfig(n_nodes=10, sim_duration=20.0, n_flows=3, seed=42)
        fcfg = FitnessConfig(base_config=base_cfg)
        evaluator = DSDVFitnessEvaluator(fcfg)

        gwo = GWO(
            fitness_fn=evaluator.evaluate,
            n_wolves=8,
            n_iterations=5,
            lb=fcfg.get_lb(),
            ub=fcfg.get_ub(),
            seed=42,
        )

        result = gwo.run()
        defaults = np.array([15.0, 6.0, 64.0, 30.0])

        # Best position should differ from defaults (GWO explores the space)
        assert not np.allclose(result.best_position, defaults, atol=0.5)


class TestReproducibility:
    """Test that the full pipeline is reproducible with fixed seeds."""

    def test_full_pipeline_deterministic(self):
        """Same seeds should produce identical results through the full pipeline."""
        results_pair = []

        for _ in range(2):
            base_cfg = SimulationConfig(n_nodes=8, sim_duration=15.0, n_flows=2, seed=42)
            fcfg = FitnessConfig(base_config=base_cfg)
            evaluator = DSDVFitnessEvaluator(fcfg)

            gwo = GWO(
                fitness_fn=evaluator.evaluate,
                n_wolves=5,
                n_iterations=3,
                lb=fcfg.get_lb(),
                ub=fcfg.get_ub(),
                seed=42,
            )
            result = gwo.run()
            results_pair.append(result)

        assert results_pair[0].best_fitness == pytest.approx(results_pair[1].best_fitness)
        np.testing.assert_array_almost_equal(
            results_pair[0].best_position, results_pair[1].best_position
        )
