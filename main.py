# ==============================================================================
# SWE 4724- Software Engineering Project
# Instructor: Dr. Yan Huang
# Team: 5
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
import csv
import utilities
import env_vars

# ===================================
#  Main execution functions
# ===================================

def print_wave_characteristics(result, frame_number, fps):
    """Print extracted wave characteristics."""
    timestamp = frame_number / fps
    # center_freq, min_amplitude, max_amplitude, center_amplitude = result
    max_amplitude = result
    print(f"Timestamp: {timestamp} seconds")
    # print(f"Center Frequency: {center_freq}")
    # print(f"Minimum Amplitude: {min_amplitude}")
    print(f"Maximum Amplitude: {max_amplitude}")
    # print(f"Center Amplitude: {center_amplitude}\n")

def main():
    """Main execution function for analyzing the video."""
    # Open the video file for processing
    cap = cv2.VideoCapture(env_vars.Env_Vars.VIDEO_PATH)
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
            mask, (wave_x, wave_y) = utilities.Utilities.find_wave(frame)
            
            # Get detailed information from the processed wave
            result = utilities.Utilities.process_wave(frame, mask, wave_x, wave_y)

            
            # If a valid result is obtained, print and store it
            if result:
                print_wave_characteristics(result, cap.get(cv2.CAP_PROP_POS_FRAMES), fps)
                detected_signals.append(result)
            
            if mask is not None:
                # Show the cropped frame with the wave to the user
                cv2.imshow('Video', mask)
            else:
                # If screen is not detected, simply show the entire frame
                cv2.imshow('Video', frame)

        # Allow for user intervention to quit video playback
        if cv2.waitKey(1000 // fps) & 0xFF == ord(env_vars.Env_Vars.QUIT_KEY):
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