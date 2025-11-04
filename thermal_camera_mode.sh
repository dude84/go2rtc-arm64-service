#!/bin/bash
# Hikvision JS-MINI256-9 Thermal Camera Mode Switcher

DEVICE="/dev/video0"

show_usage() {
    echo "Usage: $0 [mode|list|current]"
    echo ""
    echo "Raw YUYV Modes (require FFmpeg encoding):"
    echo "  thermal     - 256x192 thermal-only mode (default)"
    echo "  dual        - 256x392 dual-plane mode"
    echo "  mode3       - 256x196"
    echo "  mode4       - 256x200"
    echo "  mode5       - 256x400"
    echo "  portrait1   - 192x520"
    echo "  portrait2   - 192x400"
    echo ""
    echo "Commands:"
    echo "  list        - Show all available formats"
    echo "  current     - Show current format"
    echo ""
    echo "Note: Modes 4, 5, and portrait2 are advertised but produce no frames (firmware bug)."
    echo "      MJPEG/H.264 modes are also advertised but produce invalid data."
    echo "      Only use the working YUYV modes listed above."
}

set_mode() {
    local width=$1
    local height=$2
    local desc=$3

    echo "Setting camera to ${width}x${height} ($desc)..."
    if v4l2-ctl -d $DEVICE --set-fmt-video=width=$width,height=$height 2>&1 | grep -q "failed"; then
        echo "ERROR: Failed to set format"
        return 1
    fi
    echo "Success! Camera is now in ${width}x${height} mode"
    v4l2-ctl -d $DEVICE --get-fmt-video | grep -E "Width|Height|Size Image"

    # Show test command for this mode
    echo ""
    show_test_commands
}

show_test_commands() {
    format_info=$(v4l2-ctl -d $DEVICE --get-fmt-video)

    # Extract current format details
    width=$(echo "$format_info" | grep "Width/Height" | awk '{print $3}' | cut -d'/' -f1)
    height=$(echo "$format_info" | grep "Width/Height" | awk '{print $3}' | cut -d'/' -f2)
    pixfmt=$(echo "$format_info" | grep "Pixel Format" | cut -d"'" -f2)

    echo "=== Test command for this mode ==="

    case "$pixfmt" in
        YUYV)
            echo "v4l2-ctl -d $DEVICE --stream-mmap=3 --stream-count=0 --stream-to=- \\"
            echo "  | ffplay -f rawvideo -pixel_format yuyv422 -video_size ${width}x${height} -"
            ;;
        MJPG)
            echo "v4l2-ctl -d $DEVICE --set-fmt-video=pixelformat=MJPG,width=${width},height=${height} \\"
            echo "  --stream-mmap=3 --stream-count=0 --stream-to=- | ffplay -f mjpeg -"
            ;;
        H264)
            echo "v4l2-ctl -d $DEVICE --set-fmt-video=pixelformat=H264,width=${width},height=${height} \\"
            echo "  --stream-mmap=3 --stream-count=0 --stream-to=- | ffplay -f h264 -"
            ;;
        *)
            echo "# Unknown format: $pixfmt"
            echo "# Manual testing required"
            ;;
    esac

}

case "${1:-current}" in
    thermal)
        set_mode 256 192 "Thermal-only"
        ;;
    dual)
        set_mode 256 392 "Dual-plane"
        ;;
    mode3)
        set_mode 256 196 "Mode 3"
        ;;
    mode4)
        set_mode 256 200 "Mode 4"
        ;;
    mode5)
        set_mode 256 400 "Mode 5"
        ;;
    portrait1)
        set_mode 192 520 "Portrait 1"
        ;;
    portrait2)
        set_mode 192 400 "Portrait 2"
        ;;
    list)
        echo "Available formats:"
        v4l2-ctl -d $DEVICE --list-formats-ext
        ;;
    current)
        echo "Current camera format:"
        v4l2-ctl -d $DEVICE --get-fmt-video
        echo ""
        show_test_commands
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
