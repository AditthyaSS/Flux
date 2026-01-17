"""
Modal dialog for adding downloads.
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class AddDownloadDialog(ModalScreen[tuple[str, str, str] | None]):
    """
    Modal dialog for adding a new download.
    
    Returns tuple of (url, path, filename) or None if cancelled.
    """
    
    DEFAULT_BORDER_TITLE = "Add Download"
    CSS = """
    AddDownloadDialog {
        align: center middle;
    }
    
    AddDownloadDialog > Container {
        width: 70;
        height: auto;
        border: heavy #00d9ff;
        background: #0a0e14;
        padding: 2;
    }
    
    AddDownloadDialog Static.title {
        text-align: center;
        color: #00d9ff;
        text-style: bold;
        margin-bottom: 1;
    }
    
    AddDownloadDialog Label {
        margin-bottom: 1;
        margin-top: 1;
        color: #00d9ff;
        text-style: bold;
    }
    
    AddDownloadDialog Input {
        margin-bottom: 1;
        background: #0f1419;
        border: solid #00d9ff;
        color: #00d9ff;
    }
    
    AddDownloadDialog Input:focus {
        border: heavy #ff006e;
        background: #1a2332;
    }
    
    AddDownloadDialog .buttons {
        height: auto;
        align: center middle;
        margin-top: 2;
    }
    
    AddDownloadDialog Button {
        margin: 0 1;
        background: #0f1419;
        color: #00d9ff;
        border: solid #00d9ff;
    }
    
    AddDownloadDialog Button:hover {
        background: #1a2332;
        color: #ff006e;
        border: heavy #ff006e;
    }
    
    AddDownloadDialog Button.-primary {
        background: #1a2332;
        color: #ff006e;
        text-style: bold;
        border: heavy #ff006e;
    }
    """
    
    def __init__(self) -> None:
        """Initialize dialog."""
        super().__init__()
        self.default_path = "~/Downloads"
    
    def compose(self) -> ComposeResult:
        """Compose dialog widgets."""
        with Container():
            yield Static("━━━ Add Download ━━━", classes="title")
            yield Label("URL:")
            yield Input(
                placeholder="https://example.com/file.zip",
                id="url_input",
            )
            yield Label("Download Path:")
            yield Input(
                value=self.default_path,
                id="path_input",
            )
            yield Label("Filename (auto-detect if empty):")
            yield Input(
                placeholder="Leave empty for auto-detect",
                id="filename_input",
            )
            
            with Vertical(classes="buttons"):
                yield Button("⚡ Start Download", variant="primary", id="start_btn")
                yield Button("Cancel", variant="default", id="cancel_btn")
    
    def on_mount(self) -> None:
        """Focus URL input on mount."""
        self.query_one("#url_input", Input).focus()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "start_btn":
            self._submit()
        elif event.button.id == "cancel_btn":
            self.dismiss(None)
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in inputs."""
        self._submit()
    
    def _submit(self) -> None:
        """Submit dialog with inputs."""
        url = self.query_one("#url_input", Input).value.strip()
        path = self.query_one("#path_input", Input).value.strip()
        filename = self.query_one("#filename_input", Input).value.strip()
        
        # Validate URL
        if not url:
            return
        
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        # Use defaults if needed
        if not path:
            path = self.default_path
        
        # Empty filename means auto-detect
        if not filename:
            filename = None
        
        self.dismiss((url, path, filename))
    
    def key_escape(self) -> None:
        """Handle Escape key."""
        self.dismiss(None)
