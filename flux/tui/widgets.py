"""
Custom Textual widgets for Flux TUI.
"""

from collections import deque
from typing import Deque, List

from rich.text import Text
from textual.widgets import DataTable, RichLog, Static

from flux.core.engine import DownloadStatus, DownloadTask


class NetworkGraph(Static):
    """
    Live sparkline graph showing network speed history.
    """
    
    def __init__(self, **kwargs) -> None:
        """Initialize network graph."""
        super().__init__(**kwargs)
        self.speed_history: Deque[float] = deque(maxlen=60)  # Fixed 60-sample window
        self.peak_speed = 0.0
    
    def update_speeds(self, speeds: List[float], peak: float) -> None:
        """
        Update speed history.
        
        Args:
            speeds: List of recent speeds
            peak: Peak speed for normalization
        """
        self.speed_history.extend(speeds)
        self.peak_speed = peak or 1.0
        self.refresh()
    
    def _rolling_average(self, data: List[float], window: int = 5) -> List[float]:
        """Calculate rolling average to smooth spikes."""
        if len(data) < window:
            return data
        
        smoothed = []
        for i in range(len(data)):
            start = max(0, i - window + 1)
            window_data = data[start:i+1]
            smoothed.append(sum(window_data) / len(window_data))
        return smoothed
    
    def render(self) -> Text:
        """Render sparkline."""
        if not self.speed_history:
            return Text("No data", style="dim #555555")
        
        # Convert to list and apply rolling average
        speeds = list(self.speed_history)
        smoothed = self._rolling_average(speeds, window=5)
        
        # Clamp spikes to 2x rolling average
        avg = sum(smoothed) / len(smoothed) if smoothed else 1.0
        max_allowed = avg * 2
        clamped = [min(s, max_allowed) for s in smoothed]
        
        # Sparkline characters (8 levels)
        chars = [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        
        # Normalize to 0-8 range
        normalized = []
        max_val = max(clamped) if clamped else 1.0
        for speed in clamped:
            if max_val > 0:
                ratio = speed / max_val
                level = int(ratio * 8)
                level = min(8, max(0, level))
            else:
                level = 0
            normalized.append(level)
        
        # Build sparkline with neon cyan color
        sparkline = "".join(chars[n] for n in normalized)
        
        return Text(sparkline, style="bold #00aaff")


class DownloadListTable(DataTable):
    """
    Data table showing downloads with filtering.
    """
    
    def __init__(self, **kwargs) -> None:
        """Initialize download list."""
        super().__init__(**kwargs)
        self.cursor_type = "row"
        self.zebra_stripes = True
        
        # Add columns
        self.add_column("File", width=30)
        self.add_column("Progress", width=10)
        self.add_column("Speed", width=15)
        self.add_column("ETA", width=12)
        self.add_column("Status", width=10)


class ActivityLogWidget(RichLog):
    """
    Scrolling activity log.
    """
    
    def __init__(self, **kwargs) -> None:
        """Initialize activity log."""
        super().__init__(**kwargs, max_lines=100, markup=True)
        self.auto_scroll = True


class IntelligencePanel(Static):
    """
    Displays recent adaptive decisions.
    """
    
    def __init__(self, **kwargs) -> None:
        """Initialize intelligence panel."""
        super().__init__(**kwargs)
        self.recent_decisions: List[str] = []
    
    def add_decision(self, formatted_decision: str) -> None:
        """
        Add a new decision.
        
        Args:
            formatted_decision: Pre-formatted decision text
        """
        self.recent_decisions.insert(0, formatted_decision)
        self.recent_decisions = self.recent_decisions[:3]  # Keep last 3
        self.refresh()
    
    def render(self) -> Text:
        """Render decisions."""
        if not self.recent_decisions:
            return Text("No adaptive decisions yet", style="dim italic #555555")
        
        result = Text()
        for i, decision in enumerate(self.recent_decisions):
            if i > 0:
                result.append("\n" + "━" * 50 + "\n", style="dim #ff00ff")
            # Decisions already formatted with rich markup, just append
            result.append(decision)
        
        return result


class FileDetailsPanel(Static):
    """
    Displays detailed information about selected download.
    """
    
    def __init__(self, **kwargs) -> None:
        """Initialize file details panel."""
        super().__init__(**kwargs)
        self.current_task: DownloadTask | None = None
        self.download_history: Deque[DownloadTask] = deque(maxlen=3)  # Track last 3 downloads
        self.last_active_id: str | None = None  # Track last active download ID
    
    def update_task(self, task: DownloadTask | None) -> None:
        """
        Update displayed task.
        
        Args:
            task: Download task to display
        """
        # If current task completed or changed, move to history
        if self.current_task and task:
            if self.current_task.id != task.id:
                # Different download, add old one to history if completed/paused
                if self.current_task.status in [DownloadStatus.COMPLETED, DownloadStatus.PAUSED, DownloadStatus.FAILED]:
                    # Check if not already in history
                    if not any(h.id == self.current_task.id for h in self.download_history):
                        self.download_history.appendleft(self.current_task)
        elif self.current_task and not task:
            # Task was cleared, move current to history
            if self.current_task.status in [DownloadStatus.COMPLETED, DownloadStatus.PAUSED, DownloadStatus.FAILED]:
                if not any(h.id == self.current_task.id for h in self.download_history):
                    self.download_history.appendleft(self.current_task)
        
        self.current_task = task
        self.refresh()
    
    def render(self) -> Text:
        """Render file details with history section."""
        result = Text()
        
        if not self.current_task:
            result.append("No download selected", style="dim #555555")
        else:
            task = self.current_task
            metrics = task.metrics
            
            # Filename and path with enhanced styling
            result.append("▸ ", style="#ff006e")
            result.append(f"{task.filename}\n", style="bold #00d9ff")
            result.append(f"  {task.filepath}\n\n", style="dim #6b7280")
            
            # Size and progress with clear formatting
            size_str = metrics.format_size(task.total_size)
            downloaded_str = metrics.format_size(metrics.bytes_downloaded)
            progress = metrics.progress_percent
            
            # Progress bar with percentage and size - clean Surge style
            bar_width = 35
            filled = int(progress / 100 * bar_width)
            bar = "━" * filled + "░" * (bar_width - filled)
            
            result.append(f"{bar}  ", style="#00d9ff")
            result.append(f"{progress:.1f}%\n", style="#00d9ff")
            result.append(f"{downloaded_str} / {size_str}\n\n", style="#00d9ff")
            
            # Speed metrics
            current_speed = metrics.format_speed(metrics.current_speed)
            avg_speed = metrics.format_speed(metrics.average_speed)
            peak_speed = metrics.format_speed(metrics.peak_speed)
            
            result.append(f"Speed: ", style="#00d9ff")
            result.append(f"{current_speed}  ", style="#00d9ff")
            result.append(f"Avg: {avg_speed}  ", style="dim #6b7280")
            result.append(f"Peak: {peak_speed}\n", style="#ff006e")
            
            # ETA and Time Analysis - Enhanced
            eta_seconds = metrics.eta_seconds
            elapsed_seconds = metrics.elapsed_seconds
            
            # Format ETA with breakdown
            if eta_seconds < 60:
                eta_str = f"{int(eta_seconds)}s"
            elif eta_seconds < 3600:
                mins = int(eta_seconds // 60)
                secs = int(eta_seconds % 60)
                eta_str = f"{mins}m {secs}s"
            else:
                hours = int(eta_seconds // 3600)
                mins = int((eta_seconds % 3600) // 60)
                eta_str = f"{hours}h {mins}m"
            
            # Format elapsed time
            if elapsed_seconds < 60:
                elapsed_str = f"{int(elapsed_seconds)}s"
            elif elapsed_seconds < 3600:
                mins = int(elapsed_seconds // 60)
                secs = int(elapsed_seconds % 60)
                elapsed_str = f"{mins}m {secs}s"
            else:
                hours = int(elapsed_seconds // 3600)
                mins = int((elapsed_seconds % 3600) // 60)
                elapsed_str = f"{hours}h {mins}m"
            
            # ETA accuracy indicator
            if metrics.current_speed > 0 and metrics.average_speed > 0:
                speed_variance = abs(metrics.current_speed - metrics.average_speed) / metrics.average_speed
                if speed_variance < 0.1:
                    accuracy = "High"
                    accuracy_color = "#00ff41"
                elif speed_variance < 0.3:
                    accuracy = "Med"
                    accuracy_color = "#ffaa00"
                else:
                    accuracy = "Low"
                    accuracy_color = "#ff6b6b"
            else:
                accuracy = "N/A"
                accuracy_color = "dim #6b7280"
            
            result.append("ETA: ", style="#ff006e")
            result.append(f"{eta_str}  ", style="#ff006e")
            result.append(f"Accuracy: ", style="dim #6b7280")
            result.append(f"{accuracy}  ", style=accuracy_color)
            result.append(f"Elapsed: {elapsed_str}\n", style="dim #6b7280")
            
            # Progress timeline
            total_time = elapsed_seconds + eta_seconds if eta_seconds > 0 else elapsed_seconds
            if total_time > 0:
                progress_ratio = elapsed_seconds / total_time
                timeline_width = 35
                filled_timeline = int(progress_ratio * timeline_width)
                timeline = "█" * filled_timeline + "░" * (timeline_width - filled_timeline)
                result.append(f"{timeline}\n", style="#00d9ff")
                result.append(f"[{elapsed_str} elapsed | {eta_str} remaining]\n\n", style="dim #6b7280")
            
            # Connections and efficiency
            result.append(f"Conns: ", style="#00d9ff")
            result.append(f"{task.num_connections}  ", style="#00d9ff")
            result.append(f"Chunk: ", style="#00d9ff")
            result.append(f"{metrics.format_size(task.chunk_size)}  ", style="#00d9ff")
            result.append(f"Efficiency: ", style="#00d9ff")
            result.append(f"{metrics.efficiency_score:.0f}%\n", style="#00d9ff")
            
            # URL (more compact)
            result.append(f"\nURL: {task.url[:60]}{'...' if len(task.url) > 60 else ''}\n", style="dim #6b7280")
        
        # Add history section if there are previous downloads
        if self.download_history:
            result.append("\n" + "─" * 40 + "\n", style="dim #555555")
            result.append("Recent History\n", style="#ff006e")
            
            for hist_task in self.download_history:
                hist_metrics = hist_task.metrics
                
                # Status icon
                if hist_task.status == DownloadStatus.COMPLETED:
                    result.append("✓ ", style="#00ff41")
                elif hist_task.status == DownloadStatus.FAILED:
                    result.append("✗ ", style="#ff0000")
                elif hist_task.status == DownloadStatus.PAUSED:
                    result.append("⏸ ", style="#ffaa00")
                else:
                    result.append("○ ", style="dim #6b7280")
                
                # Compact info: filename + size/progress
                filename = hist_task.filename if len(hist_task.filename) <= 30 else hist_task.filename[:27] + "..."
                result.append(f"{filename} ", style="#6b7280")
                
                if hist_task.status == DownloadStatus.COMPLETED:
                    size = hist_metrics.format_size(hist_task.total_size)
                    result.append(f"({size})\n", style="dim #6b7280")
                else:
                    result.append(f"({hist_metrics.progress_percent:.0f}%)\n", style="dim #6b7280")
        
        return result
