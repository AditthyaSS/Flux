# Using Flux from CMD

## 🚀 Installation (One-Time Setup)

### Option 1: Install from Local Directory (Editable Mode)
```cmd
cd "C:\Users\Aditt\Downloads\flux v1.0.0"
pip install -e .
```

### Option 2: Install from GitHub
```cmd
pip install git+https://github.com/AditthyaSS/Flux.git
```

After installation, Flux will be available globally!

## 💻 Usage from Any Directory

Once installed, you can run Flux from **anywhere** in CMD:

### Launch TUI (Terminal UI)
```cmd
flux
```

That's it! Just type `flux` and press Enter.

### Using CLI Mode
```cmd
# Add a download
flux add https://example.com/file.zip

# List downloads
flux list

# Show help
flux --help
```

## 📝 Quick Examples

### Example 1: Download from Anywhere
```cmd
# Works from any directory!
C:\> flux
```

### Example 2: Download to Specific Folder
```cmd
cd D:\Downloads
flux
# Then press 'a' and add your URL
```

### Example 3: CLI Mode
```cmd
# Add download via command line
flux add https://ash-speed.hetzner.com/1GB.bin

# Check status
flux list
```

## 🎮 TUI Keyboard Controls

Once Flux is running:
- `a` - Add download
- `↑/↓` - Navigate downloads
- `Tab` - Switch tabs (Queued/Active/Done)
- `p` - Pause/Resume
- `q` - Quit

## 🔄 Update Flux

When you make changes and want to update:

```cmd
cd "C:\Users\Aditt\Downloads\flux v1.0.0"
git pull
pip install -e . --force-reinstall
```

Or from GitHub:
```cmd
pip install --upgrade git+https://github.com/AditthyaSS/Flux.git
```

## ✅ Verify Installation

```cmd
# Check if flux is installed
flux --help

# Should show Flux help menu
```

## 🎉 That's It!

Now you can just type `flux` from anywhere in CMD and it will start! 🚀
