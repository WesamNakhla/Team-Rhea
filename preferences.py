import tkinter as tk
from tkinter import ttk

class PreferencesFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.init_ui()

    def init_ui(self):
        self.label = tk.Label(self, text="Preferences", font=('Arial', 14))
        self.label.pack(pady=10)

        # Font Size
        self.font_size_label = tk.Label(self, text="Output Console Font Size:", pady=5)
        self.font_size_label.pack()
        self.font_size_spinbox = tk.Spinbox(self, from_=8, to=48, increment=1)
        self.font_size_spinbox.pack()
        self.font_size_spinbox.delete(0, 'end')
        self.font_size_spinbox.insert(0, self.app.settings['font_size'])  # Set current font size

        # Line Distance
        self.line_distance_label = tk.Label(self, text="Output Console Line Distance:", pady=5)
        self.line_distance_label.pack()
        self.line_distance_spinbox = tk.Spinbox(self, from_=1, to=10, increment=1)
        self.line_distance_spinbox.pack()
        self.line_distance_spinbox.delete(0, 'end')
        self.line_distance_spinbox.insert(0, self.app.settings['line_distance'])  # Set current line distance

        # Letter Distance
        self.letter_distance_label = tk.Label(self, text="Output Console Letter Distance:", pady=5)
        self.letter_distance_label.pack()
        self.letter_distance_spinbox = tk.Spinbox(self, from_=0, to=10, increment=1)
        self.letter_distance_spinbox.pack()
        self.letter_distance_spinbox.delete(0, 'end')
        self.letter_distance_spinbox.insert(0, self.app.settings['letter_distance'])  # Set current letter distance

        # Save and Cancel Buttons
        self.save_button = tk.Button(self, text="Save", command=self.save_preferences)
        self.cancel_button = tk.Button(self, text="Cancel", command=self.cancel)
        self.save_button.pack(pady=5)
        self.cancel_button.pack(pady=5)

    def save_preferences(self):
        font_size = int(self.font_size_spinbox.get())
        line_distance = int(self.line_distance_spinbox.get())
        letter_distance = int(self.letter_distance_spinbox.get())
        print(f"Preferences saved: Font Size={font_size}, Line Distance={line_distance}, Letter Distance={letter_distance}")
        self.app.update_global_settings(font_size, line_distance, letter_distance)

    def cancel(self):
        # Placeholder function to cancel the operation
        print("Preferences changes cancelled")
