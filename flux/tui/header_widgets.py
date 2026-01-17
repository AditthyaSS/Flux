"""
Header widgets for Flux TUI - Network Health Indicator and Credit Marquee.
"""

from rich.console import RenderableType
from rich.text import Text
from textual.widgets import Static
from textual.timer import Timer
from typing import Optional


class NetworkHealthIndicator(Static):
    """
    Real-time network health indicator displaying quality dots.
    
    Format: Network Health: ●●●○○ (Good)   RTT: 92ms | Loss: 0.4%
    
    Color coding:
    - 4-5 dots → Green (Good)
    - 2-3 dots → Yellow (Moderate)
    - 0-1 dot → Red (Poor)
    """
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._rtt_ms: float = 0.0
        self._retry_rate: float = 0.0
        self._loss_rate: float = 0.0
        self._quality_dots: int = 5  # 0-5
        self._prev_dots: int = 5  # For smooth transitions
        
    def update_health(self, rtt_ms: float, retry_rate: float, loss_rate: float) -> None:
        """
        Update network health metrics.
        
        Args:
            rtt_ms: Round-trip time in milliseconds
            retry_rate: Retry rate (0.0 - 1.0)
            loss_rate: Estimated packet loss rate (0.0 - 1.0)
        """
        self._rtt_ms = rtt_ms
        self._retry_rate = retry_rate
        self._loss_rate = loss_rate
        
        # Calculate quality score (0-5 dots)
        # Based on RTT, retry rate, and loss rate
        score = 5.0
        
        # RTT penalty: >500ms is bad, <50ms is excellent
        if rtt_ms > 500:
            score -= 2.0
        elif rtt_ms > 200:
            score -= 1.0
        elif rtt_ms > 100:
            score -= 0.5
        
        # Retry rate penalty
        score -= retry_rate * 2.0
        
        # Loss rate penalty
        score -= loss_rate * 3.0
        
        # Clamp to 0-5
        new_dots = max(0, min(5, int(round(score))))
        
        # Smooth transition (only change by 1 at a time)
        if new_dots > self._quality_dots:
            self._quality_dots = min(self._quality_dots + 1, new_dots)
        elif new_dots < self._quality_dots:
            self._quality_dots = max(self._quality_dots - 1, new_dots)
        
        self.refresh()
    
    def render(self) -> RenderableType:
        """Render the network health indicator."""
        result = Text()
        
        # Determine quality level and colors (slightly muted for dark theme)
        dots = self._quality_dots
        if dots >= 4:
            dot_color = "#00cc33"  # Muted Green
            quality_text = "Good"
            quality_color = "#00cc33"
        elif dots >= 2:
            dot_color = "#cc8800"  # Muted Yellow
            quality_text = "Moderate"
            quality_color = "#cc8800"
        else:
            dot_color = "#cc0055"  # Muted Red
            quality_text = "Poor"
            quality_color = "#cc0055"
        
        # Build the indicator
        result.append("Network Health: ", style="#4a5568")
        
        # Filled dots
        for _ in range(dots):
            result.append("●", style=dot_color)
        
        # Empty dots
        for _ in range(5 - dots):
            result.append("○", style="#3d4451")
        
        # Quality text
        result.append(f" ({quality_text})", style=quality_color)
        
        # Separator
        result.append("   ", style="#3d4451")
        
        # RTT display
        rtt_display = f"{self._rtt_ms:.0f}ms" if self._rtt_ms > 0 else "--"
        result.append(f"RTT: {rtt_display}", style="#4a5568")
        
        result.append(" | ", style="#3d4451")
        
        # Loss display
        loss_display = f"{self._loss_rate * 100:.1f}%" if self._loss_rate >= 0 else "--"
        result.append(f"Loss: {loss_display}", style="#4a5568")
        
        return result


class CreditMarquee(Static):
    """
    Horizontal scrolling credit marquee.
    
    Text: Made by Aditthya S S • Built with love for open source • Flux is free and open-source
    
    Scrolls slowly, loops infinitely, pauses when dialogs are open.
    """
    
    CREDIT_TEXT = "Made by Aditthya S S • Built with love for open source • Flux is free and open-source"
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._scroll_offset: int = 0
        self._paused: bool = False
        self._timer: Optional[Timer] = None
        self._display_width: int = 50  # Characters to display
        
        # Add padding for seamless loop
        self._full_text = self.CREDIT_TEXT + "   •   " + self.CREDIT_TEXT
    
    def on_mount(self) -> None:
        """Start the scrolling animation."""
        # Scroll every 300ms (slow, readable)
        self._timer = self.set_interval(0.3, self._scroll_step)
    
    def _scroll_step(self) -> None:
        """Advance scroll position by one character."""
        if self._paused:
            return
        
        self._scroll_offset += 1
        
        # Reset when we've scrolled through the first copy of the text
        if self._scroll_offset >= len(self.CREDIT_TEXT) + 7:  # 7 = len("   •   ")
            self._scroll_offset = 0
        
        self.refresh()
    
    def pause(self) -> None:
        """Pause the marquee scrolling."""
        self._paused = True
    
    def resume(self) -> None:
        """Resume the marquee scrolling."""
        self._paused = False
    
    def render(self) -> RenderableType:
        """Render the scrolling marquee."""
        # Get visible portion of text
        start = self._scroll_offset
        end = start + self._display_width
        
        # Handle wrapping
        if end <= len(self._full_text):
            visible = self._full_text[start:end]
        else:
            # Wrap around
            visible = self._full_text[start:] + self._full_text[:end - len(self._full_text)]
        
        return Text(visible, style="#4a5568")
