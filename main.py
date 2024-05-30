import tkinter as tk
from tkinter import messagebox, filedialog
from tkinterdnd2 import TkinterDnD
from tkinter import ttk
from import_frame import ImportFrame
from workspace_frame import WorkspaceFrame  # Ensure this is the correct import
from export_frame import ExportFrame
from settings_frame import SettingsFrame
import os
import json

class MainApplication(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title('Mnemonic Volatility3 GUI')
        self.geometry('1024x768')
        
        self.load_theme()

        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # File Menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New...", command=self.new_session)
        file_menu.add_command(label="Export...", command=self.switch_to_export_frame)
        file_menu.add_command(label="Save Session", command=self.save_session)
        file_menu.add_command(label="Load Session", command=self.load_session)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Settings", command=self.switch_to_settings_frame)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        self.frames = {}
        self.loaded_file = None  # This holds the current loaded file
        self.scan_result = None  # To hold scan results
        self.commands_used = []  # To hold commands used
        self.highlights = []  # To hold highlights

        # Initialize all frames and store in the dictionary
        for FrameClass in (ImportFrame, WorkspaceFrame, ExportFrame, SettingsFrame):
            if FrameClass is ImportFrame:
                frame = FrameClass(self, app=self)
            elif FrameClass is ExportFrame:
                frame = ExportFrame(self, switch_frame_callback=self.switch_to_workspace_frame, scan_result=self.scan_result, commands_used=self.commands_used, highlights=self.highlights)
            elif FrameClass is SettingsFrame:
                frame = SettingsFrame(self, app=self)  # Pass self to SettingsFrame
            else:
                frame = FrameClass(self)  # Pass self to WorkspaceFrame
            self.frames[FrameClass] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Configure the grid to expand with the window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.show_frame(ImportFrame)

    def load_theme(self):
        theme_dir = os.path.join(os.path.dirname(__file__), 'theme')
        self.tk.call('source', os.path.join(theme_dir, 'azure.tcl'))
        self.tk.call('set_theme', 'dark')

    def new_session(self):
        """Ask to export changes if any, then reset to the initial drag and drop page."""
        response = messagebox.askyesnocancel("Save Changes", "Do you want to export changes before starting a new session?")
        if response:  # Yes, export changes
            self.show_frame(ExportFrame)
        elif response is False:  # No or already exported
            self.reset_to_import()

    def reset_to_import(self):
        """Reset the application state and go back to the drag and drop page."""
        self.show_frame(ImportFrame)

    def switch_to_export_frame(self):
        """Switch to the export frame."""
        frame = self.frames[ExportFrame]
        frame.update_data(self.scan_result, self.commands_used, self.highlights)
        self.show_frame(ExportFrame)

    def switch_to_workspace_frame(self):
        """Switch to the workspace frame."""
        frame = self.frames[WorkspaceFrame]
        print("Switching to WorkspaceFrame")
        try:
            frame.update_loaded_file_label()  # Update label when switching to workspace
        except AttributeError as e:
            print(f"Error: {e}")
            messagebox.showerror("Error", f"WorkspaceFrame has no method 'update_loaded_file_label'")
        self.show_frame(WorkspaceFrame)

    def switch_to_settings_frame(self):
        """Switch to the settings frame."""
        self.show_frame(SettingsFrame)

    def show_frame(self, frame_class):
        """Raise the given frame to the top for viewing."""
        frame = self.frames[frame_class]
        frame.tkraise()

    def save_session(self):
        session_data = {
            'loaded_file': self.loaded_file,
            'scan_result': self.scan_result,
            'commands_used': self.commands_used,
            'highlights': self.highlights
        }
        save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(session_data, f)
            messagebox.showinfo("Session Saved", f"Session successfully saved to {save_path}")

    def load_session(self):
        load_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if load_path:
            with open(load_path, 'r') as f:
                session_data = json.load(f)
                self.loaded_file = session_data.get('loaded_file')
                self.scan_result = session_data.get('scan_result')
                self.commands_used = session_data.get('commands_used', [])
                self.highlights = session_data.get('highlights', [])

                # Update frames with loaded data
                frame = self.frames.get(WorkspaceFrame)
                if frame:
                    print("Updating WorkspaceFrame with loaded session data")
                    try:
                        frame.update_loaded_file_label()
                        frame.load_previous_commands()
                    except AttributeError as e:
                        print(f"Error: {e}")
                        messagebox.showerror("Error", f"AttributeError: {str(e)}")

                # Automatically switch to the WorkspaceFrame after loading the session
                self.switch_to_workspace_frame()

                messagebox.showinfo("Session Loaded", f"Session successfully loaded from {load_path}")

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()