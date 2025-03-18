import asyncio
import statistics
from collections import deque
from datetime import datetime
from enum import Enum
from typing import Any

from rich import box
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from sing_box_service.client import SingBoxAPIClient


class RefreshRate(Enum):
    """Refresh rate options for stats display."""

    SLOW = 1.0
    NORMAL = 0.5
    FAST = 0.25


def format_bytes(num_bytes_i: int | float) -> str:
    """
    Format bytes to human-readable format.

    Args:
        num_bytes: Number of bytes

    Returns:
        Formatted string representation in bytes
    """
    num_bytes = float(num_bytes_i)
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024.0 or unit == "GB":
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0

    # This line should never be reached due to the "GB" condition above,
    # but is needed to satisfy the type checker
    return f"{num_bytes:.2f} GB"


def format_speed(bytes_per_sec_i: int | float) -> str:
    """
    Format network speed to human-readable format.

    Args:
        bytes_per_sec: Speed in kilobits per second (B/s)

    Returns:
        Formatted string representation in bytes per second
    """
    bytes_per_sec = float(bytes_per_sec_i)
    for unit in ["B/s", "KB/s", "MB/s", "GB/s"]:
        if bytes_per_sec < 1024.0 or unit == "GB/s":
            return f"{bytes_per_sec:.2f} {unit}"
        bytes_per_sec /= 1024.0

    # This line should never be reached due to the "GB/s" condition above,
    # but is needed to satisfy the type checker
    return f"{bytes_per_sec:.2f} GB/s"


def calculate_averages(
    data_history: deque[dict[str, int]], key: str
) -> tuple[float, float]:
    """
    Calculate 5s and 10s averages for a specific metric.

    Args:
        data_history: Deque containing historical data
        key: The key to extract from each data point

    Returns:
        Tuple of (5s_avg, 10s_avg)
    """
    history_len = len(data_history)

    # Calculate 5s average (or less if not enough history)
    five_sec_samples = (
        list(data_history)[-5:] if history_len >= 5 else list(data_history)
    )
    five_sec_avg = (
        statistics.mean(item.get(key, 0) for item in five_sec_samples)
        if five_sec_samples
        else 0
    )

    # Calculate 10s average (or less if not enough history)
    ten_sec_samples = (
        list(data_history)[-10:] if history_len >= 10 else list(data_history)
    )
    ten_sec_avg = (
        statistics.mean(item.get(key, 0) for item in ten_sec_samples)
        if ten_sec_samples
        else 0
    )

    return five_sec_avg, ten_sec_avg


def sort_connections(connections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Sort connections by time in descending order.

    This function takes a list of connection dictionaries and sorts them primarily by the 'start' time
    and secondarily by the 'host' field, both in descending order.

    Args:
        connections (list[dict[str, Any]]): A list of dictionaries representing connections.
            Each dictionary should contain 'start' and 'host' keys.

    Returns:
        list[dict[str, Any]]: The sorted list of connection dictionaries.
    """
    return sorted(
        connections, key=lambda x: (x.get("start", ""), x.get("host", "")), reverse=True
    )


def format_rule(rule: str) -> str:
    """
    Format a rule string for display.

    This function takes a rule string and extracts the relevant parts for display.
    It tries to extract the rule pattern, e.g., from "rule_set=proxy-rule => route(proxy)".

    Args:
        rule (str): The rule string to format.

    Returns:
        str: The formatted rule string.
    """
    if rule:
        if "=>" in rule:
            rule_parts = rule.split("=>")
            return rule_parts[0].strip()
        return rule
    else:
        raise ValueError(f"Invalid rule data: {rule}")


def format_duration(start_str: str) -> str:
    """
    Calculate the duration of a connection.

    This function takes a start time string and calculates the duration from the start time to the current time.

    Args:
        start_str (str): The start time string in ISO format.

    Returns:
        str: The duration string in seconds.
    """
    try:
        # Parse ISO format time and calculate duration
        start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        now = datetime.now(tz=start_time.tzinfo)
        duration = now - start_time
        seconds = int(duration.total_seconds())
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        elif seconds < 86400:
            return f"{seconds // 3600}h {(seconds % 3600) // 60}m"
        else:
            return f"{seconds // 86400}d {(seconds % 86400) // 3600}h"
    except (ValueError, TypeError):
        raise ValueError(f"Invalid start time: {start_str}")


def format_chain(chains: list[str]) -> str:
    """
    Format a chain list for display.

    This function takes a list of chain names and formats them for display.

    Args:
        chains (list[str]): A list of chain names.

    Returns:
        str: The formatted chain string.
    """
    if chains:
        return " → ".join(reversed(chains))
    else:
        raise ValueError(f"Invalid chains data: {chains}")


class ResourceVisualizer:
    """Class for visualizing Sing-Box resource statistics."""

    def __init__(self, refresh_rate: float = RefreshRate.FAST.value) -> None:
        """Initialize the visualizer with data history tracking."""
        self.refresh_rate = refresh_rate
        self.console = Console()

        # For averages calculation
        self.traffic_data_history: deque[dict[str, int]] = deque(maxlen=10)
        self.memory_data_history: deque[dict[str, int]] = deque(maxlen=10)

    def create_traffic_table(self, traffic_data: dict[str, Any]) -> Table:
        """Create a table displaying traffic statistics with averages."""
        # Add current data to history
        self.traffic_data_history.append(traffic_data.copy())

        # Get the raw values
        up_bytes = traffic_data.get("up", 0)
        down_bytes = traffic_data.get("down", 0)

        # Calculate averages
        up_5s_avg, up_10s_avg = calculate_averages(self.traffic_data_history, "up")
        down_5s_avg, down_10s_avg = calculate_averages(
            self.traffic_data_history, "down"
        )

        # Create table with expanded columns
        table = Table(title="Network Traffic", expand=True)
        table.add_column("Direction", style="cyan")
        table.add_column("Current", justify="right", style="green", width=10)
        table.add_column("5s Avg", justify="right", style="yellow", width=10)
        table.add_column("10s Avg", justify="right", style="bright_blue", width=10)

        # Add rows with current values and averages
        table.add_row(
            "Upload",
            format_speed(up_bytes),
            format_speed(up_5s_avg),
            format_speed(up_10s_avg),
        )
        table.add_row(
            "Download",
            format_speed(down_bytes),
            format_speed(down_5s_avg),
            format_speed(down_10s_avg),
        )
        return table

    def create_memory_table(self, memory_data: dict[str, Any]) -> Table:
        """Create a table displaying memory usage statistics with averages."""
        # Add current data to history
        self.memory_data_history.append(memory_data.copy())

        # Extract current memory values
        inuse = memory_data.get("inuse", 0)
        total = memory_data.get("total", 0)

        # Calculate averages
        inuse_5s_avg, inuse_10s_avg = calculate_averages(
            self.memory_data_history, "inuse"
        )
        total_5s_avg, total_10s_avg = calculate_averages(
            self.memory_data_history, "total"
        )

        # Create table with expanded columns
        table = Table(title="Memory Usage", expand=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Current", justify="right", style="green", width=10)
        table.add_column("5s Avg", justify="right", style="yellow", width=10)
        table.add_column("10s Avg", justify="right", style="bright_blue", width=10)

        # Add rows with current values and averages
        table.add_row(
            "In Use",
            format_bytes(inuse),
            format_bytes(inuse_5s_avg),
            format_bytes(inuse_10s_avg),
        )
        table.add_row(
            "Total Allocated",
            format_bytes(total),
            format_bytes(total_5s_avg),
            format_bytes(total_10s_avg),
        )

        # Add usage percentage if total is not zero
        if total > 0:
            current_percent = (inuse / total) * 100
            avg_5s_percent = (inuse_5s_avg / total) * 100 if total else 0
            avg_10s_percent = (inuse_10s_avg / total) * 100 if total else 0

            table.add_row(
                "Usage",
                f"{current_percent:.1f}%",
                f"{avg_5s_percent:.1f}%",
                f"{avg_10s_percent:.1f}%",
            )

        return table

    @staticmethod
    def create_connections_table(connections_data: dict[str, Any]) -> Panel:
        """
        Create a panel displaying active connections.

        Args:
            connections_data: Connections data from the API

        Returns:
            Rich Panel containing the connections information
        """
        if not connections_data or "connections" not in connections_data:
            return Panel("No connections data available", title="Active Connections")

        connections = connections_data.get("connections", [])

        if not connections:
            return Panel("No active connections", title="Active Connections")

        # Create table to display connections
        table = Table(
            title=f"Active Connections ({len(connections)})",
            expand=True,
            pad_edge=False,  # Reduce padding
        )
        table.add_column("Host", style="cyan", no_wrap=True, max_width=20)
        table.add_column("Rule", style="bright_green", no_wrap=True, max_width=15)
        table.add_column("Chain", style="yellow", no_wrap=True, max_width=20)
        table.add_column("Network", justify="center", style="green")
        table.add_column("↑", justify="right", style="bright_blue")
        table.add_column("↓", justify="right", style="magenta")
        table.add_column("Duration", justify="right", style="green")

        # Sort connections by time
        sorted_connections = sort_connections(connections)

        # Show top connections (limit to avoid overwhelming the display)
        max_display = 15
        for conn in sorted_connections[:max_display]:
            # Extract data
            metadata = conn.get("metadata", {})
            host = metadata.get("host", "") or metadata.get("destinationIP", "?")

            network = metadata.get("network", "?").upper()
            upload = format_bytes(conn.get("upload", 0))
            download = format_bytes(conn.get("download", 0))

            # Extract rule information
            # Format rule display - extract useful parts
            rule_display = format_rule(conn.get("rule", ""))

            # Calculate duration
            duration_str = format_duration(conn.get("start", ""))

            # Format chains (usually shows proxy names)
            chain_str = format_chain(conn.get("chains", []))

            table.add_row(
                host, rule_display, chain_str, network, upload, download, duration_str
            )

        # Add summary information
        total_upload = format_bytes(connections_data.get("uploadTotal", 0))
        total_download = format_bytes(connections_data.get("downloadTotal", 0))
        memory_usage = format_bytes(connections_data.get("memory", 0))

        summary = f"Total Upload: {total_upload} | Total Download: {total_download} | Memory: {memory_usage}"
        if len(connections) > max_display:
            summary += f" | Showing {max_display} of {len(connections)} connections"

        # Return as a panel
        return Panel(
            Group(table, Text(summary, justify="center")), title="Connection Details"
        )

    def create_resources_layout(
        self,
        traffic_data: dict[str, Any],
        memory_data: dict[str, Any],
        connections_data: dict[str, Any],
    ) -> Layout:
        """
        Create the main layout with all resource components.

        Args:
            traffic_data: Traffic statistics data
            memory_data: Memory usage data
            connections_data: Connections data

        Returns:
            Rich Layout object
        """
        layout = Layout()

        # Create main sections
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=1),
        )

        # Split main section into upper and connections
        layout["main"].split(
            Layout(name="upper", ratio=1), Layout(name="connections", ratio=3)
        )

        # Split upper section into left and right
        layout["upper"].split_row(Layout(name="left"), Layout(name="right"))

        # Add components
        layout["header"].update(
            Panel(
                Text("Sing-Box Resource Monitor", justify="center"),
                style="bold white on bright_blue",
                box=box.SIMPLE,
            )
        )

        layout["upper"]["left"].update(self.create_traffic_table(traffic_data))
        layout["upper"]["right"].update(self.create_memory_table(memory_data))

        # Add connections panel
        layout["connections"].update(self.create_connections_table(connections_data))

        # Add footer
        layout["footer"].update(Text("Press Ctrl+C to exit", justify="center"))

        return layout


class ResourceMonitor:
    """Class that connects the API client with visualization for resource monitoring."""

    def __init__(
        self, api_client: SingBoxAPIClient, visualizer: ResourceVisualizer
    ) -> None:
        """
        Initialize the resource monitor.

        Args:
            api_client: SingBox API client
            visualizer: Resource visualizer
        """
        self.api_client = api_client
        self.visualizer = visualizer
        self.running = False
        self.current_traffic = {"up": 0, "down": 0}  # in bytes
        self.current_memory = {"inuse": 0, "total": 0}  # in bytes

    async def monitor_traffic(self) -> None:
        """Monitor traffic stream from the API."""
        try:
            async for traffic_data in self.api_client.traffic_stream():
                self.current_traffic = traffic_data
                if not self.running:
                    break
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.visualizer.console.print(f"[red]Error monitoring traffic: {str(e)}")

    async def monitor_memory(self) -> None:
        """Monitor memory stream from the API."""
        try:
            async for memory_data in self.api_client.memory_stream():
                self.current_memory = memory_data
                if not self.running:
                    break
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.visualizer.console.print(f"[red]Error monitoring memory: {str(e)}")

    async def refresh_display(self) -> None:
        """Main display refresh loop."""
        self.running = True
        # Start monitoring in separate tasks
        traffic_task = asyncio.create_task(self.monitor_traffic())
        memory_task = asyncio.create_task(self.monitor_memory())
        with Live(
            refresh_per_second=1 / self.visualizer.refresh_rate, screen=True
        ) as live:
            while self.running:
                try:
                    # Use the current data from the streams
                    traffic_data = self.current_traffic
                    memory_data = self.current_memory
                    connections_data = await self.api_client.get_connections()

                    # Update display
                    layout = self.visualizer.create_resources_layout(
                        traffic_data, memory_data, connections_data
                    )
                    live.update(layout)

                    # Wait for next refresh
                    await asyncio.sleep(self.visualizer.refresh_rate - 0.1)
                except KeyboardInterrupt:
                    self.running = False
                    break
                except Exception as e:
                    live.update(
                        Panel(
                            f"Unexpected error: {str(e)}",
                            title="Error",
                            border_style="red",
                        )
                    )
                    await asyncio.sleep(2)

        # Clean up monitoring tasks
        self.running = False
        traffic_task.cancel()
        memory_task.cancel()
        try:
            await asyncio.gather(traffic_task, memory_task, return_exceptions=True)
        except asyncio.CancelledError:
            pass

    async def start(self) -> None:
        """Start the resource monitor."""
        try:
            await self.refresh_display()
        except KeyboardInterrupt:
            self.running = False
            self.visualizer.console.print("Exiting resource monitor...")
