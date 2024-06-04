# located at logic/export_frame.py
import json
import os
import tkinter as tk
from tkinter import messagebox, filedialog
import zipfile
from ui.workspace_frame import WorkspaceFrame
import threading

class ExportFrameLogic:
    def __init__(self, parent, scan_result, commands_details, highlights):
        self.parent = parent
        self.scan_result = scan_result
        self.commands_details = commands_details
        self.highlights = highlights
        self.include_memory_dump = tk.BooleanVar(value=True)
        self.include_highlighting = tk.BooleanVar(value=True)

    def save_command_outputs(self, export_dir, commands):
        for command in commands:
            filename = f"{command['command'].replace('.', '_')}.txt"
            filepath = os.path.join(export_dir, filename)
            with open(filepath, 'w') as file:
                file.write(command.get('output', ''))  # Use .get to handle missing 'output'
            command['output_file'] = filename  # Update the command dict with the output file path for later use in the metadata

    def save_metadata(self, export_dir, memory_dump_file, commands):
        metadata = {
            "memory_dump_file": os.path.basename(memory_dump_file) if self.include_memory_dump.get() else None,
            "commands": [
                {
                    "command": cmd["command"],
                    "highlights": cmd.get("highlights", []) if self.include_highlighting.get() else [],
                    "output_file": cmd['output_file']  # Include the output file in the metadata
                }
                for cmd in commands
            ]
        }
        metadata_path = os.path.join(export_dir, "metadata.json")
        with open(metadata_path, 'w') as file:
            json.dump(metadata, file, indent=4)
        return metadata_path

    def zip_files(self, files, zip_path):
        with zipfile.ZipFile(zip_path, 'w') as zf:
            for file in files:
                if file and os.path.exists(file):  # Check if file path is not None and file exists
                    zf.write(file, os.path.basename(file))
                else:
                    print(f"Skipping missing file: {file}")  # Logging the skipped file

    def export_package(self):
        export_data = self.parent.frames[WorkspaceFrame].get_export_data() if hasattr(self.parent.frames[WorkspaceFrame], 'get_export_data') else {}
        print(f"Export data at export time: {export_data}")

        if not export_data.get('commands'):
            messagebox.showerror("Export Error", "Required data is missing.")
            return

        zip_path = filedialog.asksaveasfilename(title="Export zip as...", filetypes=[("Zip files", "*.zip")], defaultextension=".zip")
        if not zip_path:
            return  # User cancelled the save

        threading.Thread(target=self.create_zip_file, args=(zip_path, export_data)).start()

    def create_zip_file(self, zip_path, export_data):
        self.export_dir = os.path.dirname(zip_path)
        self.save_command_outputs(self.export_dir, export_data['commands'])
        memory_dump_file = export_data['memory_dump_file'] if self.include_memory_dump.get() else None
        metadata_path = self.save_metadata(self.export_dir, memory_dump_file, export_data['commands'])

        files_to_zip = [metadata_path]
        if self.include_memory_dump.get():
            files_to_zip.append(export_data['memory_dump_file'])
        files_to_zip += [os.path.join(self.export_dir, cmd['output_file']) for cmd in export_data['commands'] if 'output_file' in cmd]

        self.zip_files(files_to_zip, zip_path)
        self.parent.after(0, self.parent.frames[self.__class__].export_complete)


    def cancel(self):
        self.parent.switch_frame_callback()
