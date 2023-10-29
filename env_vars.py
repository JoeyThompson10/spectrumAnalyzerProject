import numpy as np

class Env_Vars:
    # User-configurable constants for color filtering
    LOWER_GREEN = np.array([33, 45, 45])
    UPPER_GREEN = np.array([92, 260, 260])
    LOWER_WAVE_COLOR = np.array([78, 145, 115])
    UPPER_WAVE_COLOR = np.array([102, 260, 260])

    LOWER_GRID_COLOR = np.array([31, 41, 41])
    UPPER_GRID_COLOR = np.array([78, 145, 115])

    # Image filtering parameters
    KERNEL_SIZE = np.ones((5, 5), np.uint8)
    DILATE_ITERATIONS = 1
    ERODE_ITERATIONS = 1

    # Video configuration
    VIDEO_PATH = 'CW Signal.mp4'
    QUIT_KEY = 'q'
pass