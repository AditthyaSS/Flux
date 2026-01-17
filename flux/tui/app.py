"""
Main Textual TUI application for Flux.
"""

import asyncio
import os
from pathlib import Path
from typing import Optional

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Footer, Header, Static, TabbedContent, TabPane

from flux.core.engine import AdaptiveDownloadEngine, DownloadStatus, DownloadTask
from flux.tui.dialogs import AddDownloadDialog
from flux.tui.widgets import (
    ActivityLogWidget,
    FileDetailsPanel,
)
from flux.tui.network_widgets import DownloadListWidget
from flux.tui.network_activity import NetworkActivityWidget
from flux.tui.header_widgets import NetworkHealthIndicator, CreditMarquee


class FluxApp(App):
    """
    Main Flux TUI application.
    """
    
    CSS = """
    Screen {
        background: #0a0e14;
    }
    
    Header {
        display: none;
    }
    
    #header_bar {
        height: 2;
        background: #0a0e14;
        padding: 0 2;
        border-bottom: solid #1a2332;
    }
    
    #network_health {
        width: auto;
        min-width: 55;
        text-style: bold;
    }
    
    #credit_marquee {
        width: 1fr;
        text-align: right;
        text-style: bold;
    }
    
    #logo_panel {
        height: 8;
        background: #0a0e14;
        padding: 1 2;
    }
    
    #flux_logo {
        color: #ff006e;
        text-style: bold;
    }
    
    #server_status {
        color: #00d9ff;
        text-style: bold;
        margin-top: 1;
    }
    
    #main_grid {
        height: 1fr;
        background: #0a0e14;
        layout: grid;
        grid-size: 2 2;
        grid-columns: 1fr 1fr;
        grid-rows: 18 1fr;
    }
    
    #activity_container {
        background: #0a0e14;
        border: solid #00d9ff;
        padding: 1 2;
    }
    
    .section_title {
        color: #00d9ff;
        text-style: bold;
        background: #0a0e14;
        margin-bottom: 1;
    }
    
    ActivityLogWidget {
        background: #0a0e14;
        color: #00d9ff;
        border: none;
        height: 100%;
    }
    
    #network_container {
        background: #0a0e14;
        border: solid #00d9ff;
        padding: 1 2;
    }
    
    #network_title {
        color: #00d9ff;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #network_graph_display {
        height: 15;
        background: #0a0e14;
        margin-bottom: 1;
    }
    
    #network_stats {
        color: #00d9ff;
        text-style: bold;
        margin-top: 1;
    }
    
    #downloads_container {
        background: #0a0e14;
        border: solid #00d9ff;
        padding: 1 2;
    }
    
    #downloads_header {
        height: 3;
        margin-bottom: 1;
    }
    
    #downloads_tabs {
        color: #00d9ff;
        text-style: bold;
    }
    
    #downloads_list {
        height: 1fr;
        background: #0a0e14;
        color: #00d9ff;
    }
    
    #details_container {
        background: #0a0e14;
        border: solid #00d9ff;
        padding: 1 2;
    }
    
    #details_title {
        color: #00d9ff;
        text-style: bold;
        margin-bottom: 1;
    }
    
    FileDetailsPanel {
        height: 1fr;
        background: #0a0e14;
        overflow-y: auto;
        scrollbar-size-vertical: 1;
    }
    
    Footer {
        height: 3;
        background: #0a0e14;
        color: #00d9ff;
        border-top: solid #00d9ff;
    }
    
    Footer > .footer--key {
        background: #1a2332;
        color: #00d9ff;
        text-style: bold;
    }
    """
    
    TITLE = "Flux"
    BINDINGS = [
        ("a", "add_download", "Add"),
        ("s", "start", "Start"),
        ("p", "pause", "Pause"),
        ("r", "resume", "Resume"),
        ("o", "toggle_autostart", "Auto-Start"),
        ("left", "prev_tab", "← Tab"),
        ("right", "next_tab", "Tab →"),
        ("up", "prev_download", "↑"),
        ("down", "next_download", "↓"),
        ("tab", "focus_next", "Next Section"),
        ("shift+tab", "focus_prev", "Prev Section"),
        ("1", "focus_activity", "Activity"),
        ("2", "focus_network", "Network"),
        ("3", "focus_downloads", "Downloads"),
        ("4", "focus_details", "Details"),
        ("q", "quit", "Quit"),
    ]
    
    def __init__(self) -> None:
        """Initialize app."""
        super().__init__()
        self.engine = AdaptiveDownloadEngine()
        self.selected_download_id: Optional[str] = None
        self.current_tab_index = 1  # 0=Queued, 1=Active, 2=Done
        self.tab_names = ["Queued", "Active", "Done"]
        self.auto_start_enabled = True  # Auto-start new downloads by default
    
    def compose(self) -> ComposeResult:
        """Compose TUI layout."""
        # Logo panel at top
        with Container(id="logo_panel"):
            # Clean FLUX logo matching Surge style
            flux_logo = """ ███████╗██╗     ██╗   ██╗██╗  ██╗
 ██╔════╝██║     ██║   ██║╚██╗██╔╝
 █████╗  ██║     ██║   ██║ ╚███╔╝ 
 ██╔══╝  ██║     ██║   ██║ ██╔██╗ 
 ██║     ███████╗╚██████╔╝██╔╝ ██╗
 ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝"""
            yield Static(flux_logo, id="flux_logo")
            yield Static("● Server", id="server_status")
        
        # Header bar below logo with network health and credits
        with Horizontal(id="header_bar"):
            yield NetworkHealthIndicator(id="network_health")
            yield CreditMarquee(id="credit_marquee")
        
        # Main 2x2 grid layout
        with Container(id="main_grid"):
            # Top-left: Activity Log
            with Vertical(id="activity_container"):
                yield Static("Activity Log", classes="section_title")
                yield ActivityLogWidget(id="activity_log")
            
            # Top-right: Network Activity
            with Vertical(id="network_container"):
                yield Static("Network Activity", id="network_title")
                yield NetworkActivityWidget(id="network_display")
            
            # Bottom-left: Downloads
            with Vertical(id="downloads_container"):
                yield DownloadListWidget(id="downloads_list")
            
            # Bottom-right: File Details
            with Vertical(id="details_container"):
                yield Static("File Details", id="details_title")
                yield FileDetailsPanel(id="file_details")
        
        # Footer
        yield Footer()
    
    async def on_mount(self) -> None:
        """Initialize engine and start update loop."""
        # Start engine
        await self.engine.start()
        
        # Register event callback
        self.engine.on_event(self._handle_engine_event)
        
        # Start periodic UI updates (100ms)
        self.set_interval(0.1, self._update_ui)
        """Start UI update loop."""
        self.set_interval(0.5, self._update_ui)  # Update every 500ms for better performance  
    def _handle_engine_event(self, event_type: str, data: dict) -> None:
        """
        Handle events from download engine.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        log = self.query_one("#activity_log", ActivityLogWidget)
        
        if event_type == "download_added":
            log.write(f"[#00ff41]Added: {data['filename']}[/#00ff41]")
        
        elif event_type == "download_started":
            download_id = data["download_id"]
            task = self.engine.get_download(download_id)
            if task:
                timestamp = __import__("time").strftime("%H:%M:%S")
                log.write(f"[#00ff41][{timestamp}] 1 Started: {task.filename}[/#00ff41]")
        
        elif event_type == "download_completed":
            log.write(f"[#00ff41]Completed: {data['filepath']}[/#00ff41]")
            
            # Auto-start next queued download
            queued = self.engine.get_downloads_by_status(DownloadStatus.QUEUED)
            if queued:
                asyncio.create_task(self.engine.start_download(queued[0].id))
        
        elif event_type == "download_failed":
            error_msg = data.get('error', 'Unknown error')
            filename = data.get('filename', 'download')
            log.write(f"[#ff0000]Failed: {filename} - {error_msg}[/#ff0000]")
        
        elif event_type == "download_paused":
            download_id = data["download_id"]
            task = self.engine.get_download(download_id)
            if task:
                log.write(f"[#ffaa00]Paused: {task.filename}[/#ffaa00]")
        
        elif event_type == "download_cancelled":
            download_id = data["download_id"]
            task = self.engine.get_download(download_id)
            if task:
                log.write(f"[dim #555555]Cancelled: {task.filename}[/dim #555555]")
    
    def _update_ui(self) -> None:
        """Update all UI components with latest data."""
        try:
            # Update network activity widget
            network_widget = self.query_one("#network_display", NetworkActivityWidget)
            
            # Aggregate speeds from all active downloads
            active = self.engine.get_downloads_by_status(DownloadStatus.ACTIVE)
            all_downloads = list(self.engine.downloads.values())
            
            if active:
                total_speed = sum(t.metrics.current_speed for t in active)
                peak_speed = max(t.metrics.peak_speed for t in active)
                total_downloaded = sum(t.metrics.bytes_downloaded for t in active)
                
                network_widget.update_stats(total_speed, peak_speed, total_downloaded)
                
                # Update network health indicator
                health_widget = self.query_one("#network_health", NetworkHealthIndicator)
                avg_rtt = sum(t.metrics.rtt_ms for t in active) / len(active)
                total_retries = sum(t.metrics.retry_count for t in active)
                total_errors = sum(t.metrics.error_count for t in active)
                total_ops = max(1, sum(t.metrics.bytes_downloaded // (1024 * 1024) for t in active))
                retry_rate = total_retries / total_ops if total_ops > 0 else 0
                loss_rate = total_errors / total_ops if total_ops > 0 else 0
                health_widget.update_health(avg_rtt, retry_rate, loss_rate)
            else:
                network_widget.update_stats(0, 0.1, 0)
                # Reset health indicator when no active downloads
                health_widget = self.query_one("#network_health", NetworkHealthIndicator)
                health_widget.update_health(0, 0, 0)
            
            # Update download list
            downloads_widget = self.query_one("#downloads_list", DownloadListWidget)
            current_filter = self.tab_names[self.current_tab_index]
            downloads_widget.set_downloads(all_downloads, current_filter, self.selected_download_id)
            
            # CRITICAL FIX: Smart auto-switching for file details
            details = self.query_one("#file_details", FileDetailsPanel)
            
            if self.selected_download_id:
                # Get fresh task data
                task = self.engine.get_download(self.selected_download_id)
                if task:
                    # Check if current selection is completed/failed - auto-switch to active
                    if task.status in [DownloadStatus.COMPLETED, DownloadStatus.FAILED] and active:
                        # Move completed to history and switch to first active
                        details.update_task(task)  # This will move it to history
                        self.selected_download_id = active[0].id
                        details.update_task(active[0])  # Switch to new active
                    else:
                        # Normal update
                        details.update_task(task)
                else:
                    # Selection is invalid, clear it
                    self.selected_download_id = None
                    details.update_task(None)
            
            # Auto-select first download if nothing selected
            if not self.selected_download_id and all_downloads:
                # Try active first, then any download
                if active:
                    self.selected_download_id = active[0].id
                    details.update_task(active[0])
                else:
                    self.selected_download_id = all_downloads[0].id
                    details.update_task(all_downloads[0])
        except Exception as e:
            pass
    
    def _update_download_table(
        self, table_id: str, status: DownloadStatus
    ) -> None:
        """Update a download table."""
        try:
            table = self.query_one(f"#{table_id}", DownloadListTable)
            downloads = self.engine.get_downloads_by_status(status)
            
            # Clear and repopulate
            table.clear()
            for task in downloads:
                metrics = task.metrics
                
                # Format row
                filename = task.filename[:28] + "..." if len(task.filename) > 28 else task.filename
                progress = f"{metrics.progress_percent:.1f}%"
                speed = metrics.format_speed(metrics.current_speed)
                eta = metrics.format_eta(metrics.eta_seconds)
                status_text = task.status.value
                
                table.add_row(filename, progress, speed, eta, status_text, key=task.id)
        except Exception:
            pass
    
    def _update_network_graph(self) -> None:
        """Update network activity graph."""
        try:
            graph = self.query_one("#network_graph", NetworkGraph)
            stats = self.query_one("#network_stats", Static)
            
            # Aggregate speeds from all active downloads
            active = self.engine.get_downloads_by_status(DownloadStatus.ACTIVE)
            
            if active:
                total_speed = sum(t.metrics.current_speed for t in active)
                peak_speed = max(t.metrics.peak_speed for t in active)
                
                # Collect all speed histories
                all_speeds = []
                for task in active:
                    all_speeds.extend(list(task.metrics.speed_history))
                
                graph.update_speeds(all_speeds[-40:], peak_speed)
                
                # Update stats
                speed_str = active[0].metrics.format_speed(total_speed)
                peak_str = active[0].metrics.format_speed(peak_speed)
                total_downloaded = sum(t.metrics.bytes_downloaded for t in active)
                size_str = active[0].metrics.format_size(total_downloaded)
                
                stats.update(
                    f"Speed: [bold green]{speed_str}[/bold green]  "
                    f"Peak: [yellow]{peak_str}[/yellow]  "
                    f"Downloaded: [cyan]{size_str}[/cyan]"
                )
            else:
                stats.update("[dim]No active downloads[/dim]")
        except Exception:
            pass
    
    def _update_file_details(self) -> None:
        """Update file details panel."""
        try:
            details = self.query_one("#file_details", FileDetailsPanel)
            
            if self.selected_download_id:
                task = self.engine.get_download(self.selected_download_id)
                details.update_task(task)
            else:
                # Auto-select first active download
                active = self.engine.get_downloads_by_status(DownloadStatus.ACTIVE)
                if active:
                    self.selected_download_id = active[0].id
                    details.update_task(active[0])
        except Exception:
            pass
    
    @work(exclusive=True)
    async def action_add_download(self) -> None:
        """Show add download dialog."""
        # Pause marquee while dialog is open
        try:
            marquee = self.query_one("#credit_marquee", CreditMarquee)
            marquee.pause()
        except Exception:
            pass
        
        result = await self.push_screen_wait(AddDownloadDialog())
        
        # Resume marquee after dialog closes
        try:
            marquee = self.query_one("#credit_marquee", CreditMarquee)
            marquee.resume()
        except Exception:
            pass
        
        if result:
            url, path, filename = result
            
            # Expand path
            path = os.path.expanduser(path)
            
            try:
                # Pass auto_start flag to engine - if OFF, download stays queued
                download_id = await self.engine.add_download(
                    url, path, filename, auto_start=self.auto_start_enabled
                )
                
                # Log appropriate message
                if not self.auto_start_enabled:
                    log = self.query_one("#activity_log", ActivityLogWidget)
                    log.write(f"[#ffaa00]Queued (auto-start OFF): {filename or 'download'}[/#ffaa00]")
            except Exception as e:
                log = self.query_one("#activity_log", ActivityLogWidget)
                log.write(f"[bold red]Error:[/bold red] {str(e)}")
    

    @work(exclusive=True)
    async def action_start(self) -> None:
        """Start a queued or paused download."""
        if not self.selected_download_id:
            # Try to find a queued or paused download to start
            queued = self.engine.get_downloads_by_status(DownloadStatus.QUEUED)
            paused = self.engine.get_downloads_by_status(DownloadStatus.PAUSED)
            available = queued + paused
            if available:
                self.selected_download_id = available[0].id
            else:
                return
        
        task = self.engine.get_download(self.selected_download_id)
        if not task or task.status not in [DownloadStatus.QUEUED, DownloadStatus.PAUSED]:
            return
        
        log = self.query_one("#activity_log", ActivityLogWidget)
        await self.engine.start_download(task.id)
        log.write(f"[#00ff41]▶ Started: {task.filename}[/#00ff41]")
    
    @work(exclusive=True)
    async def action_pause(self) -> None:
        """Pause an active download."""
        if not self.selected_download_id:
            active = self.engine.get_downloads_by_status(DownloadStatus.ACTIVE)
            if active:
                self.selected_download_id = active[0].id
            else:
                return
        
        task = self.engine.get_download(self.selected_download_id)
        if not task or task.status != DownloadStatus.ACTIVE:
            return
        
        log = self.query_one("#activity_log", ActivityLogWidget)
        await self.engine.pause_download(task.id)
        log.write(f"[#ffaa00]⏸ Paused: {task.filename}[/#ffaa00]")
    
    @work(exclusive=True)
    async def action_resume(self) -> None:
        """Resume a paused download."""
        if not self.selected_download_id:
            paused = self.engine.get_downloads_by_status(DownloadStatus.PAUSED)
            if paused:
                self.selected_download_id = paused[0].id
            else:
                return
        
        task = self.engine.get_download(self.selected_download_id)
        if not task or task.status != DownloadStatus.PAUSED:
            return
        
        log = self.query_one("#activity_log", ActivityLogWidget)
        await self.engine.start_download(task.id)
        log.write(f"[#00ff41]▶ Resumed: {task.filename}[/#00ff41]")
    
    def action_show_details(self) -> None:
        """Show details panel (already visible, just focus)."""
        pass
    
    
    def action_prev_tab(self) -> None:
        """Switch to previous tab (Done → Active → Queued → Done)."""
        self.current_tab_index = (self.current_tab_index - 1) % 3
        
        log = self.query_one("#activity_log", ActivityLogWidget)
        log.write(f"[dim #00ff41]Switched to: {self.tab_names[self.current_tab_index]}[/dim #00ff41]")
    
    def action_next_tab(self) -> None:
        """Switch to next tab (Queued → Active → Done → Queued)."""
        self.current_tab_index = (self.current_tab_index + 1) % 3
        
        log = self.query_one("#activity_log", ActivityLogWidget)
        log.write(f"[dim #00ff41]Switched to: {self.tab_names[self.current_tab_index]}[/dim #00ff41]")
    
    def action_next_download(self) -> None:
        """Select next download in current tab."""
        # If downloads list has focus, let DataTable handle arrow keys natively
        try:
            downloads_widget = self.query_one("#downloads_list", DownloadListWidget)
            if downloads_widget.has_focus:
                return
        except Exception:
            pass
        
        all_downloads = list(self.engine.downloads.values())
        current_filter = self.tab_names[self.current_tab_index]
        
        # Filter downloads based on current tab
        if current_filter == "Active":
            filtered = [d for d in all_downloads if d.status == DownloadStatus.ACTIVE]
        elif current_filter == "Queued":
            filtered = [d for d in all_downloads if d.status in [DownloadStatus.QUEUED, DownloadStatus.PAUSED]]
        else:  # Done
            filtered = [d for d in all_downloads if d.status == DownloadStatus.COMPLETED]
        
        if not filtered:
            return
        
        # Find current index and move to next
        if self.selected_download_id:
            try:
                current_idx = [d.id for d in filtered].index(self.selected_download_id)
                next_idx = (current_idx + 1) % len(filtered)
                self.selected_download_id = filtered[next_idx].id
            except ValueError:
                self.selected_download_id = filtered[0].id
        else:
            self.selected_download_id = filtered[0].id
    
    def action_prev_download(self) -> None:
        """Select previous download in current tab."""
        # If downloads list has focus, let DataTable handle arrow keys natively
        try:
            downloads_widget = self.query_one("#downloads_list", DownloadListWidget)
            if downloads_widget.has_focus:
                return
        except Exception:
            pass
        
        all_downloads = list(self.engine.downloads.values())
        current_filter = self.tab_names[self.current_tab_index]
        
        # Filter downloads based on current tab
        if current_filter == "Active":
            filtered = [d for d in all_downloads if d.status == DownloadStatus.ACTIVE]
        elif current_filter == "Queued":
            filtered = [d for d in all_downloads if d.status in [DownloadStatus.QUEUED, DownloadStatus.PAUSED]]
        else:  # Done
            filtered = [d for d in all_downloads if d.status == DownloadStatus.COMPLETED]
        
        if not filtered:
            return
        
        # Find current index and move to previous
        if self.selected_download_id:
            try:
                current_idx = [d.id for d in filtered].index(self.selected_download_id)
                prev_idx = (current_idx - 1) % len(filtered)
                self.selected_download_id = filtered[prev_idx].id
            except ValueError:
                self.selected_download_id = filtered[0].id
        else:
            self.selected_download_id = filtered[0].id
    
    def action_toggle_autostart(self) -> None:
        """Toggle auto-start for new downloads."""
        self.auto_start_enabled = not self.auto_start_enabled
        log = self.query_one("#activity_log", ActivityLogWidget)
        status = "ON" if self.auto_start_enabled else "OFF"
        log.write(f"[#00d9ff]Auto-start: {status}[/#00d9ff]")
    
    def action_focus_next(self) -> None:
        """Focus next section (Tab key)."""
        try:
            sections = ["#activity_log", "#downloads_list"]
            for section_id in sections:
                widget = self.query_one(section_id)
                if widget.has_focus:
                    idx = sections.index(section_id)
                    next_id = sections[(idx + 1) % len(sections)]
                    self.query_one(next_id).focus()
                    return
            # Default: focus first
            self.query_one(sections[0]).focus()
        except Exception:
            pass
    
    def action_focus_prev(self) -> None:
        """Focus previous section (Shift+Tab)."""
        try:
            sections = ["#activity_log", "#downloads_list"]
            for section_id in sections:
                widget = self.query_one(section_id)
                if widget.has_focus:
                    idx = sections.index(section_id)
                    prev_id = sections[(idx - 1) % len(sections)]
                    self.query_one(prev_id).focus()
                    return
            # Default: focus last
            self.query_one(sections[-1]).focus()
        except Exception:
            pass
    
    def action_focus_activity(self) -> None:
        """Focus Activity Log (1 key)."""
        try:
            self.query_one("#activity_log").focus()
        except Exception:
            pass
    
    def action_focus_network(self) -> None:
        """Focus Network Activity (2 key) - read-only."""
        log = self.query_one("#activity_log", ActivityLogWidget)
        log.write("[dim #6b7280]Network is read-only, use 1 or 3[/dim #6b7280]")
    
    def action_focus_downloads(self) -> None:
        """Focus Downloads (3 key)."""
        try:
            self.query_one("#downloads_list").focus()
        except Exception:
            pass
    
    def action_focus_details(self) -> None:
        """Focus File Details (4 key) - read-only."""
        log = self.query_one("#activity_log", ActivityLogWidget)
        log.write("[dim #6b7280]File Details is read-only, use 1 or 3[/dim #6b7280]")
    
    @work(exclusive=True)
    async def action_quit(self) -> None:
        """Quit application with proper cleanup."""
        try:
            # Stop the engine to close HTTP client session
            await self.engine.stop()
        except Exception:
            pass
        self.exit()
    
    async def on_unmount(self) -> None:
        """Cleanup when app is unmounted."""
        try:
            await self.engine.stop()
        except Exception:
            pass


def main() -> None:
    """Entry point for Flux TUI."""
    app = FluxApp()
    app.run()


if __name__ == "__main__":
    main()
