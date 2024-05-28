import tkinter as tk
from tkinter import ttk

class ExportFrame(ttk.Frame):
    def __init__(self, parent, switch_frame_callback):
        super().__init__(parent)
        self.switch_frame_callback = switch_frame_callback
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
        self.location_entry.insert(0, "c:/programfiles86/filesomewhere")

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

    def export_package(self):
        # Placeholder function for exporting the package
        print("Package exported to:", self.location_entry.get())
        print("Include image dump file:", self.include_image_var.get())
        print("Include all command outputs:", self.include_commands_var.get())
        print("Include text formatting:", self.include_formatting_var.get())

    def cancel(self):
        # Switch back to the CombinedFrame
        self.switch_frame_callback()

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

    export_frame = ExportFrame(root, switch_frame_callback=switch_to_workspace_frame)
    export_frame.grid(row=0, column=0, sticky="nsew")

    root.mainloop()
