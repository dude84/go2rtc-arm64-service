# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository manages a go2rtc ARM64 binary deployment for streaming camera feeds on Raspberry Pi or other ARM64 Linux systems. go2rtc is a camera streaming application that supports multiple protocols (WebRTC, RTSP, etc.).

## Key Components

- **[Makefile](Makefile)**: Primary interface for managing go2rtc - handles updates, daemon control, and systemd service management
- **[go2rtc.service](go2rtc.service)**: Systemd service unit file template
- **[bin/go2rtc](bin/go2rtc)**: The go2rtc binary (statically linked ARM64 executable)
- **[bin/go2rtc.yaml](bin/go2rtc.yaml)**: Configuration file defining camera streams
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

The [bin/go2rtc.yaml](bin/go2rtc.yaml) file defines camera streams using the `rpicam-vid` command for Raspberry Pi cameras. The configuration shows:
- Stream name: `cam0`
- Uses `rpicam-vid` to capture H.264 video at 1920x1080
- Alternative commented configurations for different resolutions/framerates

To modify camera settings, edit the stream configuration in [bin/go2rtc.yaml](bin/go2rtc.yaml) and adjust the `rpicam-vid` parameters (resolution, framerate, bitrate, codec profile).

## Architecture Notes

This is a deployment repository, not a source code repository. It manages:
1. Binary distribution of go2rtc for ARM64
2. Configuration for local camera streaming setup
3. Update mechanism to fetch new releases

The binary is excluded from git via [.gitignore](.gitignore) to avoid bloat, but the update script ensures reproducible deployment.
