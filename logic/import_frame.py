import os
import tkinter as tk
from tkinter import filedialog, messagebox

ALLOWED_FILE_TYPES = ['.dmp', '.raw', '.mem', '.bin', '.vmem', '.mddramimage', '.winddramimage']

def load_memory_file(file_path):
    if not os.path.isfile(file_path):
        return "Error: File does not exist."
    
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension not in ALLOWED_FILE_TYPES:
        return "Error: Invalid file type. Allowed types are: " + ", ".join(ALLOWED_FILE_TYPES)
    
    loaded_file_path = file_path
    return f"File loaded: {loaded_file_path}"

class ImportFrameLogic:
    def __init__(self, app):
        self.app = app

    def drop(self, event):
        files = self.parse_file_drop(event.data)
        if files:
            self.handle_file(files)
            self.on_leave(event)  # Reset color after file drop

    def import_file(self):
        filenames = filedialog.askopenfilenames()
        if filenames:
            self.handle_file(filenames)

    def browse_file(self):
        filenames = filedialog.askopenfilenames()
        if filenames:
            self.handle_file(filenames)

    def handle_file(self, filenames):
        for filename in filenames:
            result = load_memory_file(filename)
            if result.startswith("Error"):
                messagebox.showerror("File Error", result)
            else:
                self.app.loaded_files.append(filename)
        self.app.update_loaded_file_label()
        self.app.switch_to_workspace_frame()

    def parse_file_drop(self, drop_data):
        return self.tk.splitlist(drop_data)
