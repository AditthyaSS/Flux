<div align="center">

```
 ███████╗██╗     ██╗   ██╗██╗  ██╗
 ██╔════╝██║     ██║   ██║╚██╗██╔╝
 █████╗  ██║     ██║   ██║ ╚███╔╝ 
 ██╔══╝  ██║     ██║   ██║ ██╔██╗ 
 ██║     ███████╗╚██████╔╝██╔╝ ██╗
 ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝
```

### ⚡ Adaptive • Explainable • Beautiful ⚡

[![MIT License](https://img.shields.io/badge/License-MIT-00d9ff?style=for-the-badge)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-ff006e?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Textual TUI](https://img.shields.io/badge/Built_with-Textual-00ff41?style=for-the-badge)](https://github.com/Textualize/textual)

**Next-generation download manager with a stunning terminal interface that adapts to network conditions in real-time.**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Controls](#%EF%B8%8F-keyboard-controls)

</div>



```
┌──────────────────────────────────────────────────────────────────────────────┐
│  ███████╗██╗     ██╗   ██╗██╗  ██╗                                           │
│  ██╔════╝██║     ██║   ██║╚██╗██╔╝          Network Health: ●●●●● (Good)    │
│  █████╗  ██║     ██║   ██║ ╚███╔╝           RTT: 45ms | Loss: 0.0%          │
│  ██╔══╝  ██║     ██║   ██║ ██╔██╗                                           │
│  ██║     ███████╗╚██████╔╝██╔╝ ██╗          Made by Aditthya S S • Open    │
│  ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝          Source • Free Forever           │
├──────────────────────────────────┬───────────────────────────────────────────┤
│ 📋 Activity Log                  │ 📊 Network Activity                       │
│ ─────────────────────            │ ─────────────────────                     │
│ ✓ Flux started                   │ ▼ 12.46 MB/s                              │
│ ✓ Added: ubuntu-22.04.iso        │   ████████████████▇▆▅▄▃▂▁                 │
│ ⚡ Downloading at 12.46 MB/s     │ Peak: 15.2 MB/s | Total: 1.2 GB          │
│ ✓ Completed: setup.exe           │                                           │
├──────────────────────────────────┼───────────────────────────────────────────┤
│ 📁 Downloads                     │ 📄 File Details                           │
│ ─────────────────────            │ ─────────────────────                     │
│ Queued (2)  Active (1)  Done (5) │ ▸ ubuntu-22.04.iso                        │
│                                  │ ━━━━━━━━━━━━━━━░░░░░ 75.3%               │
│ ▸ ● ubuntu-22.04.iso             │ 3.2 GB / 4.2 GB                           │
│     Downloading • 75% • 12 MB/s  │ Speed: 12.46 MB/s | ETA: 1m 23s          │
├──────────────────────────────────┴───────────────────────────────────────────┤
│  [A]dd  [S]tart  [P]ause  [R]esume  [O]Auto  [←→]Tabs  [↑↓]Select  [Q]uit   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎯 Adaptive Intelligence
Automatically adjusts chunk size and connection count based on real-time network conditions.

### 📊 Live Dashboard
Full-screen terminal UI with live metrics, network graphs, and professional visualizations.

### 🧠 Explainable Decisions
See exactly **why** Flux changes its download strategy in real-time.

</td>
<td width="50%">

### ⚡ Multi-Connection Downloads
Parallel chunk downloading for maximum throughput - up to **500+ MB/s**.

### 💾 Resume Support
Seamlessly resume interrupted downloads with intelligent chunk tracking.

### 📈 Network Health Monitor
Real-time network quality indicator with RTT and packet loss metrics.

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Installation

```bash
# From PyPI
pip install flux-download

# Or clone and install
git clone https://github.com/aditthyass/flux.git
cd flux
pip install -e .
```

### Launch the Dashboard

```bash
flux
```

Press `a` to add a download and watch Flux work its magic! ✨

### CLI Mode (Headless)

```bash
flux-cli download https://example.com/file.zip --output ~/Downloads
```

---

## ⌨️ Keyboard Controls

<table>
<tr>
<th>🎮 Download Management</th>
<th>🧭 Navigation</th>
</tr>
<tr>
<td>

| Key | Action |
|:---:|--------|
| `A` | Add new download |
| `S` | Start queued download |
| `P` | Pause active download |
| `R` | Resume paused download |
| `O` | Toggle auto-start |

</td>
<td>

| Key | Action |
|:---:|--------|
| `↑↓` | Navigate downloads |
| `←→` | Switch tabs |
| `Tab` | Next section |
| `1-4` | Jump to section |
| `Q` | Quit Flux |

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                           🖥️  FLUX TUI LAYER                              ║
║  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌────────────────┐  ║
║  │ Activity    │  │  Network     │  │  Downloads  │  │ File Details   │  ║
║  │ Log         │  │  Graph       │  │  List       │  │ Panel          │  ║
║  └─────────────┘  └──────────────┘  └─────────────┘  └────────────────┘  ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                        ⚙️  ADAPTIVE ENGINE CORE                           ║
║  ┌──────────────────┐  ┌────────────────┐  ┌─────────────────────────┐   ║
║  │ 🧠 Decision      │  │ 📊 Metrics     │  │ 📋 Task Queue           │   ║
║  │    Engine        │  │    Tracker     │  │    Manager              │   ║
║  │                  │  │                │  │                         │   ║
║  │ • Smart Chunking │  │ • RTT Tracking │  │ • Priority Scheduling   │   ║
║  │ • Connection     │  │ • Speed Stats  │  │ • Auto-Start Logic      │   ║
║  │   Scaling        │  │ • Efficiency   │  │ • Resume Support        │   ║
║  └──────────────────┘  └────────────────┘  └─────────────────────────┘   ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                          🌐 I/O LAYER                                     ║
║         ┌─────────────────────┐       ┌─────────────────────┐             ║
║         │ 🔌 HTTP Client      │       │ 💾 File Writer      │             ║
║         │   • Range Requests  │       │   • Async I/O       │             ║
║         │   • RTT Measurement │       │   • Chunk Mapping   │             ║
║         │   • Auto Retry      │       │   • State Persist   │             ║
║         └─────────────────────┘       └─────────────────────┘             ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

---

## 🧠 How Flux Thinks

<table>
<tr>
<td width="50%">

### 📦 Chunk Size Optimization

| Condition | Action |
|-----------|--------|
| Stable throughput + High RTT | ⬆️ Increase chunk size |
| Unstable throughput + Low RTT | ⬇️ Decrease chunk size |

</td>
<td width="50%">

### 🔗 Connection Scaling

| Condition | Action |
|-----------|--------|
| Low error rate + Server OK | ⬆️ More connections |
| High error rate | ⬇️ Fewer connections |

</td>
</tr>
</table>

> 💡 Every decision is logged in real-time with full explanations!

---

## 🛠️ Development

```bash
# Clone the repository
git clone https://github.com/aditthyass/flux.git
cd flux

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest flux/tests/ -v --cov=flux

# Code formatting
black flux/ && isort flux/ && mypy flux/
```

---

## 📦 Building

```bash
python build/build.py
```

| Platform | Output |
|----------|--------|
| Windows | `dist/flux.exe` |
| Linux | `dist/flux` |
| macOS | `dist/flux` |

---

## 🌟 Why Flux?

<table>
<tr>
<td align="center">🔍</td>
<td><strong>Explainability</strong> - Understand <em>why</em> your download is fast or slow</td>
</tr>
<tr>
<td align="center">🎨</td>
<td><strong>Beautiful TUI</strong> - htop-style design with Surge-inspired aesthetics</td>
</tr>
<tr>
<td align="center">⚡</td>
<td><strong>Modern Architecture</strong> - Async Python with real-time adaptive intelligence</td>
</tr>
<tr>
<td align="center">🧠</td>
<td><strong>Smart Decisions</strong> - Every optimization is logged and explained</td>
</tr>
</table>

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                       Developed                                  ║
║                                                                  ║
║                         by Aditthya S S                          ║
║                                                                  ║
║              🌟 For Open Source • Free Forever 🌟               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

**Built with ❤️ using [Textual](https://github.com/Textualize/textual) • [aiohttp](https://docs.aiohttp.org/) • [Rich](https://github.com/Textualize/rich)**

<sub>⭐ Star this repo if you find it useful!</sub>

</div>
