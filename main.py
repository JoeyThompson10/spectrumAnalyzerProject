# ==============================================================================
# SWE 4724- Software Engineering Project
# Instructor: Dr. Yan Huang
# Group: 8
# Members:
#     - Masood Afzal
#     - Ashly Altman
#     - Brooke Ebetino
#     - Tyler Halley
#     - Joey Thompson
# Project Title: Spectrum Analyzer Analysis Tool
# Client: 402 SWEG
# ==============================================================================

import cv2
import numpy as np
from scipy.optimize import curve_fit

# User-configurable constants
# RGB lower and upper bounds to identify the "screen" region
LOWER_GREEN = np.array([33, 45, 45])
UPPER_GREEN = np.array([92, 260, 260])

# RGB lower and upper bounds to identify the "wave" region
LOWER_WAVE_COLOR = np.array([78, 145, 115])
UPPER_WAVE_COLOR = np.array([102, 260, 260])

# Kernel size and dilation/erosion iterations for image filtering
KERNEL_SIZE = np.ones((5, 5), np.uint8)
DILATE_ITERATIONS = 1
ERODE_ITERATIONS = 1

# File path to the video to analyze
VIDEO_PATH = 'CW Signal.mp4'

# Key to quit the video playback
QUIT_KEY = 'q'

# Define a parabolic function for curve fitting
def parabola(x, a, b, c):
    """Defines a parabolic function."""
    return a * x ** 2 + b * x + c

# Apply a color filter based on RGB lower and upper bounds
def apply_color_filter(frame, lower_bound, upper_bound):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    return mask

# Find and return the largest contour in a given binary mask
def find_largest_contour(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return max(contours, key=cv2.contourArea) if contours else None

# Identify the screen area within a video frame based on its color
def find_screen(frame):
    mask = apply_color_filter(frame, LOWER_GREEN, UPPER_GREEN)
    largest_contour = find_largest_contour(mask)
    
    if largest_contour is not None and largest_contour.size > 0:
        return cv2.boundingRect(largest_contour)
    else:
        return None

# Find and process the wave within a video frame
def find_wave(frame):
    mask = apply_color_filter(frame, LOWER_WAVE_COLOR, UPPER_WAVE_COLOR)
    largest_contour = find_largest_contour(mask)

    if largest_contour is not None and largest_contour.size > 0:
        mask = np.zeros_like(mask)
        cv2.drawContours(mask, [largest_contour], -1, (255), thickness=cv2.FILLED)
        
        # Connect nearby contours by dilating and then eroding
        mask = cv2.dilate(mask, KERNEL_SIZE, iterations=DILATE_ITERATIONS)
        mask = cv2.erode(mask, KERNEL_SIZE, iterations=ERODE_ITERATIONS)

    return mask, np.where(mask)

# Analyze and extract wave characteristics
def process_wave(wave_x, wave_y):
    if len(wave_x) > 0 and len(wave_y) > 0:
        params, _ = curve_fit(parabola, wave_x, wave_y)
        a, b, c = params

        # Calculate various wave characteristics
        center_freq = -b / (2 * a)
        min_amplitude, max_amplitude = np.min(wave_y), np.max(wave_y)
        center_amplitude = (max_amplitude + min_amplitude) / 2
        return center_freq, min_amplitude, max_amplitude, center_amplitude
    return None

# Main execution function
def main():
    # Initialization and video metadata fetching
    video_path = VIDEO_PATH
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open the video file.")
        return

    frame_width, frame_height = int(cap.get(3)), int(cap.get(4))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"Playing video with dimensions: {frame_width}x{frame_height} and {fps} FPS.")

    # Initialize some variables
    peak_counter = 0

    # Main video processing loop
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Reached the end of the video or an error occurred.")
            break

        # Detect screen and wave regions
        screen_info = find_screen(frame)
        if screen_info:
            x, y, w, h = screen_info
            cropped_frame = frame[y:y + h, x:x + w]
            mask, (wave_x, wave_y) = find_wave(cropped_frame)
            result = process_wave(wave_x, wave_y)

            # Additional stabilization logic can be added here

            # If a wave was successfully processed
            if result:
                peak_counter += 1
                if peak_counter % (fps * 3) == 0:
                    print_wave_characteristics(result, cap.get(cv2.CAP_PROP_POS_FRAMES), fps)

            cv2.imshow('Video', mask)
        else:
            cv2.imshow('Video', frame)

        if cv2.waitKey(1000 // fps) & 0xFF == ord(QUIT_KEY):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Video playback is done.")

# Function to print extracted wave characteristics
def print_wave_characteristics(result, frame_number, fps):
    timestamp = frame_number / fps
    center_freq, min_amplitude, max_amplitude, center_amplitude = result
    print(f"Timestamp: {timestamp} seconds")
    print(f"Center Frequency: {center_freq}")
    print(f"Minimum Amplitude: {min_amplitude}")
    print(f"Maximum Amplitude: {max_amplitude}")
    print(f"Center Amplitude: {center_amplitude}\n")

# Entry point of the script
if __name__ == "__main__":
    main()
