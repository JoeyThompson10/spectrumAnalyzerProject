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

# ===================================
# 1. Import necessary libraries
# ===================================
import cv2
import numpy as np
from scipy.optimize import curve_fit
import csv

# ===================================
# 2. Define constants
# ===================================

# User-configurable constants for color filtering
LOWER_GREEN = np.array([33, 45, 45])
UPPER_GREEN = np.array([92, 260, 260])
LOWER_WAVE_COLOR = np.array([78, 145, 115])
UPPER_WAVE_COLOR = np.array([102, 260, 260])

# Image filtering parameters
KERNEL_SIZE = np.ones((5, 5), np.uint8)
DILATE_ITERATIONS = 1
ERODE_ITERATIONS = 1

# Video configuration
VIDEO_PATH = 'CW Signal.mp4'
QUIT_KEY = 'q'

# ===================================
# 3. Define utility functions
# ===================================

def parabola(x, a, b, c):
    """Defines a parabolic function."""
    return a * x ** 2 + b * x + c

def apply_color_filter(frame, lower_bound, upper_bound):
    """Apply a color filter based on RGB lower and upper bounds."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    return mask

def find_largest_contour(mask):
    """Find and return the largest contour in a given binary mask."""
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return max(contours, key=cv2.contourArea) if contours else None

def find_wave(frame):
    """Find and process the wave within a video frame."""
    mask = apply_color_filter(frame, LOWER_WAVE_COLOR, UPPER_WAVE_COLOR)
    largest_contour = find_largest_contour(mask)

    if largest_contour is not None and largest_contour.size > 0:
        mask = np.zeros_like(mask)
        cv2.drawContours(mask, [largest_contour], -1, (255), thickness=cv2.FILLED)
        
        # Connect nearby contours by dilating and then eroding
        mask = cv2.dilate(mask, KERNEL_SIZE, iterations=DILATE_ITERATIONS)
        mask = cv2.erode(mask, KERNEL_SIZE, iterations=ERODE_ITERATIONS)

    return mask, np.where(mask)

#Need to rework this function to return the correct values
def process_wave(wave_x, wave_y):
    """Analyze and extract wave characteristics."""
    if wave_x.size > 0 and wave_y.size > 0:
        params, _ = curve_fit(parabola, wave_x, wave_y)
        a, b, c = params

        # Calculate various wave characteristics
        center_freq = -b / (2 * a)
        min_amplitude, max_amplitude = np.min(wave_y), np.max(wave_y)
        center_amplitude = (max_amplitude + min_amplitude) / 2
        return center_freq, min_amplitude, max_amplitude, center_amplitude
    return None

# ===================================
# 4. Main execution functions
# ===================================

def print_wave_characteristics(result, frame_number, fps):
    """Print extracted wave characteristics to the console."""
    timestamp = frame_number / fps
    center_freq, min_amplitude, max_amplitude, center_amplitude = result
    print(f"Timestamp: {timestamp} seconds")
    print(f"Center Frequency: {center_freq}")
    print(f"Minimum Amplitude: {min_amplitude}")
    print(f"Maximum Amplitude: {max_amplitude}")
    print(f"Center Amplitude: {center_amplitude}\n")

def main():
    """Main execution function for analyzing the video."""
    # Open the video file for processing
    cap = cv2.VideoCapture(VIDEO_PATH)
    # Check if the video file opened successfully
    if not cap.isOpened():
        print("Error: Could not open the video file.")
        return

    # Get video properties like width, height, and FPS
    frame_width, frame_height = int(cap.get(3)), int(cap.get(4))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"Playing video with dimensions: {frame_width}x{frame_height} and {fps} FPS.")

    # List to store detected signals' information
    detected_signals = []

    # Main loop to process each frame in the video
    while cap.isOpened():
        ret, frame = cap.read()
        # If there's no more frame to read, exit the loop
        if not ret:
            break

        if frame is not None:
            # Process and identify the wave from the frame using color filtering and contour detection
            # mask will be displayed to the user to show the detected wave
            # wave_x and wave_y will be used to extract wave characteristics
            # mask will be None if no wave is detected
            mask, (wave_x, wave_y) = find_wave(frame)
            
            # Get detailed information from the processed wave
            result = process_wave(wave_x, wave_y)
            
            # If a valid result is obtained, print and store it
            if result:
                print_wave_characteristics(result, cap.get(cv2.CAP_PROP_POS_FRAMES), fps)
                detected_signals.append(result)
                # Show the cropped frame with the wave to the user
                cv2.imshow('Video', mask)

            else:
                # If screen is not detected, simply show the entire frame
                cv2.imshow('Video', frame)

        # Allow for user intervention to quit video playback
        if cv2.waitKey(1000 // fps) & 0xFF == ord(QUIT_KEY):
            break

    # Store detected signals' information to a CSV file
    csv_file = 'detected_signals.csv'
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Define the CSV columns
        writer.writerow(['Timestamp (s)', 'Center Frequency', 'Minimum Amplitude', 'Maximum Amplitude', 'Center Amplitude'])
        for signal in detected_signals:
            frame_number = cap.get(cv2.CAP_PROP_POS_FRAMES) - len(detected_signals) + detected_signals.index(signal)
            timestamp = frame_number / fps
            center_freq, min_amplitude, max_amplitude, center_amplitude = signal
            writer.writerow([timestamp, center_freq, min_amplitude, max_amplitude, center_amplitude])

    # Properly release the video and close any GUI windows
    cap.release()
    cv2.destroyAllWindows()
    print("Video playback is done.")

# ===================================
# 5. Script entry point
# ===================================
if __name__ == "__main__":
    main()