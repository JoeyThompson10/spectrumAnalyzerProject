import cv2
import numpy as np
from scipy.optimize import curve_fit
import env_vars


class Utilities:
    """Utility functions for the spectrum analyzer."""
    def findGrid(frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(
            hsv, env_vars.Env_Vars.LOWER_GRID_COLOR, env_vars.Env_Vars.UPPER_GRID_COLOR
        )
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        green_grid = cv2.bitwise_and(frame, frame, mask=mask)
        gray = cv2.cvtColor(green_grid, cv2.COLOR_BGR2GRAY)
        low_threshold = 10
        high_threshold = 500
        edges = cv2.Canny(gray, low_threshold, high_threshold)
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        return contours
    
    def getPixtoDb(px_value, span, gridheight): 
        dbPxHeight = (gridheight)/span
        wave_amplitude = px_value/dbPxHeight
        return wave_amplitude

    def parabola(x, a, b, c):
        """Defines a parabolic function."""
        return a * x**2 + b * x + c

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
        mask = Utilities.apply_color_filter(
            frame,
            env_vars.Env_Vars.LOWER_WAVE_COLOR,
            env_vars.Env_Vars.UPPER_WAVE_COLOR,
        )
        largest_contour = Utilities.find_largest_contour(mask)

        if largest_contour is not None and largest_contour.size > 0:
            mask = np.zeros_like(mask)
            cv2.drawContours(mask, [largest_contour], -1, (255), thickness=cv2.FILLED)

            # Connect nearby contours by dilating and then eroding
            mask = cv2.dilate(
                mask,
                env_vars.Env_Vars.KERNEL_SIZE,
                iterations=env_vars.Env_Vars.DILATE_ITERATIONS,
            )
            mask = cv2.erode(
                mask,
                env_vars.Env_Vars.KERNEL_SIZE,
                iterations=env_vars.Env_Vars.ERODE_ITERATIONS,
            )

        return mask, np.where(mask)
    def find_center_freq(frame):
        threshold_value = 100
        thresholded_frame = cv2.threshold(frame, threshold_value, 255, cv2.THRESH_BINARY)[1]
        center_freq = 0
        contours, _ = cv2.findContours(thresholded_frame , cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 1:
            line_distances = [contours[i + 1][0][0][0] - contours[i][0][0][0] for i in range(len(contours) - 1)]
            center_freq = np.mean(line_distances)
        
        return center_freq

    def process_wave(frame, mask, span, gridheight, wave_x, wave_y):
        """Analyze and extract wave characteristics."""
        if len(wave_x) > 0 and len(wave_y) > 0:
            # Fit the points to a parabola
            params, _ = curve_fit(Utilities.parabola, wave_x, wave_y)

        # Extract the coefficients of the fitted parabola
        a, b, c = params

        # Calculate center frequency using vertex formula (-b / 2a)
        center_freq_px = -b / (2 * a)
        center_freq = Utilities.getPixtoDb(center_freq_px, span, gridheight)
        mask_height = Utilities.get_mask_height(mask) #pixel height of the mask
        amplitude = Utilities.getPixtoDb(mask_height, span, gridheight)
        min_amplitude = amplitude
        max_amplitude = amplitude
        center_amplitude = 0
        return center_freq, min_amplitude, max_amplitude, center_amplitude


    def get_mask_height(mask):
        # Find the row indices of non-zero pixels in the mask
        non_zero_rows = np.where(mask)[0]

        if non_zero_rows.size > 0:
            # Calculate the minimum and maximum row indices to find the height
            min_row = np.min(non_zero_rows)
            max_row = np.max(non_zero_rows)

            # Calculate the height as the difference between max and min rows
            height = (
                max_row - min_row + 1
            )  # Adding 1 to account for inclusive row indices
            return height
        else:
            # If there are no non-zero pixels, return 0 as the height
            return 0

    def print_wave_characteristics(result, frame_number, fps, gridheight):
        """Print extracted wave characteristics."""
        timestamp = frame_number / fps
        # center_freq, min_amplitude, max_amplitude, center_amplitude = result
        max_amplitude = result
        print(f"Timestamp: {timestamp} seconds")
        print(f"Gridheight: {gridheight}")
        # print(f"Center Frequency: {center_freq}")
        # print(f"Minimum Amplitude: {min_amplitude}")
        print(f"Maximum Amplitude: {max_amplitude}")
        # print(f"Center Amplitude: {center_amplitude}\n")
