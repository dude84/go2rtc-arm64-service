# Available Camera Streams

Your Hikvision JS-MINI256-9 thermal camera has firmware bugs that prevent many advertised modes from working. Only the YUYV modes listed below actually work.

## Working Stream Configurations

| Stream Name | Resolution | FPS | CPU Usage | Description |
|-------------|-----------|-----|-----------|-------------|
| `uvc_cam` | 256x192 | 25 | Medium | Thermal-only (recommended) |
| `uvc_cam_dual` | 256x392 | 25 | High | Dual-plane (thermal + visible) |

Both streams use:
- **Format:** YUYV 4:2:2 (raw, uncompressed)
- **Encoding:** FFmpeg software encoding to H.264
- **CPU:** Moderate to high (real-time encoding required)

## Other Modes (For Reference)

You can also use these YUYV modes by editing `bin/go2rtc.yaml`:
- `mode3` (256x196) - Works, but unclear what it shows
- `portrait1` (192x520) - Works, portrait orientation

## Broken/Unusable Modes

**DO NOT USE** - These are advertised but don't work (firmware bugs):

- ❌ `mode4` (256x200) - No frames produced
- ❌ `mode5` (256x400) - No frames produced
- ❌ `portrait2` (192x400) - No frames produced
- ❌ **ALL MJPEG modes** - Invalid data, cannot be decoded
- ❌ **ALL H.264 modes** - Invalid data, cannot be decoded

The camera firmware claims to support hardware-compressed MJPEG and H.264, but actually produces garbage data. This is a known firmware bug with this camera model.

## Usage Examples

### Start go2rtc and Access Stream

```bash
# Start the server
make run

# Access thermal-only stream via web browser
firefox http://localhost:1984/stream.html?src=uvc_cam

# Access dual-plane stream
firefox http://localhost:1984/stream.html?src=uvc_cam_dual
```

### Test Locally Without go2rtc

```bash
# Switch camera mode
./thermal_camera_mode.sh thermal

# Get test command and run it
./thermal_camera_mode.sh current
# Copy and paste the command shown
```

### Example Test Commands

**Thermal-only (256x192):**
```bash
./thermal_camera_mode.sh thermal
v4l2-ctl -d /dev/video0 --stream-mmap=3 --stream-count=0 --stream-to=- \
  | ffplay -f rawvideo -pixel_format yuyv422 -video_size 256x192 -
```

**Dual-plane (256x392):**
```bash
./thermal_camera_mode.sh dual
v4l2-ctl -d /dev/video0 --stream-mmap=3 --stream-count=0 --stream-to=- \
  | ffplay -f rawvideo -pixel_format yuyv422 -video_size 256x392 -
```

## Performance

| Stream | Encoding | CPU % | Latency | Quality |
|--------|----------|-------|---------|---------|
| `uvc_cam` | Software | ~25% | Medium | Good |
| `uvc_cam_dual` | Software | ~40% | Medium | High |

*CPU % based on typical Intel i5/i7 desktop processor*

**Note:** All streams require software H.264 encoding via FFmpeg because the camera's hardware compression modes don't work.

## Troubleshooting

### Stream won't start
1. Check camera mode matches config
2. Stop go2rtc: `make stop`
3. Verify mode: `./thermal_camera_mode.sh current`
4. Restart: `make run`

### Poor quality
- Lower resolution (use thermal instead of dual)
- Adjust CRF in go2rtc.yaml (higher = lower quality/CPU)

### Camera in wrong mode
```bash
./thermal_camera_mode.sh thermal  # or dual
make restart
```

## See Also

- [CAMERA.md](CAMERA.md) - Camera hardware documentation and firmware bugs
- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [CLAUDE.md](CLAUDE.md) - Project documentation
