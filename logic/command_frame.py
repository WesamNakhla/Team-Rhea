import json
from tkinter import messagebox

class CommandFrameLogic:
    def __init__(self, parent):
        self.parent = parent
        self.commands = self.load_commands()
        self.initial_commands_count = len(self.commands)
        self.deleted_commands_count = 0

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
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
            return []

    def save_commands(self):
        if self.deleted_commands_count > 0:
            confirm = messagebox.askyesno("Confirm Deletion", f"{self.deleted_commands_count} commands will be deleted. Are you sure you want to proceed?")
            if not confirm:
                return

        commands_to_save = []
        for command_entry, type_entry, description_entry in zip(self.parent.command_entries, self.parent.type_entries, self.parent.description_entries):
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
                messagebox.showinfo("Success", "\n".join(messages))

            self.initial_commands_count = len(commands_to_save)  # Update initial count
            self.commands = commands_to_save  # Update current commands
        except Exception as e:
            messagebox.showerror("Error", f"Error saving commands: {e}")

    def delete_command(self, index):
        self.deleted_commands_count += 1
        del self.commands[index]
        self.parent.load_commands_ui()
