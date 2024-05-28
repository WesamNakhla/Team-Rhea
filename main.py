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
            if FrameClass is DragAndDropFrame:
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

    def new_session(self):
        """Ask to export changes if any, then reset to the initial drag and drop page."""
        response = messagebox.askyesnocancel("Save Changes", "Do you want to export changes before starting a new session?")
        if response:  # Yes, export changes
            self.show_frame(ExportFrame)
        elif response is False:  # No or already exported
            self.reset_to_drag_and_drop()

    def reset_to_drag_and_drop(self):
        """Reset the application state and go back to the drag and drop page."""
        self.show_frame(DragAndDropFrame)

    def switch_to_export_frame(self):
        """Switch to the export frame."""
        self.show_frame(ExportFrame)

    def switch_to_combined_frame(self):
        """Switch to the combined frame."""
        self.show_frame(CombinedFrame)

    def show_frame(self, cont):
        """Raise the given frame to the top for viewing."""
        frame = self.frames[cont]
        frame.tkraise()

    def open_file(self):
        # Placeholder function to open a file
        print("File opened")

    def save_file(self):
        # Placeholder function to save a file
        print("File saved")

    def open_preferences(self):
        """Switch to the preferences frame."""
        self.show_frame(PreferencesFrame)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
