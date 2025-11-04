# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository manages a go2rtc AMD64 binary deployment for streaming camera feeds from a Hikvision JS-MINI256-9 thermal UVC camera. go2rtc is a camera streaming application that supports multiple protocols (WebRTC, RTSP, etc.).

## Key Components

- **[Makefile](Makefile)**: Primary interface for managing go2rtc - handles updates, daemon control, and systemd service management
- **[go2rtc.service](go2rtc.service)**: Systemd service unit file template
- **[bin/go2rtc](bin/go2rtc)**: The go2rtc binary (statically linked AMD64 executable)
- **[bin/go2rtc.yaml](bin/go2rtc.yaml)**: Configuration file defining camera streams
- **[thermal_camera_mode.sh](thermal_camera_mode.sh)**: Utility for switching thermal camera display modes
- **[CAMERA.md](CAMERA.md)**: Comprehensive documentation for the Hikvision JS-MINI256-9 thermal camera (UVC quirks, modes, troubleshooting)
- **[STREAMS.md](STREAMS.md)**: Guide to all available camera streams (MJPEG, H.264, raw YUYV) with performance comparisons
- **[update_go2rtc_arm64.sh](update_go2rtc_arm64.sh)**: Legacy script for downloading go2rtc (use `make update` instead)

## Common Commands

All operations are managed through the Makefile:

### Binary Management
```bash
make update          # Download latest go2rtc ARM64 binary
```

### Daemon Control
```bash
make run             # Start go2rtc as daemon
make stop            # Stop go2rtc daemon
make restart         # Restart go2rtc daemon
make status          # Check if go2rtc is running
```

### Systemd Service
```bash
make service-install    # Install, enable, and start systemd service (requires sudo)
make service-uninstall  # Stop, disable, and remove systemd service (requires sudo)

# Manual control after installation:
sudo systemctl stop go2rtc
sudo systemctl restart go2rtc
sudo systemctl status go2rtc
```

The `service-install` target automatically starts the service after installation. The service uses the [go2rtc.service](go2rtc.service) template with placeholders that are replaced during installation.

## Configuration

### Thermal Camera Configuration

The [bin/go2rtc.yaml](bin/go2rtc.yaml) file defines camera streams using V4L2 and FFmpeg for the Hikvision JS-MINI256-9 thermal camera:
- Stream name: `uvc_cam`
- Uses `v4l2-ctl` to capture raw YUYV 4:2:2 video from `/dev/video0`
- Pipes to `ffmpeg` for H.264 encoding at 256x192 (thermal-only mode)
- Default settings: 25 fps, baseline profile, CRF 23

**IMPORTANT:** The thermal camera requires specific UVC driver quirks to function. See [CAMERA.md](CAMERA.md) for:
- Required quirks configuration (`quirks=0x2` in `/etc/modprobe.d/uvcvideo.conf`)
- Available display modes (thermal-only, dual-plane, etc.)
- Mode switching instructions
- Troubleshooting guide

### Available Streams

The camera supports only YUYV modes due to firmware bugs - see [STREAMS.md](STREAMS.md) for details:

**Working Streams (Raw YUYV, Software Encoding):**
- `uvc_cam` - 256x192 thermal-only @ 25fps (recommended, requires mode switching)
- `uvc_cam_dual` - 256x392 dual-plane @ 25fps (requires mode switching)

**Note:** Camera advertises MJPEG/H.264 modes but they produce invalid data (firmware bug). Only YUYV modes work. All streams require FFmpeg software encoding to H.264.

## Architecture Notes

This is a deployment repository, not a source code repository. It manages:
1. Binary distribution of go2rtc for AMD64
2. Configuration for UVC thermal camera streaming setup
3. Update mechanism to fetch new releases
4. Thermal camera mode management and UVC driver quirks configuration

The binary is excluded from git via [.gitignore](.gitignore) to avoid bloat, but the update script ensures reproducible deployment.

### Hardware-Specific Requirements

The Hikvision JS-MINI256-9 thermal camera requires:
- **UVC Driver Quirks:** `quirks=0x2` (UVC_QUIRK_PROBE_MINMAX) for proper format negotiation
- **Configuration File:** `/etc/modprobe.d/uvcvideo.conf` must contain `options uvcvideo quirks=0x2`
- **Format Matching:** The resolution in go2rtc.yaml must match the camera's current mode

Without the proper quirk setting, the camera cannot change formats and will be stuck in its power-on default mode (256x392 dual-plane).
