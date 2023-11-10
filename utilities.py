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

        return contours, np.where(mask)
    
    def getAmplitude(px_value, dbPerHLine, gridheight): 
        dbPxHeight = (gridheight)/(dbPerHLine*10)
        wave_amplitude = px_value/dbPxHeight
        return wave_amplitude
    
    def getCenterFreq(center_freq_px, span, center, gridwidth, center_x): 
        
        hzPxWidth = gridwidth/(span) # get width of 1HZ
        print(f"center_x: {center_x} px")
        print(f"center_freq_px: {center_freq_px} px")
        deviation_px = center_x - center_freq_px # get the deviation of the center frequency pixel value from the center line's x value
        center_freq = center+(deviation_px/hzPxWidth)*0.001 # convert the deviation in pixels to HZ and add to the center (eg 1GHZ) to find center frequency
        return center_freq

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
        # find the leftmost point of the mask 
        leftmost_x = None
        rightmost_x = None
        leftmost_y = None
        for point in largest_contour:
            x, y = point[0]
            x2, y2 = point[len(point)-1]
            if leftmost_x is None or x < leftmost_x:
                leftmost_x = x
                leftmost_y = y
            if rightmost_x is None or x2 > rightmost_x:
                rightmost_x = x2
        
        center_x = (rightmost_x+leftmost_x)/2
        mask_width = rightmost_x-leftmost_x
        return mask, np.where(mask), leftmost_x, leftmost_y, center_x, mask_width

    def process_wave(frame, mask, span, center, dbPerHLine, gridheight, wave_x, wave_y, initial_x, leftmost_y, initial_y, gridwidth, center_x):
        """Analyze and extract wave characteristics."""
        print(f"wave_x: {wave_x} px")
        print(f"wave_y: {wave_y} px")
        if len(wave_x) > 0 and len(wave_y) > 0:
            # Fit the points to a parabola
            params, _ = curve_fit(Utilities.parabola, wave_x, wave_y)

        # Extract the coefficients of the fitted parabola
        a, b, c = params

       

        if(leftmost_y < (initial_y+initial_y*0.1)):
             # Calculate center frequency using vertex formula (-b / 2a)
            center_freq_px = -b/ (2 * a)  # x coorinate of the vertex of the wave
            
            center_freq = Utilities.getCenterFreq(center_freq_px, span, center, gridwidth, center_x)
            mask_height = Utilities.get_mask_height(mask, initial_y) #pixel height of the mask
            amplitude = Utilities.getAmplitude(mask_height, dbPerHLine, gridheight)
            return center_freq, amplitude


    def get_mask_height(mask, initial_y):
        # Find the row indices of non-zero pixels in the mask
        non_zero_rows = np.where(mask)[0]

        if non_zero_rows.size > 0:
            # Calculate the minimum and maximum row indices to find the height
            min_row = np.min(non_zero_rows)
            max_row = initial_y
            # Calculate the height as the difference between max and min rows
            height = (
                max_row - min_row + 1
            )  # Adding 1 to account for inclusive row indices
            return height
        else:
            # If there are no non-zero pixels, return 0 as the height
            return 0

    def print_wave_characteristics(min_amplitude, max_amplitude, center_freq, frame_number, fps, gridheight):
        """Print extracted wave characteristics."""
        timestamp = frame_number / fps
        # center_freq, min_amplitude, max_amplitude, center_amplitude = result
        center_amplitude = (max_amplitude + min_amplitude)/2
        print(f"Timestamp: {timestamp} seconds")
        print(f"Gridheight: {gridheight} px")
        print(f"Center Frequency: {center_freq} GHZ")
        print(f"Minimum Amplitude: {min_amplitude} dB")
        print(f"Maximum Amplitude: {max_amplitude} dB")
        print(f"Center Amplitude: {center_amplitude} dB\n")
