import os
import tkinter as tk
from tkinter import filedialog, messagebox

ALLOWED_FILE_TYPES = ['.dmp', '.raw', '.mem', '.bin', '.vmem', '.mddramimage', '.winddramimage']

class ImportFrameLogic:
    def __init__(self, app, file_handler, switch_to_workspace_frame):
        self.app = app
        self.file_handler = file_handler
        self.switch_to_workspace_frame = switch_to_workspace_frame

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
        filenames = filedialog.askopenfilenames(filetypes=[("Memory Dump Files", ALLOWED_FILE_TYPES)])
        if filenames:
            self.handle_file(filenames)

    def handle_file(self, file_paths):
        for file_path in file_paths:
            if not os.path.isfile(file_path):
                messagebox.showerror("Error", f"File does not exist: {file_path}")
                continue
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension not in ALLOWED_FILE_TYPES:
                messagebox.showerror("Error", f"Invalid file type: {file_extension}. Allowed types are: {', '.join(ALLOWED_FILE_TYPES)}")
                continue
            self.file_handler.load_files(file_path)
            messagebox.showinfo("Success", f"File loaded: {file_path}")
            self.switch_to_workspace_frame()

    def parse_file_drop(self, drop_data):
        return self.app.tk.splitlist(drop_data)
