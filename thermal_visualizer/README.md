# Thermal Camera ASCII Visualizer

Real-time thermal data visualization for the Hikvision JS-MINI256-9 thermal camera in dual mode (256x392).

## Overview

This tool extracts the green thermal data from the camera's dual-plane mode and renders it as colored ASCII art in your terminal using the inferno colormap (dark purple → red → orange → yellow).

### What It Does

1. **Sets camera to dual mode** (256x392): Top 192 lines contain green thermal data, bottom 192 lines contain user-friendly view
2. **Extracts green channel**: The top section's green channel contains thermal intensity data
3. **Renders as ASCII**: Maps intensity values to inferno colors and ASCII characters for terminal display

### Important Limitation

⚠️ **This visualizer shows relative thermal intensity, NOT actual temperature values (°C/°F).**

The camera outputs YUYV format, which contains intensity data (0-255) but not calibrated temperature measurements. To get actual temperatures, you would need access to the camera's proprietary calibration data and algorithms, which are not available via the UVC interface.

## Installation

The virtual environment and dependencies are already installed. If you need to recreate:

```bash
cd /home/maciej/_dev/go2rtc-amd64-service/thermal_visualizer

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### 1. Test Frame Capture (test_frame.py)

Captures a single frame and analyzes the dual-mode structure. Saves PNG files for inspection.

```bash
source venv/bin/activate
python test_frame.py
```

**Output:**
- `frame_full.png` - Complete 256x392 frame
- `frame_top_green.png` - Top 192 lines (green thermal data)
- `frame_bottom_thermal.png` - Bottom 192 lines (user-friendly view)
- Console statistics about frame structure and intensity values

**Use this to:**
- Verify camera is in dual mode
- Inspect the thermal data structure
- Check if green channel contains expected data
- Debug frame capture issues

### 2. Real-Time ASCII Visualizer (thermal_ascii.py)

Displays live thermal data as colored ASCII art in your terminal.

```bash
source venv/bin/activate
python thermal_ascii.py [options]
```

**Options:**
- `--downsample N` - Downsample factor for display (default: 4)
  - `1` = Full resolution (256x192 pixels → very large terminal output)
  - `2` = Half resolution (128x96)
  - `4` = Quarter resolution (64x48, recommended)
  - `8` = Eighth resolution (32x24, compact)

- `--contrast FACTOR` - Contrast enhancement (default: 1.5)
  - `1.0` = No enhancement
  - `1.5` = Moderate enhancement (recommended)
  - `2.0` = Strong enhancement
  - Higher values increase contrast but may clip values

**Examples:**

```bash
# Recommended default settings
python thermal_ascii.py

# Full resolution (requires large terminal)
python thermal_ascii.py --downsample 1

# Compact view with strong contrast
python thermal_ascii.py --downsample 8 --contrast 2.0

# High resolution with moderate contrast
python thermal_ascii.py --downsample 2 --contrast 1.5
```

**Controls:**
- Press `Ctrl+C` to stop

**Display:**
```
████▓▓▓░░░    <- ASCII art with inferno colors
▓▓▓▒▒▒░░      <- Purple (cold) to yellow (hot)
▒▒▒░░░

────────────────────────────────────────
FPS: 24.8
Min: 45  Max: 198  Mean: 112.3
Size: 64x48 (downsampled from 256x192)
Contrast: 1.5x

Controls: q=quit  +=increase contrast  -=decrease contrast  r=reset
```

## Color Map

The inferno colormap shows thermal intensity as:

```
Dark Purple  →  Purple  →  Red  →  Orange  →  Yellow
   (cold)                                      (hot)
     0                                          255
```

**Note:** These are intensity values (0-255), not actual temperatures!

## ASCII Characters

Intensity is also mapped to ASCII characters for better visibility:
```
' ' = darkest (lowest intensity)
'░' = dark
'▒' = medium
'▓' = bright
'█' = brightest (highest intensity)
```

Each character is doubled horizontally for better aspect ratio.

## Frame Structure

The dual-mode camera outputs a 256x392 frame with this structure:

```
Lines   0-191: Green thermal data (192 lines) ← We extract this
Lines 192-194: Metadata (3 lines)
Lines 195-386: User-friendly thermal view (192 lines)
Lines 387-391: Metadata (3-5 lines)
```

The visualizer processes only the top 192 lines and extracts the green channel (BGR format, index 1).

## Performance

- **FPS:** Typically 20-25 fps (depends on CPU and downsample factor)
- **CPU Usage:** Moderate (OpenCV capture + processing + terminal rendering)
- **Terminal:** Works best with terminals supporting 24-bit ANSI colors
  - ✅ Works: GNOME Terminal, Konsole, iTerm2, Windows Terminal
  - ⚠️ Limited: xterm (256 colors only)
  - ❌ Not supported: Very old terminals without color support

## Troubleshooting

### "Error: Could not open camera"

**Cause:** Camera not accessible or in wrong mode

**Fix:**
```bash
# Check camera is connected
ls -l /dev/video0

# Set to dual mode
cd /home/maciej/_dev/go2rtc-amd64-service
./thermal_camera_mode.sh dual

# Verify mode
./thermal_camera_mode.sh current
```

### "Error setting camera mode"

**Cause:** UVC quirks not set correctly

**Fix:**
```bash
# Check quirks
cat /sys/module/uvcvideo/parameters/quirks
# Should show: 2

# If wrong, reload driver
sudo modprobe -r uvcvideo
sudo modprobe uvcvideo quirks=0x2
```

### Camera is already in use

**Cause:** Another application (like go2rtc) is using the camera

**Fix:**
```bash
# Stop go2rtc
cd /home/maciej/_dev/go2rtc-amd64-service
make stop

# Now run visualizer
cd thermal_visualizer
source venv/bin/activate
python thermal_ascii.py
```

### Display looks wrong/corrupted

**Possible causes:**
1. **Terminal too small** - Increase terminal size or use higher `--downsample`
2. **Terminal doesn't support colors** - Use a modern terminal emulator
3. **Wrong camera mode** - Ensure camera is in dual mode (256x392)

**Fix:**
```bash
# Verify camera mode
../thermal_camera_mode.sh current
# Should show: Width/Height: 256/392

# Try compact display
python thermal_ascii.py --downsample 8
```

### Low FPS or stuttering

**Cause:** CPU overload or high downsample setting

**Fix:**
```bash
# Use higher downsample to reduce processing
python thermal_ascii.py --downsample 8

# Or reduce contrast processing
python thermal_ascii.py --contrast 1.0
```

### "No frames captured" or black screen

**Cause:** Camera producing no data or wrong format

**Fix:**
```bash
# Test with v4l2-ctl directly
v4l2-ctl -d /dev/video0 --stream-mmap=3 --stream-count=10 --stream-to=/tmp/test.raw

# Check file size (should be ~2MB for 10 frames)
ls -lh /tmp/test.raw

# If empty, camera is not producing frames - check USB connection
# Replug camera and try again
```

## Dependencies

- **numpy** ≥1.24.0 - Array processing
- **opencv-python** ≥4.8.0 - Video capture and image processing
- **matplotlib** ≥3.7.0 - Inferno colormap generation

## Technical Details

- **Input format:** YUYV 4:2:2 (256x392 @ 25 fps)
- **Processing:** Extract green channel (8-bit, 0-255)
- **Downsampling:** cv2.INTER_AREA interpolation
- **Contrast:** Linear enhancement around mean value
- **Color mapping:** Matplotlib inferno colormap → ANSI 24-bit RGB
- **ASCII mapping:** Linear mapping to 5-character gradient

## See Also

- [../CAMERA.md](../CAMERA.md) - Camera hardware documentation
- [../STREAMS.md](../STREAMS.md) - Working stream modes
- [../thermal_camera_mode.sh](../thermal_camera_mode.sh) - Camera mode switching script
- [../QUICKSTART.md](../QUICKSTART.md) - Quick setup guide

## License

Part of the go2rtc-amd64-service project.
