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
from datetime import datetime
from time import sleep

# ===================================
#  Main execution functions
# ===================================

def video_to_csv(cap, fileName):
    span = env_vars.Env_Vars.SPAN
    """Main execution function for analyzing the video."""
    # Open the video file for processing
    # Check if the video file opened successfully
    if not cap.isOpened():
        print("Error: Could not open the video file.")
        sleep(5)
        return

    # Get first frame of the video
    ret0, first_frame = cap.read()
    if not ret0:
        print("Unable to read first frame")
        sleep(5)
        exit()

    utilities.Utilities.findGrid(first_frame)

    # Get video properties like width, height, and FPS
    frame_width, frame_height = int(cap.get(3)), int(cap.get(4))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"Playing video with dimensions: {frame_width}x{frame_height} and {fps} FPS.")
    rect_cnt = 0
    gridheight = 0

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
            while(rect_cnt <= 10):
                contours = utilities.Utilities.findGrid(frame)
                for contour in contours:
                    perimeter = cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, 0.02*perimeter, True)
                    if len(approx)==4:
                        x, y, w, h = cv2.boundingRect(approx)
                        if(h > 50 & h < 100):
                            if(rect_cnt <= 10):
                                gridheight+=h
                                rect_cnt +=1
                
                           

            # Get detailed information from the processed wave
            result = utilities.Utilities.process_wave(frame, mask, span, gridheight)

          
            # If a valid result is obtained, print and store it
            if result:
                utilities.Utilities.print_wave_characteristics(result, cap.get(cv2.CAP_PROP_POS_FRAMES), fps, gridheight)
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
    csv_file = fileName + ".csv"


    # Check if the Completed folder exists, if not, create it
    completed_directory = 'Completed'
    if not os.path.exists(completed_directory):
        os.makedirs(completed_directory)
    csvLocation = os.path.join(completed_directory, csv_file)


    csvLocation = os.path.join('Completed', csv_file) 
    with open(csvLocation, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Define the CSV columns
        writer.writerow(['Timestamp (s)', 'Center Frequency', 'Minimum Amplitude', 'Maximum Amplitude', 'Center Amplitude'])
        for signal in detected_signals:
            frame_number = cap.get(cv2.CAP_PROP_POS_FRAMES) - len(detected_signals) + detected_signals.index(signal)
            timestamp = frame_number / fps

            # center_freq, min_amplitude, max_amplitude, center_amplitude = signal
            max_amplitude = signal

            # writer.writerow([timestamp, center_freq, min_amplitude, max_amplitude, center_amplitude])
            writer.writerow([timestamp, max_amplitude])
            

    # Properly release the video and close any GUI windows
    cap.release()
    cv2.destroyAllWindows()
    print("Video playback is done.")

def process_video_file(video_file):
    cap = cv2.VideoCapture(video_file)
    fileName = os.path.basename(video_file)
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    fileName = current_time + "_CSV_" + fileName
    video_to_csv(cap, fileName)

def main():
    # Specify the folder containing the videos
    video_folder_path = env_vars.Env_Vars.VIDEO_FOLDER
    
    # Check if the folder exists
    if not os.path.exists(video_folder_path):
        print("The specified folder does not exist: " + video_folder_path)
        sleep(5)
        return
    
    # List all files in the video folder
    video_files = [f for f in os.listdir(video_folder_path) if f.endswith('.mp4')]
    
    # Check if there are any mp4 files in the folder
    if not video_files:
        print("No videos found in " + video_folder_path + ".")
        sleep(5)
        return
    
    # Process each video file
    for video_file in video_files:
        full_video_path = os.path.join(video_folder_path, video_file)
        print("Processing video: " + full_video_path)
        process_video_file(full_video_path)

# ===================================
# 5. Script entry point
# ===================================
if __name__ == "__main__":
    main()