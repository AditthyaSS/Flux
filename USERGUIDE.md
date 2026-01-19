<div align="center">

```
 ██╗   ██╗███████╗███████╗██████╗      ██████╗ ██╗   ██╗██╗██████╗ ███████╗
 ██║   ██║██╔════╝██╔════╝██╔══██╗    ██╔════╝ ██║   ██║██║██╔══██╗██╔════╝
 ██║   ██║███████╗█████╗  ██████╔╝    ██║  ███╗██║   ██║██║██║  ██║█████╗  
 ██║   ██║╚════██║██╔══╝  ██╔══██╗    ██║   ██║██║   ██║██║██║  ██║██╔══╝  
 ╚██████╔╝███████║███████╗██║  ██║    ╚██████╔╝╚██████╔╝██║██████╔╝███████╗
  ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝     ╚═════╝  ╚═════╝ ╚═╝╚═════╝ ╚══════╝
```

### Complete Guide to Using Flux Download Manager

</div>

---

## 📋 Table of Contents

1. [Prerequisites](#-prerequisites)
2. [Installation](#-installation)
3. [Launching Flux](#-launching-flux)
4. [Understanding the Interface](#-understanding-the-interface)
5. [Your First Download](#-your-first-download)
6. [Managing Downloads](#-managing-downloads)
7. [Keyboard Shortcuts](#%EF%B8%8F-keyboard-shortcuts)
8. [Understanding Network Health](#-understanding-network-health)
9. [Advanced Features](#-advanced-features)
10. [Troubleshooting](#-troubleshooting)

---

## 📦 Prerequisites

Before installing Flux, make sure you have:

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Python | 3.10 or higher | `python --version` |
| pip | Latest | `pip --version` |
| Terminal | Any modern terminal | - |

> 💡 **Windows Users**: Use PowerShell or Windows Terminal for the best experience.

---

## 🔧 Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install flux-download
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/aditthyass/flux.git

# Navigate to the directory
cd flux

# Install in editable mode
pip install -e .
```

### Option 3: Download Binary (No Python Required)

Download the pre-built binary for your platform:

| Platform | Download |
|----------|----------|
| Windows | `flux.exe` |
| Linux | `flux` |
| macOS | `flux` |

### ✅ Verify Installation

```bash
flux --version
```

You should see:
```
Flux Download Manager v1.0.0
```

---

## 🚀 Launching Flux

### Start the TUI Dashboard

```bash
flux
```

Or if running from source:

```bash
python -c "from flux.app import main; main()"
```

### What You'll See

```
┌──────────────────────────────────────────────────────────────────────┐
│  ███████╗██╗     ██╗   ██╗██╗  ██╗                                   │
│  ██╔════╝██║     ██║   ██║╚██╗██╔╝     ● Server                     │
│  █████╗  ██║     ██║   ██║ ╚███╔╝                                    │
│  ██╔══╝  ██║     ██║   ██║ ██╔██╗                                    │
│  ██║     ███████╗╚██████╔╝██╔╝ ██╗                                   │
│  ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝                                   │
├──────────────────────────────────────────────────────────────────────┤
│  Network Health: ●●●●● (Good)   RTT: --   Made by Aditthya S S...   │
├──────────────────────────────────────────────────────────────────────┤
│ Activity Log          │ Network Activity                             │
│ Flux started...       │ No active downloads                          │
├───────────────────────┼──────────────────────────────────────────────┤
│ Downloads             │ File Details                                 │
│ No downloads          │ Select a download to view details            │
├──────────────────────────────────────────────────────────────────────┤
│ [A]dd [S]tart [P]ause [R]esume [O]Auto [←→]Tabs [↑↓]Nav [Q]uit      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Understanding the Interface

Flux has a **4-panel layout** designed for maximum productivity:

```
┌─────────────────────────────────────────────────────────────┐
│                        HEADER BAR                           │
│  Network Health: ●●●●● (Good)    Scrolling credit text...  │
├─────────────────────────┬───────────────────────────────────┤
│                         │                                   │
│    📋 ACTIVITY LOG      │    📊 NETWORK ACTIVITY           │
│                         │                                   │
│    Shows all events:    │    Live visualization:            │
│    • Downloads added    │    • Speed graph                  │
│    • Status changes     │    • Current speed                │
│    • Completions        │    • Peak speed                   │
│    • Errors             │    • Total downloaded             │
│                         │                                   │
├─────────────────────────┼───────────────────────────────────┤
│                         │                                   │
│    📁 DOWNLOADS LIST    │    📄 FILE DETAILS               │
│                         │                                   │
│    Three tabs:          │    Selected file info:            │
│    • Queued             │    • Progress bar                 │
│    • Active             │    • Speed stats                  │
│    • Done               │    • ETA & efficiency             │
│                         │    • Connection info              │
│                         │                                   │
├─────────────────────────┴───────────────────────────────────┤
│                      FOOTER (Shortcuts)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📥 Your First Download

### Step 1: Press `A` to Add a Download

A dialog will appear:

```
┌─────────────────────────────────────────┐
│            Add Download              ✕  │
├─────────────────────────────────────────┤
│                                         │
│  URL:                                   │
│  ┌─────────────────────────────────┐   │
│  │ https://example.com/file.zip   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Save to:                               │
│  ┌─────────────────────────────────┐   │
│  │ ~/Downloads                     │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Filename (optional):                   │
│  ┌─────────────────────────────────┐   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│        [ Cancel ]    [ Add ]           │
│                                         │
└─────────────────────────────────────────┘
```

### Step 2: Enter the Details

1. **URL**: Paste the download link
2. **Save to**: Choose download location (default: `~/Downloads`)
3. **Filename**: Optional custom name

### Step 3: Press `Tab` to navigate, `Enter` to confirm

The download will start automatically (if auto-start is ON).

### Step 4: Watch the Magic! ✨

```
Activity Log                    │ Network Activity
─────────────────────           │ ─────────────────
✓ Added: ubuntu.iso             │ ▼ 15.2 MB/s
⚡ Started: ubuntu.iso          │   ████████████▇▆▅▄
✓ Downloading at 15.2 MB/s      │ Peak: 18.4 MB/s
```

---

## 🎛️ Managing Downloads

### Download States

| State | Icon | Description |
|-------|------|-------------|
| Queued | ○ | Waiting to start |
| Active | ● | Currently downloading |
| Paused | ⏸ | Manually paused |
| Complete | ✓ | Successfully finished |
| Failed | ✗ | Error occurred |

### Switching Tabs

Use **← →** arrow keys to switch between:

```
┌─────────────────────────────────────────┐
│  Queued (2)    Active (1)    Done (5)  │
│     ←              ↑             →      │
└─────────────────────────────────────────┘
```

### Selecting Downloads

Use **↑ ↓** arrow keys to navigate the download list:

```
│ Downloads                               │
│ ─────────────────                       │
│   ○ file1.zip          Queued         │
│ ▸ ● file2.iso          78% • 12 MB/s  │  ← Selected
│   ○ file3.exe          Queued         │
```

### Start, Pause, Resume

| Action | Key | When to Use |
|--------|-----|-------------|
| **Start** | `S` | Start a queued download |
| **Pause** | `P` | Pause an active download |
| **Resume** | `R` | Resume a paused download |

### Toggle Auto-Start

Press `O` to toggle auto-start mode:

```
Activity Log
─────────────
Auto-start: ON   ← New downloads start immediately
Auto-start: OFF  ← New downloads stay queued
```

---

## ⌨️ Keyboard Shortcuts

### Quick Reference Card

```
╔═══════════════════════════════════════════════════════════════╗
║                    FLUX KEYBOARD SHORTCUTS                    ║
╠═══════════════════════════════════════════════════════════════╣
║  DOWNLOADS                    NAVIGATION                      ║
║  ──────────                   ──────────                      ║
║  A  → Add new download        ↑↓ → Navigate list              ║
║  S  → Start selected          ←→ → Switch tabs                ║
║  P  → Pause selected          Tab → Next section              ║
║  R  → Resume selected         1-4 → Jump to section           ║
║  D  → Delete from list                                        ║
║  Shift+D → Delete + files     SECTIONS                        ║
║  O  → Toggle auto-start       ────────                        ║
║                               1 → Activity Log                ║
║  GENERAL                      2 → Network (read-only)         ║
║  ───────                      3 → Downloads                   ║
║  Q  → Quit Flux               4 → Details (read-only)         ║
║  Esc → Close dialog                                           ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 📡 Understanding Network Health

The header displays real-time network quality:

```
Network Health: ●●●●○ (Good)   RTT: 45ms | Loss: 0.2%
```

### Quality Indicators

| Dots | Color | Status | Meaning |
|------|-------|--------|---------|
| ●●●●● | 🟢 Green | Good | Excellent connection |
| ●●●○○ | 🟡 Yellow | Moderate | Acceptable, some latency |
| ●○○○○ | 🔴 Red | Poor | High latency or packet loss |

### Metrics Explained

- **RTT**: Round-trip time (lower is better)
- **Loss**: Estimated packet loss percentage

---

## 🔥 Advanced Features

### 1. Multi-Connection Downloads

Flux automatically uses multiple connections for faster downloads:

```
File Details
────────────
Connections: 8        ← 8 parallel streams
Chunk Size: 4.00 MB   ← Optimized chunk size
Efficiency: 98%       ← How well it's performing
```

### 2. Adaptive Intelligence

Watch Flux adapt in the Activity Log:

```
Activity Log
────────────
⚡ Increased connections: 4 → 8 (low error rate)
⚡ Increased chunk size: 1MB → 4MB (stable throughput)
```

### 3. Resume Support

If your download is interrupted:

1. Close Flux or lose connection
2. Reopen Flux and add the same URL
3. Flux automatically resumes from where it stopped!

```
Activity Log
────────────
↻ Resuming: file.iso (65% complete)
```

### 4. File Details Panel

Select any download to see detailed stats:

```
┌─────────────────────────────────────────────┐
│ 📄 File Details                             │
├─────────────────────────────────────────────┤
│ ▸ ubuntu-22.04.iso                          │
│ ~/Downloads/ubuntu-22.04.iso                │
│                                             │
│ Progress                                    │
│ ━━━━━━━━━━━━━━━━━━░░░░░░ 75.3%             │
│ 3.2 GB / 4.2 GB                             │
│                                             │
│ Speed Stats                                 │
│ Current: 15.2 MB/s                          │
│ Average: 12.8 MB/s                          │
│ Peak:    18.4 MB/s                          │
│                                             │
│ Time                                        │
│ ETA: 1m 23s                                 │
│ Elapsed: 4m 12s                             │
│                                             │
│ Connection                                  │
│ Connections: 8 | Chunk: 4 MB | Eff: 98%     │
└─────────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### Common Issues

<details>
<summary><b>❌ "Module not found" error</b></summary>

```bash
# Reinstall Flux
pip uninstall flux-download
pip install flux-download
```
</details>

<details>
<summary><b>❌ Download stuck at 0%</b></summary>

1. Check your internet connection
2. Verify the URL is accessible
3. Try pausing and resuming (`P` then `R`)
</details>

<details>
<summary><b>❌ "Unclosed client session" warning</b></summary>

This is fixed in the latest version. Update Flux:
```bash
pip install --upgrade flux-download
```
</details>

<details>
<summary><b>❌ Terminal looks broken</b></summary>

1. Use a modern terminal (Windows Terminal, iTerm2, etc.)
2. Ensure UTF-8 encoding is enabled
3. Try resizing the terminal window
</details>

### Getting Help

If you encounter issues:

1. Check the [GitHub Issues](https://github.com/aditthyass/flux/issues)
2. Create a new issue with:
   - Your OS and Python version
   - Steps to reproduce
   - Error message (if any)

---

## 🎯 Tips & Best Practices

1. **Use Auto-Start for batch downloads** - Queue multiple files, enable auto-start, and let Flux handle them sequentially.

2. **Monitor Network Health** - If quality drops, Flux automatically adjusts, but you might want to pause and retry later.

3. **Check the Activity Log** - It shows exactly what Flux is doing and why.

4. **Use keyboard shortcuts** - They're faster than clicking!

5. **Let large files run overnight** - Flux will handle interruptions gracefully.

---

<div align="center">

```
╔══════════════════════════════════════════════════════╗
║                                                      ║
║   🎉 You're now ready to use Flux like a pro! 🎉    ║
║                                                      ║
║              Happy Downloading! ⚡                   ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
```

**Developed by Aditthya S S • Open Source • Free Forever**

[Back to README](README.md) • [Report Issues](https://github.com/aditthyass/flux/issues)

</div>
