import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json

class SettingsFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app  # Store the reference to the MainApplication instance
        self.original_settings = {}
        self.init_ui()
        self.load_settings()

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
        self.save_button = tk.Button(self, text="Save", command=self.save_settings)
        self.exit_button = tk.Button(self, text="Exit", command=self.exit_settings)
        self.save_button.pack(pady=5)
        self.exit_button.pack(pady=5)

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.volatility_path_entry.delete(0, tk.END)
            self.volatility_path_entry.insert(0, folder_path)

    def save_settings(self):
        settings = {
            'volatility_path': self.volatility_path_entry.get(),
            'font_size': self.font_size_spinbox.get(),
            'line_distance': self.line_distance_spinbox.get(),
            'letter_distance': self.letter_distance_spinbox.get()
        }
        with open('settings.json', 'w') as settings_file:
            json.dump(settings, settings_file)
        self.original_settings = settings.copy()
        messagebox.showinfo("Settings", "Settings saved successfully!")

    def load_settings(self):
        try:
            with open('settings.json', 'r') as settings_file:
                settings = json.load(settings_file)
                self.volatility_path_entry.insert(0, settings.get('volatility_path', ''))
                self.font_size_spinbox.delete(0, tk.END)
                self.font_size_spinbox.insert(0, settings.get('font_size', 12))
                self.line_distance_spinbox.delete(0, tk.END)
                self.line_distance_spinbox.insert(0, settings.get('line_distance', 1))
                self.letter_distance_spinbox.delete(0, tk.END)
                self.letter_distance_spinbox.insert(0, settings.get('letter_distance', 1))
                self.original_settings = settings.copy()
        except FileNotFoundError:
            print("Settings file not found. Using defaults.")

    def revert_unsaved_changes(self):
        # Revert changes by resetting the entry fields to original settings
        self.volatility_path_entry.delete(0, tk.END)
        self.volatility_path_entry.insert(0, self.original_settings.get('volatility_path', ''))
        self.font_size_spinbox.delete(0, tk.END)
        self.font_size_spinbox.insert(0, self.original_settings.get('font_size', 12))
        self.line_distance_spinbox.delete(0, tk.END)
        self.line_distance_spinbox.insert(0, self.original_settings.get('line_distance', 1))
        self.letter_distance_spinbox.delete(0, tk.END)
        self.letter_distance_spinbox.insert(0, self.original_settings.get('letter_distance', 1))

    def exit_settings(self):
        # Compare the current UI settings with the original settings
        current_settings = {
            'volatility_path': self.volatility_path_entry.get(),
            'font_size': self.font_size_spinbox.get(),
            'line_distance': self.line_distance_spinbox.get(),
            'letter_distance': self.letter_distance_spinbox.get()
        }
        # Check if there are unsaved changes
        if current_settings != self.original_settings:
            # Confirm if the user wants to exit without saving
            if messagebox.askyesno("Exit Settings", "Are you sure you want to exit without saving your latest changes?"):
                self.app.switch_to_workspace_frame()
            else:
                self.revert_unsaved_changes()
        else:
            self.app.switch_to_workspace_frame()


    def cancel(self):
        print("Settings changes cancelled.")
