import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from logic.export_logic import ExportFrameLogic
from PIL import Image, ImageTk, ImageSequence
import os
import threading
from ui.workspace_frame import WorkspaceFrame

class ExportFrame(ttk.Frame, ExportFrameLogic):
    def __init__(self, parent, switch_frame_callback=None, scan_result=None, commands_used=None, highlights=None):
        ttk.Frame.__init__(self, parent)
        ExportFrameLogic.__init__(self, parent, scan_result, commands_used, highlights)
        self.switch_frame_callback = switch_frame_callback
        self.init_ui()

    def init_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        frame = ttk.Frame(self)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        # Create a label for the title
        title_label = ttk.Label(frame, text="Export Zipped Package", font=('Arial', 28))
        title_label.grid(row=0, column=0, pady=(200, 30), padx=20)

        # Create checkboxes for export options
        self.include_memory_dump_check = ttk.Checkbutton(frame, text="Include memory dump file", variable=self.include_memory_dump)
        self.include_memory_dump_check.grid(row=1, column=0, pady=(10), sticky="n", padx=20)

        self.include_highlighting_check = ttk.Checkbutton(frame, text="Include text formatting", variable=self.include_highlighting)
        self.include_highlighting_check.grid(row=2, column=0, pady=(10, 30), sticky="n", padx=20)

        # Buttons for exporting and cancelling
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, pady=(20), padx=20)

        export_button = ttk.Button(button_frame, text="\U0001F5BF Export", command=self.choose_save_location)
        export_button.grid(row=0, column=0, padx=(10))

        cancel_button = ttk.Button(button_frame, text="\U000025C1 Back", command=self.cancel)
        cancel_button.grid(row=0, column=1, padx=(10))

        # Loading GIF and message label (initially hidden)
        self.loading_frame = ttk.Frame(frame)
        self.loading_frame.grid(row=4, column=0, pady=(10, 20), padx=20)
        self.loading_frame.grid_remove()

        self.loading_label = ttk.Label(self.loading_frame, text="Exporting... Please wait!", font=('Arial', 12))
        self.loading_label.pack(side=tk.TOP, pady=10)

        # Resize the GIF to an appropriate size
        self.loading_gif = Image.open("img/loading.gif")
        self.loading_frames = [ImageTk.PhotoImage(frame.resize((50, 50), Image.LANCZOS)) for frame in ImageSequence.Iterator(self.loading_gif)]
        
        self.loading_image_label = ttk.Label(self.loading_frame)  # Initialize loading_image_label
        self.loading_image_label.pack(side=tk.TOP)

        self.loading_frame_index = 0
        self.loading_animation = None

    def choose_save_location(self):
        zip_path = filedialog.asksaveasfilename(title="Export Zip to...", filetypes=[("Zip files", "*.zip")], defaultextension=".zip")
        if zip_path:
            self.show_loading()
            threading.Thread(target=self.create_zip_file, args=(zip_path, self.parent.frames[WorkspaceFrame].get_export_data())).start()

    def show_loading(self):
        self.loading_frame.grid()
        self.loading_animation = self.loading_image_label.after(100, self.animate_loading)

    def hide_loading(self):
        self.loading_frame.grid_remove()
        if self.loading_animation:
            self.loading_image_label.after_cancel(self.loading_animation)
            self.loading_animation = None

    def animate_loading(self):
        frame = self.loading_frames[self.loading_frame_index]
        self.loading_image_label.configure(image=frame)
        self.loading_frame_index = (self.loading_frame_index + 1) % len(self.loading_frames)
        self.loading_animation = self.loading_image_label.after(100, self.animate_loading)

    def export_complete(self):
        self.hide_loading()
        messagebox.showinfo("Export Complete", "Exported package saved successfully.")
        os.startfile(self.export_dir)

    def cancel(self):
        self.switch_frame_callback()
