import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD
from ui.import_frame import ImportFrame
from ui.workspace_frame import WorkspaceFrame
from ui.export_frame import ExportFrame
from ui.settings_frame import SettingsFrame
from ui.command_frame import CommandFrame
from logic.src.file_handler import FileHandler
from logic.workspace_logic import WorkspaceFrameLogic

class MainApplication(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title('Mnemonic Volatility3 GUI')
        self.geometry('1024x768')

        self.file_handler = FileHandler()  # Initialize FileHandler

        self.load_theme()
        self.logic = WorkspaceFrameLogic(parent=self, file_handler=self.file_handler)
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # Initialize placeholders for frame data
        self.scan_result = None
        self.commands_used = []
        self.highlights = []

        # File Menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="New...", command=self.new_session)
        file_menu.add_command(label="Export...", command=self.switch_to_export_frame)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Settings", command=self.switch_to_settings_frame)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        commands_menu = tk.Menu(self.menu_bar, tearoff=0)
        commands_menu.add_command(label="Manage Commands", command=self.switch_to_command_frame)
        commands_menu.add_command(label="Add Custom Plugins",  command=self.logic.add_custom_plugin)
        self.menu_bar.add_cascade(label="Commands", menu=commands_menu)


        self.frames = {}

        # Initialize all frames properly
        self.frames[ImportFrame] = ImportFrame(self, app=self, file_handler=self.file_handler, switch_to_workspace_frame=self.switch_to_workspace_frame)
        self.frames[WorkspaceFrame] = WorkspaceFrame(self, app=self, file_handler=self.file_handler, switch_to_export_frame=self.switch_to_export_frame)
        self.frames[ExportFrame] = ExportFrame(self, switch_frame_callback=self.switch_to_workspace_frame, scan_result=self.scan_result, commands_used=self.commands_used, highlights=self.highlights)
        self.frames[SettingsFrame] = SettingsFrame(self, app=self)
        self.frames[CommandFrame] = CommandFrame(self, app=self)

        # Grid all frames
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.show_frame(ImportFrame)

        self.bind('<Control-q>', self.quit_app)
        self.bind('<Control-f>', self.search_text,)
        self.bind('<Control-o>', self.open_file)

    def load_theme(self):
        theme_dir = os.path.join(os.path.dirname(__file__), 'theme')
        azure_tcl_path = os.path.join(theme_dir, 'azure.tcl')
        if os.path.exists(azure_tcl_path):
            self.tk.call('source', azure_tcl_path)
            self.tk.call('set_theme', 'dark')
        else:
            print(f"Theme file {azure_tcl_path} not found.")

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def new_session(self):
        """Ask to export changes if any, then reset to the initial drag and drop page."""
        response = messagebox.askyesnocancel("Save Changes", "Do you want to export changes before starting a new session?")
        if response:  # Yes, export changes
            self.show_frame(ExportFrame)
        elif response is False:  # No or already exported
            self.reset_to_import()

    def reset_to_import(self):
        """Reset the application state and go back to the drag and drop page."""
        self.file_handler = FileHandler()  # Reset the file handler
        self.frames[ImportFrame].file_handler = self.file_handler
        self.frames[WorkspaceFrame].file_handler = self.file_handler
        self.update_loaded_file_label()  # Update label
        self.show_frame(ImportFrame)

    def switch_to_export_frame(self):
        """Switch to the export frame."""
        self.show_frame(ExportFrame)

    def switch_to_workspace_frame(self):
        """Switch to the workspace frame."""
        self.update_loaded_file_label()  # Update the loaded file label
        self.show_frame(WorkspaceFrame)

    def switch_to_settings_frame(self):
        """Switch to the settings frame."""
        self.show_frame(SettingsFrame)

    def switch_to_command_frame(self):
        self.show_frame(CommandFrame)

    def open_file(self, event=None):
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            self.frames[ImportFrame].handle_file(file_paths)

    def save_file(self):
        # Placeholder function to save a file
        print("File saved")

    def update_loaded_file_label(self):
        frame = self.frames[WorkspaceFrame]
        frame.update_loaded_file_label()  # Update label using file handler

    def set_selected_file(self, file):
        self.file_handler.selected_file = file
        frame = self.frames[WorkspaceFrame]
        frame.update_selected_file_label(file)
    
    def quit_app(self, event=None):
        self.quit()

    def search_text(self, event=None):
        current_frame = self.frames.get(WorkspaceFrame)
        if current_frame:
            current_frame.search_text()


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
