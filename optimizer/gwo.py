"""
Grey Wolf Optimisation (GWO) Algorithm
======================================

Implementation based on:
    S. Mirjalili, S. M. Mirjalili, A. Lewis,
    "Grey Wolf Optimizer," Advances in Engineering Software, vol. 69, pp. 46-61, 2014.

The algorithm models the social hierarchy and hunting behaviour of grey wolves:
    - Alpha (α): best solution found so far
    - Beta (β):  second-best solution
    - Delta (δ): third-best solution
    - Omega (ω): remaining candidate solutions

Key equations:
    a = 2 - 2 * (t / T)                    # linearly decreases from 2 to 0
    A = 2 * a * r1 - a                      # coefficient vector
    C = 2 * r2                              # coefficient vector
    D = |C * X_leader - X|                  # distance to leader
    X_new = X_leader - A * D               # updated position

Position update combines guidance from α, β, δ:
    X(t+1) = (X1 + X2 + X3) / 3

where X1, X2, X3 are positions guided by α, β, δ respectively.
"""

from __future__ import annotations

import dataclasses
import logging
from typing import Callable, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class GWOResult:
    """Container for GWO optimisation results."""

    best_position: np.ndarray
    best_fitness: float
    convergence_curve: list[float]
    n_iterations: int
    n_function_evals: int
    alpha_history: list[np.ndarray]
    all_final_positions: np.ndarray
    all_final_fitness: np.ndarray


class GWO:
    """
    Grey Wolf Optimiser.

    Parameters
    ----------
    fitness_fn : callable
        Objective function to *minimise*. Signature: f(x: np.ndarray) -> float.
    n_wolves : int
        Population size (number of search agents).
    n_iterations : int
        Maximum number of iterations.
    lb : np.ndarray or list
        Lower bounds for each dimension.
    ub : np.ndarray or list
        Upper bounds for each dimension.
    seed : int or None
        Random seed for reproducibility.
    """

    def __init__(
        self,
        fitness_fn: Callable[[np.ndarray], float],
        n_wolves: int,
        n_iterations: int,
        lb: np.ndarray | list,
        ub: np.ndarray | list,
        seed: Optional[int] = None,
    ):
        self.fitness_fn = fitness_fn
        self.n_wolves = n_wolves
        self.n_iterations = n_iterations
        self.lb = np.asarray(lb, dtype=np.float64)
        self.ub = np.asarray(ub, dtype=np.float64)
        self.dim = len(self.lb)
        self.seed = seed

        if len(self.lb) != len(self.ub):
            raise ValueError("lb and ub must have the same length.")
        if np.any(self.lb >= self.ub):
            raise ValueError("Each lb[i] must be strictly less than ub[i].")
        if self.n_wolves < 4:
            raise ValueError("Need at least 4 wolves (1 alpha, 1 beta, 1 delta, ≥1 omega).")
        if self.n_iterations < 1:
            raise ValueError("Need at least 1 iteration.")

    def _clip(self, x: np.ndarray) -> np.ndarray:
        """Clip positions to stay within bounds."""
        return np.clip(x, self.lb, self.ub)

    def _init_population(self, rng: np.random.Generator) -> np.ndarray:
        """Initialise wolf positions uniformly within bounds."""
        return rng.uniform(self.lb, self.ub, size=(self.n_wolves, self.dim))

    @staticmethod
    def compute_a(t: int, T: int) -> float:
        """
        Compute the linearly decreasing parameter 'a'.

        a = 2 - 2 * (t / T)

        Controls the transition from exploration (a > 1) to exploitation (a < 1).
        """
        return 2.0 - 2.0 * (t / T)

    @staticmethod
    def compute_A(a: float, r1: np.ndarray) -> np.ndarray:
        """Compute coefficient vector A = 2 * a * r1 - a."""
        return 2.0 * a * r1 - a

    @staticmethod
    def compute_C(r2: np.ndarray) -> np.ndarray:
        """Compute coefficient vector C = 2 * r2."""
        return 2.0 * r2

    @staticmethod
    def update_position(
        x: np.ndarray,
        x_alpha: np.ndarray,
        x_beta: np.ndarray,
        x_delta: np.ndarray,
        a: float,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """
        Compute the new position for a wolf guided by alpha, beta, delta.

        For each leader L in {alpha, beta, delta}:
            A_L = compute_A(a, r1)
            C_L = compute_C(r2)
            D_L = |C_L * X_L - X|
            X_L_new = X_L - A_L * D_L

        X_new = (X_alpha_new + X_beta_new + X_delta_new) / 3
        """
        dim = len(x)

        # Alpha guidance
        r1 = rng.random(dim)
        r2 = rng.random(dim)
        A1 = GWO.compute_A(a, r1)
        C1 = GWO.compute_C(r2)
        D_alpha = np.abs(C1 * x_alpha - x)
        X1 = x_alpha - A1 * D_alpha

        # Beta guidance
        r1 = rng.random(dim)
        r2 = rng.random(dim)
        A2 = GWO.compute_A(a, r1)
        C2 = GWO.compute_C(r2)
        D_beta = np.abs(C2 * x_beta - x)
        X2 = x_beta - A2 * D_beta

        # Delta guidance
        r1 = rng.random(dim)
        r2 = rng.random(dim)
        A3 = GWO.compute_A(a, r1)
        C3 = GWO.compute_C(r2)
        D_delta = np.abs(C3 * x_delta - x)
        X3 = x_delta - A3 * D_delta

        return (X1 + X2 + X3) / 3.0

    def run(self) -> GWOResult:
        """
        Execute the GWO optimisation loop.

        Returns
        -------
        GWOResult
            Contains best position, best fitness, convergence curve, etc.
        """
        rng = np.random.default_rng(self.seed)

        # Initialise population
        positions = self._init_population(rng)
        fitness = np.array([self.fitness_fn(positions[i]) for i in range(self.n_wolves)])
        n_evals = self.n_wolves

        # Sort to find alpha, beta, delta
        sorted_idx = np.argsort(fitness)
        alpha_pos = positions[sorted_idx[0]].copy()
        alpha_fit = fitness[sorted_idx[0]]
        beta_pos = positions[sorted_idx[1]].copy()
        beta_fit = fitness[sorted_idx[1]]
        delta_pos = positions[sorted_idx[2]].copy()
        delta_fit = fitness[sorted_idx[2]]

        convergence = [float(alpha_fit)]
        alpha_history = [alpha_pos.copy()]

        logger.info(
            "GWO started: %d wolves, %d dims, %d iters",
            self.n_wolves, self.dim, self.n_iterations,
        )

        for t in range(self.n_iterations):
            a = self.compute_a(t, self.n_iterations)

            for i in range(self.n_wolves):
                new_pos = self.update_position(
                    positions[i], alpha_pos, beta_pos, delta_pos, a, rng
                )
                positions[i] = self._clip(new_pos)

                fit = self.fitness_fn(positions[i])
                n_evals += 1
                fitness[i] = fit

            # Update hierarchy
            sorted_idx = np.argsort(fitness)

            if fitness[sorted_idx[0]] < alpha_fit:
                alpha_pos = positions[sorted_idx[0]].copy()
                alpha_fit = fitness[sorted_idx[0]]
            if fitness[sorted_idx[1]] < beta_fit:
                beta_pos = positions[sorted_idx[1]].copy()
                beta_fit = fitness[sorted_idx[1]]
            if fitness[sorted_idx[2]] < delta_fit:
                delta_pos = positions[sorted_idx[2]].copy()
                delta_fit = fitness[sorted_idx[2]]

            convergence.append(float(alpha_fit))
            alpha_history.append(alpha_pos.copy())

            if (t + 1) % max(1, self.n_iterations // 10) == 0:
                logger.info("Iter %d/%d: best_fitness=%.6e, a=%.4f",
                            t + 1, self.n_iterations, alpha_fit, a)

        logger.info("GWO finished: best_fitness=%.6e", alpha_fit)

        return GWOResult(
            best_position=alpha_pos.copy(),
            best_fitness=float(alpha_fit),
            convergence_curve=convergence,
            n_iterations=self.n_iterations,
            n_function_evals=n_evals,
            alpha_history=alpha_history,
            all_final_positions=positions.copy(),
            all_final_fitness=fitness.copy(),
        )
