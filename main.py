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
import os
import cv2
import csv
import utilities
import env_vars
import numpy as np
from datetime import datetime
from time import sleep
import multiprocessing
import SpectrumAnalyzerGUI
import webbrowser

# ===================================
#  Main execution functions
# ===================================

#Takes in the new parameters from multiprocessing span, center, dbPerHLine
def video_to_csv(cap, fileName, span, center, dbPerHLine): 
    """Main execution function for analyzing the video."""
    
    try:
        # Open the video file for processing
        # Check if the video file opened successfully
        if not cap.isOpened():
            raise Exception("Error: Could not open the video file.")

        # Get first frame of the video
        ret0, first_frame = cap.read()
        if not ret0:
            raise Exception("Unable to read the first frame.")

        # Get video properties like width, height, and FPS
        frame_width, frame_height = int(cap.get(3)), int(cap.get(4))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        print(f"Playing video with dimensions: {frame_width}x{frame_height} and {fps} FPS.")
        rect_cnt = 0
        gridheight = 0
        gridwidth = 0
        center_x = 0  # x value of the center line of the grid which correlates with CENTER value from the spectrum analyzer
        min_amplitude = 1000
        max_amplitude = 0
        center_amplitude = 0
        # initialize y coordinate of the wave to check for when wave data is being cleared
        initial_y = 0

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
                # leftmost_x is used to check position in the video where the wave data begins
                # leftmost_y is to check the y position of the wave data to determine when wave data is being cleared and should be ignored
                mask, (wave_y, wave_x), leftmost_x, leftmost_y, center_x, mask_width = utilities.Utilities.find_wave(frame)

                while rect_cnt <= 10:
                    contours, (grid_y, grid_x) = utilities.Utilities.findGrid(frame)
                    for contour in contours:
                        perimeter = cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
                        if len(approx) == 4:
                            x, y, w, h = cv2.boundingRect(approx)
                            if 50 < h < 100:
                                if rect_cnt <= 10:
                                    gridwidth += w
                                    gridheight += h
                                    rect_cnt += 1
                    initial_y = leftmost_y  # initialize the y value of the wave based on the start of the video
                    initial_x = leftmost_x  # initialize the x value of the wave based on the start of the video
                print(f"initial x: {initial_x}")
                # center_x = initial_x + (gridwidth/2) #establish center x position of the center of the spectrum analyzer
                gridheight = grid_y[len(grid_y) - 1] - grid_y[0] - 252  # 252px is the distance between the actual grid and the top and bottom of the
                print(f"gridwidth: {gridwidth}")
                gridwidth = mask_width  # Since the width of the wave mask is the same as the width of the grid, we can use this as the basis for the grid width to determine the pixel to HZ ratio

                # Get detailed information from the processed wave

                result = utilities.Utilities.process_wave(frame, mask, span, center, dbPerHLine, gridheight, wave_x,
                                                           wave_y, initial_x, leftmost_y, initial_y, gridwidth, center_x)

                if result:
                    center_freq, amplitude = result
                    if amplitude > max_amplitude:
                        max_amplitude = amplitude
                    if amplitude < min_amplitude:
                        min_amplitude = amplitude

                # If a valid result is obtained, print and store it
                if result:
                    center_amplitude = (min_amplitude + max_amplitude) / 2
                    data = center_freq, min_amplitude, max_amplitude, center_amplitude
                    utilities.Utilities.print_wave_characteristics(min_amplitude, max_amplitude, center_freq,
                                                                   cap.get(cv2.CAP_PROP_POS_FRAMES), fps, gridheight)
                    detected_signals.append(data)

                if mask is not None:
                    # Show the cropped frame with the wave to the user
                    cv2.imshow('Video', mask)

                else:
                    # If screen is not detected, simply show the entire frame
                    cv2.imshow('Video', frame)

            # Allow for user intervention to quit video playback
            if cv2.waitKey(1000 // fps) & 0xFF == ord(env_vars.Env_Vars.QUIT_KEY):
                break

    except Exception as e:
        print(f"Error: {e}")
        sleep(5)

    finally:
        # Store detected signals' information to a CSV file after removing mp4 extension from the video file name
        csv_file = fileName.replace('.mp4', '.csv')

        # Check if the Completed folder exists, if not, create it
        completed_directory = 'Completed'
        if not os.path.exists(completed_directory):
            os.makedirs(completed_directory)
        csvLocation = os.path.join(completed_directory, csv_file)

        csvLocation = os.path.join('Completed', csv_file)
        try:
            with open(csvLocation, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Define the CSV columns
                writer.writerow(['Timestamp (s)', 'Center Frequency', 'Minimum Amplitude', 'Maximum Amplitude',
                                 'Center Amplitude'])
                for signal in detected_signals:
                    frame_number = cap.get(cv2.CAP_PROP_POS_FRAMES) - len(detected_signals) + detected_signals.index(
                        signal)
                    timestamp = frame_number / fps

                    # center_freq, min_amplitude, max_amplitude, center_amplitude = signal
                    max_amplitude = signal

                    # writer.writerow([timestamp, center_freq, min_amplitude, max_amplitude, center_amplitude])
                    writer.writerow([timestamp, max_amplitude[0], max_amplitude[1], max_amplitude[2], max_amplitude[3]])

            print("CSV file created successfully.")
        except Exception as e:
            print(f"Error writing to CSV file: {e}")

        # Properly release the video and close any GUI windows
        cap.release()
        cv2.destroyAllWindows()
        print("Video playback is done.")

# Takes the video and converts to CSV file with the new parameters from multiprocessing
def video_to_csv_worker(video_file, span, center, dbPerHLine):
    cap = cv2.VideoCapture(video_file)
    fileName = os.path.basename(video_file)
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    fileName = current_time + "_CSV_" + fileName
    video_to_csv(cap, fileName, span, center, dbPerHLine)

# This function is what each worker executes to process the video and uses the video_to_CSV to make the CSV files
def process_video_file_worker(video_file, span, center, dbPerHLine):
    full_video_path = os.path.join(env_vars.Env_Vars.VIDEO_FOLDER, video_file)
    print("Processing video: " + full_video_path)
    video_to_csv_worker(full_video_path, span, center, dbPerHLine)

def main():
    try:
        # Specify the folder containing the videos
        video_folder_path = env_vars.Env_Vars.VIDEO_FOLDER

        # Check if the folder exists
        if not os.path.exists(video_folder_path):
            raise Exception(f"The specified folder does not exist: {video_folder_path}")

        # List all files in the video folder
        video_files = [f for f in os.listdir(video_folder_path) if f.endswith('.mp4')]

        # Check if there are any mp4 files in the folder
        if not video_files:
            raise Exception(f"No videos found in {video_folder_path}.")

        # # Process each video file
        # Set multiprocessing parameters
        num_processes = min(multiprocessing.cpu_count(), len(video_files))  # Determines the number of processes that can be used based on the CPU core count and the number of videos

        span = env_vars.Env_Vars.SPAN
        center = env_vars.Env_Vars.center
        dbPerHLine = env_vars.Env_Vars.dbPerHLine

        # Use multiprocessing.Pool to process videos in parallel, can iterate through the list of videos and apply the video_file_worker function to each element
        with multiprocessing.Pool(processes=num_processes) as pool:  # Creates a pool of worker processes and the parameter process is based on the number of worker processes
            pool.starmap(process_video_file_worker,
                         [(video, span, center, dbPerHLine) for video in video_files])  # starmap is used to apply video_file_worker to each element and each element is a tuple containing the video file name and the new parameters

        # After all video processing is done, open the Completed folder
        completed_folder_path = os.path.abspath("Completed")
        webbrowser.open(completed_folder_path)

    except Exception as e:
        print(f"Error: {e}")

# ===================================
# 5. Script entry point
# ===================================
if __name__ == "__main__":
    app = SpectrumAnalyzerGUI.SpectrumAnalyzerGUI() #Creates the GUI
    app.mainloop()  # The main analysis starts when the user clicks "Start" in the GUI