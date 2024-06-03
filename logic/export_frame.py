import json
import tkinter as tk
from tkinter import messagebox

class ExportFrameLogic:
    def __init__(self, scan_result, commands_used, highlights):
        self.scan_result = scan_result
        self.commands_used = commands_used
        self.highlights = highlights

    def export_package(self):
        destination_path = self.location_entry.get()
        include_image = self.include_image_var.get()
        include_commands = self.include_commands_var.get()
        include_formatting = self.include_formatting_var.get()

        try:
            data = {
                "scan_result": self.scan_result,
                "commands_used": self.commands_used if include_commands else [],
                "highlights": self.highlights if include_formatting else []
            }
            with open(destination_path, 'w') as file:
                json.dump(data, file, indent=4)

            print("Package exported to:", destination_path)
            messagebox.showinfo("Export Successful", f"Package successfully exported to {destination_path}")
        except Exception as e:
            print("Error exporting package:", e)
            messagebox.showerror("Export Failed", f"Failed to export package: {e}")

    def cancel(self):
        self.switch_frame_callback()

    def update_data(self, scan_result, commands_used, highlights):
        self.scan_result = scan_result
        self.commands_used = commands_used
        self.highlights = highlights
