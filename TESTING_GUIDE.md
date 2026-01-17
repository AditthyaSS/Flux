# Flux TUI - Complete Testing Guide

## Quick Start Test (2 minutes)
1. **Launch:** `python -m flux.app`
2. **Add download:** Press `a` → Enter URL → Press Enter twice
3. **Verify:** Download appears in Active tab and progresses
4. **Quit:** Press `q`

✅ **Success:** Download starts and shows progress

---

## Complete Feature Tests

### 1. Basic Download Test
**Steps:**
1. Launch app: `python -m flux.app`
2. Press `a` to add download
3. Enter URL (test with: `https://speed.hetzner.de/100MB.bin`)
4. Press Enter for default path
5. Press Enter for auto filename

**Expected:**
- Activity Log shows "Added:" message
- Download appears in Active (1) tab
- File Details shows progress bar
- Network Activity shows live graph
- Speed increases, progress goes up
- Download completes → moves to Done tab

---

### 2. Auto-Start Toggle Test
**Steps:**
1. Launch app
2. Press `o` → Activity Log shows "Auto-start: OFF"
3. Press `a` and add download
4. Verify: Activity Log shows "Paused: [filename]"
5. Press `←` (left arrow) to switch to Queued tab
6. Verify: Download appears in Queued list
7. Press `↑/↓` to select download
8. Press `s` to start
9. Verify: Download starts and moves to Active tab

**Expected:**
- Auto-start OFF → Downloads pause immediately
- Queued tab shows paused downloads
- 's' key starts queued downloads

---

### 3. Tab Navigation Test
**Steps:**
1. Add 3 downloads (with auto-start OFF)
2. Start first download with `s`
3. Press `←` to go to Queued tab
4. Verify: 2 queued downloads visible
5. Press `→` to go to Active tab
6. Verify: 1 active download
7. Wait for completion
8. Press `→` to go to Done tab
9. Verify: Completed download appears

**Expected:**
- ← → arrows cycle through Queued/Active/Done
- Activity Log shows "Switched to: [tab]"
- Download counts correct: Queued (2), Active (1), Done (0)

---

### 4. Section Navigation Test
**Steps:**
1. Press `1` → Activity Log gets focus (scrollable)
2. Press `2` → Message: "Network is read-only, use 1 or 3"
3. Press `3` → Downloads list gets focus
4. Use `↑/↓` to navigate downloads
5. Press `Tab` → Focus switches to next section
6. Press `Shift+Tab` → Focus switches to previous section

**Expected:**
- Number keys jump to sections
- Tab/Shift+Tab cycle between focused sections
- Arrow keys work in Downloads when focused

---

### 5. Download Control Test
**Steps:**
1. Add and start download
2. Press `p` to pause
3. Verify: Status shows "Paused", moves to Queued tab
4. Press `←` to switch to Queued
5. Select download
6. Press `r` to resume
7. Verify: Download resumes, moves to Active

**Expected:**
- `s` = Start queued download
- `p` = Pause active download
- `r` = Resume paused download
- Status changes reflected in tabs

---

### 6. File Details Test
**Steps:**
1. Start download
2. Look at File Details (bottom-right)
3. Verify shows:
   - Filename and path
   - Progress bar with percentage
   - Downloaded / Total size
   - Speed: Current, Avg, Peak
   - ETA with accuracy indicator
   - Progress timeline bar
   - Elapsed time
   - Connections, Chunk size, Efficiency
4. Scroll down with mouse wheel
5. Verify all content visible

**Expected:**
- File Details updates in real-time
- ETA accuracy shows High/Med/Low
- Timeline bar shows progress visually
- Scrolling works

---

### 7. Network Graph Test
**Steps:**
1. Start large download (>100MB)
2. Watch Network Activity (top-right)
3. Verify:
   - Current speed updates (▼ X MB/s)
   - Top speed tracks peak
   - Total downloaded increases
   - Vertical bar graph animates
   - Grid lines visible

**Expected:**
- Graph updates smoothly
- Bars grow with download speed
- Stats accurate and real-time

---

### 8. Multiple Downloads Test
**Steps:**
1. Press `o` to turn auto-start OFF
2. Add 5 downloads quickly
3. Verify: All appear in Queued (5)
4. Press `←` to go to Queued tab
5. Select first, press `s`
6. Select second, press `s`
7. Verify: Active (2), Queued (3)
8. Wait for first to complete
9. Verify: Done (1), Active (1), Queued (3)

**Expected:**
- All downloads queue properly
- Can start multiple manually
- Queued downloads visible and selectable
- Completed downloads move to Done

---

### 9. Mouse Support Test
**Steps:**
1. Click on Activity Log → Focus changes
2. Click on Downloads section → Focus changes
3. Click on a download in list → Selects download
4. Scroll mouse wheel in File Details → Scrolls content
5. Click buttons in Add Download dialog → Works

**Expected:**
- Clicking sections focuses them
- Clicking downloads selects them
- Mouse wheel scrolls
- All mouse interactions work

---

### 10. Keyboard Shortcuts Test
**Steps:**
Test all bindings:
- `a` → Add Download dialog opens
- `s` → Starts selected queued download
- `p` → Pauses selected active download
- `r` → Resumes selected paused download
- `o` → Toggles auto-start (shows message)
- `←` → Previous tab
- `→` → Next tab
- `↑` → Previous download (when focused)
- `↓` → Next download (when focused)
- `Tab` → Next section
- `Shift+Tab` → Previous section
- `1` → Focus Activity Log
- `2` → Network (shows message)
- `3` → Focus Downloads
- `4` → Details (shows message)
- `q` → Quit app
- `Esc` → Close dialog

**Expected:**
- All keys respond quickly
- Footer shows current bindings
- Actions happen immediately

---

## Performance Test

### Speed Test
- UI should respond within 50ms
- No lag when pressing keys
- Smooth scrolling
- Refresh rate: 500ms (2 FPS)

### If App is Slow:
1. Check CPU usage - should be <5%
2. Restart the app
3. Reduce number of active downloads
4. Check network connection

---

## Common Issues & Solutions

### Downloads Not Starting
- ✅ Turn auto-start ON with `o` key
- ✅ Manually press `s` to start queued downloads
- ✅ Check Activity Log for error messages

### Can't See Queued Downloads
- ✅ Press `←` to switch to Queued tab
- ✅ Turn auto-start OFF first with `o`
- ✅ Downloads must be PAUSED or QUEUED status

### Arrow Keys Not Working
- ✅ Press `3` to focus Downloads section first
- ✅ Then use `↑/↓` to navigate
- ✅ Unfocus with `Tab` or `1`

### File Details Cut Off
- ✅ Scroll down with mouse wheel
- ✅ Focus File Details and use arrow keys
- ✅ Make terminal window larger

### App Feels Slow
- ✅ Restart the app (quit with `q` and relaunch)
- ✅ Performance improved - now 500ms refresh
- ✅ Close other terminal programs

---

## Success Criteria

✅ All downloads complete successfully
✅ Auto-start toggle works (ON/OFF)
✅ Tab switching works (←/→)
✅ Section navigation works (Tab, 1-4)
✅ All keyboard shortcuts responsive
✅ Mouse clicks and scrolling work
✅ Network graph displays smoothly
✅ File Details shows complete info
✅ No crashes or freezes
✅ Activity Log shows all events

---

## Quick Troubleshooting

**Problem:** Download fails
- Check URL is valid and accessible
- Check network connection
- Look for error in Activity Log

**Problem:** UI frozen
- Close with `q` and restart
- Check terminal for errors
- Reduce active downloads

**Problem:** Can't start download
- Check if auto-start is OFF
- Press `s` to manually start
- Switch to Queued tab with `←`

---

## Test URLs

**Small (10MB):** `https://speed.hetzner.de/10MB.bin`
**Medium (100MB):** `https://speed.hetzner.de/100MB.bin`
**Large (1GB):** `https://speed.hetzner.de/1GB.bin`

**Note:** Use small files for quick testing, large files for performance testing.
