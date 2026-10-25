"""
Unit Tests for GWO Algorithm
=============================

Tests cover:
1. GWO equation correctness (compute_a, compute_A, compute_C)
2. Bounds handling (clipping)
3. Population initialisation
4. Convergence on benchmark functions
5. Deterministic behaviour under fixed seed
6. Input validation
"""

import numpy as np
import pytest

from optimizer.gwo import GWO, GWOResult
from optimizer.benchmarks import sphere, rastrigin, rosenbrock, ackley


class TestGWOEquations:
    """Test individual GWO equations."""

    def test_compute_a_start(self):
        """a should be 2.0 at iteration 0."""
        assert GWO.compute_a(0, 100) == pytest.approx(2.0)

    def test_compute_a_end(self):
        """a should be 0.0 at the final iteration."""
        assert GWO.compute_a(100, 100) == pytest.approx(0.0)

    def test_compute_a_midpoint(self):
        """a should be 1.0 at the midpoint."""
        assert GWO.compute_a(50, 100) == pytest.approx(1.0)

    def test_compute_a_quarter(self):
        """a should be 1.5 at quarter point."""
        assert GWO.compute_a(25, 100) == pytest.approx(1.5)

    def test_compute_A_with_r1_zero(self):
        """A should be -a when r1=0."""
        a = 1.5
        r1 = np.array([0.0, 0.0])
        A = GWO.compute_A(a, r1)
        np.testing.assert_array_almost_equal(A, [-1.5, -1.5])

    def test_compute_A_with_r1_one(self):
        """A should be a when r1=1."""
        a = 1.5
        r1 = np.array([1.0, 1.0])
        A = GWO.compute_A(a, r1)
        np.testing.assert_array_almost_equal(A, [1.5, 1.5])

    def test_compute_A_with_r1_half(self):
        """A should be 0 when r1=0.5."""
        a = 2.0
        r1 = np.array([0.5, 0.5])
        A = GWO.compute_A(a, r1)
        np.testing.assert_array_almost_equal(A, [0.0, 0.0])

    def test_compute_C_bounds(self):
        """C = 2*r2, so C ∈ [0, 2]."""
        r2 = np.array([0.0, 0.5, 1.0])
        C = GWO.compute_C(r2)
        np.testing.assert_array_almost_equal(C, [0.0, 1.0, 2.0])

    def test_A_range_with_a2(self):
        """With a=2, A should range in [-2, 2]."""
        a = 2.0
        # Test extremes
        A_min = GWO.compute_A(a, np.array([0.0]))
        A_max = GWO.compute_A(a, np.array([1.0]))
        assert A_min[0] == pytest.approx(-2.0)
        assert A_max[0] == pytest.approx(2.0)


class TestGWOBounds:
    """Test bounds handling."""

    def test_clip_within_bounds(self):
        gwo = GWO(sphere, 5, 10, [-5, -5], [5, 5])
        x = np.array([1.0, -2.0])
        clipped = gwo._clip(x)
        np.testing.assert_array_equal(clipped, x)

    def test_clip_exceeds_upper(self):
        gwo = GWO(sphere, 5, 10, [-5, -5], [5, 5])
        x = np.array([10.0, 3.0])
        clipped = gwo._clip(x)
        np.testing.assert_array_equal(clipped, [5.0, 3.0])

    def test_clip_below_lower(self):
        gwo = GWO(sphere, 5, 10, [-5, -5], [5, 5])
        x = np.array([-10.0, 0.0])
        clipped = gwo._clip(x)
        np.testing.assert_array_equal(clipped, [-5.0, 0.0])


class TestGWOInitialisation:
    """Test population initialisation."""

    def test_population_size(self):
        gwo = GWO(sphere, 10, 5, [-5, -5], [5, 5], seed=42)
        rng = np.random.default_rng(42)
        pop = gwo._init_population(rng)
        assert pop.shape == (10, 2)

    def test_population_within_bounds(self):
        gwo = GWO(sphere, 20, 5, [-3, -3, -3], [3, 3, 3], seed=42)
        rng = np.random.default_rng(42)
        pop = gwo._init_population(rng)
        assert np.all(pop >= -3)
        assert np.all(pop <= 3)


class TestGWOConvergence:
    """Test GWO convergence on benchmark functions."""

    def test_sphere_convergence(self):
        """GWO should find near-optimal solution for Sphere."""
        gwo = GWO(sphere, n_wolves=20, n_iterations=50, lb=[-10]*5, ub=[10]*5, seed=42)
        result = gwo.run()
        assert result.best_fitness < 1.0  # should get close to 0
        assert len(result.convergence_curve) == 51  # initial + 50 iterations
        # Convergence curve should be monotonically non-increasing
        for i in range(1, len(result.convergence_curve)):
            assert result.convergence_curve[i] <= result.convergence_curve[i - 1] + 1e-10

    def test_rastrigin_convergence(self):
        """GWO should make progress on Rastrigin (harder, multimodal)."""
        gwo = GWO(rastrigin, n_wolves=30, n_iterations=100, lb=[-5.12]*5, ub=[5.12]*5, seed=42)
        result = gwo.run()
        assert result.best_fitness < 20.0  # reasonable for 5D Rastrigin
        # Should improve from initial random fitness
        assert result.convergence_curve[-1] < result.convergence_curve[0]

    def test_sphere_2d_accuracy(self):
        """2D Sphere should converge very close to origin."""
        gwo = GWO(sphere, n_wolves=15, n_iterations=100, lb=[-100, -100], ub=[100, 100], seed=42)
        result = gwo.run()
        assert result.best_fitness < 0.01
        assert np.allclose(result.best_position, [0, 0], atol=0.1)


class TestGWODeterminism:
    """Test reproducibility with fixed seeds."""

    def test_same_seed_same_result(self):
        """Two runs with the same seed should give identical results."""
        gwo1 = GWO(sphere, n_wolves=10, n_iterations=20, lb=[-5]*3, ub=[5]*3, seed=123)
        gwo2 = GWO(sphere, n_wolves=10, n_iterations=20, lb=[-5]*3, ub=[5]*3, seed=123)

        r1 = gwo1.run()
        r2 = gwo2.run()

        assert r1.best_fitness == pytest.approx(r2.best_fitness)
        np.testing.assert_array_almost_equal(r1.best_position, r2.best_position)
        assert r1.convergence_curve == r2.convergence_curve

    def test_different_seed_different_result(self):
        """Two runs with different seeds should generally give different results."""
        gwo1 = GWO(sphere, n_wolves=10, n_iterations=20, lb=[-5]*3, ub=[5]*3, seed=42)
        gwo2 = GWO(sphere, n_wolves=10, n_iterations=20, lb=[-5]*3, ub=[5]*3, seed=99)

        r1 = gwo1.run()
        r2 = gwo2.run()

        # Not necessarily different fitness, but positions should differ
        assert not np.array_equal(r1.best_position, r2.best_position)


class TestGWOResult:
    """Test GWOResult dataclass."""

    def test_result_fields(self):
        gwo = GWO(sphere, n_wolves=5, n_iterations=5, lb=[-1, -1], ub=[1, 1], seed=42)
        result = gwo.run()

        assert isinstance(result, GWOResult)
        assert isinstance(result.best_position, np.ndarray)
        assert isinstance(result.best_fitness, float)
        assert len(result.convergence_curve) == 6  # initial + 5 iters
        assert result.n_iterations == 5
        assert result.n_function_evals == 5 + 5 * 5  # init + iters * wolves
        assert len(result.alpha_history) == 6
        assert result.all_final_positions.shape == (5, 2)
        assert len(result.all_final_fitness) == 5


class TestGWOValidation:
    """Test input validation."""

    def test_mismatched_bounds(self):
        with pytest.raises(ValueError, match="same length"):
            GWO(sphere, 5, 10, [-1, -1], [1])

    def test_lb_geq_ub(self):
        with pytest.raises(ValueError, match="strictly less"):
            GWO(sphere, 5, 10, [1, 1], [1, 1])

    def test_too_few_wolves(self):
        with pytest.raises(ValueError, match="at least 4"):
            GWO(sphere, 3, 10, [-1], [1])

    def test_zero_iterations(self):
        with pytest.raises(ValueError, match="at least 1"):
            GWO(sphere, 5, 0, [-1], [1])
