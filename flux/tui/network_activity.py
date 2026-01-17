"""
Enhanced network activity widget with side-by-side layout.
"""

from rich.console import RenderableType
from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from flux.core.engine import DownloadStatus


class NetworkActivityWidget(Static):
    """Network activity display with stats on left and graph on right."""
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        from collections import deque
        self.speed_history = deque(maxlen=60)
        self.current_speed = 0.0
        self.peak_speed = 0.1
        self.total_downloaded = 0
    
    def update_stats(self, speed: float, peak: float, total: int) -> None:
        """Update network statistics."""
        self.speed_history.append(speed)
        self.current_speed = speed
        if peak > 0:
            self.peak_speed = peak
        self.total_downloaded = total
        self.refresh()
    
    def _format_speed(self, speed: float) -> str:
        """Format speed in MB/s."""
        return f"{speed / (1024 * 1024):.2f} MB/s"
    
    def _format_size(self, size: int) -> str:
        """Format size in MB."""
        return f"{size / (1024 * 1024):.1f} MB"
    
    def render(self) -> RenderableType:
        """Render network activity with side-by-side layout."""
        # Create table for side-by-side layout
        table = Table.grid(padding=(0, 2))
        table.add_column(width=18)  # Stats column
        table.add_column()  # Graph column
        
        # Left side: Stats
        stats = Text()
        stats.append(f"▼ {self._format_speed(self.current_speed)}\n", style="bold #00d9ff")
        stats.append(f"  (3 Mbps)\n\n", style="dim #6b7280")
        stats.append(f"Top: {self.peak_speed:.2f}\n\n", style="#00d9ff")
        stats.append(f"Total: {self._format_size(self.total_downloaded)}", style="#00d9ff")
        
        # Right side: Graph with grid lines
        graph = self._render_graph()
        
        table.add_row(stats, graph)
        return table
    
    def _render_graph(self) -> Text:
        """Render vertical bar graph with grid lines and Y-axis."""
        result = Text()
        
        if not self.speed_history or self.peak_speed == 0:
            # Empty graph
            for i in range(15):
                result.append(" " * 50 + "\n")
            return result
        
        # Calculate max speed for Y-axis (round up to nice number)
        max_display = max(2.0, self.peak_speed / (1024 * 1024))  # Minimum 2 MB/s
        max_display = ((int(max_display) + 1) // 2 + 1) * 2  # Round to nearest 2
        
        # Render 15 rows (graph height)
        height = 15
        
        # Apply smoothing
        smoothed = list(self.speed_history)
        if len(smoothed) >= 3:
            window = 3
            temp = []
            for i in range(len(smoothed)):
                start = max(0, i - window + 1)
                window_data = smoothed[start:i+1]
                temp.append(sum(window_data) / len(window_data))
            smoothed = temp
        
        for row in range(height):
            # Y-axis label (every 5 rows)
            y_value_mb = max_display * (1 - row / (height - 1))
            
            # Grid line
            if row % 5 == 0:
                result.append(f"{y_value_mb:.1f} MB/s".rjust(10) + " ", style="dim #6b7280")
                result.append("─" * 40, style="dim #333333")
                result.append("\n")
            else:
                result.append(" " * 11, style="dim #6b7280")
                
                # Draw bars for this row
                for speed in smoothed:
                    speed_mb = speed / (1024 * 1024)
                    normalized = speed_mb / max_display  # 0-1 range
                    bar_height = normalized * (height - 1)
                    
                    # Check if this row should have a bar segment
                    row_threshold = (height - 1 - row) / (height - 1)
                    
                    if normalized >= row_threshold:
                        # Pick color based on intensity
                        if normalized > 0.9:
                            result.append("█", style="#ff006e")
                        elif normalized > 0.7:
                            result.append("█", style="#00d9ff")
                        else:
                            result.append("█", style="#00aaff")
                    else:
                        result.append(" ")
                
                result.append("\n")
        
        # Bottom axis label
        result.append(" " * 11 + "0 MB/s".ljust(40), style="dim #6b7280")
        
        return result


class NetworkBarChart(Static):
    """Legacy horizontal network bar - kept for compatibility."""
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        from collections import deque
        self.speed_history = deque(maxlen=60)
        self.peak_speed = 1.0
    
    def update_speed(self, speed: float, peak: float) -> None:
        """Update speed for visualization."""
        self.speed_history.append(speed)
        if peak > 0:
            self.peak_speed = peak
        self.refresh()
    
    def render(self) -> RenderableType:
        """Render as horizontal bar."""
        if not self.speed_history or self.peak_speed == 0:
            return Text("No active downloads", style="dim #555555")
        
        # Simple horizontal bar
        avg = sum(self.speed_history) / len(self.speed_history)
        ratio = avg / self.peak_speed if self.peak_speed > 0 else 0
        bar_width = int(ratio * 50)
        
        result = Text()
        result.append("█" * bar_width, style="#ff006e")
        result.append("░" * (50 - bar_width), style="dim #333333")
        
        return result
