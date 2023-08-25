import cv2

# Specify the path for your video file
video_path = 'CW Signal.mp4'

# Create a VideoCapture object
cap = cv2.VideoCapture(video_path)

# Check if the video file was opened successfully
if not cap.isOpened():
    print("Error: Could not open the video file.")
else:
    # Get the video's frame width, frame height, and frames per second
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    print(f"Playing video with dimensions: {frame_width}x{frame_height} and {fps} FPS.")

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # If the frame was read correctly, display it
        if ret:
            cv2.imshow('Video', frame)

            # Wait for the duration of 1 frame, and break the loop if the 'q' key is pressed
            if cv2.waitKey(1000 // fps) & 0xFF == ord('q'):
                break
        else:
            print("Reached the end of the video or an error occurred.")
            break

    # Release the VideoCapture object
    cap.release()

    # Destroy all OpenCV windows
    cv2.destroyAllWindows()

print("Video playback is done.")
