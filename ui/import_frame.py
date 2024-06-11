import json
import os
import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import DND_FILES
from PIL import Image, ImageTk
from logic.import_logic import ImportFrameLogic, ALLOWED_FILE_TYPES

class ImportFrame(tk.Frame):
    def __init__(self, parent, app, file_handler, switch_to_workspace_frame):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.file_handler = file_handler
        self.logic = ImportFrameLogic(app=self, file_handler=self.file_handler, switch_to_workspace_frame=switch_to_workspace_frame)

        # Main content frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill="both")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Load images
        logo_image = Image.open("img/Logo2.png")
        logo_image = logo_image.resize((495, 174), Image.LANCZOS)
        self.logo_image = ImageTk.PhotoImage(logo_image)

        drag_image = Image.open("img/Drag3.png")
        drag_image = drag_image.resize((120, 120), Image.LANCZOS)
        self.drag_image = ImageTk.PhotoImage(drag_image)

        # Top logo
        self.logo_label = tk.Label(self.main_frame, image=self.logo_image, bg="#333333")
        self.logo_label.grid(row=0, column=0, pady=(10, 0), padx=(0, 60), sticky="n")

        settings_file_path = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
        with open(settings_file_path, 'r') as f:
            settings = json.load(f)

        volatility_version = settings.get('volatility_version', 'Unknown')
        version_text = f"VolGUI 1.0.0 and Volatility 3 Framework {volatility_version}"

        self.version_label = tk.Label(self.main_frame, text=version_text, font=('Arial', 11), bg="#333333", fg="white")
        self.version_label.grid(row=1, column=0, pady=(0, 20), padx=10, sticky="n")

        self.import_label = tk.Label(self.main_frame, text="Import your file", font=('Arial', 28), bg="#333333", fg="white")
        self.import_label.grid(row=2, column=0, pady=(10, 5), padx=10, sticky="n")

        self.drag_area_frame = tk.Frame(self.main_frame, bd=0, relief="solid", bg="#333333", highlightbackground="#a3a3a3", highlightcolor="#a3a3a3", highlightthickness=2)
        self.drag_area_frame.grid(row=3, column=0, pady=(1, 1), padx=20, sticky="n")

        self.drag_area = tk.Label(self.drag_area_frame, text="\n" * 9 + "Drag and drop here", font=("Arial", 18), bg="#333333", fg="white", width=60, height=13, relief="flat")
        self.drag_area.pack()

        self.drag_label = tk.Label(self.drag_area, image=self.drag_image, bg="#333333")
        self.drag_label.place(relx=0.5, rely=0.6, anchor="center")

        self.browse_button = ttk.Button(self.main_frame, text="\U0001F5C1 or Browse Manually", command=self.browse_file)
        self.browse_button.grid(row=4, column=0, pady=10, padx=10, sticky="n")

        self.drag_area.drop_target_register(DND_FILES)
        self.drag_area.dnd_bind('<<DropEnter>>', self.on_enter)
        self.drag_area.dnd_bind('<<DropLeave>>', self.on_leave)
        self.drag_area.dnd_bind('<<Drop>>', self.drop)

    def on_enter(self, event):
        self.drag_area.config(bg="#a3a3a3")

    def on_leave(self, event):
        self.drag_area.config(bg="#333333")

    def drop(self, event):
        self.logic.drop(event)

    def browse_file(self):
        self.logic.browse_file()

    def handle_file(self, file_paths):
        self.logic.handle_file(file_paths)
