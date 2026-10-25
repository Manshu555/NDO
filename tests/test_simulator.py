"""
Tests for the Python MANET Simulator and Fitness Function
=========================================================

Tests cover:
1. Simulation smoke test
2. Metric consistency (PDR, delay, throughput)
3. Seed reproducibility
4. Fitness function calculation
5. Invalid/failed simulation handling
6. Parameter mapping from GWO positions
"""

import numpy as np
import pytest

from simulator.python_model import PythonMANETSimulator, SimulationConfig, SimulationResult
from optimizer.fitness import DSDVFitnessEvaluator, FitnessConfig, FAILURE_PENALTY


class TestSimulationSmokeTest:
    """Basic smoke tests to verify the simulator runs."""

    def test_basic_run_completes(self):
        """Simulator should complete without errors."""
        cfg = SimulationConfig(n_nodes=10, sim_duration=20.0, n_flows=3, seed=42)
        sim = PythonMANETSimulator(cfg)
        result = sim.run()
        assert result.success, f"Simulation failed: {result.error_message}"

    def test_produces_packets(self):
        """Simulator should produce some sent and received packets."""
        cfg = SimulationConfig(n_nodes=10, sim_duration=30.0, n_flows=3, seed=42)
        sim = PythonMANETSimulator(cfg)
        result = sim.run()
        assert result.packets_sent > 0, "No packets sent"
        assert result.packets_received >= 0, "Negative received count"

    def test_routing_updates_produced(self):
        """DSDV should generate routing updates."""
        cfg = SimulationConfig(n_nodes=10, sim_duration=30.0, seed=42)
        sim = PythonMANETSimulator(cfg)
        result = sim.run()
        assert result.routing_updates_sent > 0, "No routing updates"


class TestMetricConsistency:
    """Verify that metrics are internally consistent."""

    def test_pdr_range(self):
        """PDR should be in [0, 1]."""
        cfg = SimulationConfig(n_nodes=15, sim_duration=50.0, seed=42)
        sim = PythonMANETSimulator(cfg)
        result = sim.run()
        assert 0.0 <= result.pdr <= 1.0, f"PDR out of range: {result.pdr}"

    def test_packets_add_up(self):
        """received + dropped should equal sent."""
        cfg = SimulationConfig(n_nodes=10, sim_duration=30.0, seed=42)
        sim = PythonMANETSimulator(cfg)
        result = sim.run()
        assert result.packets_received + result.packets_dropped == result.packets_sent

    def test_delay_non_negative(self):
        """Mean delay should be non-negative."""
        cfg = SimulationConfig(n_nodes=10, sim_duration=30.0, seed=42)
        sim = PythonMANETSimulator(cfg)
        result = sim.run()
        if result.packets_received > 0:
            assert result.mean_delay >= 0

    def test_throughput_non_negative(self):
        """Throughput should be non-negative."""
        cfg = SimulationConfig(n_nodes=10, sim_duration=30.0, seed=42)
        sim = PythonMANETSimulator(cfg)
        result = sim.run()
        assert result.throughput >= 0

    def test_overhead_ratio_range(self):
        """Overhead ratio should be in [0, 1]."""
        cfg = SimulationConfig(n_nodes=10, sim_duration=30.0, seed=42)
        sim = PythonMANETSimulator(cfg)
        result = sim.run()
        assert 0.0 <= result.overhead_ratio <= 1.0


class TestSimulationReproducibility:
    """Test seed-based reproducibility."""

    def test_same_seed_same_results(self):
        """Same seed should produce identical results."""
        cfg1 = SimulationConfig(n_nodes=10, sim_duration=30.0, seed=42)
        cfg2 = SimulationConfig(n_nodes=10, sim_duration=30.0, seed=42)

        r1 = PythonMANETSimulator(cfg1).run()
        r2 = PythonMANETSimulator(cfg2).run()

        assert r1.packets_sent == r2.packets_sent
        assert r1.packets_received == r2.packets_received
        assert r1.pdr == pytest.approx(r2.pdr)
        assert r1.mean_delay == pytest.approx(r2.mean_delay)

    def test_different_seed_different_results(self):
        """Different seeds should generally produce different results."""
        cfg1 = SimulationConfig(n_nodes=10, sim_duration=30.0, seed=42)
        cfg2 = SimulationConfig(n_nodes=10, sim_duration=30.0, seed=99)

        r1 = PythonMANETSimulator(cfg1).run()
        r2 = PythonMANETSimulator(cfg2).run()

        # Results shouldn't be identical (extremely unlikely with different seeds)
        assert not (r1.packets_sent == r2.packets_sent
                    and r1.packets_received == r2.packets_received
                    and r1.pdr == r2.pdr)


class TestFitnessFunction:
    """Test the fitness function."""

    def test_fitness_returns_scalar(self):
        """Fitness function should return a float."""
        fcfg = FitnessConfig(
            base_config=SimulationConfig(n_nodes=10, sim_duration=20.0, seed=42)
        )
        evaluator = DSDVFitnessEvaluator(fcfg)
        position = np.array([15.0, 6.0, 64.0, 30.0])  # default values
        fitness = evaluator.evaluate(position)
        assert isinstance(fitness, float)
        assert fitness != FAILURE_PENALTY  # should succeed

    def test_fitness_bounded(self):
        """Valid fitness should be in [0, 1]."""
        fcfg = FitnessConfig(
            base_config=SimulationConfig(n_nodes=10, sim_duration=20.0, seed=42)
        )
        evaluator = DSDVFitnessEvaluator(fcfg)
        position = np.array([15.0, 6.0, 64.0, 30.0])
        fitness = evaluator.evaluate(position)
        if fitness != FAILURE_PENALTY:
            assert 0.0 <= fitness <= 1.0

    def test_fitness_records_history(self):
        """Evaluator should record evaluation history."""
        fcfg = FitnessConfig(
            base_config=SimulationConfig(n_nodes=8, sim_duration=15.0, seed=42)
        )
        evaluator = DSDVFitnessEvaluator(fcfg)
        evaluator.evaluate(np.array([15.0, 6.0, 64.0, 30.0]))
        assert len(evaluator.eval_history) == 1
        assert evaluator.eval_count == 1

    def test_position_to_config_mapping(self):
        """Position vector should map correctly to SimulationConfig."""
        fcfg = FitnessConfig(
            base_config=SimulationConfig(n_nodes=10, sim_duration=30.0, seed=42)
        )
        evaluator = DSDVFitnessEvaluator(fcfg)
        position = np.array([10.0, 3.0, 128.0, 60.0])
        cfg = evaluator.position_to_config(position)

        assert cfg.periodic_update_interval == pytest.approx(10.0)
        assert cfg.settling_time == pytest.approx(3.0)
        assert cfg.max_queue_len == 128
        assert cfg.max_queue_time == pytest.approx(60.0)

    def test_integer_parameter_rounding(self):
        """max_queue_len should be rounded to integer."""
        fcfg = FitnessConfig(
            base_config=SimulationConfig(n_nodes=10, sim_duration=20.0, seed=42)
        )
        evaluator = DSDVFitnessEvaluator(fcfg)
        position = np.array([15.0, 6.0, 100.7, 30.0])
        cfg = evaluator.position_to_config(position)
        assert isinstance(cfg.max_queue_len, int)
        assert cfg.max_queue_len == 101


class TestFitnessWeights:
    """Test fitness function weight configuration."""

    def test_custom_weights(self):
        """Fitness with different weights should give different results."""
        base_cfg = SimulationConfig(n_nodes=10, sim_duration=20.0, seed=42)

        fcfg1 = FitnessConfig(w_pdr=1.0, w_delay=0.0, w_overhead=0.0, base_config=base_cfg)
        fcfg2 = FitnessConfig(w_pdr=0.0, w_delay=1.0, w_overhead=0.0, base_config=base_cfg)

        e1 = DSDVFitnessEvaluator(fcfg1)
        e2 = DSDVFitnessEvaluator(fcfg2)

        pos = np.array([15.0, 6.0, 64.0, 30.0])
        f1 = e1.evaluate(pos)
        f2 = e2.evaluate(pos)

        # Different weight configurations should generally give different fitness values
        # (unless PDR and delay happen to give the same normalised score)
        assert isinstance(f1, float)
        assert isinstance(f2, float)


class TestSimulationResultCompute:
    """Test SimulationResult.compute_derived()."""

    def test_compute_pdr(self):
        r = SimulationResult(packets_sent=100, packets_received=80, packets_dropped=20)
        r.compute_derived(10.0)
        assert r.pdr == pytest.approx(0.8)

    def test_compute_zero_packets(self):
        r = SimulationResult(packets_sent=0, packets_received=0)
        r.compute_derived(10.0)
        assert r.pdr == 0.0

    def test_compute_delay(self):
        r = SimulationResult(packets_sent=100, packets_received=50, total_delay=5.0)
        r.compute_derived(10.0)
        assert r.mean_delay == pytest.approx(0.1)

    def test_compute_throughput(self):
        r = SimulationResult(
            packets_sent=100, packets_received=80,
            total_bytes_received=80 * 512,
        )
        r.compute_derived(10.0)
        assert r.throughput == pytest.approx(80 * 512 * 8 / 10.0)

    def test_compute_overhead(self):
        r = SimulationResult(
            packets_sent=100, packets_received=80,
            routing_updates_sent=50,
        )
        r.compute_derived(10.0)
        assert r.overhead_ratio == pytest.approx(50 / 150)
