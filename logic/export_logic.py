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



    def cancel(self):
        self.parent.switch_frame_callback()
