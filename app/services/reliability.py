import asyncio
import time
from typing import Dict, Any


class ReliabilityService:
    def __init__(self):
        self._is_ready: bool = True
        self._start_time: float = time.time()
        self._simulated_latency: float = 0.0

    def is_alive(self) -> Dict[str, Any]:
        """Liveness check: process uptime."""
        return {
            "status": "pass",
            "uptime_seconds": round(time.time() - self._start_time, 2),
        }

    def is_ready(self) -> Dict[str, Any]:
        """Readiness check: ready to accept traffic."""
        return {
            "status": "ready" if self._is_ready else "not_ready",
            "ready": self._is_ready,
        }

    def set_readiness(self, ready: bool) -> None:
        """Toggle readiness for chaos / maintenance simulation."""
        self._is_ready = ready

    def set_latency_simulation(self, seconds: float) -> None:
        """Set simulated artificial latency."""
        self._simulated_latency = max(0.0, seconds)

    async def apply_simulated_latency(self) -> None:
        """Simulate artificial latency if configured."""
        if self._simulated_latency > 0:
            await asyncio.sleep(self._simulated_latency)


reliability_service = ReliabilityService()
