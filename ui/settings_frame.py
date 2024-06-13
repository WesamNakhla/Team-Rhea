import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from logic.settings_logic import SettingsFrameLogic

class SettingsFrame(tk.Frame, SettingsFrameLogic):
    def __init__(self, parent, app):
        tk.Frame.__init__(self, parent)
        SettingsFrameLogic.__init__(self, app)
        self.app = app  # Store the reference to the MainApplication instance
        self.init_ui()
        self.load_settings()  # Ensure this is called after UI initialization

    def init_ui(self):
        # Main content frame
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_columnconfigure(2, weight=1)

        # Bottom frame for version label
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.grid(row=1, column=0, sticky="ew")
        self.bottom_frame.grid_columnconfigure(0, weight=1)

        # Configure the main grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # Settings label
        self.label = tk.Label(self.main_frame, text="Settings", font=('Arial', 28))
        self.label.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="w")

        # Volatility Path
        self.volatility_path_label = tk.Label(self.main_frame, text="Path to Volatility3:", pady=5, font=('Arial', 12))
        self.volatility_path_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.volatility_path_entry = ttk.Entry(self.main_frame, width=50)
        self.volatility_path_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        self.browse_button = ttk.Button(self.main_frame, text="\U0001F5C1 Browse", command=self.browse_folder)
        self.browse_button.grid(row=1, column=2, sticky="w", padx=10, pady=5)

        # Result Window Options
        self.result_window_options_label = tk.Label(self.main_frame, text="Result window options", font=('Arial', 18))
        self.result_window_options_label.grid(row=2, column=0, columnspan=3, pady=20, padx=10, sticky="w")

        # Font Size
        self.font_size_label = tk.Label(self.main_frame, text="Font size:", font=('Arial', 12))
        self.font_size_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.font_size_spinbox = ttk.Spinbox(self.main_frame, from_=8, to=48, width=5)
        self.font_size_spinbox.grid(row=3, column=1, sticky="ew", padx=10, pady=5)

        # Line Distance
        self.line_distance_label = tk.Label(self.main_frame, text="Line distance:", font=('Arial', 12))
        self.line_distance_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.line_distance_spinbox = ttk.Spinbox(self.main_frame, from_=1, to=10, width=5)
        self.line_distance_spinbox.grid(row=4, column=1, sticky="ew", padx=10, pady=5)

        # Letter Distance
        self.letter_distance_label = tk.Label(self.main_frame, text="Letter distance:", font=('Arial', 12))
        self.letter_distance_label.grid(row=5, column=0, sticky="w", padx=10, pady=5)
        self.letter_distance_spinbox = ttk.Spinbox(self.main_frame, from_=0, to=10, width=5)
        self.letter_distance_spinbox.grid(row=5, column=1, sticky="ew", padx=10, pady=5)

        # Save and Exit Buttons
        self.save_button = ttk.Button(self.main_frame, text="\U0001F5AA Save", command=self.save_settings)
        self.save_button.grid(row=6, column=1, pady=20, padx=10, sticky="e")
        self.exit_button = ttk.Button(self.main_frame, text="\U000025C1 Back", command=self.exit_settings)
        self.exit_button.grid(row=6, column=2, pady=20, padx=10, sticky="w")

        # Version Label at Bottom Left corner
        settings_file_path = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
        with open(settings_file_path, 'r') as f:
            settings = json.load(f)

        # Extract the version information
        volatility_version = settings.get('volatility_version', 'Unknown')
        version_text = f"VolGUI 1.0.0 and Volatility 3 Framework {volatility_version}"

        self.version_label = tk.Label(self.bottom_frame, text=version_text)
        self.version_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

    def load_settings(self):
        settings_file_path = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
        if os.path.exists(settings_file_path):
            with open(settings_file_path, 'r') as f:
                settings = json.load(f)
                self.volatility_path_entry.insert(0, settings.get("volatility_path", ""))
                self.font_size_spinbox.set(settings.get("font_size", "12"))
                self.line_distance_spinbox.set(settings.get("line_distance", "1"))
                self.letter_distance_spinbox.set(settings.get("letter_distance", "1"))
        else:
            messagebox.showerror("Error", f"Settings file not found at {settings_file_path}")

    def save_settings(self):
        settings = {
            "volatility_path": self.volatility_path_entry.get(),
            "font_size": self.font_size_spinbox.get(),
            "line_distance": self.line_distance_spinbox.get(),
            "letter_distance": self.letter_distance_spinbox.get(),
            "volatility_version": "2.7.0"  # Keep this constant for now
        }
        settings_file_path = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
        with open(settings_file_path, 'w') as f:
            json.dump(settings, f, indent=4)
        messagebox.showinfo("Settings Saved", "Settings have been saved successfully.")
        self.app.apply_font_settings_to_console()

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.volatility_path_entry.delete(0, tk.END)
            self.volatility_path_entry.insert(0, folder_path)

    def exit_settings(self):
        self.app.switch_to_workspace_frame()
