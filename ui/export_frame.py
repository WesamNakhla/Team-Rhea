import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from logic.export_frame import ExportFrameLogic

class ExportFrame(ttk.Frame, ExportFrameLogic):
    def __init__(self, parent, switch_frame_callback, scan_result, commands_used, highlights):
        ttk.Frame.__init__(self, parent)
        ExportFrameLogic.__init__(self, scan_result, commands_used, highlights)
        self.switch_frame_callback = switch_frame_callback
        self.init_ui()

    def init_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        frame = ttk.Frame(self)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        inner_frame = ttk.Frame(frame)
        inner_frame.grid(row=0, column=0)
        
        self.label = ttk.Label(inner_frame, text="Export memory dump package", font=('Arial', 14))
        self.label.grid(row=0, column=0, pady=10, padx=20)

        self.location_entry = ttk.Entry(inner_frame, width=50)
        self.location_entry.grid(row=1, column=0, pady=10)

        self.browse_button = ttk.Button(inner_frame, text="Browse...", command=self.browse_file)
        self.browse_button.grid(row=1, column=1, padx=10)

        self.include_image_var = tk.BooleanVar(value=True)
        self.include_image_check = ttk.Checkbutton(inner_frame, text="Include image dump file", variable=self.include_image_var)
        self.include_image_check.grid(row=2, column=0, pady=5)
        
        self.include_commands_var = tk.BooleanVar(value=True)
        self.include_commands_check = ttk.Checkbutton(inner_frame, text="Include all command outputs", variable=self.include_commands_var)
        self.include_commands_check.grid(row=3, column=0, pady=5)
        
        self.include_formatting_var = tk.BooleanVar(value=True)
        self.include_formatting_check = ttk.Checkbutton(inner_frame, text="Include text formatting", variable=self.include_formatting_var)
        self.include_formatting_check.grid(row=4, column=0, pady=5)

        self.export_button = ttk.Button(inner_frame, text="Export Package", command=self.export_package)
        self.export_button.grid(row=5, column=0, pady=10)
        
        self.cancel_button = ttk.Button(inner_frame, text="Cancel", command=self.cancel)
        self.cancel_button.grid(row=6, column=0, pady=10)

    def browse_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, file_path)
