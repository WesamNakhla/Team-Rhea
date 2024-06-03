import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from logic.settings_frame import SettingsFrameLogic

class SettingsFrame(tk.Frame, SettingsFrameLogic):
    def __init__(self, parent, app):
        tk.Frame.__init__(self, parent)
        SettingsFrameLogic.__init__(self, app)
        self.app = app  # Store the reference to the MainApplication instance
        self.init_ui()
        self.load_settings()  # Ensure this is called after UI initialization

    def init_ui(self):
        self.label = tk.Label(self, text="Settings", font=('Arial', 14))
        self.label.pack(pady=10)

        # Volatility Path
        self.volatility_path_label = tk.Label(self, text="Path to Volatility3:", pady=5)
        self.volatility_path_label.pack()
        self.volatility_path_entry = ttk.Entry(self, width=50)
        self.volatility_path_entry.pack()
        self.browse_button = ttk.Button(self, text="Browse", command=self.browse_folder)
        self.browse_button.pack(pady=5)

        # Font Size
        self.font_size_label = tk.Label(self, text="Output Console Font Size:", pady=5)
        self.font_size_label.pack()
        self.font_size_spinbox = tk.Spinbox(self, from_=8, to=48)
        self.font_size_spinbox.pack()

        # Line Distance
        self.line_distance_label = tk.Label(self, text="Output Console Line Distance:", pady=5)
        self.line_distance_label.pack()
        self.line_distance_spinbox = tk.Spinbox(self, from_=1, to=10)
        self.line_distance_spinbox.pack()

        # Letter Distance
        self.letter_distance_label = tk.Label(self, text="Output Console Letter Distance:", pady=5)
        self.letter_distance_label.pack()
        self.letter_distance_spinbox = tk.Spinbox(self, from_=0, to=10)
        self.letter_distance_spinbox.pack()

        # Save and Exit Buttons
        self.save_button = ttk.Button(self, text="Save", command=self.save_settings)
        self.exit_button = ttk.Button(self, text="Exit", command=self.exit_settings)
        self.save_button.pack(pady=5)
        self.exit_button.pack(pady=5)
