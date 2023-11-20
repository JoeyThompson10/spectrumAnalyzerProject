import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, filedialog, simpledialog, colorchooser
import env_vars
import numpy as np
import main
import os
import threading
import cv2

# Class for creating tooltips
class Tooltip:
    # Initialize the tooltip
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        widget.bind("<Enter>", self.enter)
        widget.bind("<Leave>", self.leave)

    # Create the tooltip window
    def enter(self, event=None):
        x = y = 0
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#ffffff",
            relief="solid",
            borderwidth=1,
            wraplength=200,
        )
        label.pack(ipadx=1)

    # Destroy the tooltip window
    def leave(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# Class for the main GUI window
class SpectrumAnalyzerGUI(tk.Tk):
    # Initialize the window
    def __init__(self):
        super().__init__()
        self.title("Spectrum Analyzer - Team 5")
        
        # Main frame that will hold everything
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        # Create a dedicated frame for the video display
        self.video_frame = ttk.Frame(self.main_frame)
        self.video_frame.pack(side="left", fill=tk.Y, expand=False)
        self.create_video_display()

        # Frame for changing screens (settings, main page, etc.)
        self.screen_frame = ttk.Frame(self.main_frame)
        self.screen_frame.pack(side="right", fill=tk.BOTH, expand=True)

        self.create_main_page()  # Create the main page in the screen frame

    def create_video_display(self):
        # This function should only be called once to set up the video display initially
        self.image_label = ttk.Label(self.video_frame)
        self.display_video_frame()  # Function to update the video frame
        self.image_label.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    # Create the main page
    def create_main_page(self):
        self.clear_frame(self.screen_frame)

        # Paned window for frame display by gui
        paned_window = ttk.PanedWindow(self.screen_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)

        self.right_frame = ttk.Frame(paned_window)
        paned_window.add(self.right_frame, weight=1)

        # Main label with the application title
        ttk.Label(
            left_frame, text="Spectrum Analyzer - Team 5", font=("Helvetica", 16)
        ).pack(pady=10, padx=10, fill=tk.X)

        # Welcome label
        ttk.Label(
            left_frame,
            text="Welcome to the Spectrum Analyzer application.\nPlease select an option below to get started.",
        ).pack(pady=10, padx=10, fill=tk.X)

        # Button to start analysis
        ttk.Button(
            left_frame, text="Start Analysis", command=self.start_analysis
        ).pack(pady=10, padx=10, fill=tk.X)

        # Button to open settings
        ttk.Button(
            left_frame, text="Settings", command=self.create_settings_page
        ).pack(pady=10, padx=10, fill=tk.X)

        # Help/Guide button
        ttk.Button(left_frame, text="Help/Guide", command=self.show_help).pack(
            pady=10, padx=10, fill=tk.X
        )

        # Label showing the number of videos
        video_count = self.get_video_count()
        video_info_label = ttk.Label(
            left_frame, text=f"Number of Videos in Folder: {video_count}"
        )
        video_info_label.pack(pady=5, padx=10)

        # Create a bottom frame for the Exit button
        bottom_frame = ttk.Frame(left_frame)
        bottom_frame.pack(side="bottom", fill=tk.X, expand=False)

        # Exit button at the bottom
        ttk.Button(bottom_frame, text="Exit", command=self.destroy).pack(
            side="bottom", pady=30, padx=10, fill=tk.X
        )

        self.display_video_frame()
        self.update()

    def display_video_frame(self):
        video_folder_path = env_vars.Env_Vars.VIDEO_FOLDER
        video_files = [f for f in os.listdir(video_folder_path) if f.endswith('.mp4')]

        if video_files:
            video_path = os.path.join(video_folder_path, video_files[0])
            video_capture = cv2.VideoCapture(video_path)

            if video_capture.isOpened():
                ret, frame = video_capture.read()
                if ret:
                    # Convert the color from BGR to RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Convert to PIL format
                    frame_image = Image.fromarray(frame)
                    # Convert to ImageTk format
                    baseheight = 400
                    hpercent = (baseheight / float(frame_image.size[1]))
                    wsize = int((float(frame_image.size[0]) * float(hpercent)))
                    frame_image = frame_image.resize((wsize, baseheight), Image.Resampling.LANCZOS)
                    frame_image = ImageTk.PhotoImage(frame_image)

                    # Assuming you have a label to display the image
                    self.image_label.configure(image=frame_image)
                    self.image_label.image = frame_image  # Keep a reference!
                    self.image_label.pack(pady=10, padx=10)
                else:
                    print("Failed to read a frame from the video")
            else:
                print("Failed to open video file")
        else:
            print("No video files found")
    
    # Get the number of videos in the video folder
    def get_video_count(self):
        video_folder_path = env_vars.Env_Vars.VIDEO_FOLDER
        if os.path.exists(video_folder_path):
            video_files = [
                f for f in os.listdir(video_folder_path) if f.endswith(".mp4")
            ]
            return len(video_files)
        else:
            return 0
        
    # Create the settings page
    def create_settings_page(self):
        self.clear_frame(self.screen_frame)

        settings_frame = ttk.Frame(self.screen_frame)  # Use self.screen_frame here
        settings_frame.pack(expand=True, fill=tk.BOTH)

        self.create_edit_buttons(settings_frame)
        self.create_color_buttons(settings_frame)

        ttk.Button(
            settings_frame,
            text="Back",
            command=lambda: self.switch_frame(settings_frame, self.create_main_page),
        ).pack(pady=10, padx=10, fill=tk.X)

    # Create buttons for editing numeric and string variables
    def create_edit_buttons(self, parent):
        button_labels = [
            "Edit SPAN",
            "Edit Center",
            "Edit dbPerHLine",
            "Edit Video Folder",
            "Edit Quit Key",
            "Edit Dilation Iterations",
            "Edit Erosion Iterations",
        ]
        command_funcs = [
            self.edit_span,
            self.edit_center,
            self.edit_dbPerHLine,
            self.edit_video_folder,
            self.edit_quit_key,
            self.edit_dilate_iterations,
            self.edit_erode_iterations,
        ]
        tooltips = [
            "Set the SPAN value, defining the frequency range",
            "Set the Center frequency around which to analyze",
            "Define decibels per horizontal line in the analysis",
            "Set the folder path containing video files",
            "Define the key to press for quitting the analysis",
            "Set the number of dilation iterations for video processing",
            "Set the number of erosion iterations for video processing",
        ]

        for label, command, tooltip_text in zip(button_labels, command_funcs, tooltips):
            btn = ttk.Button(parent, text=label, command=command)
            btn.pack(pady=5, padx=10, fill=tk.X)
            Tooltip(btn, tooltip_text)

    # Create buttons for editing color variables
    def create_color_buttons(self, parent):
        color_vars = [
            "LOWER_GREEN",
            "UPPER_GREEN",
            "LOWER_WAVE_COLOR",
            "UPPER_WAVE_COLOR",
            "LOWER_GRID_COLOR",
            "UPPER_GRID_COLOR",
        ]
        tooltips = [
            "Set the lower threshold color for green detection",
            "Set the upper threshold color for green detection",
            "Set the lower threshold color for wave detection",
            "Set the upper threshold color for wave detection",
            "Set the lower threshold color for grid detection",
            "Set the upper threshold color for grid detection",
        ]

        for var, tooltip_text in zip(color_vars, tooltips):
            btn = ttk.Button(
                parent,
                text=f"Edit {var}",
                command=lambda var_name=var: self.edit_color(var_name),
            )
            btn.pack(pady=5, padx=10, fill=tk.X)
            Tooltip(btn, tooltip_text)

    # Switch between frames
    def switch_frame(self, current_frame, new_frame_func):
        self.clear_frame(current_frame)
        new_frame_func()

    # Clear a frame
    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    # Show the help/guide window
    def show_help(self):
        help_window = tk.Toplevel(self)
        help_window.title("Help/Guide")
        help_window.geometry("400x360")

        # Create a Text widget with a scrollbar
        help_text_widget = tk.Text(help_window, wrap="word", height=15, width=50)
        scrollbar = tk.Scrollbar(help_window, command=help_text_widget.yview)
        help_text_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        help_text_widget.pack(side="left", fill="both", expand=True)

        # Inserting text
        help_text = (
            "Welcome to the Spectrum Analyzer Help Guide:\n\n"
            "Start Analysis: Begin processing your video files for spectrum analysis.\n\n"
            "Settings: Customize application settings including video paths, color thresholds, and keybindings.\n\n"
            "Exiting: Click 'Exit' to close the application.\n\n"
            "For more detailed instructions on each feature, please refer to the user manual or contact support.\n\n"
            "Additional Resources:\n"
        )
        help_text_widget.insert("end", help_text)

        # Inserting clickable links
        def open_link(url):
            import webbrowser

            webbrowser.open_new(url)

        help_text_widget.insert("end", "Project Website: ")
        help_text_widget.insert(
            "end",
            "https://main.d21hsol1os28ah.amplifyapp.com/\n",
            ("link", "https://main.d21hsol1os28ah.amplifyapp.com/"),
        )
        help_text_widget.insert("end", "GitHub Repository: ")
        help_text_widget.insert(
            "end",
            "https://github.com/JoeyThompson10/spectrumAnalyzerProject\n",
            ("link", "https://github.com/JoeyThompson10/spectrumAnalyzerProject"),
        )

        help_text_widget.tag_config("link", foreground="blue", underline=1)
        help_text_widget.tag_bind(
            "link",
            "<Button-1>",
            lambda e, url=help_text_widget.tag_get("link", "current")[0]: open_link(
                url
            ),
        )

        # Make the text widget read-only
        help_text_widget.config(state="disabled")

    def start_analysis(self):
        # Disable the GUI and update the title
        self.toggle_gui_state(disabled=True)
        self.title("Spectrum Analyzer - Analyzing...")

        self.add_quit_label()

        env_vars.save_settings()

        # Run the analysis in a separate thread - this is not working
        analysis_thread = threading.Thread(target=self.run_analysis)
        analysis_thread.start()

    def run_analysis(self):
        # Run the analysis
        main.main()

        # Re-enable the GUI and update the title after analysis
        self.toggle_gui_state(disabled=False)
        self.title("Spectrum Analyzer - Team 5")

    def toggle_gui_state(self, disabled):
        state = 'disabled' if disabled else 'normal'
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state=state)

        # Update window title instead of changing frame background
        if disabled:
            self.title("Spectrum Analyzer - Analyzing...")
        else:
            self.title("Spectrum Analyzer - Team 5")
            # removes instructions to quit the analysis to the greyed out GUI
            self.destroy_quit_label()
            
    # adds instructions to quit the analysis to the greyed out GUI
    def add_quit_label(self):
        ttk.Label(
            self.main_frame,
            text="Press the Q key to quit the analysis",
            foreground="red",
        ).pack(pady=10, padx=10, fill=tk.X)

    # removes instructions to quit the analysis to the greyed out GUI
    def destroy_quit_label(self):
        for widget in self.main_frame.winfo_children():
                if isinstance(widget, ttk.Label):
                    if widget.cget("text") == "Press the Q key to quit the analysis":
                        widget.destroy()


    # Methods for editing numeric and string variables
    def edit_span(self):
        self.edit_numeric_var("SPAN", "Enter new SPAN value:")

    def edit_center(self):
        self.edit_numeric_var("center", "Enter new CENTER value:")

    def edit_dbPerHLine(self):
        self.edit_numeric_var("dbPerHLine", "Enter new dbPerHLine value:")

    def edit_video_folder(self):
        # Create a new window for editing the video folder
        edit_window = tk.Toplevel(self)
        edit_window.title("Edit Video Folder")

        # Entry for manual path input
        path_var = tk.StringVar(value=env_vars.Env_Vars.VIDEO_FOLDER)
        entry = ttk.Entry(edit_window, textvariable=path_var, width=50)
        entry.pack(pady=5, padx=10)

        # Function to open a file dialog and update the entry
        def browse_folder():
            folder_path = filedialog.askdirectory(
                initialdir=env_vars.Env_Vars.VIDEO_FOLDER
            )
            if folder_path:
                path_var.set(folder_path)

        # Browse button
        browse_button = ttk.Button(edit_window, text="Browse", command=browse_folder)
        browse_button.pack(pady=5, padx=10)

        # Function to update the VIDEO_FOLDER variable
        def update_video_folder():
            folder = path_var.get()
            if os.path.isdir(folder):
                env_vars.Env_Vars.VIDEO_FOLDER = folder
                edit_window.destroy()
            else:
                tk.messagebox.showerror("Error", "Invalid folder path")

        # OK and Cancel buttons
        ttk.Button(edit_window, text="OK", command=update_video_folder).pack(
            side=tk.LEFT, pady=10, padx=10
        )
        ttk.Button(edit_window, text="Cancel", command=edit_window.destroy).pack(
            side=tk.RIGHT, pady=10, padx=10
        )

        edit_window.grab_set()  # Make the window modal

    def edit_quit_key(self):
        self.edit_string_var("QUIT_KEY", "Enter new quit key:")

    def edit_dilate_iterations(self):
        self.edit_numeric_var("DILATE_ITERATIONS", "Enter new dilation iterations:")

    def edit_erode_iterations(self):
        self.edit_numeric_var("ERODE_ITERATIONS", "Enter new erosion iterations:")

    # Helper methods
    def edit_numeric_var(self, var_name, prompt):
        new_value = simpledialog.askinteger(
            var_name, prompt, initialvalue=getattr(env_vars.Env_Vars, var_name)
        )
        if new_value is not None:
            setattr(env_vars.Env_Vars, var_name, new_value)

    def edit_string_var(self, var_name, prompt):
        new_value = simpledialog.askstring(
            var_name, prompt, initialvalue=getattr(env_vars.Env_Vars, var_name)
        )
        if new_value:
            setattr(env_vars.Env_Vars, var_name, new_value)

    def edit_color(self, color_var_name):
        initial_color = getattr(env_vars.Env_Vars, color_var_name)
        color_code = colorchooser.askcolor(
            title=f"Choose color for {color_var_name}",
            initialcolor=(initial_color[0], initial_color[1], initial_color[2]),
        )
        if color_code[1]:
            new_color = np.array([int(val) for val in color_code[0]])
            setattr(env_vars.Env_Vars, color_var_name, new_color)

if __name__ == "__main__":
    app = SpectrumAnalyzerGUI()
    app.mainloop()
    app.destroy()