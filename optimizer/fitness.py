"""
Fitness Function for GWO-DSDV Optimisation
==========================================

Combines PDR, delay, and routing overhead into a single scalar fitness value
for minimisation. The fitness function calls the simulation backend
(Python model or NS-3) with a given parameter configuration.

Fitness = w_pdr * (1 - PDR) + w_delay * norm_delay + w_overhead * norm_overhead

where:
    - (1 - PDR) is the packet loss rate (lower is better → minimise)
    - norm_delay is the normalised mean end-to-end delay
    - norm_overhead is the normalised routing overhead ratio
    - w_pdr, w_delay, w_overhead are configurable weights

All components are in [0, 1], so fitness ∈ [0, 1] for valid simulations.
"""

from __future__ import annotations

import dataclasses
import logging
from typing import Optional

import numpy as np

from simulator.python_model import PythonMANETSimulator, SimulationConfig, SimulationResult

logger = logging.getLogger(__name__)

# Penalty for failed/invalid simulations — must be worse than any valid fitness
FAILURE_PENALTY = 10.0


@dataclasses.dataclass
class FitnessConfig:
    """Configuration for the fitness function."""

    # Weights (must sum to a positive number; will be normalised internally)
    w_pdr: float = 0.5          # weight for packet delivery ratio
    w_delay: float = 0.3        # weight for end-to-end delay
    w_overhead: float = 0.2     # weight for routing overhead

    # Normalisation bounds for delay (seconds)
    delay_min: float = 0.0
    delay_max: float = 1.0      # delays above this are clipped to 1.0

    # Base simulation config (scenario parameters not being optimised)
    base_config: Optional[SimulationConfig] = None

    # Parameter bounds for GWO search space
    # Format: [(name, lower_bound, upper_bound), ...]
    # These correspond to DSDV parameters that can actually be tuned
    param_bounds: Optional[list[tuple[str, float, float]]] = None

    def __post_init__(self):
        if self.base_config is None:
            self.base_config = SimulationConfig()
        if self.param_bounds is None:
            self.param_bounds = [
                # Parameter name, lower bound, upper bound
                # PeriodicUpdateInterval: time between full DSDV table broadcasts
                #   NS-3 default: 15s, reasonable range: 5-30s
                #   Lower = more overhead but fresher routes
                #   Higher = less overhead but staler routes
                ("periodic_update_interval", 5.0, 30.0),

                # SettlingTime: delay before accepting route changes
                #   NS-3 default: 6s, reasonable range: 1-15s
                #   Lower = faster convergence but risk of route oscillation
                #   Higher = more stable but slower adaptation
                ("settling_time", 1.0, 15.0),

                # MaxQueueLen: max packets in DSDV send buffer
                #   Reasonable range: 16-256 packets
                ("max_queue_len", 16.0, 256.0),

                # MaxQueueTime: max time a packet waits in send buffer
                #   Reasonable range: 5-120 seconds
                ("max_queue_time", 5.0, 120.0),
            ]

    def get_lb(self) -> np.ndarray:
        """Get lower bounds for GWO."""
        return np.array([p[1] for p in self.param_bounds])

    def get_ub(self) -> np.ndarray:
        """Get upper bounds for GWO."""
        return np.array([p[2] for p in self.param_bounds])

    def get_param_names(self) -> list[str]:
        """Get parameter names."""
        return [p[0] for p in self.param_bounds]


class DSDVFitnessEvaluator:
    """
    Evaluates DSDV parameter configurations by running simulations.

    Each call to evaluate() takes a GWO position vector, maps it to
    DSDV parameters, runs a simulation, and returns a scalar fitness.
    """

    def __init__(self, fitness_config: FitnessConfig, use_ns3: bool = False):
        self.config = fitness_config
        self.use_ns3 = use_ns3
        self.eval_count = 0
        self.eval_history: list[dict] = []

    def position_to_config(self, position: np.ndarray) -> SimulationConfig:
        """
        Map a GWO position vector to a SimulationConfig.

        The position vector has one element per tunable parameter.
        """
        cfg = dataclasses.replace(self.config.base_config)

        for i, (name, lb, ub) in enumerate(self.config.param_bounds):
            value = float(np.clip(position[i], lb, ub))

            # Integer parameters need rounding
            if name == "max_queue_len":
                value = int(round(value))

            setattr(cfg, name, value)

        return cfg

    def evaluate(self, position: np.ndarray) -> float:
        """
        Evaluate fitness for a GWO position vector.

        Parameters
        ----------
        position : np.ndarray
            Parameter values from GWO.

        Returns
        -------
        float
            Fitness value (lower is better). FAILURE_PENALTY for failed runs.
        """
        self.eval_count += 1
        sim_config = self.position_to_config(position)

        # Run simulation
        if self.use_ns3:
            from simulator.ns3_runner import NS3Runner
            runner = NS3Runner()
            result = runner.run(sim_config)
        else:
            sim = PythonMANETSimulator(sim_config)
            result = sim.run()

        # Handle failed simulations
        if not result.success:
            logger.warning(
                "Eval #%d FAILED: %s (params=%s)",
                self.eval_count, result.error_message, position
            )
            self._record_eval(position, FAILURE_PENALTY, result, success=False)
            return FAILURE_PENALTY

        # Validate metrics
        if result.packets_sent == 0:
            logger.warning("Eval #%d: no packets sent", self.eval_count)
            self._record_eval(position, FAILURE_PENALTY, result, success=False)
            return FAILURE_PENALTY

        if result.pdr > 1.0 or result.pdr < 0.0:
            logger.warning("Eval #%d: invalid PDR=%.4f", self.eval_count, result.pdr)
            self._record_eval(position, FAILURE_PENALTY, result, success=False)
            return FAILURE_PENALTY

        # Compute fitness components
        pdr_component = 1.0 - result.pdr  # lower PDR → higher penalty

        delay_normalised = np.clip(
            (result.mean_delay - self.config.delay_min) /
            max(self.config.delay_max - self.config.delay_min, 1e-10),
            0.0, 1.0
        )

        overhead_component = min(result.overhead_ratio, 1.0)

        # Weighted sum (all components in [0, 1])
        total_weight = self.config.w_pdr + self.config.w_delay + self.config.w_overhead
        fitness = (
            self.config.w_pdr * pdr_component +
            self.config.w_delay * delay_normalised +
            self.config.w_overhead * overhead_component
        ) / total_weight

        self._record_eval(position, fitness, result, success=True)

        if self.eval_count % 10 == 0:
            logger.info(
                "Eval #%d: fitness=%.4f (PDR=%.3f, delay=%.4fs, overhead=%.3f)",
                self.eval_count, fitness, result.pdr, result.mean_delay, result.overhead_ratio
            )

        return float(fitness)

    def _record_eval(self, position: np.ndarray, fitness: float,
                     result: SimulationResult, success: bool):
        """Record evaluation for later analysis."""
        self.eval_history.append({
            "eval_num": self.eval_count,
            "position": position.tolist(),
            "fitness": fitness,
            "success": success,
            "pdr": result.pdr,
            "mean_delay": result.mean_delay,
            "throughput": result.throughput,
            "overhead_ratio": result.overhead_ratio,
            "packets_sent": result.packets_sent,
            "packets_received": result.packets_received,
        })
