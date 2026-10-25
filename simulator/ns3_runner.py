"""
NS-3 Runner — Subprocess interface to NS-3 DSDV simulation
===========================================================

This module runs the NS-3 DSDV scenario (simulator/ns3_dsdv_scenario.cc)
as a subprocess and parses its output.

⚠️ Requires a working NS-3 installation.
   If NS-3 is not available, use PythonMANETSimulator as a fallback.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from simulator.python_model import SimulationConfig, SimulationResult

logger = logging.getLogger(__name__)

# Default NS-3 directory — override with NS3_DIR environment variable
DEFAULT_NS3_DIR = os.environ.get("NS3_DIR", "/usr/local/ns-3")


class NS3Runner:
    """
    Run NS-3 DSDV simulation as a subprocess and parse results.

    The NS-3 scenario outputs metrics as key=value pairs to stdout.
    This runner:
    1. Constructs the NS-3 command line from SimulationConfig
    2. Runs the simulation as a subprocess with a timeout
    3. Parses the output into SimulationResult

    Parameters
    ----------
    ns3_dir : str or Path
        Path to the NS-3 installation directory.
    scenario_name : str
        Name of the compiled NS-3 scenario.
    timeout : int
        Maximum runtime in seconds for a single simulation.
    """

    def __init__(
        self,
        ns3_dir: str | Path = DEFAULT_NS3_DIR,
        scenario_name: str = "scratch/dsdv-manet-gwo",
        timeout: int = 300,
    ):
        self.ns3_dir = Path(ns3_dir)
        self.scenario_name = scenario_name
        self.timeout = timeout

    def is_available(self) -> bool:
        """Check if NS-3 is installed and the scenario is compiled."""
        ns3_script = self.ns3_dir / "ns3"
        if not ns3_script.exists():
            logger.warning("NS-3 not found at %s", self.ns3_dir)
            return False

        # Check if scenario is compiled
        try:
            result = subprocess.run(
                [str(ns3_script), "build"],
                cwd=str(self.ns3_dir),
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            logger.warning("NS-3 availability check failed: %s", e)
            return False

    def run(self, config: SimulationConfig) -> SimulationResult:
        """
        Run an NS-3 simulation with the given configuration.

        Maps SimulationConfig parameters to NS-3 command-line arguments.
        """
        result = SimulationResult(config=config)

        ns3_script = self.ns3_dir / "ns3"
        if not ns3_script.exists():
            result.success = False
            result.error_message = f"NS-3 not found at {self.ns3_dir}"
            return result

        # Build NS-3 command line
        # These map to the NS-3 scenario's command-line arguments
        cmd = [
            str(ns3_script), "run",
            f"{self.scenario_name} --"
            f" --nNodes={config.n_nodes}"
            f" --simDuration={config.sim_duration}"
            f" --areaSize={config.area_size}"
            f" --minSpeed={config.min_speed}"
            f" --maxSpeed={config.max_speed}"
            f" --pauseTime={config.pause_time}"
            f" --nFlows={config.n_flows}"
            f" --packetSize={config.packet_size}"
            f" --packetRate={config.packet_rate}"
            f" --periodicUpdateInterval={config.periodic_update_interval}"
            f" --settlingTime={config.settling_time}"
            f" --maxQueueLen={config.max_queue_len}"
            f" --maxQueueTime={config.max_queue_time}"
            f" --seed={config.seed}"
        ]

        logger.info("Running NS-3: %s", " ".join(cmd))

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.ns3_dir),
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if proc.returncode != 0:
                result.success = False
                result.error_message = f"NS-3 exited with code {proc.returncode}: {proc.stderr[:500]}"
                logger.error("NS-3 failed: %s", result.error_message)
                return result

            # Parse output
            result = self._parse_output(proc.stdout, config)

        except subprocess.TimeoutExpired:
            result.success = False
            result.error_message = f"NS-3 timed out after {self.timeout}s"
            logger.error(result.error_message)
        except FileNotFoundError:
            result.success = False
            result.error_message = f"NS-3 executable not found: {ns3_script}"
            logger.error(result.error_message)
        except OSError as e:
            result.success = False
            result.error_message = f"OS error running NS-3: {e}"
            logger.error(result.error_message)

        return result

    @staticmethod
    def _parse_output(stdout: str, config: SimulationConfig) -> SimulationResult:
        """
        Parse NS-3 scenario output.

        Expected output format (key=value pairs):
            PACKETS_SENT=1000
            PACKETS_RECEIVED=850
            PACKETS_DROPPED=150
            TOTAL_DELAY=12.345
            TOTAL_BYTES_RECEIVED=435200
            ROUTING_UPDATES_SENT=2000
            DATA_PACKETS_FORWARDED=3000
        """
        result = SimulationResult(config=config)
        metrics: dict[str, str] = {}

        for line in stdout.strip().split("\n"):
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, _, value = line.partition("=")
                metrics[key.strip()] = value.strip()

        try:
            result.packets_sent = int(metrics.get("PACKETS_SENT", "0"))
            result.packets_received = int(metrics.get("PACKETS_RECEIVED", "0"))
            result.packets_dropped = int(metrics.get("PACKETS_DROPPED", "0"))
            result.total_delay = float(metrics.get("TOTAL_DELAY", "0.0"))
            result.total_bytes_received = int(metrics.get("TOTAL_BYTES_RECEIVED", "0"))
            result.routing_updates_sent = int(metrics.get("ROUTING_UPDATES_SENT", "0"))
            result.data_packets_forwarded = int(metrics.get("DATA_PACKETS_FORWARDED", "0"))

            result.compute_derived(config.sim_duration)

            # Sanity checks
            if result.packets_sent > 0 and result.pdr > 1.0:
                result.success = False
                result.error_message = f"Invalid PDR > 1.0: {result.pdr}"
            elif result.packets_sent == 0:
                result.success = False
                result.error_message = "No packets sent — simulation may have failed"

        except (ValueError, KeyError) as e:
            result.success = False
            result.error_message = f"Failed to parse NS-3 output: {e}"

        return result
