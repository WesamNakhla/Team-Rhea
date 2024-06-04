# located at logic/command_frame.py
import json
from tkinter import messagebox

class CommandFrameLogic:
    def __init__(self, parent):
        self.parent = parent
        self.commands = self.load_commands()

    def load_commands(self):
        try:
            with open('commands.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Error", "Commands file not found.")
            return []
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Error decoding the commands file.")
            return []

    def save_commands(self):
        with open('commands.json', 'w') as file:
            json.dump(self.commands, file, indent=4)

    def add_command(self, command):
        self.commands.append(command)
        self.save_commands()

    def delete_command(self, index):
        if index < len(self.commands):
            del self.commands[index]
            self.save_commands()

    def update_command(self, index, command):
        if index < len(self.commands):
            self.commands[index] = command
            self.save_commands()
