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
# Import necessary libraries
# ===================================
import cv2
import numpy as np
from scipy.optimize import curve_fit
import csv
import utilities
import env_vars

# ===================================
#  Main execution functions
# ===================================

def print_wave_characteristics(result, frame_number, fps):
    """Print extracted wave characteristics."""
    timestamp = frame_number / fps
    center_freq, min_amplitude, max_amplitude, center_amplitude = result
    print(f"Timestamp: {timestamp} seconds")
    print(f"Center Frequency: {center_freq}")
    print(f"Minimum Amplitude: {min_amplitude}")
    print(f"Maximum Amplitude: {max_amplitude}")
    print(f"Center Amplitude: {center_amplitude}\n")

def main():
    """Main execution function."""
    # Video setup
    cap = cv2.VideoCapture(env_vars.Env_Vars.VIDEO_PATH)
    if not cap.isOpened():
        print("Error: Could not open the video file.")
        return

    frame_width, frame_height = int(cap.get(3)), int(cap.get(4))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"Playing video with dimensions: {frame_width}x{frame_height} and {fps} FPS.")

    detected_signals = []

    # Main video processing loop
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        screen_info = utilities.Utilities.find_screen(frame)
        if screen_info:
            x, y, w, h = screen_info
            cropped_frame = frame[y:y + h, x:x + w]
            mask, (wave_x, wave_y) = utilities.Utilities.find_wave(cropped_frame)
            result = utilities.Utilities.process_wave(wave_x, wave_y)

            if result:
                print_wave_characteristics(result, cap.get(cv2.CAP_PROP_POS_FRAMES), fps)
                detected_signals.append(result)
            cv2.imshow('Video', mask)
        else:
            cv2.imshow('Video', frame)

        if cv2.waitKey(1000 // fps) & 0xFF == ord(env_vars.Env_Vars.QUIT_KEY):
            break

    # Save results to CSV
    csv_file = 'detected_signals.csv'
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp (s)', 'Center Frequency', 'Minimum Amplitude', 'Maximum Amplitude', 'Center Amplitude'])
        for signal in detected_signals:
            frame_number = cap.get(cv2.CAP_PROP_POS_FRAMES) - len(detected_signals) + detected_signals.index(signal)
            timestamp = frame_number / fps
            center_freq, min_amplitude, max_amplitude, center_amplitude = signal
            writer.writerow([timestamp, center_freq, min_amplitude, max_amplitude, center_amplitude])

    cap.release()
    cv2.destroyAllWindows()
    print("Video playback is done.")

# ===================================
# 5. Script entry point
# ===================================
if __name__ == "__main__":
    main()