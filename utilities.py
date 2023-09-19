import cv2
import csv
import numpy as np
from scipy.optimize import curve_fit
import env_vars

# ===================================
# Utility functions
# ===================================
class Utilities:
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
        mask = Utilities.apply_color_filter(frame, env_vars.Env_Vars.LOWER_WAVE_COLOR, env_vars.Env_Vars.UPPER_WAVE_COLOR)
        largest_contour = Utilities.find_largest_contour(mask)

        if largest_contour is not None and largest_contour.size > 0:
            mask = np.zeros_like(mask)
            cv2.drawContours(mask, [largest_contour], -1, (255), thickness=cv2.FILLED)
            
            # Connect nearby contours by dilating and then eroding
            mask = cv2.dilate(mask, env_vars.Env_Vars.KERNEL_SIZE, iterations=env_vars.Env_Vars.DILATE_ITERATIONS)
            mask = cv2.erode(mask, env_vars.Env_Vars.KERNEL_SIZE, iterations=env_vars.Env_Vars.ERODE_ITERATIONS)

        return mask, np.where(mask)

    def process_wave(wave_x, wave_y):
        """Analyze and extract wave characteristics."""
        if wave_x.size > 0 and wave_y.size > 0:
            params, _ = curve_fit(Utilities.parabola, wave_x, wave_y)
            a, b, c = params

            # Calculate various wave characteristics
            center_freq = -b / (2 * a)
            min_amplitude, max_amplitude = np.min(wave_y), np.max(wave_y)
            center_amplitude = (max_amplitude + min_amplitude) / 2
            return center_freq, min_amplitude, max_amplitude, center_amplitude
        return None
    pass

    def print_wave_characteristics(result, frame_number, fps):
        """Print extracted wave characteristics to the console."""
        timestamp = frame_number / fps
        center_freq, min_amplitude, max_amplitude, center_amplitude = result
        print(f"Timestamp: {timestamp} seconds")
        print(f"Center Frequency: {center_freq}")
        print(f"Minimum Amplitude: {min_amplitude}")
        print(f"Maximum Amplitude: {max_amplitude}")
        print(f"Center Amplitude: {center_amplitude}\n")

    def store_to_csv(detected_signals, cap, fps):
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