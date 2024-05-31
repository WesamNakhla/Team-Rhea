import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import time
import threading
import json
import re
import os
import textwrap

class LineNumberCanvas(tk.Canvas):
    def __init__(self, master, text_widget, start_line=5, **kwargs): 
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        self.start_line = start_line
        self.text_widget.bind("<KeyRelease>", self.on_key_release)
        self.text_widget.bind("<MouseWheel>", self.on_scroll)
        self.update_line_numbers()

    def on_key_release(self, event=None):
        self.update_line_numbers()

    def on_scroll(self, event=None):
        self.update_line_numbers()

    def update_line_numbers(self):
        self.delete("all")
        i = self.text_widget.index(f"{self.start_line}.0")
        line_count = 1  # Start line count from 1
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            self.create_text(2, y, anchor="nw", text=line_count, font=("Arial", 10), fill="white")
            i = self.text_widget.index(f"{i}+1line")
            line_count += 1

class WorkspaceFrame(tk.Frame):
    def __init__(self, parent, switch_frame_callback):
        super().__init__(parent)
        self.parent = parent
        self.switch_frame_callback = switch_frame_callback  # Callback to switch frames
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

        # Kill command button
        self.kill_command_button = ttk.Button(self, text="\u25A0 Kill", command=self.run_command)
        self.kill_command_button.grid(row=1, column=4, padx=(10, 10), pady=5, sticky="w")
        
        # Command description label
        self.command_info_label = ttk.Label(self, text="Select a command to see the description and type.", width=50, anchor="w", wraplength=400)
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
        self.highlight_frame.grid(row=4, column=0, columnspan=4, pady=5, sticky="we")

        self.highlight_button_red = tk.Button(self.highlight_frame, text="\U0001F58D", fg="white", bg="red", command=lambda: self.highlight_text('red'))
        self.highlight_button_red.pack(side="left", padx=5, pady=5)

        self.highlight_button_green = tk.Button(self.highlight_frame, text="\U0001F58D", fg="white", bg="green", command=lambda: self.highlight_text('green'))
        self.highlight_button_green.pack(side="left", padx=5, pady=5)

        self.highlight_button_orange = tk.Button(self.highlight_frame, text="\U0001F58D", fg="white", bg="orange", command=lambda: self.highlight_text('orange'))
        self.highlight_button_orange.pack(side="left", padx=5, pady=5)

        self.remove_highlight_button = ttk.Button(self.highlight_frame, text="Remove Highlight", command=self.remove_highlight)
        self.remove_highlight_button.pack(side="left", padx=5, pady=5)

        # Export button with unicode icon
        self.export_button = ttk.Button(self.highlight_frame, text="\u23CF Export", command=self.export_results)
        self.export_button.pack(side="right", padx=5, pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=100, mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        # Configure grid to expand correctly
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(3, weight=1)

    def export_results(self):
        self.switch_frame_callback()  # Call the function to switch frames

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
        if selected_command == "Custom":
            self.custom_command_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
            self.custom_command_entry.grid(row=2, column=1, padx=10, pady=5, sticky="we")
            self.command_info_label.config(text="Enter your custom command.")
            self.run_command_button.config(state=tk.NORMAL)
        elif selected_command == "-choose command-":
            self.custom_command_label.grid_forget()
            self.custom_command_entry.grid_forget()
            self.command_info_label.config(text="Select a command to see the description and type.")
            self.run_command_button.config(state=tk.DISABLED)
        else:
            self.custom_command_label.grid_forget()
            self.custom_command_entry.grid_forget()
            index = self.command_dropdown.current() - 2  # Adjust the index
            if index >= 0 and index < len(self.commands):
                command_info = self.commands[index]
                wrapped_text = textwrap.fill(f"Type: {command_info['type']}\nDescription: {command_info['description']}", width=50)
                self.command_info_label.config(text=wrapped_text)
                self.run_command_button.config(state=tk.NORMAL)

    def run_command(self):
        file_path = self.parent.loaded_file
        if not file_path:
            messagebox.showerror("Error", "No file loaded.")
            return

        selected_index = self.command_dropdown.current()
        if selected_index <= 1:  # 'Choose command...' or 'Custom'
            if selected_index == 1 and self.custom_command_entry.get().strip():
                command = self.custom_command_entry.get().strip()
            else:
                messagebox.showerror("Error", "Please select a command or enter a custom command.")
                return
        else:
            command_index = selected_index - 2  # Adjust index for 'Choose command...' and 'Custom'
            if command_index < len(self.commands):
                command = self.commands[command_index]['command']
            else:
                messagebox.showerror("Error", "Selected command index is out of range.")
                return

        # Check if the command has already been run (tab exists)
        if command in self.command_tabs:
            self.tab_control.select(self.command_tabs[command])  # Focus the existing tab
            messagebox.showinfo("Info", f"The command '{command}' has already been run.")
            return

        # Continue running the command if not already executed
        self.execute_command(file_path, command)

    def execute_command(self, file_path, command):
        vol_path = self.get_volatility_path()
        if not os.path.isfile(vol_path):
            messagebox.showerror("Error", f"Volatility script not found at: {vol_path}")
            return

        full_command = f"python {vol_path} -f {file_path} {command}"
        self.run_volatility(full_command)

    def run_volatility(self, command):
        print(f"Running command: {command}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            findings = result.stdout if result.stdout else "No output received."

            if result.stderr:
                findings += "\nError:\n" + result.stderr

            # Directly use the command name for the tab title
            self.add_tab(command.split()[-1], findings)  # Assumes command.split()[-1] gives a simplified command identifier
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

    def add_tab(self, command, output):
        # Check if the tab for this command already exists
        if command in self.command_tabs:
            # If the tab exists, focus it and notify the user
            self.tab_control.select(self.command_tabs[command])
            messagebox.showinfo("Info", f"The command '{command}' has already been run.")
        else:
            # If the tab does not exist, create a new one
            new_tab = ttk.Frame(self.tab_control)
            text_output = tk.Text(new_tab, height=15, width=50, selectbackground="yellow", selectforeground="black")
            text_output.pack(expand=1, fill='both')
            text_output.insert(tk.END, output)
            
            # Add the new tab to the notebook with the command as its title
            self.tab_control.add(new_tab, text=command)
            self.command_tabs[command] = new_tab  # Store the reference to the new tab
            # Add line number canvas
            line_number_canvas = LineNumberCanvas(new_tab, text_output, start_line=5, width=30)  
            line_number_canvas.pack(side="left", fill="y")
            text_output.pack(side="right", fill="both", expand=True)  

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
    def switch_to_export_frame():
        print("Switch to export frame")

    app = WorkspaceFrame(root, switch_to_export_frame)
    app.pack(fill="both", expand=True)
    root.mainloop()