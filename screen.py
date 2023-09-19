import cv2  # OpenCV library for computer vision
import numpy as np  # NumPy library for numerical operations
from scipy.optimize import curve_fit  # SciPy function for curve fitting

class Screen:
        # Function to find the oscilloscope screen based on its green color
    def find_screen(frame):
        # Convert the color frame from BGR to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define the range of green color in HSV
        lower_green = np.array([35, 50, 50])
        upper_green = np.array([90, 255, 255])

        # Create a binary mask where green color is "1" and others are "0"
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Return None if no contour is found
        if not contours:
            return None

        # Find the largest contour by area
        largest_contour = max(contours, key=cv2.contourArea)

        # Get the bounding rectangle of the largest contour
        return cv2.boundingRect(largest_contour)
    pass