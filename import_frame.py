import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import os

# Define the allowed file types
ALLOWED_FILE_TYPES = ['.dmp', '.raw', '.mem', '.bin', '.vmem', '.mddramimage']

def load_memory_file(file_path):
    if not os.path.isfile(file_path):
        return "Error: File does not exist."
    
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension not in ALLOWED_FILE_TYPES:
        return "Error: Invalid file type. Allowed types are: " + ", ".join(ALLOWED_FILE_TYPES)
    
    loaded_file_path = file_path
    return f"File loaded: {loaded_file_path}"

class ImportFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # Frame for content
        content_frame = ttk.Frame(self)
        content_frame.pack(expand=True)

        # Add text and button
        self.label = ttk.Label(content_frame, text="Drag and drop your file here OR", font=("Arial", 14), padding=20)
        self.label.pack()

        # Create a canvas to display the image
        self.canvas = tk.Canvas(content_frame, width=200, height=200)
        self.canvas.pack()

        # Load the image
        self.image = tk.PhotoImage(file="img/Drag.png")
        self.canvas.create_image(100, 80, anchor="center", image=self.image)

        # Add text and button
        self.browse_label = ttk.Label(content_frame, text="Browse for file", font=("Arial", 14), padding=20)
        self.browse_label.pack()

        self.browse_button = ttk.Button(content_frame, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=5)

        self.import_button = ttk.Button(content_frame, text="Import dump package", command=self.import_file)
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
        self.geometry("600x600")
        self.loaded_file = None

        self.frame = ImportFrame(self, self)
        self.frame.pack(expand=True, fill=tk.BOTH)

    def switch_to_workspace_frame(self):
        print("Switching to workspace frame...")
        self.frame.pack_forget()
        self.workspace_frame = WorkspaceFrame(self)
        self.workspace_frame.pack(expand=True, fill=tk.BOTH)

class WorkspaceFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.file_label = ttk.Label(self, text=f"Loaded file: {self.parent.loaded_file}", font=("Arial", 14))
        self.file_label.pack(pady=10)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()