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
        self.grid(sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.label = tk.Label(self.main_frame, text="Command Management", font=('Arial', 32))
        self.label.grid(row=0, column=0, pady=20, sticky="n")

        self.add_headers()

        self.command_frame = tk.Frame(self.main_frame)
        self.command_frame.grid(row=2, column=0, pady=10, sticky="nsew")
        self.command_frame.grid_columnconfigure(0, weight=1)
        self.command_frame.grid_rowconfigure(0, weight=1)

        self.scrollbar = Scrollbar(self.command_frame, orient=VERTICAL)
        self.scrollbar.grid(row=0, column=1, sticky='ns')

        self.command_canvas = tk.Canvas(self.command_frame, yscrollcommand=self.scrollbar.set)
        self.command_canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.config(command=self.command_canvas.yview)

        self.command_container = tk.Frame(self.command_canvas)
        self.command_canvas.create_window((0, 0), window=self.command_container, anchor="n")

        self.command_container.bind(
            "<Configure>",
            lambda e: self.command_canvas.configure(scrollregion=self.command_canvas.bbox("all"))
        )

        self.command_entries = []
        self.type_entries = []
        self.description_entries = []

        self.load_commands_ui()

        self.add_command_button = ttk.Button(self.main_frame, text="Add Command", command=self.add_command_ui)
        self.add_command_button.grid(row=3, column=0, pady=10, sticky="ew")

        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.grid(row=4, column=0, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        self.save_button = ttk.Button(self.button_frame, text="Save", command=self.save_commands)
        self.save_button.grid(row=0, column=1, padx=10, sticky="ew")

        self.exit_button = ttk.Button(self.button_frame, text="Cancel", command=self.app.switch_to_workspace_frame)
        self.exit_button.grid(row=0, column=0, padx=10, sticky="ew")

    def add_headers(self):
        self.header_frame = tk.Frame(self.main_frame)
        self.header_frame.grid(row=1, column=0, pady=10, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_columnconfigure(2, weight=1)
        self.header_frame.grid_columnconfigure(3, weight=1)

        self.new_command_label = tk.Label(self.header_frame, text="Enter command", font=('Arial', 16))
        self.new_command_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.new_type_label = tk.Label(self.header_frame, text="Enter type", font=('Arial', 16))
        self.new_type_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.new_description_label = tk.Label(self.header_frame, text="Enter description", font=('Arial', 16))
        self.new_description_label.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

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
            "command": "Enter command",
            "type": "Enter type",
            "description": "Enter description"
        }
        self.commands.append(command)
        self.load_commands_ui()
        self.command_canvas.after(100, lambda: self.command_canvas.yview_moveto(1))  # Scroll to the bottom after adding a new command

    def delete_command_ui(self, index):
        del self.commands[index]
        self.load_commands_ui()
