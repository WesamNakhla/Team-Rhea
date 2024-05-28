import tkinter as tk
from tkinter import ttk

class PreferencesFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.label = tk.Label(self, text="Preferences", font=('Arial', 14))
        self.label.pack(pady=10)

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

        # Save and Cancel Buttons
        self.save_button = tk.Button(self, text="Save", command=self.save_preferences)
        self.cancel_button = tk.Button(self, text="Cancel", command=self.cancel)
        self.save_button.pack(pady=5)
        self.cancel_button.pack(pady=5)

    def save_preferences(self):
        font_size = self.font_size_spinbox.get()
        line_distance = self.line_distance_spinbox.get()
        letter_distance = self.letter_distance_spinbox.get()
        print(f"Preferences saved: Font Size={font_size}, Line Distance={line_distance}, Letter Distance={letter_distance}")

    def cancel(self):
        # Placeholder function to cancel the operation
        print("Preferences changes cancelled")
