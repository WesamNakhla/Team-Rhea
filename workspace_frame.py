import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import time
import threading
import json
import re
import os

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
        self.file_label = ttk.Label(self, text="Memory Dump File:")
        self.file_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.file_entry = ttk.Entry(self, width=50)
        self.file_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")

        self.browse_button = ttk.Button(self, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=10, pady=5)

        # Populate command dropdown with descriptions
        command_descriptions = [f"{cmd['command']} - {cmd['description']}" for cmd in self.commands]
        self.command_dropdown = ttk.Combobox(self, values=command_descriptions, state="readonly")
        self.command_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="we")
        self.command_dropdown.current(0)

        self.run_button = ttk.Button(self, text="Run Command", command=self.run_command)
        self.run_button.grid(row=1, column=2, padx=10, pady=5)

        self.output_text = tk.Text(self, height=20, width=80)
        self.output_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

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

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

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
        file = self.file_entry.get().strip()
        selected_index = self.command_dropdown.current()
        if selected_index < 0:
            messagebox.showerror("Error", "Please select a command.")
            return
        
        selected_command = self.commands[selected_index]["command"]
        vol_path = r"C:\Projects\VolatilityGUI\volatility3-develop\vol.py"  # Adjust this path to your environment

        if not os.path.isfile(vol_path):
            messagebox.showerror("Error", f"Volatility script not found at: {vol_path}")
            return

        command = f"python {vol_path} -f {file} {selected_command}"
        print(f"Command to run: {command}")  # Debugging output
        self.run_volatility(command)

    def run_volatility(self, command):
        print(f"Running command: {command}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            self.output_text.delete(1.0, tk.END)
            if result.stderr:
                self.output_text.insert(tk.END, "\nError:\n" + result.stderr)
            self.output_text.insert(tk.END, result.stdout)
            findings = self.parse_output(result.stdout, command)
            self.display_findings(findings)
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
    app = WorkspaceFrame(root)
    app.pack(fill="both", expand=True)
    root.mainloop()
