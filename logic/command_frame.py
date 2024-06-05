# logic/command_frame.py
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
        commands_to_save = []
        for command_entry, type_entry, description_entry in zip(self.parent.command_entries, self.parent.type_entries, self.parent.description_entries):
            command = {
                "command": command_entry.get(),
                "type": type_entry.get(),
                "description": description_entry.get()
            }
            commands_to_save.append(command)
        with open('commands.json', 'w') as file:
            json.dump(commands_to_save, file, indent=4)
        
        if len(commands_to_save) == 1:
            messagebox.showinfo("Success", "The command has been saved.")
        else:
            messagebox.showinfo("Success", "The commands have been saved.")