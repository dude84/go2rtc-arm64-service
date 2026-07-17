# go2rtc-arm64-service

Camera + microphone streaming for a Raspberry Pi, built around [go2rtc](https://github.com/AlexxIT/go2rtc). This repo manages the ARM64 binary, its configuration, and a systemd service so the stream comes up automatically after boot.

This is a **deployment repo**, not source code: it downloads the prebuilt go2rtc binary, configures it for the local hardware, and installs it as a service.

## Hardware

- Raspberry Pi 4 (ARM64, Raspberry Pi OS)
- Raspberry Pi **HQ Camera (IMX477)** on the CSI connector
  (previously: Camera Module v2 NoIR / IMX219 — old settings kept commented out)
- **INMP441** I2S MEMS microphone (via the `googlevoicehat-soundcard` overlay, captured through PipeWire)

## Quick start

```bash
make update             # download the latest go2rtc ARM64 binary into bin/
make service-install    # install + enable + start the systemd service (sudo)
```

Then open the go2rtc web UI at `http://<pi>:1984`.

## Streams

Defined in [bin/go2rtc.yaml](bin/go2rtc.yaml):

| Stream | Content |
|--------|---------|
| `cam0` | H.264 1920x1080 @ 15 fps from `rpicam-vid` (rotated 180°), plus Opus audio from the I2S mic |
| `mic`  | Audio only (16 kHz mono Opus via PipeWire → ffmpeg) — allows concurrent access to the mic |

Video comes from `rpicam-vid`, so the camera is only opened while a client is connected. Adjust resolution, framerate, bitrate, or rotation by editing the `rpicam-vid` arguments in the yaml, then `sudo systemctl restart go2rtc`.

## Makefile targets

```bash
make update             # download latest go2rtc ARM64 binary
make run / stop / restart / status   # ad-hoc daemon control (without systemd)
make service-install    # install, enable, and start the systemd service (sudo)
make service-uninstall  # stop, disable, and remove the service (sudo)
```

After installation the service is managed normally:

```bash
sudo systemctl status go2rtc
sudo systemctl restart go2rtc
journalctl -u go2rtc -f
```

## Boot configuration (camera)

The camera overlay is pinned in `/boot/firmware/config.txt` (auto-detect is off):

```
camera_auto_detect=0
dtoverlay=imx477,cam1        # HQ camera
#dtoverlay=imx219,cam1       # old Camera Module v2 NoIR
dtoverlay=googlevoicehat-soundcard   # I2S microphone
```

A reboot is required after changing overlays. Verify the camera is detected with:

```bash
rpicam-hello --list-cameras
```

The HQ camera's tuning file (`imx477.json`) is picked up by libcamera automatically — no `--tuning-file` flag needed. For the old NoIR camera a `--tuning-file` override was used; it is preserved as a comment at the bottom of the yaml.

## Troubleshooting

- **"No cameras available!"** — the `dtoverlay` in `/boot/firmware/config.txt` doesn't match the connected sensor, or the ribbon cable is loose. Check `dmesg | grep -i imx` for probe errors.
- **Stream won't start** — `journalctl -u go2rtc -f` while opening the stream; exec producers log their stderr there.
- **Mic silent** — check the source exists: `pw-record --list-targets` (PipeWire must be running for the service user).

## Files

- [Makefile](Makefile) — all operations (update, daemon control, service install)
- [go2rtc.service](go2rtc.service) — systemd unit template (placeholders filled at install time)
- [bin/go2rtc.yaml](bin/go2rtc.yaml) — stream configuration
- `bin/go2rtc` — the binary itself (git-ignored; fetched by `make update`)
