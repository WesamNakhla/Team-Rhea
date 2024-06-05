# ui/command_frame.py
import tkinter as tk
from tkinter import ttk, Scrollbar, VERTICAL
from logic.command_frame import CommandFrameLogic

class CommandFrame(tk.Frame, CommandFrameLogic):
    def __init__(self, parent, app):
        tk.Frame.__init__(self, parent)
        CommandFrameLogic.__init__(self, self)
        self.app = app
        self.init_ui()

    def init_ui(self):
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_columnconfigure(2, weight=1)

        self.label = tk.Label(self.main_frame, text="Command management", font=('Arial', 28))
        self.label.grid(row=0, column=0, columnspan=4, pady=10, padx=10, sticky="w")

        self.add_form_ui()  # Add new form UI for adding commands
        self.command_frame = tk.Frame(self.main_frame)
        self.command_frame.grid(row=2, column=0, columnspan=4, pady=10, padx=10, sticky="nsew")
        self.command_frame.grid_columnconfigure(0, weight=1)
        self.command_frame.grid_columnconfigure(1, weight=1)
        self.command_frame.grid_columnconfigure(2, weight=2)
        self.command_frame.grid_columnconfigure(3, weight=1)

        self.scrollbar = Scrollbar(self.command_frame, orient=VERTICAL)
        self.scrollbar.grid(row=0, column=4, sticky='ns')

        self.command_canvas = tk.Canvas(self.command_frame, yscrollcommand=self.scrollbar.set)
        self.command_canvas.grid(row=0, column=0, columnspan=4, sticky="nsew")
        self.scrollbar.config(command=self.command_canvas.yview)

        self.command_container = tk.Frame(self.command_canvas)
        self.command_canvas.create_window((0, 0), window=self.command_container, anchor="nw")

        self.command_container.bind(
            "<Configure>",
            lambda e: self.command_canvas.configure(scrollregion=self.command_canvas.bbox("all"))
        )

        self.command_entries = []
        self.type_entries = []
        self.description_entries = []

        self.load_commands_ui()

        self.add_command_button = ttk.Button(self.main_frame, text="Add command", command=self.add_command_ui)
        self.add_command_button.grid(row=3, column=0, columnspan=4, pady=10, padx=10, sticky="ew")

        self.save_button = ttk.Button(self.main_frame, text="Save", command=self.save_commands)
        self.save_button.grid(row=4, column=2, pady=10, padx=10, sticky="e")

        self.exit_button = ttk.Button(self.main_frame, text="Cancel", command=self.app.switch_to_workspace_frame)
        self.exit_button.grid(row=4, column=3, pady=10, padx=10, sticky="w")

    def add_form_ui(self):
        # New command input form at the top
        self.new_command_frame = tk.Frame(self.main_frame)
        self.new_command_frame.grid(row=1, column=0, columnspan=4, pady=10, padx=10, sticky="nsew")
        self.new_command_frame.grid_columnconfigure(0, weight=1)
        self.new_command_frame.grid_columnconfigure(1, weight=1)
        self.new_command_frame.grid_columnconfigure(2, weight=2)

        self.new_command_entry = ttk.Entry(self.new_command_frame, width=30)
        self.new_command_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.new_command_entry.insert(0, "Enter command")

        self.new_type_entry = ttk.Entry(self.new_command_frame, width=30)
        self.new_type_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.new_type_entry.insert(0, "Enter type")

        self.new_description_entry = ttk.Entry(self.new_command_frame, width=50)
        self.new_description_entry.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.new_description_entry.insert(0, "Enter description")

    def load_commands_ui(self):
        for widget in self.command_container.winfo_children():
            widget.destroy()

        self.command_entries.clear()
        self.type_entries.clear()
        self.description_entries.clear()

        for index, command in enumerate(self.commands):
            self.create_command_row(index, command)

    def create_command_row(self, index, command):
        command_entry = ttk.Entry(self.command_container, width=30)
        command_entry.grid(row=index, column=0, padx=5, pady=5, sticky="ew")
        command_entry.insert(0, command["command"])
        self.command_entries.append(command_entry)

        type_entry = ttk.Entry(self.command_container, width=30)
        type_entry.grid(row=index, column=1, padx=5, pady=5, sticky="ew")
        type_entry.insert(0, command["type"])
        self.type_entries.append(type_entry)

        description_entry = ttk.Entry(self.command_container, width=50)
        description_entry.grid(row=index, column=2, padx=5, pady=5, sticky="ew")
        description_entry.insert(0, command["description"])
        self.description_entries.append(description_entry)

        delete_button = ttk.Button(self.command_container, text="x", command=lambda idx=index: self.delete_command_ui(idx))
        delete_button.grid(row=index, column=3, padx=5, pady=5)

    def add_command_ui(self):
        command = {
            "command": self.new_command_entry.get(),
            "type": self.new_type_entry.get(),
            "description": self.new_description_entry.get()
        }
        self.commands.append(command)
        self.load_commands_ui()

    def delete_command_ui(self, index):
        del self.commands[index]
        self.load_commands_ui()
