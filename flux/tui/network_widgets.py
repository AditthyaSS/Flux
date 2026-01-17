"""
Network visualization widget using vertical bar chart.
"""

from rich.console import RenderableType
from rich.text import Text
from textual.widgets import Static

from flux.core.engine import DownloadStatus


class NetworkBarChart(Static):
    """Enhanced network visualization with gradient colors."""
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        from collections import deque
        self.speed_history = deque(maxlen=60)  # Fixed 60-sample window
        self.peak_speed = 1.0
    
    def update_speed(self, speed: float, peak: float) -> None:
        """Update speed for visualization."""
        self.speed_history.append(speed)
        
        if peak > 0:
            self.peak_speed = peak
        self.refresh()
    
    def _rolling_average(self, data, window=5):
        """Calculate rolling average to smooth spikes."""
        if len(data) < window:
            return list(data)
        
        smoothed = []
        data_list = list(data)
        for i in range(len(data_list)):
            start = max(0, i - window + 1)
            window_data = data_list[start:i+1]
            smoothed.append(sum(window_data) / len(window_data))
        return smoothed
    
    def render(self) -> RenderableType:
        """Render network activity with gradient colors and enhanced theming."""
        if not self.speed_history or self.peak_speed == 0:
            return Text("No active downloads", style="dim #555555")
        
        # Apply rolling average for smoothing
        smoothed = self._rolling_average(self.speed_history, window=5)
        
        # Clamp spikes to 2x average
        avg = sum(smoothed) / len(smoothed) if smoothed else 1.0
        max_allowed = avg * 2
        clamped = [min(s, max_allowed) for s in smoothed]
        
        result = Text()
        
        # Use bars at varying heights with gradient color mapping
        max_val = max(clamped) if clamped else 1.0
        
        for speed in clamped:
            ratio = speed / max_val if max_val > 0 else 0
            
            # Gradient color scheme: dim cyan -> bright cyan -> magenta for peak intensity
            if ratio > 0.9:
                # Peak: bright magenta
                result.append("█", style="#ff006e")
            elif ratio > 0.8:
                # Very high: bright cyan
                result.append("█", style="#00d9ff")
            elif ratio > 0.7:
                # High: cyan
                result.append("█", style="#00aaff")
            elif ratio > 0.5:
                # Medium-high: lighter cyan with slightly shorter bar
                result.append("▇", style="#00aaff")
            elif ratio > 0.35:
                # Medium: normal cyan
                result.append("▆", style="#0099ee")
            elif ratio > 0.2:
                # Low-medium: half bar
                result.append("▄", style="#0088dd")
            elif ratio > 0.1:
                # Low: small bar
                result.append("▂", style="#0077cc")
            elif ratio > 0.05:
                # Very low: minimal
                result.append("▁", style="dim #0066bb")
            else:
                # Idle: barely visible
                result.append("▁", style="dim #555555")
        
        return result


class DownloadListWidget(Static):
    """Custom download list widget with navigation support."""
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.downloads = []
        self.current_filter = "Active"
        self.selected_id = None  # Track selected download
    
    def set_downloads(self, downloads: list, filter_type: str, selected_id: str = None) -> None:
        """Update download list with selection."""
        self.downloads = downloads
        self.current_filter = filter_type
        self.selected_id = selected_id
        self.refresh()
    
    def render(self) -> RenderableType:
        """Render download list."""
        result = Text()
        
        # Count downloads by status
        queued_count = len([d for d in self.downloads if d.status in [DownloadStatus.QUEUED, DownloadStatus.PAUSED]])
        active_count = len([d for d in self.downloads if d.status == DownloadStatus.ACTIVE])
        done_count = len([d for d in self.downloads if d.status == DownloadStatus.COMPLETED])
        
        # Header with tabs
        result.append("Downloads\n", style="bold #00d9ff")
        
        # Tab buttons
        if self.current_filter == "Queued":
            result.append(f"Queued ({queued_count})  ", style="bold #00d9ff")
        else:
            result.append(f"Queued ({queued_count})  ", style="dim #6b7280")
            
        if self.current_filter == "Active":
            result.append(f"Active ({active_count})  ", style="bold #00d9ff")
        else:
            result.append(f"Active ({active_count})  ", style="dim #6b7280")
            
        if self.current_filter == "Done":
            result.append(f"Done ({done_count})\n\n", style="bold #00d9ff")
        else:
            result.append(f"Done ({done_count})\n\n", style="dim #6b7280")
        
        # Filter and display downloads
        displayed = 0
        for task in self.downloads:
            # Apply filter
            show = False
            if self.current_filter == "Active" and task.status == DownloadStatus.ACTIVE:
                show = True
            elif self.current_filter == "Queued" and task.status in [DownloadStatus.QUEUED, DownloadStatus.PAUSED]:
                show = True
            elif self.current_filter == "Done" and task.status == DownloadStatus.COMPLETED:
                show = True
            
            if not show:
                continue
            
            # Render download item
            metrics = task.metrics
            progress = metrics.progress_percent
            speed = metrics.format_speed(metrics.current_speed)
            eta = metrics.format_eta(metrics.eta_seconds)
            
            # Selection cursor
            is_selected = (self.selected_id == task.id)
            if is_selected:
                result.append("▶ ", style="bold #00ff41")
            else:
                result.append("  ")
            
            # Status indicator
            if task.status == DownloadStatus.ACTIVE:
                result.append("● ", style="bold #00d9ff")
                status_text = f"Downloading • {progress:.0f}% • {speed} • {eta}"
            elif task.status == DownloadStatus.PAUSED:
                result.append("⏸ ", style="bold #ff006e")
                status_text = f"Paused • {progress:.0f}% • {metrics.format_size(task.metrics.bytes_downloaded)}"
            elif task.status == DownloadStatus.COMPLETED:
                result.append("✓ ", style="bold #00d9ff")
                total_size = metrics.format_size(task.total_size)
                status_text = f"Complete  • {total_size}"
            elif task.status == DownloadStatus.QUEUED:
                result.append("○ ", style="dim #6b7280")
                status_text = "Queued"
            elif task.status == DownloadStatus.FAILED:
                result.append("✗ ", style="bold #ff006e")
                status_text = f"Failed: {task.error_message or 'Unknown error'}"
            else:
                result.append("○ ", style="dim #6b7280")
                status_text = task.status.value
            
            # Filename (truncate if too long, highlight if selected)
            filename = task.filename if len(task.filename) <= 35 else task.filename[:32] + "..."
            filename_style = "bold reverse #00d9ff" if is_selected else "bold #00d9ff"
            result.append(f"{filename}\n", style=filename_style)
            
            # Status details
            status_style = "reverse #00d9ff" if is_selected else "#00d9ff"
            result.append(f"     {status_text}\n", style=status_style)
            displayed += 1
        
        if displayed == 0:
            result.append("No downloads", style="dim #555555")
        
        return result
