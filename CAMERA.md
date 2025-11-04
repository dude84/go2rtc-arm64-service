# Hikvision JS-MINI256-9 Thermal Camera Documentation

## Camera Overview

**Model:** Hikvision JS-MINI256-9 Thermal UVC Camera  
**USB ID:** 2bdf:0102  
**Firmware:** 4.09  
**Serial:** F10615613  
**Driver:** uvcvideo (Linux UVC Video Class driver)

## Available Display Modes

The camera advertises multiple modes, but only some actually work due to firmware bugs:

### ✅ Working Modes (YUYV 4:2:2, 25 fps)

| Mode | Resolution | Description | Frame Size | Status |
|------|-----------|-------------|------------|--------|
| **thermal** | 256x192 | Thermal-only (recommended) | 98,304 bytes | ✅ Works |
| **dual** | 256x392 | Dual-plane (thermal + visible) | 200,704 bytes | ✅ Works |
| mode3 | 256x196 | Alternative mode | 100,352 bytes | ✅ Works |
| portrait1 | 192x520 | Portrait orientation | 199,680 bytes | ✅ Works |

### ❌ Broken Modes (Firmware Bugs)

| Mode | Resolution | Issue |
|------|-----------|-------|
| mode4 | 256x200 | Sets but produces no frames |
| mode5 | 256x400 | Sets but produces no frames |
| portrait2 | 192x400 | Sets but produces no frames |
| MJPEG (all) | 640x360, 240x320, 120x160 | Advertised but produces invalid data |
| H.264 | 240x320 | Advertised but produces invalid data |

**Note:** The camera advertises compressed formats (MJPEG/H.264) but they produce garbage data that cannot be decoded. This is a firmware bug. Only use the working YUYV modes.

## Critical Configuration: UVC Driver Quirks

**IMPORTANT:** This camera requires the `UVC_QUIRK_PROBE_MINMAX` quirk to function properly.

### Problem
The camera cannot change formats and gets stuck in dual-plane mode (256x392) without the proper quirk setting.

### Solution
The UVC driver must be loaded with `quirks=0x2`:

```bash
# Persistent configuration (survives reboots)
echo "options uvcvideo quirks=0x2" | sudo tee /etc/modprobe.d/uvcvideo.conf

# Reload driver immediately
sudo modprobe -r uvcvideo
sudo modprobe uvcvideo quirks=0x2
```

### Why quirks=0x2?

The quirk value `0x2` corresponds to `UVC_QUIRK_PROBE_MINMAX`, which forces the kernel to properly query the camera's minimum and maximum probe values during format negotiation. Without this quirk:
- Format changes fail with I/O errors
- Camera locks into whatever mode it initialized with
- Dynamic resolution switching is impossible

## Switching Camera Modes

### Using the Helper Script

```bash
# Show current mode with test commands
./thermal_camera_mode.sh current

# Switch to thermal-only mode (256x192)
./thermal_camera_mode.sh thermal

# Switch to dual-plane mode (256x392)
./thermal_camera_mode.sh dual

# List all available formats
./thermal_camera_mode.sh list
```

**Tip:** The `current` command shows the exact v4l2-ctl + ffplay command to test the current mode locally without starting go2rtc!

### Using v4l2-ctl Directly

```bash
# Check current format
v4l2-ctl -d /dev/video0 --get-fmt-video

# Switch to thermal-only (256x192)
v4l2-ctl -d /dev/video0 --set-fmt-video=width=256,height=192

# Switch to dual-plane (256x392)
v4l2-ctl -d /dev/video0 --set-fmt-video=width=256,height=392

# List all supported formats
v4l2-ctl -d /dev/video0 --list-formats-ext
```

## go2rtc Configuration

The camera is configured in `bin/go2rtc.yaml`:

```yaml
streams:
  uvc_cam:
    - "exec:/usr/bin/sh -c '/usr/bin/v4l2-ctl -d /dev/video0 --stream-mmap=3 --stream-count=0 --stream-to=- \
      | /usr/bin/ffmpeg -hide_banner -loglevel error -fflags nobuffer -flags low_delay \
        -f rawvideo -pix_fmt yuyv422 -s 256x192 -r 25 -i - \
        -vf format=yuv420p \
        -c:v libx264 -preset veryfast -tune zerolatency -profile:v baseline -crf 23 \
        -f mpegts -'"
```

**Note:** The `-s 256x192` parameter in the ffmpeg command must match the current camera mode. Change it to match your desired resolution.

## UVC Extension Unit

The camera has a UVC Extension Unit with 15 controls:
- **Unit ID:** 10
- **GUID:** `a29e7641-de04-47e3-8b2b-f4341aff003b`
- **Controls:** 15 vendor-specific controls (currently not accessible via standard UVC queries)

These controls are likely for advanced thermal camera features (palette, temperature range, etc.) but require vendor-specific SDK or Windows tools to access.

## Troubleshooting

### Camera stuck in wrong mode after boot

The camera defaults to 256x392 dual-plane mode on power-up. Switch to your desired mode:

```bash
./thermal_camera_mode.sh thermal
```

### Format changes fail with I/O error

Check that the UVC quirk is set correctly:

```bash
cat /sys/module/uvcvideo/parameters/quirks
# Should output: 2
```

If it shows a different value, reload the driver:

```bash
sudo modprobe -r uvcvideo
sudo modprobe uvcvideo quirks=0x2
```

### Camera not detected

Check USB connection and kernel messages:

```bash
lsusb | grep -i hik
dmesg | grep -i uvc | tail -20
```

### go2rtc stream not working

1. Verify camera mode matches go2rtc config
2. Check if another process is using the camera:

```bash
lsof /dev/video0
```

## Technical Details

### UVC Quirks Reference

The Linux UVC driver supports these quirk flags (bitmask values):

| Value | Quirk Name | Description |
|-------|-----------|-------------|
| 0x00000001 | STATUS_INTERVAL | Poll status endpoint at intervals |
| **0x00000002** | **PROBE_MINMAX** | **Query min/max probe values (required for this camera)** |
| 0x00000004 | PROBE_EXTRAFIELDS | Handle extra probe fields |
| 0x00000080 | FIX_BANDWIDTH | Recalculate bandwidth |
| 0x00000100 | PROBE_DEF | Use default probe values |
| 0x00000200 | RESTRICT_FRAME_RATE | Limit frame rates |
| 0x00000400 | RESTORE_CTRLS_ON_INIT | Restore controls on init |

Multiple quirks can be combined using bitwise OR (e.g., `0x102` = PROBE_DEF + PROBE_MINMAX).

### Why was quirks previously 0xFFFFFFFF?

The driver was previously loaded with all quirks enabled (`0xFFFFFFFF`), likely from a troubleshooting attempt or system default. This caused conflicts that prevented proper format negotiation.

## Files Reference

- `thermal_camera_mode.sh` - Camera mode switching utility
- `bin/go2rtc.yaml` - go2rtc streaming configuration
- `/etc/modprobe.d/uvcvideo.conf` - Persistent UVC driver quirks configuration
- `CAMERA.md` - This documentation file

## See Also

- [go2rtc Documentation](https://github.com/AlexxIT/go2rtc)
- [Linux UVC Driver FAQ](https://www.ideasonboard.org/uvc/faq/)
- [V4L2 API Documentation](https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/v4l2.html)
