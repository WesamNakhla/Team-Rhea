#located at ui/export_frame.py
import tkinter as tk
from tkinter import ttk
from logic.export_frame import ExportFrameLogic

class ExportFrame(ttk.Frame, ExportFrameLogic):
    def __init__(self, parent, switch_frame_callback, scan_result, commands_used, highlights):
        ttk.Frame.__init__(self, parent)
        ExportFrameLogic.__init__(self, parent, scan_result, commands_used, highlights)
        self.switch_frame_callback = switch_frame_callback
        self.init_ui()

    def init_ui(self):
        # This method should set up the UI components
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        frame = ttk.Frame(self)
        frame.grid(row=0, column=0, sticky="nsew")

        # Create a label
        label = ttk.Label(frame, text="Export Options", font=('Arial', 14))
        label.grid(row=0, column=0, pady=10, padx=20)

        # Create checkboxes for export options
        self.include_image_var = tk.BooleanVar(value=True)
        self.include_image_check = ttk.Checkbutton(frame, text="Include memory dump file", variable=self.include_image_var)
        self.include_image_check.grid(row=1, column=0, pady=5)

        self.include_commands_var = tk.BooleanVar(value=True)
        self.include_commands_check = ttk.Checkbutton(frame, text="Include all command outputs", variable=self.include_commands_var)
        self.include_commands_check.grid(row=2, column=0, pady=5)

        self.include_formatting_var = tk.BooleanVar(value=True)
        self.include_formatting_check = ttk.Checkbutton(frame, text="Include text formatting", variable=self.include_formatting_var)
        self.include_formatting_check.grid(row=3, column=0, pady=5)

        # Buttons for exporting and cancelling
        export_button = ttk.Button(frame, text="Export", command=self.export_package)
        export_button.grid(row=4, column=0, padx=10, pady=10)

        cancel_button = ttk.Button(frame, text="Cancel", command=self.cancel)
        cancel_button.grid(row=4, column=1, padx=10, pady=10)

    def export_package(self):
        # Override this method if needed or use the logic layer's method directly
        super().export_package()

    def cancel(self):
        # Call the switch frame callback or perform any necessary cleanup
        self.switch_frame_callback()

