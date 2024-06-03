import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from logic.import_frame import ImportFrameLogic, ALLOWED_FILE_TYPES

class ImportFrame(ttk.Frame, ImportFrameLogic):
    def __init__(self, parent, app):
        ttk.Frame.__init__(self, parent)
        ImportFrameLogic.__init__(self, app)
        self.app = app

        content_frame = ttk.Frame(self)
        content_frame.pack(expand=True)

        ascii_logo = """
       ____   ____________  .____     ________ ____ ___.___ 
       \\   \\ /   /\\_____  \\ |    |   /  _____/|    |   \\   |
        \\   Y   /  /   |   \\|    |  /   \\  ___|    |   /   |
         \\     /  /    |    \\    |__\\    \\_\\  \\    |  /|   |
          \\___/   \\_______  /_______ \\______  /______/ |___|
                          \\/        \\/      \\/                      
        """
        self.logo_label = tk.Label(content_frame, text=ascii_logo, font=("Courier", 12), fg="#4a90e2", justify="left", padx=10, pady=20)
        self.logo_label.pack()

        self.drag_area = tk.Label(content_frame, text="Drag and Drop File Here", font=("Arial", 20), bg="#d9d9d9", fg="#4a90e2", width=60, height=10, relief="sunken")
        self.drag_area.pack(pady=10)

        self.browse_label = ttk.Label(content_frame, text="Or manually browse for a file", font=("Arial", 14), padding=20)
        self.browse_label.pack()

        self.browse_button = ttk.Button(content_frame, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=10)

        self.drag_area.drop_target_register(DND_FILES)
        self.drag_area.dnd_bind('<<DropEnter>>', self.on_enter)
        self.drag_area.dnd_bind('<<DropLeave>>', self.on_leave)
        self.drag_area.dnd_bind('<<Drop>>', self.drop)

    def on_enter(self, event):
        self.drag_area.config(bg="#a3a3a3")

    def on_leave(self, event):
        self.drag_area.config(bg="#d9d9d9")
