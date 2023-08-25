#Group 8
# Import necessary libraries
import cv2  # OpenCV library for computer vision
import numpy as np  # NumPy library for numerical operations
from scipy.optimize import curve_fit  # SciPy function for curve fitting


# Define a function representing a parabola to fit wave data
def parabola(x, a, b, c):
    return a * x ** 2 + b * x + c  # Equation of a parabola


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


# Function to find the wave pixels in the frame
def find_wave(frame):
    # Convert the frame to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the color range for the wave (cyan-ish color)
    lower_bound = np.array([80, 150, 120])
    upper_bound = np.array([100, 255, 255])

    # Create a binary mask
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Find coordinates of the wave
    return np.where(mask)


# Function to process the wave and extract relevant information
def process_wave(wave_x, wave_y):
    # If both wave_x and wave_y are not empty
    if len(wave_x) > 0 and len(wave_y) > 0:
        # Fit the points to a parabola
        params, _ = curve_fit(parabola, wave_x, wave_y)

        # Extract the coefficients of the fitted parabola
        a, b, c = params

        # Calculate center frequency using vertex formula (-b / 2a)
        center_freq = -b / (2 * a)

        # Calculate amplitudes
        min_amplitude = np.min(wave_y)
        max_amplitude = np.max(wave_y)
        center_amplitude = (max_amplitude + min_amplitude) / 2

        return center_freq, min_amplitude, max_amplitude, center_amplitude

    return None


# Main function where video processing happens
def main():
    # File path to the video
    video_path = 'CW Signal.mp4'
    cap = cv2.VideoCapture(video_path)

    # Check if video was opened successfully
    if not cap.isOpened():
        print("Error: Could not open the video file.")
        return

    # Get video properties
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    print(f"Playing video with dimensions: {frame_width}x{frame_height} and {fps} FPS.")

    peak_counter = 0  # Initialize peak counter to 0

    # Loop through video frames
    while cap.isOpened():
        # Read a frame from the video
        ret, frame = cap.read()

        # Get current frame number and calculate timestamp
        frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        timestamp = frame_number / fps  # Timestamp in seconds

        # Break loop if video ends
        if not ret:
            print("Reached the end of the video or an error occurred.")
            break

        # Find oscilloscope screen in the frame
        screen_info = find_screen(frame)

        # If screen is found
        if screen_info:
            x, y, w, h = screen_info  # Extract position and size
            # Crop the frame to only contain the oscilloscope screen
            cropped_frame = frame[y:y + h, x:x + w]

            # Find wave in the cropped frame
            wave_x, wave_y = find_wave(cropped_frame)

            # Process the wave to get frequency and amplitude
            result = process_wave(wave_x, wave_y)

            if result:  # If wave data is successfully processed
                peak_counter += 1  # Increment peak counter
                if peak_counter % (fps * 3) == 0:  # Log data every 3 seconds
                    center_freq, min_amplitude, max_amplitude, center_amplitude = result
                    print(f"Timestamp: {timestamp} seconds")
                    print(f"Center Frequency: {center_freq}")
                    print(f"Minimum Amplitude: {min_amplitude}")
                    print(f"Maximum Amplitude: {max_amplitude}")
                    print(f"Center Amplitude: {center_amplitude}\n")

            # Display the cropped frame with the wave
            cv2.imshow('Video', cropped_frame)
        else:
            # Display the original frame if screen is not found
            cv2.imshow('Video', frame)

        # Break loop if 'q' is pressed
        if cv2.waitKey(1000 // fps) & 0xFF == ord('q'):
            break

    # Release video and destroy all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

    print("Video playback is done.")


# Run the main function when the script is executed
if __name__ == "__main__":
    main()
