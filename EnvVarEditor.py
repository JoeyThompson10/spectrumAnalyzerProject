import tkinter as tk # For creating the GUI
from tkinter import simpledialog, colorchooser, ttk # For creating the GUI
import env_vars # For editing environment variables
import numpy as np # For color filtering
import main # For running the main function

class EnvVarEditor(tk.Tk): # GUI for editing environment variables
    def __init__(self): # Constructor for the GUI
        super().__init__() # Call the constructor of the parent class
        self.title("Spectrum Analyzer - Team 5") # Set the title of the window
        self.geometry("400x600")  # Set a default size for the window
        self.style = ttk.Style(self) # Create a style object
        self.style.theme_use('clam') # Set the theme to 'clam' (a light theme)
        self.create_widgets() # Create the widgets for the GUI

    def create_widgets(self): # Create the widgets for the GUI
        # Frame for the Start Analysis button
        top_frame = ttk.Frame(self) 
        top_frame.pack(padx=10, pady=10, fill='x')
        ttk.Button(top_frame, text="Start Analysis", command=self.start_analysis).pack(fill='x', pady=5)

        # Frame for numeric and string variable editing
        edit_frame = ttk.Frame(self)
        edit_frame.pack(padx=10, pady=10, fill='x', expand=True)
        self.create_edit_buttons(edit_frame)

        # Frame for color variable editing
        color_frame = ttk.Frame(self)
        color_frame.pack(padx=10, pady=10, fill='x', expand=True)
        self.create_color_buttons(color_frame)

    def create_edit_buttons(self, parent):
        # Buttons for editing numeric and string variables
        ttk.Button(parent, text="Edit SPAN", command=self.edit_span).pack(fill='x', pady=5)
        ttk.Button(parent, text="Edit Center", command=self.edit_center).pack(fill='x', pady=5)
        ttk.Button(parent, text="Edit dbPerHLine", command=self.edit_dbPerHLine).pack(fill='x', pady=5)
        ttk.Button(parent, text="Edit Video Path", command=self.edit_video_path).pack(fill='x', pady=5)
        ttk.Button(parent, text="Edit Video Folder", command=self.edit_video_folder).pack(fill='x', pady=5)
        ttk.Button(parent, text="Edit Quit Key", command=self.edit_quit_key).pack(fill='x', pady=5)
        ttk.Button(parent, text="Edit Dilation Iterations", command=self.edit_dilate_iterations).pack(fill='x', pady=5)
        ttk.Button(parent, text="Edit Erosion Iterations", command=self.edit_erode_iterations).pack(fill='x', pady=5)

    def create_color_buttons(self, parent):
        color_vars = ['LOWER_GREEN', 'UPPER_GREEN', 'LOWER_WAVE_COLOR', 'UPPER_WAVE_COLOR', 'LOWER_GRID_COLOR', 'UPPER_GRID_COLOR']
        for var in color_vars:
            ttk.Button(parent, text=f"Edit {var}", command=lambda var_name=var: self.edit_color(var_name)).pack(fill='x', pady=5)

    def start_analysis(self):
        env_vars.save_settings() # Save the environment variables
        self.destroy() # Close the GUI
        main.main() # Run the main function

    # Methods for editing numeric and string variables
    def edit_span(self):
        self.edit_numeric_var('SPAN', "Enter new SPAN value:")

    def edit_center(self):
        self.edit_numeric_var('center', "Enter new CENTER value:")
    
    def edit_dbPerHLine(self):
        self.edit_numeric_var('dbPerHLine', "Enter new dbPerHLine value:")

    def edit_video_path(self):
        self.edit_string_var('VIDEO_PATH', "Enter new video path:")

    def edit_video_folder(self):
        self.edit_string_var('VIDEO_FOLDER', "Enter new video folder:")

    def edit_quit_key(self):
        self.edit_string_var('QUIT_KEY', "Enter new quit key:")

    def edit_dilate_iterations(self):
        self.edit_numeric_var('DILATE_ITERATIONS', "Enter new dilation iterations:")

    def edit_erode_iterations(self):
        self.edit_numeric_var('ERODE_ITERATIONS', "Enter new erosion iterations:")

    # Helper methods
    def edit_numeric_var(self, var_name, prompt):
        new_value = simpledialog.askinteger(var_name, prompt, initialvalue=getattr(env_vars.Env_Vars, var_name))
        if new_value is not None:
            setattr(env_vars.Env_Vars, var_name, new_value)

    def edit_string_var(self, var_name, prompt):
        new_value = simpledialog.askstring(var_name, prompt, initialvalue=getattr(env_vars.Env_Vars, var_name))
        if new_value:
            setattr(env_vars.Env_Vars, var_name, new_value)

    def edit_color(self, color_var_name):
        initial_color = getattr(env_vars.Env_Vars, color_var_name)
        color_code = colorchooser.askcolor(title=f"Choose color for {color_var_name}", initialcolor=(initial_color[0], initial_color[1], initial_color[2]))
        if color_code[1]:
            new_color = np.array([int(val) for val in color_code[0]])
            setattr(env_vars.Env_Vars, color_var_name, new_color)

if __name__ == "__main__":
    app = EnvVarEditor() # Create the GUI
    app.mainloop() # Run the GUI