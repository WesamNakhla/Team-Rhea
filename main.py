import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import TkinterDnD
from tkinter import ttk
from drag_and_drop_frame import DragAndDropFrame
from combined_frame import CombinedFrame
from export_frame import ExportFrame
from preferences import PreferencesFrame
import os

class MainApplication(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title('Mnemonic Volatility3 GUI')
        self.geometry('1024x768')

        # Initialize global settings
        self.settings = {
            'font_size': 14,
            'line_distance': 1,
            'letter_distance': 0
        }

        # Load the Azure theme
        self.load_theme()

        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # File Menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New...", command=self.new_session)
        file_menu.add_command(label="Export...", command=self.switch_to_export_frame)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Preferences", command=self.open_preferences)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        self.frames = {}
        self.loaded_file = "No file loaded"
        # Initialize all frames and store in the dictionary
        for FrameClass in (DragAndDropFrame, CombinedFrame, ExportFrame, PreferencesFrame):
            if FrameClass in (DragAndDropFrame, PreferencesFrame):
                frame = FrameClass(self, app=self)
            elif FrameClass is ExportFrame:
                frame = FrameClass(self, switch_frame_callback=self.switch_to_combined_frame)
            else:
                frame = FrameClass(self)
            self.frames[FrameClass] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Configure the grid to expand with the window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.show_frame(DragAndDropFrame)

    def load_theme(self):
        theme_dir = os.path.join(os.path.dirname(__file__), 'theme')
        self.tk.call('source', os.path.join(theme_dir, 'azure.tcl'))
        self.tk.call('set_theme', 'dark')

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()

    def switch_to_export_frame(self):
        self.show_frame(ExportFrame)

    def switch_to_combined_frame(self):
        self.show_frame(CombinedFrame)

    def new_session(self):
        self.loaded_file = "No file loaded"
        self.show_frame(DragAndDropFrame)

    def open_preferences(self):
        self.show_frame(PreferencesFrame)

    def update_global_settings(self, font_size=None, line_distance=None, letter_distance=None):
        if font_size is not None:
            self.settings['font_size'] = font_size
        if line_distance is not None:
            self.settings['line_distance'] = line_distance
        if letter_distance is not None:
            self.settings['letter_distance'] = letter_distance
        # Update settings in all frames if needed
        for frame in self.frames.values():
            if hasattr(frame, 'update_console_settings'):
                frame.update_console_settings(self.settings['font_size'], self.settings['line_distance'], self.settings['letter_distance'])

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
