import os
import platform
import time

import psutil

from tools.abstract_tool import AbstractTool


class SystemHealthTool(AbstractTool):
    """Tool to check system health metrics."""

    @property
    def name(self) -> str:
        return "system_health"

    @property
    def description(self) -> str:
        return (
            "Returns current system health metrics including CPU usage, "
            "memory usage, disk usage, and basic system info. "
            "Use 'metric' to request a specific metric or 'all' for everything."
        )

    def get_parameters_schema(self) -> dict:
        return {
            "metric": {
                "type": "string",
                "description": (
                    "Which metric to fetch. "
                    "Options: 'cpu', 'memory', 'disk', 'system', 'all','agent'"
                ),
                "enum": ["cpu", "memory", "disk", "system", "all", "agent"],
            }
        }

    def execute(self, **kwargs) -> str:
        metric = kwargs.get("metric", "all").lower()
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()

        collectors = {
            "cpu": self._cpu_info,
            "memory": self._memory_info,
            "disk": self._disk_info,
            "system": self._system_info,
            "agent": self._agent_health,
        }

        if metric == "all":
            results = {key: fn() for key, fn in collectors.items()}
        elif metric in collectors:
            results = {metric: collectors[metric]()}
        else:
            return f"Unknown metric '{metric}'. Choose from: cpu, memory, disk, system, all."

        return self._format(results)

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _cpu_info(self) -> dict:
        return {
            "usage_percent": psutil.cpu_percent(interval=1),
            "logical_cores": psutil.cpu_count(logical=True),
            "physical_cores": psutil.cpu_count(logical=False),
            "frequency_mhz": round(psutil.cpu_freq().current, 1)
            if psutil.cpu_freq()
            else "N/A",
            "load_avg_1m": round(psutil.getloadavg()[0], 2),
        }

    def _memory_info(self) -> dict:
        vm = psutil.virtual_memory()
        return {
            "total_gb": round(vm.total / 1e9, 2),
            "available_gb": round(vm.available / 1e9, 2),
            "used_gb": round(vm.used / 1e9, 2),
            "usage_percent": vm.percent,
        }

    def _disk_info(self) -> dict:
        du = psutil.disk_usage("/")
        io = psutil.disk_io_counters()
        return {
            "total_gb": round(du.total / 1e9, 2),
            "used_gb": round(du.used / 1e9, 2),
            "free_gb": round(du.free / 1e9, 2),
            "usage_percent": du.percent,
            "reads_total": io.read_count if io else "N/A",
            "writes_total": io.write_count if io else "N/A",
        }

    def _system_info(self) -> dict:
        boot = psutil.boot_time()
        uptime_h = round((psutil.time.time() - boot) / 3600, 1)
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "python": platform.python_version(),
            "uptime_hours": uptime_h,
        }

    def _agent_health(self) -> dict:
        process = psutil.Process(os.getpid())

        mem = process.memory_info()
        cpu = process.cpu_percent(interval=0.1)

        uptime_sec = time.time() - process.create_time()
        uptime_h = round(uptime_sec / 3600, 2)

        return {
            "agent": "AgentChimp",
            "pid": process.pid,
            "memory_mb": round(mem.rss / 1024 / 1024, 2),
            "cpu_percent": cpu,
            "threads": process.num_threads(),
            "uptime_hours": uptime_h,
        }

    def _format(self, results: dict) -> str:
        lines = []
        for section, data in results.items():
            lines.append(f"[{section.upper()}]")
            for k, v in data.items():
                lines.append(f"  {k}: {v}")
        return "\n".join(lines)
