"""
Real-time download metrics tracking.
"""

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque


@dataclass
class DownloadMetrics:
    """
    Tracks real-time metrics for a download.
    """

    download_id: str
    total_size: int
    bytes_downloaded: int = 0
    start_time: float = field(default_factory=time.time)
    
    # Speed tracking
    current_speed: float = 0.0  # bytes/sec
    average_speed: float = 0.0  # bytes/sec
    peak_speed: float = 0.0  # bytes/sec
    
    # Network quality
    rtt_ms: float = 0.0  # round-trip time in milliseconds
    error_count: int = 0
    retry_count: int = 0
    
    # History for graphs (last 60 samples)
    speed_history: Deque[float] = field(default_factory=lambda: deque(maxlen=60))
    
    def __post_init__(self) -> None:
        """Initialize computed fields."""
        self._last_update_time = time.time()
        self._last_bytes = 0
    
    def update(self, bytes_downloaded: int, rtt_ms: float = 0.0) -> None:
        """
        Update metrics with new progress.
        
        Args:
            bytes_downloaded: Total bytes downloaded so far
            rtt_ms: Round-trip time in milliseconds
        """
        now = time.time()
        time_delta = now - self._last_update_time
        
        if time_delta > 0:
            bytes_delta = bytes_downloaded - self._last_bytes
            self.current_speed = bytes_delta / time_delta
            
            # Update peak
            if self.current_speed > self.peak_speed:
                self.peak_speed = self.current_speed
            
            # Add to history
            self.speed_history.append(self.current_speed)
        
        self.bytes_downloaded = bytes_downloaded
        self.rtt_ms = rtt_ms
        
        # Calculate average speed
        elapsed = now - self.start_time
        if elapsed > 0:
            self.average_speed = self.bytes_downloaded / elapsed
        
        self._last_update_time = now
        self._last_bytes = bytes_downloaded
    
    def increment_errors(self) -> None:
        """Increment error count."""
        self.error_count += 1
    
    def increment_retries(self) -> None:
        """Increment retry count."""
        self.retry_count += 1
    
    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage."""
        if self.total_size == 0:
            return 0.0
        return (self.bytes_downloaded / self.total_size) * 100
    
    @property
    def eta_seconds(self) -> float:
        """
        Calculate estimated time to completion in seconds.
        Returns -1 if cannot be calculated.
        """
        if self.current_speed == 0:
            return -1.0
        
        remaining_bytes = self.total_size - self.bytes_downloaded
        return remaining_bytes / self.current_speed
    
    @property
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self.start_time
    
    @property
    def efficiency_score(self) -> float:
        """
        Calculate efficiency score (0-100).
        Based on speed stability and error rate.
        """
        if not self.speed_history or self.average_speed == 0:
            return 0.0
        
        # Speed stability (coefficient of variation)
        speeds = list(self.speed_history)
        if len(speeds) < 2:
            stability = 1.0
        else:
            import statistics
            mean = statistics.mean(speeds)
            if mean == 0:
                stability = 0.0
            else:
                stdev = statistics.stdev(speeds)
                cv = stdev / mean
                stability = max(0, 1 - cv)  # Lower CV = higher stability
        
        # Error penalty
        total_operations = self.bytes_downloaded // (1024 * 1024) or 1  # Per MB
        error_rate = self.error_count / total_operations if total_operations > 0 else 0
        error_penalty = max(0, 1 - error_rate)
        
        # Combined score
        score = (stability * 0.7 + error_penalty * 0.3) * 100
        return min(100, max(0, score))
    
    def format_speed(self, speed: float) -> str:
        """Format speed in human-readable format."""
        units = ["B/s", "KB/s", "MB/s", "GB/s"]
        unit_idx = 0
        
        while speed >= 1024 and unit_idx < len(units) - 1:
            speed /= 1024
            unit_idx += 1
        
        return f"{speed:.2f} {units[unit_idx]}"
    
    def format_size(self, size: int) -> str:
        """Format size in human-readable format."""
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_idx = 0
        size_f = float(size)
        
        while size_f >= 1024 and unit_idx < len(units) - 1:
            size_f /= 1024
            unit_idx += 1
        
        return f"{size_f:.2f} {units[unit_idx]}"
    
    def format_eta(self, seconds: float) -> str:
        """Format ETA in human-readable format."""
        if seconds < 0:
            return "calculating..."
        
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
