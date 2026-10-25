"""
Statistical Analysis and Plotting
===================================

Generates publication-quality plots and statistical comparisons
for the DSDV-GWO optimisation experiments.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)

# Publication-quality plot settings
plt.rcParams.update({
    "figure.figsize": (8, 5),
    "figure.dpi": 150,
    "font.size": 11,
    "font.family": "serif",
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "legend.fontsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "lines.linewidth": 1.5,
    "lines.markersize": 6,
    "grid.alpha": 0.3,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
})


class ResultAnalyser:
    """
    Analyse and visualise experiment results.

    Parameters
    ----------
    results_dir : Path
        Base results directory (containing raw/ and processed/).
    plots_dir : Path
        Where to save plots.
    """

    def __init__(self, results_dir: Path, plots_dir: Optional[Path] = None):
        self.results_dir = Path(results_dir)
        self.processed_dir = self.results_dir / "processed"
        self.raw_dir = self.results_dir / "raw"
        self.plots_dir = plots_dir or (self.results_dir / "plots")
        self.plots_dir.mkdir(parents=True, exist_ok=True)

    def load_results(self, scenario_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Load baseline and optimised results for a scenario."""
        baseline_path = self.processed_dir / f"{scenario_name}_baseline.csv"
        optimised_path = self.processed_dir / f"{scenario_name}_optimised.csv"

        baseline_df = pd.read_csv(baseline_path) if baseline_path.exists() else pd.DataFrame()
        optimised_df = pd.read_csv(optimised_path) if optimised_path.exists() else pd.DataFrame()

        return baseline_df, optimised_df

    def compute_statistics(self, scenario_name: str) -> dict:
        """Compute summary statistics for baseline vs optimised."""
        baseline_df, optimised_df = self.load_results(scenario_name)

        metrics = ["pdr", "mean_delay", "throughput", "overhead_ratio"]
        summary = {}

        for metric in metrics:
            entry = {}
            if not baseline_df.empty and metric in baseline_df.columns:
                bvals = baseline_df[metric].dropna().values
                entry["baseline_mean"] = float(np.mean(bvals))
                entry["baseline_std"] = float(np.std(bvals, ddof=1)) if len(bvals) > 1 else 0.0
                entry["baseline_n"] = len(bvals)

                if len(bvals) > 1:
                    ci = stats.t.interval(
                        0.95, df=len(bvals) - 1,
                        loc=np.mean(bvals),
                        scale=stats.sem(bvals)
                    )
                    entry["baseline_ci95"] = [float(ci[0]), float(ci[1])]

            if not optimised_df.empty and metric in optimised_df.columns:
                ovals = optimised_df[metric].dropna().values
                entry["optimised_mean"] = float(np.mean(ovals))
                entry["optimised_std"] = float(np.std(ovals, ddof=1)) if len(ovals) > 1 else 0.0
                entry["optimised_n"] = len(ovals)

                if len(ovals) > 1:
                    ci = stats.t.interval(
                        0.95, df=len(ovals) - 1,
                        loc=np.mean(ovals),
                        scale=stats.sem(ovals)
                    )
                    entry["optimised_ci95"] = [float(ci[0]), float(ci[1])]

            # Statistical test (independent t-test)
            if ("baseline_mean" in entry and "optimised_mean" in entry
                    and entry.get("baseline_n", 0) >= 2 and entry.get("optimised_n", 0) >= 2):
                bv = baseline_df[metric].dropna().values
                ov = optimised_df[metric].dropna().values
                t_stat, p_value = stats.ttest_ind(bv, ov, equal_var=False)
                entry["t_statistic"] = float(t_stat)
                entry["p_value"] = float(p_value)
                entry["significant_005"] = p_value < 0.05

                # Improvement percentage
                if entry["baseline_mean"] != 0:
                    if metric in ("mean_delay", "overhead_ratio"):
                        # Lower is better
                        entry["improvement_pct"] = (
                            (entry["baseline_mean"] - entry["optimised_mean"])
                            / entry["baseline_mean"] * 100
                        )
                    else:
                        # Higher is better (PDR, throughput)
                        entry["improvement_pct"] = (
                            (entry["optimised_mean"] - entry["baseline_mean"])
                            / entry["baseline_mean"] * 100
                        )

            summary[metric] = entry

        return summary

    def plot_convergence(self, scenario_name: str):
        """Plot GWO convergence curve."""
        conv_path = self.raw_dir / f"{scenario_name}_convergence.json"
        if not conv_path.exists():
            logger.warning("No convergence data for %s", scenario_name)
            return

        with open(conv_path) as f:
            data = json.load(f)

        curve = data["convergence_curve"]

        fig, ax = plt.subplots()
        ax.plot(range(len(curve)), curve, "b-o", markersize=4, label="Best fitness")
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Best Fitness (lower is better)")
        ax.set_title(f"GWO Convergence — {scenario_name}")
        ax.legend()
        ax.grid(True, alpha=0.3)

        filepath = self.plots_dir / f"{scenario_name}_convergence.png"
        fig.savefig(filepath)
        plt.close(fig)
        logger.info("Convergence plot saved to %s", filepath)

    def plot_comparison_bars(self, scenario_name: str):
        """Plot baseline vs optimised comparison bar charts."""
        baseline_df, optimised_df = self.load_results(scenario_name)

        if baseline_df.empty or optimised_df.empty:
            logger.warning("Missing data for comparison plot: %s", scenario_name)
            return

        metrics = {
            "pdr": ("Packet Delivery Ratio", "PDR"),
            "mean_delay": ("Mean End-to-End Delay (s)", "Delay (s)"),
            "throughput": ("Throughput (bps)", "Throughput (bps)"),
            "overhead_ratio": ("Routing Overhead Ratio", "Overhead Ratio"),
        }

        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        axes = axes.flatten()

        for idx, (metric, (title, ylabel)) in enumerate(metrics.items()):
            ax = axes[idx]

            b_mean = baseline_df[metric].mean()
            b_std = baseline_df[metric].std() if len(baseline_df) > 1 else 0
            o_mean = optimised_df[metric].mean()
            o_std = optimised_df[metric].std() if len(optimised_df) > 1 else 0

            x = np.arange(2)
            bars = ax.bar(x, [b_mean, o_mean], yerr=[b_std, o_std],
                         capsize=5, color=["#2196F3", "#4CAF50"], edgecolor="black", linewidth=0.5)

            ax.set_xticks(x)
            ax.set_xticklabels(["Default DSDV", "GWO-Optimised"])
            ax.set_ylabel(ylabel)
            ax.set_title(title)
            ax.grid(True, axis="y", alpha=0.3)

            # Add value labels on bars
            for bar, mean, std in zip(bars, [b_mean, o_mean], [b_std, o_std]):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + std + 0.01 * abs(b_mean),
                        f"{mean:.4f}", ha="center", va="bottom", fontsize=9)

        fig.suptitle(f"DSDV Performance: Default vs GWO-Optimised — {scenario_name}",
                     fontsize=14, fontweight="bold")
        fig.tight_layout(rect=[0, 0, 1, 0.95])

        filepath = self.plots_dir / f"{scenario_name}_comparison.png"
        fig.savefig(filepath)
        plt.close(fig)
        logger.info("Comparison plot saved to %s", filepath)

    def plot_per_seed_comparison(self, scenario_name: str):
        """Plot per-seed PDR comparison."""
        baseline_df, optimised_df = self.load_results(scenario_name)
        if baseline_df.empty or optimised_df.empty:
            return

        # Merge on seed for paired comparison
        merged = pd.merge(
            baseline_df[["seed", "pdr"]], optimised_df[["seed", "pdr"]],
            on="seed", suffixes=("_baseline", "_optimised")
        )

        if merged.empty:
            return

        fig, ax = plt.subplots(figsize=(8, 5))
        x = np.arange(len(merged))
        width = 0.35

        ax.bar(x - width / 2, merged["pdr_baseline"], width, label="Default DSDV",
               color="#2196F3", edgecolor="black", linewidth=0.5)
        ax.bar(x + width / 2, merged["pdr_optimised"], width, label="GWO-Optimised",
               color="#4CAF50", edgecolor="black", linewidth=0.5)

        ax.set_xlabel("Random Seed")
        ax.set_ylabel("Packet Delivery Ratio")
        ax.set_title(f"Per-Seed PDR Comparison — {scenario_name}")
        ax.set_xticks(x)
        ax.set_xticklabels(merged["seed"].astype(str))
        ax.legend()
        ax.grid(True, axis="y", alpha=0.3)
        ax.set_ylim(0, 1.05)

        filepath = self.plots_dir / f"{scenario_name}_per_seed_pdr.png"
        fig.savefig(filepath)
        plt.close(fig)
        logger.info("Per-seed plot saved to %s", filepath)

    def generate_summary_table(self, scenario_names: list[str]) -> pd.DataFrame:
        """Generate a summary table across all scenarios."""
        rows = []
        for name in scenario_names:
            summary = self.compute_statistics(name)
            for metric, data in summary.items():
                row = {"scenario": name, "metric": metric}
                row.update(data)
                rows.append(row)

        df = pd.DataFrame(rows)
        filepath = self.processed_dir / "summary_statistics.csv"
        df.to_csv(filepath, index=False)
        logger.info("Summary table saved to %s", filepath)
        return df

    def plot_benchmark_validation(self, sphere_curve: list[float],
                                  rastrigin_curve: list[float]):
        """Plot GWO convergence on benchmark functions."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        ax1.semilogy(range(len(sphere_curve)), sphere_curve, "b-o", markersize=3)
        ax1.set_xlabel("Iteration")
        ax1.set_ylabel("Best Fitness (log scale)")
        ax1.set_title("GWO on Sphere Function")
        ax1.grid(True, alpha=0.3)

        ax2.semilogy(range(len(rastrigin_curve)), rastrigin_curve, "r-s", markersize=3)
        ax2.set_xlabel("Iteration")
        ax2.set_ylabel("Best Fitness (log scale)")
        ax2.set_title("GWO on Rastrigin Function")
        ax2.grid(True, alpha=0.3)

        fig.suptitle("GWO Validation on Benchmark Functions", fontsize=14, fontweight="bold")
        fig.tight_layout(rect=[0, 0, 1, 0.95])

        filepath = self.plots_dir / "benchmark_validation.png"
        fig.savefig(filepath)
        plt.close(fig)
        logger.info("Benchmark validation plot saved to %s", filepath)
