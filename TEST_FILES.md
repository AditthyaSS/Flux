# Test File URLs for Flux

## Large File Downloads (Perfect for Testing)

### 1GB Files
- **Hetzner**: `https://ash-speed.hetzner.com/1GB.bin`
- **OVH**: `https://proof.ovh.net/files/1Gb.dat`

### 500MB Files  
- **Hetzner**: `https://ash-speed.hetzner.com/500MB.bin`

### 100MB Files
- **Hetzner**: `https://ash-speed.hetzner.com/100MB.bin`
- **Cloudflare**: `https://speed.cloudflare.com/100mb.bin`

### 10MB Files (Quick Test)
- **Hetzner**: `https://ash-speed.hetzner.com/10MB.bin`
- **OVH**: `https://proof.ovh.net/files/10Mb.dat`

## How to Test

1. **Launch Flux**:
   ```powershell
   python -m flux.app
   ```

2. **Press `a`** to add download

3. **Paste URL** from above list

4. **Watch**:
   - 📊 Magenta sparkline animating
   - ⚡ Speed climbing as connections scale
   - 📈 Progress bar updating
   - 🎯 File details showing real-time stats

## What to Observe

- **Adaptive Intelligence**: Watch connections increase (2→4→8) as download stabilizes
- **Network Visualization**: Sparkline shows speed variations
- **Progress Tracking**: Real-time percentage, speed, ETA
- **Multiple Downloads**: Add several and watch them all download in parallel!

Try the **1GB file** to really see Flux's adaptive engine in action! 🚀
