# Quick Start Guide

## TL;DR - Best Setup

```bash
# 1. Ensure UVC quirks are set (one-time setup)
cat /sys/module/uvcvideo/parameters/quirks  # Should show: 2

# 2. Set camera to thermal-only mode
./thermal_camera_mode.sh thermal

# 3. Start go2rtc
make run

# 4. Access stream
firefox http://localhost:1984/stream.html?src=uvc_cam
```

**That's it!** You'll have a 256x192 thermal stream.

## Quick Testing (Without go2rtc)

```bash
# Get the exact test command for current camera mode
./thermal_camera_mode.sh current

# Copy and paste the command shown to test with ffplay
```

## Available Streams

| Stream | Resolution | CPU | Notes |
|--------|-----------|-----|-------|
| **uvc_cam** ⭐ | 256x192 | Medium | Thermal-only (recommended) |
| uvc_cam_dual | 256x392 | High | Dual-plane mode |

⭐ = Recommended

**Note:** Camera advertises MJPEG/H.264 modes but they don't work (firmware bug). Only YUYV modes work.

## Common Tasks

### Switch Camera Mode
```bash
./thermal_camera_mode.sh thermal    # 256x192 thermal-only
./thermal_camera_mode.sh dual       # 256x392 dual-plane
./thermal_camera_mode.sh current    # Check current mode + get test command
```

### Control go2rtc
```bash
make run        # Start daemon
make stop       # Stop daemon
make restart    # Restart daemon
make status     # Check status
```

### Access Streams
- **Web Interface:** http://localhost:1984/
- **RTSP:** rtsp://localhost:8554/uvc_cam
- **WebRTC:** http://localhost:1984/stream.html?src=uvc_cam

## Troubleshooting

### Camera stuck in wrong mode?
```bash
./thermal_camera_mode.sh current    # Check current mode
./thermal_camera_mode.sh thermal    # Switch to desired mode
make restart
```

### Stream not working?
```bash
# Test directly without go2rtc
./thermal_camera_mode.sh current    # Get test command
# Copy and run the command shown
```

### Format changes fail?
```bash
# Check quirks setting
cat /sys/module/uvcvideo/parameters/quirks  # Should be: 2

# If wrong, reload driver
sudo modprobe -r uvcvideo
sudo modprobe uvcvideo quirks=0x2
```

## Documentation

- **[STREAMS.md](STREAMS.md)** - All working streams and firmware bugs
- **[CAMERA.md](CAMERA.md)** - Camera hardware and UVC quirks
- **[CLAUDE.md](CLAUDE.md)** - Project documentation

## Quick Examples

### Test thermal mode
```bash
./thermal_camera_mode.sh thermal
v4l2-ctl -d /dev/video0 --stream-mmap=3 --stream-count=0 --stream-to=- \
  | ffplay -f rawvideo -pixel_format yuyv422 -video_size 256x192 -
```

### Test dual-plane mode
```bash
./thermal_camera_mode.sh dual
v4l2-ctl -d /dev/video0 --stream-mmap=3 --stream-count=0 --stream-to=- \
  | ffplay -f rawvideo -pixel_format yuyv422 -video_size 256x392 -
```

## Known Issues

- **Modes 4, 5, portrait2** - Advertised but produce no frames (firmware bug)
- **MJPEG/H.264** - Advertised but produce invalid data (firmware bug)
- Only use the working YUYV modes: thermal, dual, mode3, portrait1
