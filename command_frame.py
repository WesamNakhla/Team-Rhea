import tkinter as tk
from tkinter import ttk

class CommandFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.option_label = ttk.Label(self, text="Select an Option")
        self.option_label.pack(pady=10)

        self.option_menu = ttk.Combobox(self, values=["Option 1", "Option 2", "Option 3"])
        self.option_menu.pack(pady=5)

        self.option1_radio = ttk.Radiobutton(self, text="Option 1", value=1)
        self.option1_radio.pack(pady=2)

        self.option2_radio = ttk.Radiobutton(self, text="Option 2", value=2)
        self.option2_radio.pack(pady=2)

        self.option3_radio = ttk.Radiobutton(self, text="Option 3", value=3)
        self.option3_radio.pack(pady=2)

        self.command_entry_label = ttk.Label(self, text="Profile text or command parameters:")
        self.command_entry_label.pack(pady=5)

        self.command_entry = ttk.Entry(self)
        self.command_entry.pack(pady=5)

        self.run_command_button = ttk.Button(self, text="Run Command", command=self.run_command)
        self.run_command_button.pack(pady=10)

    def run_command(self):
        # Dummy function for running command
        print("Command executed!")
