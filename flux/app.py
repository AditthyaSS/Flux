"""
Main entry point for Flux application.
"""


def main() -> None:
    """Launch Flux TUI dashboard."""
    from flux.tui.app import FluxApp
    
    app = FluxApp()
    app.run()


if __name__ == "__main__":
    main()
