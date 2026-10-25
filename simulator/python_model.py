"""
Python-based MANET Simulation Model
====================================

⚠️  IMPORTANT DISCLAIMER ⚠️
This is a **simplified Python model** of a DSDV MANET scenario.
It is NOT an NS-3 packet-level simulation.

This model approximates:
- Random waypoint mobility
- Wireless link quality based on distance (free-space path loss)
- DSDV-like periodic routing table updates
- UDP packet forwarding with hop-by-hop delay
- Packet drops due to: out-of-range, no route, queue overflow

Purpose: Provide a functional simulation backend so that the GWO optimiser
can be tested and demonstrated. For publication-quality results, use the
NS-3 C++ scenario provided in simulator/ns3_dsdv_scenario.cc.
"""

from __future__ import annotations

import dataclasses
import logging
import math
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SimulationConfig:
    """Configuration for a MANET simulation run."""

    # Scenario parameters
    n_nodes: int = 20
    area_size: float = 500.0         # metres (square area)
    sim_duration: float = 100.0      # seconds
    seed: int = 42

    # Mobility parameters
    min_speed: float = 1.0           # m/s
    max_speed: float = 10.0          # m/s
    pause_time: float = 2.0          # seconds at each waypoint

    # Wireless parameters
    tx_range: float = 150.0          # metres (communication range)
    bandwidth: float = 2e6           # bits/sec (2 Mbps)
    propagation_delay_per_hop: float = 0.002  # seconds (2 ms per hop)

    # Traffic parameters
    n_flows: int = 5                 # number of UDP flows
    packet_size: int = 512           # bytes
    packet_rate: float = 4.0         # packets/sec per flow

    # DSDV parameters (these are what GWO will tune)
    periodic_update_interval: float = 15.0   # seconds (NS-3 default)
    settling_time: float = 6.0               # seconds (NS-3 default)
    max_queue_len: int = 64                  # max packets in send buffer
    max_queue_time: float = 30.0             # max seconds in send buffer

    # Simulation fidelity
    time_step: float = 0.1           # seconds per simulation tick


@dataclasses.dataclass
class SimulationResult:
    """Results from a simulation run."""

    # Primary metrics
    packets_sent: int = 0
    packets_received: int = 0
    packets_dropped: int = 0
    total_delay: float = 0.0          # sum of all end-to-end delays (seconds)
    total_bytes_received: int = 0
    routing_updates_sent: int = 0     # total routing control packets
    data_packets_forwarded: int = 0   # intermediate hops

    # Derived metrics
    pdr: float = 0.0                  # Packet Delivery Ratio
    mean_delay: float = 0.0           # mean end-to-end delay (seconds)
    throughput: float = 0.0           # bits/sec
    overhead_ratio: float = 0.0       # routing_updates / (data_sent + routing_updates)

    # Status
    success: bool = True
    error_message: str = ""
    config: Optional[SimulationConfig] = None

    def compute_derived(self, duration: float):
        """Compute derived metrics from raw counters."""
        if self.packets_sent > 0:
            self.pdr = self.packets_received / self.packets_sent
        else:
            self.pdr = 0.0

        if self.packets_received > 0:
            self.mean_delay = self.total_delay / self.packets_received
        else:
            self.mean_delay = float("inf")

        if duration > 0:
            self.throughput = (self.total_bytes_received * 8) / duration
        else:
            self.throughput = 0.0

        total_control_and_data = self.packets_sent + self.routing_updates_sent
        if total_control_and_data > 0:
            self.overhead_ratio = self.routing_updates_sent / total_control_and_data
        else:
            self.overhead_ratio = 0.0


class Node:
    """A mobile node in the MANET."""

    def __init__(self, node_id: int, x: float, y: float, rng: np.random.Generator,
                 area_size: float, min_speed: float, max_speed: float, pause_time: float):
        self.node_id = node_id
        self.x = x
        self.y = y
        self.rng = rng
        self.area_size = area_size
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.pause_time = pause_time

        # Mobility state
        self.target_x = x
        self.target_y = y
        self.speed = 0.0
        self.pause_remaining = 0.0
        self._pick_new_waypoint()

        # Routing table: dest_id -> (next_hop, hop_count, seq_num, last_update_time)
        self.routing_table: dict[int, tuple[int, int, int, float]] = {}
        self.seq_num = 0

        # Packet queue: list of (dest, packet_id, enqueue_time, send_time_origin)
        self.packet_queue: list[tuple[int, int, float, float]] = []

    def _pick_new_waypoint(self):
        """Select a new random waypoint and speed."""
        self.target_x = self.rng.uniform(0, self.area_size)
        self.target_y = self.rng.uniform(0, self.area_size)
        self.speed = self.rng.uniform(self.min_speed, self.max_speed)
        self.pause_remaining = self.pause_time

    def move(self, dt: float):
        """Move towards current waypoint for dt seconds."""
        if self.pause_remaining > 0:
            self.pause_remaining -= dt
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < self.speed * dt:
            self.x = self.target_x
            self.y = self.target_y
            self._pick_new_waypoint()
        else:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

    def distance_to(self, other: "Node") -> float:
        """Euclidean distance to another node."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class PythonMANETSimulator:
    """
    Simplified DSDV MANET simulator in Python.

    ⚠️ This is a MODEL, not an NS-3 packet-level simulation.
    See module docstring for details.
    """

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.rng = np.random.default_rng(config.seed)

    def run(self) -> SimulationResult:
        """Execute the simulation and return results."""
        cfg = self.config
        result = SimulationResult(config=cfg)

        try:
            # Initialise nodes at random positions
            nodes = []
            for i in range(cfg.n_nodes):
                x = self.rng.uniform(0, cfg.area_size)
                y = self.rng.uniform(0, cfg.area_size)
                nodes.append(Node(
                    i, x, y, self.rng, cfg.area_size,
                    cfg.min_speed, cfg.max_speed, cfg.pause_time,
                ))

            # Select source-destination pairs for flows
            all_pairs = [(i, j) for i in range(cfg.n_nodes) for j in range(cfg.n_nodes) if i != j]
            flow_indices = self.rng.choice(len(all_pairs), size=min(cfg.n_flows, len(all_pairs)), replace=False)
            flows = [all_pairs[idx] for idx in flow_indices]

            # Simulation loop
            current_time = 0.0
            dt = cfg.time_step
            next_update_time = 0.0
            next_packet_time = {i: self.rng.exponential(1.0 / cfg.packet_rate) for i in range(len(flows))}
            packet_counter = 0

            while current_time < cfg.sim_duration:
                # 1. Move all nodes
                for node in nodes:
                    node.move(dt)

                # 2. Compute adjacency (who can hear whom)
                adjacency = self._compute_adjacency(nodes, cfg.tx_range)

                # 3. Periodic DSDV routing updates
                if current_time >= next_update_time:
                    updates = self._dsdv_update(nodes, adjacency, current_time, cfg.settling_time)
                    result.routing_updates_sent += updates
                    next_update_time = current_time + cfg.periodic_update_interval

                # 4. Generate and send data packets
                for flow_idx, (src_id, dst_id) in enumerate(flows):
                    if next_packet_time[flow_idx] <= current_time:
                        packet_counter += 1
                        result.packets_sent += 1

                        # Try to route the packet
                        delivered, delay, hops = self._route_packet(
                            nodes, adjacency, src_id, dst_id, current_time, cfg
                        )

                        if delivered:
                            result.packets_received += 1
                            result.total_delay += delay
                            result.total_bytes_received += cfg.packet_size
                            result.data_packets_forwarded += hops
                        else:
                            result.packets_dropped += 1

                        # Schedule next packet (Poisson arrivals)
                        next_packet_time[flow_idx] = current_time + self.rng.exponential(1.0 / cfg.packet_rate)

                current_time += dt

            result.compute_derived(cfg.sim_duration)

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            logger.error("Simulation failed: %s", e)

        return result

    @staticmethod
    def _compute_adjacency(nodes: list[Node], tx_range: float) -> dict[int, set[int]]:
        """Compute which nodes are within transmission range of each other."""
        adj: dict[int, set[int]] = {n.node_id: set() for n in nodes}
        for i, ni in enumerate(nodes):
            for j in range(i + 1, len(nodes)):
                nj = nodes[j]
                if ni.distance_to(nj) <= tx_range:
                    adj[ni.node_id].add(nj.node_id)
                    adj[nj.node_id].add(ni.node_id)
        return adj

    @staticmethod
    def _dsdv_update(
        nodes: list[Node],
        adjacency: dict[int, set[int]],
        current_time: float,
        settling_time: float,
    ) -> int:
        """
        Perform a DSDV-style full routing table exchange.

        Each node advertises its routing table to its 1-hop neighbours.
        Neighbours update their tables using DSDV rules:
            - Higher sequence number always wins
            - Same sequence number: prefer lower hop count
            - New routes are accepted after settling_time delay

        Returns the total number of routing update messages sent.
        """
        update_count = 0

        # Each node increments its own sequence number
        for node in nodes:
            node.seq_num += 2  # DSDV uses even increments for self-originated
            node.routing_table[node.node_id] = (node.node_id, 0, node.seq_num, current_time)

        # Exchange routing tables with neighbours
        # We do multiple passes to propagate beyond 1 hop (simplified Bellman-Ford)
        for _ in range(min(3, len(nodes))):
            for node in nodes:
                for neighbour_id in adjacency[node.node_id]:
                    neighbour = nodes[neighbour_id]
                    update_count += 1

                    for dest_id, (_, hop_count, seq_num, update_time) in node.routing_table.items():
                        new_hop_count = hop_count + 1
                        current_entry = neighbour.routing_table.get(dest_id)

                        if current_entry is None:
                            # New route - accept it
                            neighbour.routing_table[dest_id] = (
                                node.node_id, new_hop_count, seq_num, current_time
                            )
                        else:
                            _, curr_hops, curr_seq, curr_time = current_entry

                            # DSDV rule: higher seq_num wins
                            if seq_num > curr_seq:
                                # Check settling time for non-trivial changes
                                if current_time - curr_time >= settling_time or new_hop_count <= curr_hops:
                                    neighbour.routing_table[dest_id] = (
                                        node.node_id, new_hop_count, seq_num, current_time
                                    )
                            elif seq_num == curr_seq and new_hop_count < curr_hops:
                                # Same seq, shorter path
                                if current_time - curr_time >= settling_time:
                                    neighbour.routing_table[dest_id] = (
                                        node.node_id, new_hop_count, seq_num, current_time
                                    )

        return update_count

    @staticmethod
    def _route_packet(
        nodes: list[Node],
        adjacency: dict[int, set[int]],
        src_id: int,
        dst_id: int,
        current_time: float,
        cfg: SimulationConfig,
    ) -> tuple[bool, float, int]:
        """
        Route a packet from src to dst using the current routing tables.

        Returns (delivered: bool, total_delay: float, hop_count: int).
        """
        current_node_id = src_id
        visited = {src_id}
        hops = 0
        total_delay = 0.0
        max_hops = cfg.n_nodes  # loop prevention

        while current_node_id != dst_id and hops < max_hops:
            node = nodes[current_node_id]

            # Look up route to destination
            route_entry = node.routing_table.get(dst_id)
            if route_entry is None:
                return False, 0.0, 0  # no route

            next_hop_id = route_entry[0]

            # Check if next hop is reachable (within range)
            if next_hop_id not in adjacency[current_node_id]:
                return False, 0.0, 0  # stale route, link broken

            # Check for routing loop
            if next_hop_id in visited:
                return False, 0.0, 0  # loop detected

            visited.add(next_hop_id)
            hops += 1
            total_delay += cfg.propagation_delay_per_hop

            # Add queuing/transmission delay
            tx_delay = (cfg.packet_size * 8) / cfg.bandwidth
            total_delay += tx_delay

            current_node_id = next_hop_id

        if current_node_id == dst_id:
            return True, total_delay, hops
        else:
            return False, 0.0, 0  # exceeded max hops
