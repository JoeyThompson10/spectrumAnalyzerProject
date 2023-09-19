# Import necessary libraries
import cv2  # OpenCV library for computer vision
import numpy as np  # NumPy library for numerical operations
from scipy.optimize import curve_fit  # SciPy function for curve fitting
import screen
import wave_1



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
        screen_info = screen.Screen.find_screen(frame)

        # If screen is found
        if screen_info:
            x, y, w, h = screen_info  # Extract position and size
            # Crop the frame to only contain the oscilloscope screen
            cropped_frame = frame[y:y + h, x:x + w]

            # Find wave in the cropped frame
            wave_x, wave_y = wave_1.Wave.find_wave(cropped_frame)

            # Process the wave to get frequency and amplitude
            result =  wave_1.Wave.process_wave(wave_x, wave_y)

            if result:  # If wave data is successfully processed
                peak_counter += 1  # Increment peak counter
                if peak_counter % (fps * 3) == 0:  # Log data every 3 seconds
                    center_freq, min_amplitude, max_amplitude, center_amplitude = result
                    print(f"Timestamp: {timestamp} seconds")
                    print(f"Center Frequency: {center_freq} MHZ")
                    print(f"Minimum Amplitude: {min_amplitude} MHZ")
                    print(f"Maximum Amplitude: {max_amplitude} MHZ")
                    print(f"Center Amplitude: {center_amplitude} MHZ\n")

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
