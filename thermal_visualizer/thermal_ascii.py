#!/usr/bin/env python3
"""
Real-time thermal ASCII visualizer with inferno colormap.
Captures from Hikvision JS-MINI256-9 thermal camera in dual mode (256x392)
and displays the green thermal data as colored ASCII art.
"""

import cv2
import numpy as np
import sys
import subprocess
import time
import warnings

# Suppress matplotlib deprecation warning
warnings.filterwarnings('ignore', category=DeprecationWarning)

try:
    from matplotlib import pyplot as plt
    get_colormap = lambda name: plt.get_cmap(name)
except:
    from matplotlib import cm
    get_colormap = lambda name: cm.get_cmap(name)

DEVICE = "/dev/video0"
WIDTH = 256
HEIGHT = 392
GREEN_LINES = 192  # Top 192 lines contain green thermal data

# ANSI color codes for inferno colormap
def get_inferno_colors(num_levels=256):
    """Get inferno colormap as ANSI escape codes"""
    inferno = get_colormap('inferno')
    colors = []
    for i in range(num_levels):
        rgba = inferno(i / num_levels)
        r, g, b = int(rgba[0] * 255), int(rgba[1] * 255), int(rgba[2] * 255)
        # ANSI 24-bit color escape code
        colors.append(f"\033[38;2;{r};{g};{b}m")
    return colors

INFERNO_COLORS = get_inferno_colors()
RESET_COLOR = "\033[0m"

# ASCII gradient characters (dark to light)
ASCII_GRADIENT = " ░▒▓█"

class ThermalVisualizer:
    def __init__(self, downsample=4, contrast=1.0):
        self.downsample = downsample
        self.contrast = contrast
        self.running = False
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.fps = 0
        
    def set_camera_mode(self):
        """Set camera to dual mode"""
        print(f"Setting camera to dual mode ({WIDTH}x{HEIGHT})...")
        result = subprocess.run(
            ["v4l2-ctl", "-d", DEVICE, f"--set-fmt-video=width={WIDTH},height={HEIGHT}"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        print("Camera mode set successfully")
        return True
    
    def process_frame(self, frame):
        """Extract and process green thermal data"""
        # Extract top 192 lines (green thermal data)
        thermal_section = frame[0:GREEN_LINES, :]
        
        # Extract green channel (OpenCV uses BGR, so green is index 1)
        green_channel = thermal_section[:, :, 1]
        
        # Downsample for ASCII display
        if self.downsample > 1:
            h, w = green_channel.shape
            new_h = h // self.downsample
            new_w = w // self.downsample
            green_channel = cv2.resize(green_channel, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # Apply contrast
        green_channel = green_channel.astype(float)
        mean_val = green_channel.mean()
        green_channel = mean_val + self.contrast * (green_channel - mean_val)
        green_channel = np.clip(green_channel, 0, 255).astype(np.uint8)
        
        return green_channel
    
    def render_ascii(self, data):
        """Render thermal data as colored ASCII"""
        lines = []
        h, w = data.shape
        
        for y in range(h):
            line = ""
            for x in range(w):
                intensity = data[y, x]
                
                # Map to inferno color
                color_idx = min(int(intensity), 255)
                color = INFERNO_COLORS[color_idx]
                
                # Map to ASCII character
                char_idx = min(int((intensity / 255.0) * (len(ASCII_GRADIENT) - 1)), len(ASCII_GRADIENT) - 1)
                char = ASCII_GRADIENT[char_idx]
                
                line += f"{color}{char}{char}{RESET_COLOR}"  # Double char for aspect ratio
            
            lines.append(line)
        
        return "\n".join(lines)
    
    def display_stats(self, data):
        """Display statistics overlay"""
        stats = [
            f"FPS: {self.fps:.1f}",
            f"Min: {data.min():.0f}  Max: {data.max():.0f}  Mean: {data.mean():.1f}",
            f"Size: {data.shape[1]}x{data.shape[0]} (downsampled from {WIDTH}x{GREEN_LINES})",
            f"Contrast: {self.contrast:.1f}x",
            "",
            "Controls: q=quit  +=increase contrast  -=decrease contrast  r=reset",
        ]
        return "\n".join(stats)
    
    def clear_screen(self):
        """Clear terminal screen"""
        print("\033[2J\033[H", end="")
    
    def run(self):
        """Main visualization loop"""
        # Set camera mode
        if not self.set_camera_mode():
            return False
        
        # Open camera
        print("Opening camera...")
        cap = cv2.VideoCapture(DEVICE, cv2.CAP_V4L2)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return False
        
        # Set format
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V'))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        
        print("\nStarting visualization...")
        print("Press Ctrl+C to stop\n")
        time.sleep(1)
        
        self.running = True
        self.clear_screen()
        
        try:
            while self.running:
                # Capture frame
                ret, frame = cap.read()
                if not ret:
                    print("Warning: Failed to capture frame")
                    time.sleep(0.1)
                    continue
                
                # Process frame
                thermal_data = self.process_frame(frame)
                
                # Render ASCII
                ascii_art = self.render_ascii(thermal_data)
                
                # Calculate FPS
                self.frame_count += 1
                if self.frame_count % 10 == 0:
                    current_time = time.time()
                    elapsed = current_time - self.last_fps_time
                    self.fps = 10 / elapsed
                    self.last_fps_time = current_time
                
                # Display
                self.clear_screen()
                print(ascii_art)
                print("\n" + "─" * 80)
                print(self.display_stats(thermal_data))
                
                # Small delay to prevent overwhelming the terminal
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n\nStopping visualization...")
        finally:
            cap.release()
            self.clear_screen()
            print(f"Total frames: {self.frame_count}")
            print("Visualization stopped")
        
        return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Real-time thermal ASCII visualizer")
    parser.add_argument("--downsample", type=int, default=4,
                       help="Downsample factor (1=full resolution, 4=quarter, default=4)")
    parser.add_argument("--contrast", type=float, default=1.5,
                       help="Contrast enhancement factor (default=1.5)")
    
    args = parser.parse_args()
    
    visualizer = ThermalVisualizer(
        downsample=args.downsample,
        contrast=args.contrast
    )
    
    success = visualizer.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
