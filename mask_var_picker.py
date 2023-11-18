import cv2
import numpy as np
import env_vars
import os


#does nothing but is required by trackbar
def required_func(x):
    pass

# Start with a sample image or video frame
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
    

except Exception as e:
    print(f"Error: {e}")


video_path = os.path.join(video_folder_path, video_files[0])
video_capture = cv2.VideoCapture(video_path)
print(video_capture.isOpened())
ret, image = video_capture.read()

# Convert to HSV
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Create trackbars for lower and upper mask limits
cv2.namedWindow('Set Upper and Lower Bounds', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
cv2.createTrackbar('Lower H', 'Set Upper and Lower Bounds', 0, 180, required_func)
cv2.createTrackbar('Lower S', 'Set Upper and Lower Bounds', 0, 255, required_func)
cv2.createTrackbar('Lower V', 'Set Upper and Lower Bounds', 0, 255, required_func)
cv2.createTrackbar('Upper H', 'Set Upper and Lower Bounds', 180, 180, required_func)
cv2.createTrackbar('Upper S', 'Set Upper and Lower Bounds', 255, 255, required_func)
cv2.createTrackbar('Upper V', 'Set Upper and Lower Bounds', 255, 255, required_func)
cv2.setWindowProperty('Set Upper and Lower Bounds', cv2.WND_PROP_TOPMOST, 1)

while True:
    # Get positions of the trackbars
    l_h = cv2.getTrackbarPos('Lower H', 'Set Upper and Lower Bounds')
    l_s = cv2.getTrackbarPos('Lower S', 'Set Upper and Lower Bounds')
    l_v = cv2.getTrackbarPos('Lower V', 'Set Upper and Lower Bounds')
    u_h = cv2.getTrackbarPos('Upper H', 'Set Upper and Lower Bounds')
    u_s = cv2.getTrackbarPos('Upper S', 'Set Upper and Lower Bounds')
    u_v = cv2.getTrackbarPos('Upper V', 'Set Upper and Lower Bounds')

    # Set the lower and upper from trackbars
    lower_HSV_bound = np.array([l_h, l_s, l_v])
    upper_HSV_bound = np.array([u_h, u_s, u_v])

    # Update mask
    mask = cv2.inRange(hsv, lower_HSV_bound, upper_HSV_bound)

    cv2.namedWindow('Mask', cv2.WINDOW_KEEPRATIO)
    cv2.imshow('Mask', mask)
    cv2.resizeWindow('Mask', 1200, 720)

    key = cv2.waitKey(1)
    if key == 13 or key == 10:  # Esc key to stop
        #set lower_HSV_bound, upper_HSV_bound
        break

# Print the final chosen HSV range
print(f"Chosen Lower HSV: [{l_h}, {l_s}, {l_v}]")
print(f"Chosen Upper HSV: [{u_h}, {u_s}, {u_v}]")

cv2.destroyAllWindows()