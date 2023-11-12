import numpy as np
import json
import os

class Env_Vars:
    SPAN = 1
    center = 0
    dbPerHLine = 0
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
    VIDEO_PATH = 'Videos/CW Signal.mp4'
    VIDEO_FOLDER = 'Videos'

    QUIT_KEY = 'q'

def save_settings():
        settings = {}
        for attr in dir(Env_Vars):
            if not callable(getattr(Env_Vars, attr)) and not attr.startswith("__"):
                value = getattr(Env_Vars, attr)
                if isinstance(value, np.ndarray):
                    value = value.tolist()  # Convert numpy array to list
                settings[attr] = value
        with open('env_settings.json', 'w') as file:
            json.dump(settings, file)

def load_settings():
    if os.path.exists('env_settings.json'):
        with open('env_settings.json', 'r') as file:
            settings = json.load(file)
            for attr in settings:
                value = settings[attr]
                if isinstance(value, list):
                    value = np.array(value)  # Convert list to numpy array
                elif isinstance(value, str):
                    value = value.replace('\\', '/')
                elif isinstance(value, bool):
                    value = value
                
                setattr(Env_Vars, attr, value)
    else:
        save_settings()

load_settings()