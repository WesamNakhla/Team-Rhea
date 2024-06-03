#located at logic/export_frame.py
import json
import os
import tkinter as tk
from tkinter import messagebox, filedialog
import zipfile
from ui.workspace_frame import WorkspaceFrame 

class ExportFrameLogic:
    def __init__(self, parent, scan_result, commands_details, highlights):
        self.parent = parent
        self.scan_result = scan_result
        self.commands_details = commands_details
        self.highlights = highlights

    def save_command_outputs(self, export_dir, commands):
        for idx, command in enumerate(commands):
            filename = f"command_output_{idx}.txt"
            filepath = os.path.join(export_dir, filename)
            with open(filepath, 'w') as file:
                file.write(command['output'])
            command['output_file'] = filename  # Update the command dict with the output file path for later use in the metadata


    def save_metadata(self, export_dir, memory_dump_file, commands, highlights):
        metadata = {
            "memory_dump_file": memory_dump_file,
            "commands": commands,
            "highlights": highlights
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

        if not export_data.get('commands') or not export_data.get('memory_dump_file'):
            messagebox.showerror("Export Error", "Required data is missing.")
            return

        zip_path = filedialog.asksaveasfilename(title="Save exported package", filetypes=[("Zip files", "*.zip")], defaultextension=".zip")
        if not zip_path:
            return  # User cancelled the save

        export_dir = os.path.dirname(zip_path)
        self.save_command_outputs(export_dir, export_data['commands'])  # Corrected to pass two arguments
        metadata_path = self.save_metadata(export_dir, export_data['memory_dump_file'], export_data['commands'], export_data['highlights'])

        files_to_zip = [metadata_path, export_data['memory_dump_file']] + [os.path.join(export_dir, cmd['output_file']) for cmd in export_data['commands'] if 'output_file' in cmd]
        self.zip_files(files_to_zip, zip_path)

        messagebox.showinfo("Export Complete", "Exported package saved successfully.")




    def cancel(self):
        self.parent.switch_frame_callback()

