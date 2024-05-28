import tkinter as tk
from tkinter import ttk
import time
import threading
import json

class CombinedFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.command_tabs = {}  # Dictionary to store command titles and corresponding tabs
        self.commands = self.load_commands()  # Load commands from JSON
        self.init_ui()

    def load_commands(self):
        with open('dummy_commands.json', 'r') as file:
            return json.load(file)

    def init_ui(self):
        # Using grid layout for better control

        # File loaded label
        self.file_label = ttk.Label(self, text="Loaded file: memory_dummy.DMP")
        self.file_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Choose command label
        self.command_label = ttk.Label(self, text="Choose command:")
        self.command_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Command dropdown
        self.command_options = ["-choose command-", "Custom"] + [command['command'] for command in self.commands]
        self.command_var = tk.StringVar()
        self.command_dropdown = ttk.Combobox(self, values=self.command_options, textvariable=self.command_var, state="readonly")
        self.command_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.command_dropdown.bind("<<ComboboxSelected>>", self.update_command_info)

        # Execute command button
        self.run_command_button = ttk.Button(self, text="Execute Command", command=self.run_command)
        self.run_command_button.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        # Command description label
        self.command_info_label = ttk.Label(self, text="Select a command to see the description and type.")
        self.command_info_label.grid(row=1, column=3, padx=10, pady=5, sticky="w")

        # Custom command label and entry
        self.custom_command_label = ttk.Label(self, text="Custom command:")
        self.custom_command_entry = ttk.Entry(self)

        # Initially hide the custom command entry
        self.custom_command_label.grid_forget()
        self.custom_command_entry.grid_forget()

        # OutputFrame UI elements
        self.tab_control = ttk.Notebook(self)
        self.tab_control.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        # Highlight buttons
        self.highlight_frame = tk.Frame(self)
        self.highlight_frame.grid(row=4, column=0, columnspan=4, pady=5, sticky="w")

        self.highlight_button_red = tk.Button(self.highlight_frame, text="A", fg="red", command=lambda: self.highlight_text('red'))
        self.highlight_button_red.pack(side="left", padx=5, pady=5)

        self.highlight_button_green = tk.Button(self.highlight_frame, text="A", fg="green", command=lambda: self.highlight_text('green'))
        self.highlight_button_green.pack(side="left", padx=5, pady=5)

        self.highlight_button_orange = tk.Button(self.highlight_frame, text="A", fg="orange", command=lambda: self.highlight_text('orange'))
        self.highlight_button_orange.pack(side="left", padx=5, pady=5)

        self.remove_highlight_button = tk.Button(self.highlight_frame, text="Remove Highlight", command=self.remove_highlight)
        self.remove_highlight_button.pack(side="left", padx=5, pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=100, mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        # Configure grid to expand correctly
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(3, weight=1)

    def update_command_info(self, event):
        selected_command = self.command_var.get()
        if selected_command == "-choose command-":
            self.command_info_label.config(text="Select a command to see the description and type.")
            self.run_command_button.config(state=tk.DISABLED)
        elif selected_command == "Custom":
            self.command_info_label.config(text="Enter your custom command.")
            self.run_command_button.config(state=tk.NORMAL)
        else:
            for command in self.commands:
                if command['command'] == selected_command:
                    self.command_info_label.config(text=f"Type: {command['type']}\nDescription: {command['description']}")
                    self.run_command_button.config(state=tk.NORMAL)
                    break

        if selected_command == "Custom":
            self.custom_command_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
            self.custom_command_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        else:
            self.custom_command_label.grid_forget()
            self.custom_command_entry.grid_forget()

    def run_command(self):
        command = self.custom_command_entry.get() if self.command_var.get() == "Custom" else self.command_var.get()
        if command == "-choose command-":
            tk.messagebox.showerror("Error", "Please choose a valid command.")
            return

        # Check if command has already been run
        if command in self.command_tabs:
            self.show_alert(command)
            self.tab_control.select(self.command_tabs[command])
        else:
            print(f"Executing command: {command}")
            self.start_loading(command)

    def show_alert(self, command):
        tk.messagebox.showinfo("Alert", f"The command '{command}' has already been run.")

    def start_loading(self, command):
        self.progress['value'] = 0
        self.update_idletasks()
        threading.Thread(target=self.simulate_long_running_task, args=(command,)).start()

    def simulate_long_running_task(self, command):
        for i in range(30):
            time.sleep(0.1)
            self.progress['value'] += 3.33
            self.update_idletasks()
        self.progress['value'] = 100
        self.update_idletasks()
        self.parent.after(0, self.add_tab, command)
        time.sleep(0.5)  # Brief pause before resetting the progress bar
        self.progress['value'] = 0
        self.update_idletasks()

    def add_tab(self, title):
        new_tab = ttk.Frame(self.tab_control)
        text_output = tk.Text(new_tab, height=15, width=50, selectbackground="yellow", selectforeground="black")
        text_output.pack(expand=1, fill='both')

        # Read the content of dummy_output.txt
        with open('dummy_output.txt', 'r') as file:
            content = file.read()

        text_output.insert(tk.END, content)

        self.tab_control.add(new_tab, text=title)
        self.command_tabs[title] = new_tab  # Store reference to the tab

    def highlight_text(self, color):
        try:
            selected_tab = self.tab_control.nametowidget(self.tab_control.select())
            text_widget = selected_tab.winfo_children()[0]
            start = text_widget.index("sel.first")
            end = text_widget.index("sel.last")
            text_widget.tag_add(color, start, end)
            text_widget.tag_config(color, background=color)
        except tk.TclError:
            print("No text selected")

    def remove_highlight(self):
        try:
            selected_tab = self.tab_control.nametowidget(self.tab_control.select())
            text_widget = selected_tab.winfo_children()[0]
            start = text_widget.index("sel.first")
            end = text_widget.index("sel.last")
            for tag in text_widget.tag_names(start):
                text_widget.tag_remove(tag, start, end)
        except tk.TclError:
            print("No text selected")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x600")
    app = CombinedFrame(root)
    app.pack(fill="both", expand=True)
    root.mainloop()
