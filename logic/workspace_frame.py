import concurrent.futures
import json
import os
import re
import subprocess
import textwrap
import threading
import time
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser

class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class LineNumberCanvas(tk.Canvas):
    def __init__(self, master, text_widget, start_line=5, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        self.start_line = start_line
        self.text_widget.bind("<KeyRelease>", self.on_key_release)
        self.text_widget.bind("<MouseWheel>", self.on_scroll)

        self.text_widget.bind("<KeyRelease>", self.on_content_change)
        self.text_widget.bind("<MouseWheel>", self.on_content_change)
        self.text_widget.bind("<<Change>>", self.on_content_change)
        self.text_widget.bind("<Configure>", self.on_content_change)
        self.text_widget.bind("<Button-1>", self.on_content_change)

        # Synchronize scrolling
        self.text_widget.bind("<MouseWheel>", self.on_text_widget_scroll)
        self.text_widget.bind("<Button-4>", self.on_text_widget_scroll)
        self.text_widget.bind("<Button-5>", self.on_text_widget_scroll)
        self.text_widget.bind("<KeyPress>", self.on_text_widget_scroll)
        self.text_widget.bind("<Motion>", self.on_text_widget_scroll)
        self.text_widget.bind("<ButtonRelease-1>", self.on_text_widget_scroll)
        self.text_widget.bind("<<ScrollbarVisible>>", self.on_text_widget_scroll)

        self.update_line_numbers()

    def on_content_change(self, event=None):
        self.update_line_numbers()

    def on_text_widget_scroll(self, event):
        self.update_line_numbers()
        return "break"

    def on_mouse_scroll(self, event):
        self.text_widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.update_line_numbers()
        return "break"

    def on_scroll(self, event=None):
        self.update_line_numbers()

    def on_key_release(self, event=None):
        self.update_line_numbers()

    def update_line_numbers(self):
        self.delete("all")
        # Calculate the starting line index
        visible_start_index = self.text_widget.index("@0,0")
        line_index = int(visible_start_index.split(".")[0])
        line_count = max(1, line_index - self.start_line + 1)

        i = self.text_widget.index(f"{visible_start_index}")

        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            if int(i.split(".")[0]) >= self.start_line:
                self.create_text(2, y, anchor="nw", text=str(line_count), font=("Arial", 10), fill="white")
                line_count += 1
            i = self.text_widget.index(f"{i}+1line")

    def attach(self, widget):
        widget.bind("<MouseWheel>", self.on_mouse_scroll)
        widget.bind("<Button-4>", self.on_mouse_scroll)
        widget.bind("<Button-5>", self.on_mouse_scroll)

    def on_mouse_scroll(self, event):
        self.update_line_numbers()

class ToolTip(object):
    def __init__(self, widget, text):
        self.widget = widget
        self.tipwindow = None
        self.text = text
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        "Display text in tooltip window"
        if self.tipwindow or not self.text:
            return
        # print("Tooltip text:", self.text)  # Debugging: Check if the text is correctly passed
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", foreground="#000000",  # Ensure text is black on light yellow background
                         relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1, fill=tk.BOTH, expand=True)



    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class WorkspaceFrameLogic:
    def __init__(self, parent):
        self.parent = parent
        self.command_tabs = {}  # Dictionary to store command titles and corresponding tabs
        self.commands = self.load_commands()  # Load commands from JSON
        self.command_details = {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)  # Initialize ThreadPoolExecutor
        self.running_process = None  # Store the running process
        self.futures = []  # Initialize the futures list

    def update_loaded_file_label(self, loaded_files):
        full_paths = loaded_files
        filenames_only = [os.path.basename(full_path) for full_path in full_paths]
        if len(filenames_only) > 1:
            self.parent.show_sidebar(filenames_only)
        else:
            self.parent.hide_sidebar()
        for filename in filenames_only:
            print(f"Setting file label to: {filename}")  # Debug statement

    def add_custom_plugin(self):
        file_path = filedialog.askopenfilename(title="Select Custom Plugin", filetypes=[("Python Files", "*.py")])
        if file_path:
            plugin_name = os.path.basename(file_path)
            if plugin_name.endswith('.py'):
                plugin_name = plugin_name[:-3]  # Remove the .py extension
            custom_plugin_details = {
                "type": "Custom Plugin",
                "command": plugin_name,
                "description": f"This is your custom plugin {plugin_name}"
            }
            self.commands.append(custom_plugin_details)
            command_options = ["-choose command-", "Custom"] + [cmd['command'] for cmd in self.commands]
            self.parent.update_command_dropdown(command_options)  # Pass command_options to parent method

    def update_command_dropdown(self):
        command_options = ["-choose command-", "Custom"] + [cmd['command'] for cmd in self.commands]
        self.parent.update_command_dropdown(command_options)

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

    def search_text(self):
        search_term = self.parent.search_entry.get()
        if not search_term:
            return

        selected_tab = self.parent.tab_control.nametowidget(self.parent.tab_control.select())
        text_widget = selected_tab.winfo_children()[0]

        start = "1.0"
        while True:
            start = text_widget.search(search_term, start, stopindex=tk.END)
            if not start:
                break
            end = f"{start}+{len(search_term)}c"
            text_widget.tag_add('search_highlight', start, end)
            text_widget.tag_config('search_highlight', background='yellow')
            start = end

    def export_results(self):
        self.parent.switch_to_export_frame()  # Call the function to switch frames

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

    def update_command_info(self, event):
        selected_command = self.parent.command_var.get()
        if selected_command == "Custom":
            self.parent.custom_command_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
            self.parent.custom_command_entry.grid(row=2, column=1, padx=10, pady=5, sticky="we")
            self.parent.command_info_label.config(text="Enter your custom command.")
            self.parent.run_command_button.config(state=tk.NORMAL)
        elif selected_command == "-choose command-":
            self.parent.custom_command_label.grid_forget()
            self.parent.custom_command_entry.grid_forget()
            self.parent.command_info_label.config(text="Select a command to see the description and type.")
            self.parent.run_command_button.config(state=tk.DISABLED)
        else:
            self.parent.custom_command_label.grid_forget()
            self.parent.custom_command_entry.grid_forget()
            index = self.parent.command_dropdown.current() - 2  # Adjust the index
            if index >= 0 and index < len(self.commands):
                command_info = self.commands[index]
                wrapped_text = textwrap.fill(f"Type: {command_info['type']}\nDescription: {command_info['description']}", width=50)
                self.parent.command_info_label.config(text=wrapped_text)
                self.parent.run_command_button.config(state=tk.NORMAL)

    def run_command(self):
        if not self.parent.selected_file:
            messagebox.showerror("Error", "No file selected.")
            return

        selected_index = self.parent.command_dropdown.current()
        command = None
        if selected_index == 1:  # Custom command
            command = self.parent.custom_command_entry.get().strip()
        elif selected_index > 1:  # Predefined command selected
            command_index = selected_index - 2  # Adjust index for 'Choose command...' and 'Custom'
            if command_index < len(self.commands):
                command = self.commands[command_index]['command']

        if not command:
            messagebox.showerror("Error", "Please select a command or enter a custom command.")
            return

        command_parameters = self.parent.parameter_entry.get().strip()  # Retrieve parameters from the user input
        file_path = self.parent.selected_file
        vol_path = self.get_volatility_path()

        # Combine the volatility script, file path, command, and user-entered parameters
        full_command = f"python {vol_path} -f {file_path} {command} {command_parameters}"
        print(f"Running command: {full_command}")

        # Execute the command in a separate thread using ThreadPoolExecutor
        future = self.executor.submit(self.execute_command, full_command)  # Pass the full command to execution
        future.add_done_callback(lambda f, cmd=command, fp=file_path: self.command_finished(f, cmd, fp))

    def command_finished(self, future, command, file_path):
        try:
            if future.done():
                command_result, findings = future.result()
                self.parent.after(0, self.add_tab, file_path, command_result, findings)
                tab_title = f"{os.path.basename(file_path)} {command_result}"
                self.command_details[tab_title] = {
                    "command": command_result,
                    "output": findings,
                    "highlights": []  # Placeholder for any highlights data
                }
                self.check_all_commands_finished()
        except Exception as e:
            messagebox.showerror("Error", f"Error executing command {command}: {str(e)}")
            print(f"Exception when processing command result: {e}")

    def execute_command(self, full_command):
        # Run the command using subprocess
        process = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        stdout, stderr = process.communicate()

        # Handle output and errors
        findings = stdout if stdout else "No output received."
        if stderr:
            findings += "\nError:\n" + stderr

        return full_command, findings

    def check_all_commands_finished(self):
        if all(f.done() for f in self.futures):  # Check if all futures are done
            print("All commands have finished executing.")
            self.prepare_export_data()  # Now prepare export data

    def run_volatility(self, command):
        print(f"Running command: {command}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            findings = result.stdout if result.stdout else "No output received."
            if result.stderr:
                findings += "\nError:\n" + result.stderr

            command_key = command.split()[-1]  # Simple command name extraction
            self.command_details[command_key] = {
                "command": command,
                "output": findings,
                "highlights": []  # Make sure to populate highlights elsewhere
            }
            print(f"Command details updated: {self.command_details[command_key]}")
            self.add_tab(command_key, findings)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            print(f"Exception when running command: {e}")

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
            self.parent.output_text.insert(tk.END, "Findings:\n")
            for finding in findings:
                self.parent.output_text.insert(tk.END, finding + "\n")
            self.parent.output_text.insert(tk.END, "\nSuggestions:\n")
            self.parent.output_text.insert(tk.END, "1. Investigate the processes listed above for suspicious activity.\n")
            self.parent.output_text.insert(tk.END, "2. Use additional plugins for more detailed analysis.\n")
        else:
            self.parent.output_text.insert(tk.END, "No suspicious findings detected.\n")

    def show_alert(self, command):
        tk.messagebox.showinfo("Alert", f"The command '{command}' has already been run.")

    def start_loading(self, command):
        self.parent.progress['value'] = 0
        self.parent.update_idletasks()
        threading.Thread(target=self.simulate_long_running_task, args=(command,)).start()

    def simulate_long_running_task(self, command):
        for i in range(30):
            time.sleep(0.1)
            self.parent.progress['value'] += 3.33
            self.parent.update_idletasks()
        self.parent.progress['value'] = 100
        self.parent.update_idletasks()
        self.parent.after(0, self.add_tab, command)
        time.sleep(0.5)  # Brief pause before resetting the progress bar
        self.parent.progress['value'] = 0
        self.parent.update_idletasks()

    def add_tab(self, file_path, command, output):
        tab_title = f"{os.path.basename(file_path)} {command}"
        if tab_title in self.command_tabs:
            # Focus the existing tab if it's already open
            self.parent.tab_control.select(self.command_tabs[tab_title])
        else:
            # If the tab does not exist, create a new one
            new_tab = ttk.Frame(self.parent.tab_control)

            # Create the Text widget
            text_output = CustomText(new_tab, height=15, width=50, selectbackground="yellow", selectforeground="black")

            # Add a vertical scrollbar
            v_scrollbar = tk.Scrollbar(new_tab, orient="vertical", command=text_output.yview)
            v_scrollbar.pack(side="right", fill="y")
            text_output.config(yscrollcommand=v_scrollbar.set)

            # Pack the Text widget
            text_output.pack(side="right", fill="both", expand=True)

            # Add line number canvas
            line_number_canvas = LineNumberCanvas(new_tab, text_output, start_line=5, width=30)
            line_number_canvas.pack(side="left", fill="y")

            # Attach the line number canvas to the text widget
            line_number_canvas.attach(text_output)

            # Insert the output text
            text_output.insert(tk.END, output)

            # Ensure line numbers update immediately
            text_output.event_generate("<<Change>>")

            # Add the new tab to the notebook with the command as its title
            self.parent.tab_control.add(new_tab, text=tab_title)
            self.command_tabs[tab_title] = new_tab  # Store the reference to the new tab

            # Bind tab movement
            self.parent.tab_control.bind("<ButtonPress-1>", self.on_tab_click)
            self.parent.tab_control.bind("<B1-Motion>", self.on_tab_drag)

    def show_close_button(self, tab):
        close_button = ttk.Button(tab, text="Close Tab", command=lambda: self.close_tab(tab))
        close_button.pack(side="top", anchor="ne", pady=5, padx=5)

    def close_tab(self, tab):
        tab_title = self.parent.tab_control.tab(tab, "text")
        self.parent.tab_control.forget(tab)
        del self.command_tabs[tab_title]

    def close_current_tab(self):
        current_tab = self.parent.tab_control.select()
        if current_tab:
            self.close_tab(current_tab)

    def choose_highlight_color(self):
        color_code = colorchooser.askcolor(title="Choose highlight color")
        if color_code:
            self.highlight_text(color_code[1])

    def highlight_text(self, color):
        try:
            selected_tab = self.parent.tab_control.nametowidget(self.parent.tab_control.select())
            text_widget = selected_tab.winfo_children()[0]
            start = text_widget.index("sel.first")
            end = text_widget.index("sel.last")
            text_widget.tag_add(color, start, end)
            text_widget.tag_config(color, background=color)
            self.parent.highlights.append((color, start, end))  # Store the highlight without text

            # Store the highlight details for export
            title = self.parent.tab_control.tab(selected_tab, "text")
            if title in self.command_details:
                self.command_details[title]["highlights"].append({
                    "color": color,
                    "start": start,
                    "end": end
                })
            else:
                self.command_details[title] = {
                    "command": title,
                    "highlights": [{
                        "color": color,
                        "start": start,
                        "end": end
                    }]
                }
        except tk.TclError:
            print("No text selected")

    def remove_highlight(self):
        try:
            selected_tab = self.parent.tab_control.nametowidget(self.parent.tab_control.select())
            text_widget = selected_tab.winfo_children()[0]
            start = text_widget.index("sel.first")
            end = text_widget.index("sel.last")
            for tag in text_widget.tag_names():
                text_widget.tag_remove(tag, start, end)
        except tk.TclError:
            print("No text selected")

    def apply_font_settings(self, font_size):
        # Apply font settings to relevant widgets
        self.parent.file_label.config(font=('Arial', font_size))
        self.parent.command_label.config(font=('Arial', font_size))
        self.parent.command_info_label.config(font=('Arial', font_size))
        for tab in self.parent.tab_control.tabs():
            text_widget = self.parent.tab_control.nametowidget(tab).winfo_children()[0]

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

    def prepare_export_data(self):
        print("Preparing export data...")
        if self.parent.selected_file:
            export_data = {
                "memory_dump_file": self.parent.selected_file,  # Use the selected file
                "commands": [
                    {
                        "command": cmd["command"],
                        "highlights": cmd.get("highlights", []),
                        "output_file": f"{cmd['command'].replace('.', '_')}.txt"  # Ensure output_file is included
                    }
                    for cmd in self.command_details.values()
                ]
            }
            print(f"Export data collected: {export_data}")
            return export_data
        else:
            print("No loaded file or command data found.")
            return {}

    def get_export_data(self):
        return self.prepare_export_data()

    def on_tab_click(self, event):
        self._drag_data = {"x": event.x, "y": event.y}

    def on_tab_drag(self, event):
        new_index = self.parent.tab_control.index(f"@{event.x},{event.y}")
        if new_index != self.parent.tab_control.index("current"):
            self.parent.tab_control.insert(new_index, self.parent.tab_control.select())
