import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import os

# Define the allowed file types
ALLOWED_FILE_TYPES = ['.dmp', '.raw', '.bin', '.vmem', '.mddramimage',]

def load_memory_file(file_path):
    # Check if the file exists
    if not os.path.isfile(file_path):
        return "Error: File does not exist."
    
    # Check the file extension
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension not in ALLOWED_FILE_TYPES:
        return "Error: Invalid file type. Allowed types are: " + ", ".join(ALLOWED_FILE_TYPES)
    
    # Load the file path into a variable
    loaded_file_path = file_path
    return f"File loaded: {loaded_file_path}"

class ImportFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app  # Store the reference to the MainApplication instance

        # Add text and button
        self.label = ttk.Label(self, text="Drag and drop your file here OR", padding=20)
        self.label.pack()

        # Create a canvas to display the image
        self.canvas = tk.Canvas(self, width=200, height=200)
        self.canvas.pack()

        # Load the image
        self.image = tk.PhotoImage(file="img/Drag.png")  # Replace "your_image.png" with the path to your image
        self.canvas.create_image(110, 80, anchor="center", image=self.image)  # Centering the image

        # Add text and button
        self.browse_label = ttk.Label(self, text="Browse for file", padding=20)
        self.browse_label.pack()

        self.browse_button = ttk.Button(self, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=5)  # Add padding between Browse button and label

        # Add more space between the Browse button and the Import button
        self.import_button = ttk.Button(self, text="Import dump package", command=self.import_file)
        self.import_button.pack()

        # Register this widget as a drop target
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop)

    def drop(self, event):
        files = self.parse_file_drop(event.data)
        if files:
            self.handle_file(files[0])

    def import_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.handle_file(filename)

    def browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.handle_file(filename)

    def handle_file(self, filename):
        result = load_memory_file(filename)
        if result.startswith("Error"):
            messagebox.showerror("File Error", result)
        else:
            self.label.config(text=result)
            self.app.loaded_file = filename
            self.app.switch_to_workspace_frame()

    def parse_file_drop(self, drop_data):
        return self.tk.splitlist(drop_data)

class MainApplication(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("Drag and Drop Example")
        self.geometry("400x400")
        self.loaded_file = None  # Add a loaded_file attribute

        self.frame = ImportFrame(self, self)
        self.frame.pack(expand=True, fill=tk.BOTH)

    def switch_to_workspace_frame(self):
        print("Switching to workspace frame...")
        # Implement the logic to switch to the workspace frame here
        self.frame.pack_forget()  # Hide the current frame
        self.workspace_frame = WorkspaceFrame(self)  # Initialize the new frame
        self.workspace_frame.pack(expand=True, fill=tk.BOTH)  # Show the new frame

class WorkspaceFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        # Display the loaded file path
        self.file_label = ttk.Label(self, text=f"Loaded file: {self.parent.loaded_file}")
        self.file_label.pack(pady=10)

        # Additional UI elements can be added here

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()