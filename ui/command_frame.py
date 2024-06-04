# located at ui/command_frame.py
import tkinter as tk
from tkinter import ttk
from logic.command_frame import CommandFrameLogic

class CommandFrame(tk.Frame, CommandFrameLogic):
    def __init__(self, parent, app):
        tk.Frame.__init__(self, parent)
        CommandFrameLogic.__init__(self, app)
        self.app = app
        self.init_ui()

    def init_ui(self):
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_columnconfigure(2, weight=1)

        self.label = tk.Label(self.main_frame, text="Command management", font=('Arial', 28))
        self.label.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="w")

        self.command_entries = []
        self.type_entries = []
        self.description_entries = []

        self.command_frame = tk.Frame(self.main_frame)
        self.command_frame.grid(row=1, column=0, columnspan=3, pady=10, padx=10, sticky="nsew")
        self.command_frame.grid_columnconfigure(0, weight=1)
        self.command_frame.grid_columnconfigure(1, weight=1)
        self.command_frame.grid_columnconfigure(2, weight=2)

        self.load_commands_ui()

        self.add_command_button = ttk.Button(self.main_frame, text="Add command", command=self.add_command_ui)
        self.add_command_button.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="ew")

        self.save_button = ttk.Button(self.main_frame, text="Save", command=self.save_commands)
        self.save_button.grid(row=3, column=1, pady=10, padx=10, sticky="e")

        self.exit_button = ttk.Button(self.main_frame, text="Exit", command=self.app.switch_to_workspace_frame)
        self.exit_button.grid(row=3, column=2, pady=10, padx=10, sticky="w")

    def load_commands_ui(self):
        for widget in self.command_frame.winfo_children():
            widget.destroy()

        for index, command in enumerate(self.commands):
            self.create_command_row(index, command)

    def create_command_row(self, index, command):
        command_entry = ttk.Entry(self.command_frame, width=30)
        command_entry.grid(row=index, column=0, padx=5, pady=5, sticky="ew")
        command_entry.insert(0, command["command"])
        self.command_entries.append(command_entry)

        type_entry = ttk.Entry(self.command_frame, width=30)
        type_entry.grid(row=index, column=1, padx=5, pady=5, sticky="ew")
        type_entry.insert(0, command["type"])
        self.type_entries.append(type_entry)

        description_entry = ttk.Entry(self.command_frame, width=50)
        description_entry.grid(row=index, column=2, padx=5, pady=5, sticky="ew")
        description_entry.insert(0, command["description"])
        self.description_entries.append(description_entry)

        delete_button = ttk.Button(self.command_frame, text="Delete", command=lambda idx=index: self.delete_command_ui(idx))
        delete_button.grid(row=index, column=3, padx=5, pady=5)

    def add_command_ui(self):
        self.create_command_row(len(self.commands), {"command": "", "type": "", "description": ""})
        self.commands.append({"command": "", "type": "", "description": ""})

    def delete_command_ui(self, index):
        del self.commands[index]
        self.load_commands_ui()
