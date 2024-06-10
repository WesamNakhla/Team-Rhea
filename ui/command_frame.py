import tkinter as tk
from tkinter import ttk, Scrollbar, VERTICAL, messagebox
import json
from logic.command_logic import CommandFrameLogic

class PlaceholderEntry(ttk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color="grey", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['foreground']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['foreground'] = self.placeholder_color

    def foc_in(self, *args):
        if self['foreground'] == self.placeholder_color:
            self.delete('0', 'end')
            self['foreground'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()

class CommandFrame(ttk.Frame, CommandFrameLogic):
    def __init__(self, parent, app):
        ttk.Frame.__init__(self, parent)
        CommandFrameLogic.__init__(self, self)
        self.parent = parent
        self.app = app  # Reference to the app for switching frames
        self.command_entries = []
        self.type_entries = []
        self.description_entries = []
        
        # Variables for width and height
        self.frame_width = 580
        self.frame_height = 500
        
        self.create_widgets()

        # Initialize command counts
        self.initial_commands_count = len(self.commands)
        self.deleted_commands_count = 0

    def create_widgets(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        frame = ttk.Frame(self, width=self.frame_width)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        title_label = ttk.Label(frame, text="Command Management", font=('Arial', 24))
        title_label.grid(row=0, column=0, pady=(20, 10), padx=20, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)  # Ensure the title is centered

        # Container frame to limit the width and center elements
        container_frame = ttk.Frame(frame)
        container_frame.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="n")
        container_frame.grid_columnconfigure(0, weight=1)

        header_frame = ttk.Frame(container_frame)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=1)

        ttk.Label(header_frame, text="Command", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Label(header_frame, text="Type", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(header_frame, text="Description", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        scroll_frame_border = ttk.Frame(container_frame, borderwidth=2, relief="solid", width=self.frame_width, height=self.frame_height)
        scroll_frame_border.grid(row=1, column=0, sticky="nsew")
        scroll_frame_border.grid_propagate(False)
        scroll_frame_border.grid_rowconfigure(0, weight=1)
        scroll_frame_border.grid_columnconfigure(0, weight=1)

        scroll_frame = ttk.Frame(scroll_frame_border)
        scroll_frame.grid(row=0, column=0, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(scroll_frame, height=self.frame_height)
        self.scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.load_commands_ui()

        button_frame = ttk.Frame(container_frame)
        button_frame.grid(row=2, column=0, pady=20, padx=20, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)

        ttk.Button(button_frame, text="Add Command", command=self.add_command_ui).grid(row=0, column=0, padx=5, pady=10)
        ttk.Button(button_frame, text="Save", command=self.save_commands).grid(row=0, column=1, padx=5, pady=10)
        ttk.Button(button_frame, text="Cancel", command=self.app.switch_to_workspace_frame).grid(row=0, column=2, padx=5, pady=10)

    def load_commands_ui(self):
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.destroy()

        self.command_entries.clear()
        self.type_entries.clear()
        self.description_entries.clear()

        for index, command in enumerate(self.commands):
            self.create_command_row(index, command)

    def create_command_row(self, index, command):
        row_frame = ttk.Frame(self.scrollable_frame)
        row_frame.grid(row=index, column=0, sticky="ew", padx=5, pady=5)

        # Determine if this is a custom command (empty command means it's a new custom command)
        if command["command"] == "":
            command_entry = ttk.Entry(row_frame, width=20)
            type_entry = ttk.Entry(row_frame, width=20)
            description_entry = ttk.Entry(row_frame, width=20)
        else:
            command_entry = ttk.Entry(row_frame, width=20)
            command_entry.insert(0, command["command"])
            type_entry = ttk.Entry(row_frame, width=20)
            type_entry.insert(0, command["type"])
            description_entry = ttk.Entry(row_frame, width=20)
            description_entry.insert(0, command["description"])

        command_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        type_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        description_entry.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        delete_button = ttk.Button(row_frame, text="X", command=lambda idx=index: self.delete_command_ui(idx), width=3)
        delete_button.grid(row=0, column=3, padx=5, pady=5)

        row_frame.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, weight=1)
        row_frame.grid_columnconfigure(2, weight=1)
        row_frame.grid_columnconfigure(3, weight=0)

        self.command_entries.append(command_entry)
        self.type_entries.append(type_entry)
        self.description_entries.append(description_entry)

    def add_command_ui(self):
        self.commands.append({
            "command": "",
            "type": "",
            "description": ""
        })
        self.load_commands_ui()
        self.after(100, lambda: self.canvas.yview_moveto(1))  # Scroll to the bottom after a short delay

    def delete_command_ui(self, index):
        self.deleted_commands_count += 1
        del self.commands[index]
        self.load_commands_ui()

    def save_commands(self):
        if self.deleted_commands_count > 0:
            confirm = tk.messagebox.askyesno("Confirm Deletion", f"{self.deleted_commands_count} commands will be deleted. Are you sure you want to proceed?")
            if not confirm:
                return

        commands_to_save = []
        for command_entry, type_entry, description_entry in zip(self.command_entries, self.type_entries, self.description_entries):
            command = {
                "command": command_entry.get(),
                "type": type_entry.get(),
                "description": description_entry.get()
            }
            commands_to_save.append(command)

        try:
            new_commands_count = len(commands_to_save) - self.initial_commands_count + self.deleted_commands_count

            with open('commands.json', 'w') as file:
                json.dump(commands_to_save, file, indent=4)

            messages = []
            if new_commands_count > 0:
                messages.append(f"{new_commands_count} commands have been added successfully.")
            if self.deleted_commands_count > 0:
                messages.append(f"{self.deleted_commands_count} commands have been deleted.")
                self.deleted_commands_count = 0

            if messages:
                tk.messagebox.showinfo("Success", "\n".join(messages))

            self.initial_commands_count = len(commands_to_save)  # Update initial count
            self.commands = commands_to_save  # Update current commands
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error saving commands: {e}")
