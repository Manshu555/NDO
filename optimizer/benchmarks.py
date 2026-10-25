"""
Benchmark functions for validating the GWO implementation.

These are standard test functions from the optimisation literature.
All are minimisation problems with known global minima at the origin.
"""

from __future__ import annotations

import numpy as np


def sphere(x: np.ndarray) -> float:
    """
    Sphere function: f(x) = Σ x_i²

    - Unimodal, convex, separable
    - Global minimum: f(0, ..., 0) = 0
    - Typical search domain: [-100, 100]^n
    """
    return float(np.sum(x ** 2))


def rastrigin(x: np.ndarray) -> float:
    """
    Rastrigin function: f(x) = 10n + Σ [x_i² - 10 * cos(2π * x_i)]

    - Multimodal (many local minima), non-convex
    - Global minimum: f(0, ..., 0) = 0
    - Typical search domain: [-5.12, 5.12]^n
    """
    n = len(x)
    return float(10.0 * n + np.sum(x ** 2 - 10.0 * np.cos(2.0 * np.pi * x)))


def rosenbrock(x: np.ndarray) -> float:
    """
    Rosenbrock function: f(x) = Σ [100(x_{i+1} - x_i²)² + (x_i - 1)²]

    - Unimodal (for n ≤ 3), valley-shaped
    - Global minimum: f(1, ..., 1) = 0
    - Typical search domain: [-30, 30]^n
    """
    return float(np.sum(100.0 * (x[1:] - x[:-1] ** 2) ** 2 + (x[:-1] - 1.0) ** 2))


def ackley(x: np.ndarray) -> float:
    """
    Ackley function.

    - Multimodal with one deep global minimum
    - Global minimum: f(0, ..., 0) = 0
    - Typical search domain: [-32, 32]^n
    """
    n = len(x)
    sum1 = np.sum(x ** 2)
    sum2 = np.sum(np.cos(2.0 * np.pi * x))
    return float(
        -20.0 * np.exp(-0.2 * np.sqrt(sum1 / n))
        - np.exp(sum2 / n)
        + 20.0
        + np.e
    )
