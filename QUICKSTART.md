# Quick Start Guide

## Launch Flux

To start the Flux terminal dashboard:

```bash
flux
```

This will launch the full-screen TUI interface.

## First Download

1. Press `a` to open the Add Download dialog
2. Enter a URL (e.g., `https://speed.hetzner.de/100MB.bin`)
3. Set download path (default: `~/Downloads`)
4. Press Enter to start

Watch as Flux:
- Downloads with adaptive multi-connection
- Shows real-time speed graphs
- Explains every optimization decision
- Updates progress live (100ms refresh)

## Keyboard Commands

- `a` - Add new download
- `p` - Pause/Resume selected download
- `↑↓` - Navigate downloads
- `Tab` - Switch between panels
- `q` - Quit Flux

## CLI Mode

For headless usage:

```bash
flux-cli download https://example.com/file.zip --output ~/Downloads
```

## Next Steps

- Try pausing and resuming downloads
- Watch the "Explainable Intelligence" panel for adaptive decisions
- Observe the network graph animate
- Test resume capability by cancelling and restarting

Enjoy Flux! 🚀
