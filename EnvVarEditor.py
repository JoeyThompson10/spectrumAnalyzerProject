import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, colorchooser
import env_vars
import numpy as np
import main
import os

class EnvVarEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Spectrum Analyzer - Team 5")
        self.create_main_page()
        self.minsize(400, 600)  # Set a minimum size for the window

    def create_main_page(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Button(self.main_frame, text="Start Analysis", command=self.start_analysis).pack(pady=10, padx=10, fill=tk.X)
        ttk.Button(self.main_frame, text="Settings", command=self.create_settings_page).pack(pady=10, padx=10, fill=tk.X)


        # Get the count of video files in the specified folder
        video_count = self.get_video_count()

        # Display the count of videos
        video_info_label = ttk.Label(self.main_frame, text=f"Number of Videos in Folder: {video_count}")
        video_info_label.pack(pady=5, padx=10)

    def get_video_count(self):
        video_folder_path = env_vars.Env_Vars.VIDEO_FOLDER
        if os.path.exists(video_folder_path):
            video_files = [f for f in os.listdir(video_folder_path) if f.endswith('.mp4')]
            return len(video_files)
        else:
            return 0

    def create_settings_page(self):
        self.clear_frame(self.main_frame)

        settings_frame = ttk.Frame(self)
        settings_frame.pack(expand=True, fill=tk.BOTH)

        self.create_edit_buttons(settings_frame)
        self.create_color_buttons(settings_frame)

        ttk.Button(settings_frame, text="Back to Main", command=lambda: self.switch_frame(settings_frame, self.create_main_page)).pack(pady=10, padx=10, fill=tk.X)

    def create_edit_buttons(self, parent):
        button_labels = ["Edit SPAN", "Edit Center", "Edit dbPerHLine", "Edit Video Path", "Edit Video Folder", "Edit Quit Key", "Edit Dilation Iterations", "Edit Erosion Iterations"]
        command_funcs = [self.edit_span, self.edit_center, self.edit_dbPerHLine, self.edit_video_path, self.edit_video_folder, self.edit_quit_key, self.edit_dilate_iterations, self.edit_erode_iterations]

        for label, command in zip(button_labels, command_funcs):
            ttk.Button(parent, text=label, command=command).pack(pady=5, padx=10, fill=tk.X)

    def create_color_buttons(self, parent):
        color_vars = ['LOWER_GREEN', 'UPPER_GREEN', 'LOWER_WAVE_COLOR', 'UPPER_WAVE_COLOR', 'LOWER_GRID_COLOR', 'UPPER_GRID_COLOR']
        for var in color_vars:
            ttk.Button(parent, text=f"Edit {var}", command=lambda var_name=var: self.edit_color(var_name)).pack(pady=5, padx=10, fill=tk.X)

    def switch_frame(self, current_frame, new_frame_func):
        self.clear_frame(current_frame)
        new_frame_func()

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()
        frame.pack_forget()

    def edit_video_path(self):
        file_path = filedialog.askopenfilename(title="Select Video File", filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
        if file_path:
            setattr(env_vars.Env_Vars, 'VIDEO_PATH', file_path)
        else:
            self.edit_string_var('VIDEO_PATH', "Enter new video path:")

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
    app = EnvVarEditor()
    app.mainloop()