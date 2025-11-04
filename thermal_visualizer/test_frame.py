#!/usr/bin/env python3
"""
Test script to capture and analyze a single frame from the thermal camera
in dual mode (256x392) to verify the data structure.
"""

import cv2
import numpy as np
import sys
import subprocess

DEVICE = "/dev/video0"
WIDTH = 256
HEIGHT = 392

def set_camera_mode():
    """Set camera to dual mode (256x392)"""
    print("Setting camera to dual mode (256x392)...")
    result = subprocess.run(
        ["v4l2-ctl", "-d", DEVICE, f"--set-fmt-video=width={WIDTH},height={HEIGHT}"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Error setting camera mode: {result.stderr}")
        return False
    print("Camera set to dual mode successfully")
    return True

def capture_frame():
    """Capture a single YUYV frame"""
    print(f"Opening camera {DEVICE}...")
    
    # Open camera
    cap = cv2.VideoCapture(DEVICE, cv2.CAP_V4L2)
    
    # Set format to YUYV
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    
    # Capture frame
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Error: Failed to capture frame")
        return None
    
    print(f"Frame captured: shape={frame.shape}, dtype={frame.dtype}")
    return frame

def analyze_frame(frame):
    """Analyze the dual-mode frame structure"""
    print("\n=== Frame Analysis ===")
    print(f"Total frame size: {frame.shape}")
    print(f"Expected: (392, 256, 3) for BGR format")
    
    # Split into top and bottom sections
    # According to user: 192(green) + 3(metadata) + 192(user-friendly) + 3-5(metadata)
    top_thermal = frame[0:192, :]      # Green thermal data
    metadata1 = frame[192:195, :]       # First metadata lines
    bottom_thermal = frame[195:387, :]  # User-friendly thermal
    metadata2 = frame[387:, :]          # Second metadata lines
    
    print(f"\nTop thermal (green): {top_thermal.shape}")
    print(f"  Mean intensity: R={top_thermal[:,:,2].mean():.1f} G={top_thermal[:,:,1].mean():.1f} B={top_thermal[:,:,0].mean():.1f}")
    print(f"  Min/Max: {top_thermal.min()}-{top_thermal.max()}")
    
    print(f"\nMetadata 1 (lines 192-194): {metadata1.shape}")
    print(f"  Mean values: {metadata1.mean(axis=(0,1))}")
    
    print(f"\nBottom thermal (user-friendly): {bottom_thermal.shape}")
    print(f"  Mean intensity: R={bottom_thermal[:,:,2].mean():.1f} G={bottom_thermal[:,:,1].mean():.1f} B={bottom_thermal[:,:,0].mean():.1f}")
    print(f"  Min/Max: {bottom_thermal.min()}-{bottom_thermal.max()}")
    
    print(f"\nMetadata 2 (lines 387-end): {metadata2.shape}")
    print(f"  Mean values: {metadata2.mean(axis=(0,1))}")
    
    # Save sections for inspection
    cv2.imwrite("frame_full.png", frame)
    cv2.imwrite("frame_top_green.png", top_thermal)
    cv2.imwrite("frame_bottom_thermal.png", bottom_thermal)
    
    print("\n=== Files saved ===")
    print("frame_full.png - Full 256x392 frame")
    print("frame_top_green.png - Top 192 lines (green thermal)")
    print("frame_bottom_thermal.png - Bottom 192 lines (user-friendly)")
    
    # Extract green channel from top section
    green_channel = top_thermal[:, :, 1]  # OpenCV uses BGR
    print(f"\n=== Green Channel Stats ===")
    print(f"Shape: {green_channel.shape}")
    print(f"Min: {green_channel.min()}, Max: {green_channel.max()}, Mean: {green_channel.mean():.1f}")
    print(f"Std: {green_channel.std():.1f}")
    
    # Create histogram
    hist, bins = np.histogram(green_channel, bins=256, range=(0, 256))
    print(f"\nHistogram peak at intensity: {np.argmax(hist)}")
    
    return green_channel

def main():
    # Set camera mode
    if not set_camera_mode():
        sys.exit(1)
    
    # Capture frame
    frame = capture_frame()
    if frame is None:
        sys.exit(1)
    
    # Analyze frame structure
    green_data = analyze_frame(frame)
    
    print("\n✓ Test completed successfully!")
    print("Check the saved PNG files to verify the structure.")

if __name__ == "__main__":
    main()
