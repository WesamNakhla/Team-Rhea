import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import json

class ExportFrame(ttk.Frame):
    def __init__(self, parent, switch_frame_callback, scan_result, commands_used, highlights):
        super().__init__(parent)
        self.switch_frame_callback = switch_frame_callback
        self.scan_result = scan_result
        self.commands_used = commands_used
        self.highlights = highlights
        self.init_ui()

    def init_ui(self):
        # Configure the grid to center the contents
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create a frame to hold the widgets and center it
        frame = ttk.Frame(self)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Use an inner frame to pack widgets
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

        self.export_button = ttk.Button(inner_frame, text="Export dump package", command=self.export_package)
        self.cancel_button = ttk.Button(inner_frame, text="Cancel", command=self.cancel)
        self.export_button.grid(row=5, column=0, pady=5)
        self.cancel_button.grid(row=6, column=0, pady=5)

    def browse_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, file_path)

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
        # Switch back to the CombinedFrame
        self.switch_frame_callback()

    def update_data(self, scan_result, commands_used, highlights):
        self.scan_result = scan_result
        self.commands_used = commands_used
        self.highlights = highlights

# Example usage
if __name__ == "__main__":
    def switch_to_workspace_frame():
        print("Switching to workspaceFrame")

    root = tk.Tk()
    root.title('Export Frame Example')
    root.geometry('1024x768')

    # Configure the main window's grid to center the ExportFrame
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    export_frame = ExportFrame(root, switch_frame_callback=switch_to_workspace_frame, scan_result={}, commands_used=[], highlights=[])
    export_frame.grid(row=0, column=0, sticky="nsew")

    root.mainloop()
