"""
Adaptive decision engine for download optimization.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

from flux.core.metrics import DownloadMetrics


class DecisionType(Enum):
    """Types of adaptive decisions."""
    INCREASE_CHUNK_SIZE = "increase_chunk_size"
    DECREASE_CHUNK_SIZE = "decrease_chunk_size"
    INCREASE_CONNECTIONS = "increase_connections"
    DECREASE_CONNECTIONS = "decrease_connections"
    ADJUST_RETRY_STRATEGY = "adjust_retry_strategy"


@dataclass
class Decision:
    """Represents a single adaptive decision."""
    
    decision_type: DecisionType
    reason: str
    old_value: Any
    new_value: Any
    expected_impact: str
    timestamp: float = field(default_factory=time.time)
    download_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export."""
        return {
            "type": self.decision_type.value,
            "reason": self.reason,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "expected_impact": self.expected_impact,
            "timestamp": self.timestamp,
            "download_id": self.download_id,
        }
    
    def format(self) -> str:
        """Format for display in UI."""
        lines = [
            f"[{self.decision_type.value}]",
            f"Reason: {self.reason}",
            f"{self.old_value} → {self.new_value}",
            f"Expected: {self.expected_impact}",
        ]
        return "\n".join(lines)


class DecisionEngine:
    """
    Analyzes metrics and makes adaptive decisions to optimize downloads.
    """
    
    # Configuration thresholds
    STABLE_SPEED_THRESHOLD = 0.15  # 15% coefficient of variation
    HIGH_ERROR_RATE = 0.05  # 5% errors per MB
    HIGH_RTT_MS = 200  # milliseconds
    LOW_RTT_MS = 50  # milliseconds
    
    # Limits
    MIN_CHUNK_SIZE = 1024 * 1024  # 1MB
    MAX_CHUNK_SIZE = 16 * 1024 * 1024  # 16MB
    MIN_CONNECTIONS = 1
    MAX_CONNECTIONS = 16
    
    def __init__(self) -> None:
        """Initialize decision engine."""
        self.decisions: List[Decision] = []
        self._last_decision_time: Dict[str, float] = {}
        self._decision_cooldown = 5.0  # seconds between same decision type
    
    def analyze(
        self,
        metrics: DownloadMetrics,
        current_chunk_size: int,
        current_connections: int,
        supports_ranges: bool = True,
    ) -> List[Decision]:
        """
        Analyze metrics and return adaptive decisions.
        
        Args:
            metrics: Current download metrics
            current_chunk_size: Current chunk size in bytes
            current_connections: Current number of connections
            supports_ranges: Whether server supports range requests
        
        Returns:
            List of decisions to apply
        """
        new_decisions: List[Decision] = []
        
        # Need enough data to make decisions
        if len(metrics.speed_history) < 10:
            return new_decisions
        
        # Check chunk size optimization
        chunk_decision = self._analyze_chunk_size(
            metrics, current_chunk_size
        )
        if chunk_decision:
            new_decisions.append(chunk_decision)
        
        # Check connection count optimization
        if supports_ranges:
            conn_decision = self._analyze_connections(
                metrics, current_connections
            )
            if conn_decision:
                new_decisions.append(conn_decision)
        
        # Store decisions
        for decision in new_decisions:
            decision.download_id = metrics.download_id
            self.decisions.append(decision)
        
        return new_decisions
    
    def _analyze_chunk_size(
        self, metrics: DownloadMetrics, current_size: int
    ) -> Decision | None:
        """Analyze whether to adjust chunk size."""
        
        # Check cooldown
        if not self._check_cooldown("chunk_size"):
            return None
        
        # Calculate speed stability
        speeds = list(metrics.speed_history)
        if len(speeds) < 2:
            return None
        
        import statistics
        mean_speed = statistics.mean(speeds)
        if mean_speed == 0:
            return None
        
        stdev = statistics.stdev(speeds)
        cv = stdev / mean_speed  # Coefficient of variation
        
        # High RTT + stable speed → increase chunk size
        if (
            cv < self.STABLE_SPEED_THRESHOLD
            and metrics.rtt_ms > self.HIGH_RTT_MS
            and current_size < self.MAX_CHUNK_SIZE
        ):
            new_size = min(current_size * 2, self.MAX_CHUNK_SIZE)
            self._update_cooldown("chunk_size")
            return Decision(
                decision_type=DecisionType.INCREASE_CHUNK_SIZE,
                reason="Stable throughput + high RTT detected",
                old_value=self._format_size(current_size),
                new_value=self._format_size(new_size),
                expected_impact="Reduced overhead from fewer requests",
            )
        
        # Low RTT + unstable speed → decrease chunk size
        if (
            cv > self.STABLE_SPEED_THRESHOLD * 2
            and metrics.rtt_ms < self.LOW_RTT_MS
            and current_size > self.MIN_CHUNK_SIZE
        ):
            new_size = max(current_size // 2, self.MIN_CHUNK_SIZE)
            self._update_cooldown("chunk_size")
            return Decision(
                decision_type=DecisionType.DECREASE_CHUNK_SIZE,
                reason="Unstable throughput + low RTT detected",
                old_value=self._format_size(current_size),
                new_value=self._format_size(new_size),
                expected_impact="Better adaptability to network conditions",
            )
        
        return None
    
    def _analyze_connections(
        self, metrics: DownloadMetrics, current_connections: int
    ) -> Decision | None:
        """Analyze whether to adjust connection count."""
        
        # Check cooldown
        if not self._check_cooldown("connections"):
            return None
        
        # Calculate error rate
        total_ops = metrics.bytes_downloaded // (1024 * 1024) or 1
        error_rate = metrics.error_count / total_ops
        
        # Low errors + not at max → increase connections
        if (
            error_rate < self.HIGH_ERROR_RATE
            and current_connections < self.MAX_CONNECTIONS
            and metrics.efficiency_score > 70
        ):
            new_connections = min(current_connections * 2, self.MAX_CONNECTIONS)
            self._update_cooldown("connections")
            return Decision(
                decision_type=DecisionType.INCREASE_CONNECTIONS,
                reason="Low error rate, server handles load well",
                old_value=f"{current_connections} connections",
                new_value=f"{new_connections} connections",
                expected_impact="Higher throughput via parallelism",
            )
        
        # High errors → decrease connections
        if (
            error_rate > self.HIGH_ERROR_RATE * 2
            and current_connections > self.MIN_CONNECTIONS
        ):
            new_connections = max(current_connections // 2, self.MIN_CONNECTIONS)
            self._update_cooldown("connections")
            return Decision(
                decision_type=DecisionType.DECREASE_CONNECTIONS,
                reason="High error rate detected",
                old_value=f"{current_connections} connections",
                new_value=f"{new_connections} connections",
                expected_impact="Reduced server load, fewer errors",
            )
        
        return None
    
    def _check_cooldown(self, decision_key: str) -> bool:
        """Check if enough time has passed since last decision of this type."""
        last_time = self._last_decision_time.get(decision_key, 0)
        return time.time() - last_time >= self._decision_cooldown
    
    def _update_cooldown(self, decision_key: str) -> None:
        """Update last decision time."""
        self._last_decision_time[decision_key] = time.time()
    
    def _format_size(self, size: int) -> str:
        """Format size in KB/MB."""
        if size >= 1024 * 1024:
            return f"{size // (1024 * 1024)}MB"
        else:
            return f"{size // 1024}KB"
    
    def export_decisions(self) -> List[Dict[str, Any]]:
        """Export all decisions as list of dictionaries."""
        return [d.to_dict() for d in self.decisions]
    
    def get_recent_decisions(self, download_id: str, limit: int = 5) -> List[Decision]:
        """Get recent decisions for a download."""
        filtered = [d for d in self.decisions if d.download_id == download_id]
        return filtered[-limit:]
