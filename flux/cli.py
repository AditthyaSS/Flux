"""
CLI interface for headless usage.
"""

import asyncio
import sys
from pathlib import Path

import click

from flux.core.engine import AdaptiveDownloadEngine, DownloadStatus


@click.group()
@click.version_option(version="1.0.0")
def cli() -> None:
    """Flux CLI - Headless download manager."""
    pass


@cli.command()
@click.argument("url")
@click.option(
    "--output", "-o", default="~/Downloads", help="Output directory"
)
@click.option("--filename", "-f", default=None, help="Custom filename")
def download(url: str, output: str, filename: str | None) -> None:
    """Download a file via CLI."""
    asyncio.run(_download_file(url, output, filename))


async def _download_file(url: str, output: str, filename: str | None) -> None:
    """Async download implementation."""
    output_path = Path(output).expanduser()
    
    engine = AdaptiveDownloadEngine()
    await engine.start()
    
    # Register progress callback
    def on_event(event_type: str, data: dict) -> None:
        if event_type == "download_progress":
            download_id = data["download_id"]
            task = engine.get_download(download_id)
            if task:
                metrics = task.metrics
                progress = metrics.progress_percent
                speed = metrics.format_speed(metrics.current_speed)
                eta = metrics.format_eta(metrics.eta_seconds)
                
                # Print progress
                sys.stdout.write(
                    f"\r[{task.filename}] {progress:.1f}% @ {speed} - ETA: {eta}      "
                )
                sys.stdout.flush()
        
        elif event_type == "download_completed":
            print(f"\n✓ Download completed: {data['filepath']}")
        
        elif event_type == "download_failed":
            print(f"\n✗ Download failed: {data['error']}", file=sys.stderr)
    
    engine.on_event(on_event)
    
    try:
        download_id = await engine.add_download(url, str(output_path), filename)
        
        # Wait for completion
        while True:
            task = engine.get_download(download_id)
            if not task:
                break
            
            if task.status in (
                DownloadStatus.COMPLETED,
                DownloadStatus.FAILED,
                DownloadStatus.CANCELLED,
            ):
                break
            
            await asyncio.sleep(0.5)
    
    finally:
        await engine.stop()


@cli.command()
def list() -> None:
    """List recent downloads (not implemented in CLI)."""
    click.echo("List command only available in TUI mode. Run 'flux' to launch TUI.")


@cli.command()
@click.argument("output_file", default="decisions.json")
def export_decisions(output_file: str) -> None:
    """Export adaptive decisions (not implemented in CLI)."""
    click.echo(
        "Export command only available in TUI mode. Run 'flux' to launch TUI."
    )


def main() -> None:
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
