import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import time
import threading
import json
import re
import os
import datetime

class WorkspaceFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.command_tabs = {}  # Dictionary to store command titles and corresponding tabs
        self.commands = self.load_commands()  # Load commands from JSON
        self.init_ui()

    def load_commands(self):
        try:
            with open('dummy_commands.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Error", "Commands file not found.")
            return []
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Error decoding the commands file.")
            return []

    def init_ui(self):
        # Using grid layout for better control

        # Update file_label text to show the loaded file
        self.file_label = ttk.Label(self, text="Loaded file: No file loaded", anchor="w")
        self.file_label.grid(row=0, column=0, sticky="wew", padx=10, pady=5)
        self.grid_columnconfigure(0, weight=1)  # Make column expandable

        # Choose command label
        self.command_label = ttk.Label(self, text="Choose command:")
        self.command_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Command dropdown
        self.command_options = ["-choose command-", "Custom"] + [cmd['command'] for cmd in self.commands]
        self.command_var = tk.StringVar()
        self.command_dropdown = ttk.Combobox(self, values=self.command_options, textvariable=self.command_var, state="readonly")
        self.command_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="we")
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

    def get_volatility_path(self):
        # Load the settings from the settings.json file
        with open('settings.json', 'r') as file:
            settings = json.load(file)
        
        # Retrieve the base path for volatility from the settings
        base_path = settings.get('volatility_path', '')

        # Construct the full path to the vol.py file
        full_path = os.path.join(base_path, 'vol.py')
        
        # Convert path to a format suitable for Python scripts
        full_path = full_path.replace('/', os.sep)
        
        return full_path

    def update_loaded_file_label(self):
        print("Updating loaded file label")
        full_path = self.parent.loaded_file
        filename_only = os.path.basename(full_path) if full_path else "No file loaded"
        self.file_label.config(text=f"Loaded file: {filename_only}")

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
        # Use the loaded_file from the MainApplication
        file = self.parent.loaded_file
        if not file:  # Check if the file is loaded
            messagebox.showerror("Error", "No file loaded.")
            return

        selected_index = self.command_dropdown.current()
        if selected_index < 0:
            messagebox.showerror("Error", "Please select a command.")
            return

        selected_command = self.commands[selected_index]["command"]
        vol_path = self.get_volatility_path()

        if not os.path.isfile(vol_path):
            messagebox.showerror("Error", f"Volatility script not found at: {vol_path}")
            return

        command = f"python {vol_path} -f {file} {selected_command}"
        self.run_volatility(command)

    def run_volatility(self, command):
        print(f"Running command: {command}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            findings = result.stdout if result.stdout else "No output received."

            if result.stderr:
                findings += "\nError:\n" + result.stderr

            self.add_tab(self.unique_tab_title(command.split()[-1]), findings)  # Use the command name as the tab title
            self.parent.commands_used.append(command)
            self.parent.scan_result = findings  # Store the results
        except Exception as e:
            messagebox.showerror("Error", str(e))
            print(f"Exception: {e}")

    def parse_output(self, output, command):
        findings = []
        if "pslist" in command:
            findings = self.parse_pslist(output)
        elif "pstree" in command:
            findings = self.parse_pstree(output)
        elif "cmdline" in command:  # Handle cmdline output
            findings = self.parse_cmdline(output)
        return findings

    def parse_pslist(self, output):
        findings = []
        lines = output.splitlines()
        for line in lines:
            if "System" not in line and re.search(r"\b\d+\b", line):
                findings.append(line)
        return findings

    def parse_pstree(self, output):
        findings = []
        lines = output.splitlines()
        for line in lines:
            if "System" not in line and re.search(r"\b\d+\b", line):
                findings.append(line)
        return findings

    def parse_cmdline(self, output):
        findings = []
        lines = output.splitlines()
        for line in lines:
            if line.strip():  # Add any non-empty line
                findings.append(line)
        return findings

    def display_findings(self, findings):
        if findings:
            self.output_text.insert(tk.END, "Findings:\n")
            for finding in findings:
                self.output_text.insert(tk.END, finding + "\n")
            self.output_text.insert(tk.END, "\nSuggestions:\n")
            self.output_text.insert(tk.END, "1. Investigate the processes listed above for suspicious activity.\n")
            self.output_text.insert(tk.END, "2. Use additional plugins for more detailed analysis.\n")
        else:
            self.output_text.insert(tk.END, "No suspicious findings detected.\n")

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

    def add_tab(self, title, output):
        if title in self.command_tabs:
            # Focus the existing tab if it's already open
            self.tab_control.select(self.command_tabs[title])
        else:
            # Create a new tab for new command output
            new_tab = ttk.Frame(self.tab_control)
            text_output = tk.Text(new_tab, height=15, width=50, selectbackground="yellow", selectforeground="black")
            text_output.pack(expand=1, fill='both')
            text_output.insert(tk.END, output)

            # Add the new tab to the notebook
            self.tab_control.add(new_tab, text=title)
            self.command_tabs[title] = new_tab  # Store reference to the tab

    def unique_tab_title(self, base_title):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        return f"{base_title} - {current_time}"

    def highlight_text(self, color):
        try:
            selected_tab = self.tab_control.nametowidget(self.tab_control.select())
            text_widget = selected_tab.winfo_children()[0]
            start = text_widget.index("sel.first")
            end = text_widget.index("sel.last")
            text_widget.tag_add(color, start, end)
            text_widget.tag_config(color, background=color)
            self.parent.highlights.append((text_widget.get(start, end), color))  # Store the highlight
        except tk.TclError:
            print("No text selected")

    def remove_highlight(self):
        try:
            selected_tab = self.tab_control.nametowidget(self.tab_control.select())
            text_widget = selected_tab.winfo_children()[0]
            start = text_widget.index("sel.first")
            end = text_widget.index("sel.last")
            for tag in text_widget.tag_names():
                text_widget.tag_remove(tag, start, end)
        except tk.TclError:
            print("No text selected")

    def apply_font_settings(self, font_size):
        # Apply font settings to relevant widgets
        self.file_label.config(font=('Arial', font_size))
        self.command_label.config(font=('Arial', font_size))
        self.command_info_label.config(font=('Arial', font_size))
        for tab in self.tab_control.tabs():
            text_widget = self.tab_control.nametowidget(tab).winfo_children()[0]
            text_widget.config(font=('Arial', font_size))

    def load_previous_commands(self):
        for command in self.parent.commands_used:
            self.add_tab(self.unique_tab_title(command.split()[-1]), "Loaded from session: " + command)
        for text, color in self.parent.highlights:
            self.highlight_text_from_session(text, color)

    def highlight_text_from_session(self, text, color):
        for tab in self.command_tabs.values():
            text_widget = tab.winfo_children()[0]
            start = "1.0"
            while True:
                start = text_widget.search(text, start, stopindex=tk.END)
                if not start:
                    break
                end = f"{start}+{len(text)}c"
                text_widget.tag_add(color, start, end)
                text_widget.tag_config(color, background=color)
                start = end

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x600")
    app = WorkspaceFrame(root)
    app.pack(fill="both", expand=True)
    root.mainloop()
