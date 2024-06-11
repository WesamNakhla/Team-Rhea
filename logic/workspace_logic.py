import concurrent.futures
import json
import os
import subprocess
import textwrap
import re
from tkinter import ttk
import tkinter as tk
import csv
from wordcloud import WordCloud
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog, messagebox, colorchooser

# Import classes from new files
from logic.src.custom_text import CustomText
from logic.src.line_number_canvas import LineNumberCanvas
from logic.src.tool_tip import ToolTip
from logic.src.redirect_output import RedirectOutput
from logic.src.scrolling_text import ScrollingText
from logic.src.custom_dropdown import CustomDropdown
from logic.src.pslist_output_frame import PslistOutputFrame
from logic.src.pstree_output_frame import PstreeOutputFrame
# Import other output frames as necessary

class WorkspaceFrameLogic:
    def __init__(self, parent, file_handler):
        self.parent = parent
        self.file_handler = file_handler
        self.command_tabs = {}
        self.commands = self.load_commands()
        self.command_details = {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self.running_process = None
        self.futures = []
        self.highlight_color = "#ffff00"  # Default highlight color

    def update_loaded_file_label(self, loaded_files=None):
        if loaded_files is None:
            loaded_files = self.file_handler.get_loaded_files()

        filenames_only = [self.file_handler.remove_path(full_path) for full_path in loaded_files]

        if filenames_only:
            self.parent.show_sidebar(filenames_only)
            self.parent.select_first_file_in_sidebar()
        else:
            self.parent.hide_sidebar()

    def save_commands(self):
        try:
            with open('commands.json', 'w') as file:
                json.dump(self.commands, file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save commands: {str(e)}")

    def add_custom_plugin(self):
        file_path = filedialog.askopenfilename(title="Select Custom Plugin", filetypes=[("Python Files", "*.py")])
        if file_path:
            plugin_name = os.path.basename(file_path)
            if plugin_name.endswith('.py'):
                plugin_name = plugin_name[:-3]

            if any(cmd['command'] == plugin_name for cmd in self.commands):
                messagebox.showerror("Error", "Plugin already exists.")
                return

            custom_plugin_details = {
                "type": "Custom Plugin",
                "command": plugin_name,
                "description": f"This is your custom plugin {plugin_name}"
            }
            self.commands.append(custom_plugin_details)
            self.save_commands()
            self.update_command_dropdown()

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

    def export_results(self):
        self.parent.switch_to_export_frame()

    def get_volatility_path(self):
        with open('settings.json', 'r') as file:
            settings = json.load(file)

        base_path = settings.get('volatility_path', '')
        full_path = os.path.join(base_path, 'vol.py')
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
            index = self.parent.command_dropdown.current() - 2
            if index >= 0 and index < len(self.commands):
                command_info = self.commands[index]
                wrapped_text = textwrap.fill(f"Type: {command_info['type']}\nDescription: {command_info['description']}", width=50)
                self.parent.command_info_label.config(text=wrapped_text)
                self.parent.run_command_button.config(state=tk.NORMAL)

    def choose_highlight_color(self):
        color = colorchooser.askcolor(title="Choose Highlight Color", initialcolor=self.highlight_color)
        if color[1] is not None:
            self.highlight_color = color[1]

    def remove_highlight(self):
        for tab in self.command_tabs.values():
            text_widget = tab.nametowidget(tab.winfo_children()[0])
            if isinstance(text_widget, CustomText):
                text_widget.tag_remove("highlight", "1.0", tk.END)

    def run_command(self):
        selected_command = self.parent.command_var.get()
        selected_file = self.file_handler.get_selected_file()
        if not selected_command or selected_command == "-choose command-":
            messagebox.showerror("Error", "Please select a command to run.")
            return
        if not selected_file:
            messagebox.showerror("Error", "No file selected.")
            return

        self.parent.run_command_button.config(state=tk.DISABLED)
        self.parent.config(cursor="wait")

        full_command = f"{self.get_volatility_path()} -f {selected_file} {selected_command}"
        future = self.executor.submit(self.execute_command, full_command)
        future.add_done_callback(lambda fut: self.command_finished(fut, selected_command, selected_file))
        self.futures.append(future)


    def command_finished(self, future, command_name, file_path):
        try:
            if future.done():
                command_result, findings = future.result()
                self.parent.after(0, self.add_tab, file_path, command_name, findings)
                tab_title = f"{command_name} ({os.path.basename(file_path)})"
                self.command_details[tab_title] = {
                    "command": command_name,
                    "output": findings,
                    "highlights": []
                }
                self.check_all_commands_finished()
        except Exception as e:
            messagebox.showerror("Error", f"Error executing command {command_name}: {str(e)}")
            print(f"Exception when processing command result: {e}")

    def add_tab(self, file_path, command_name, findings):
        tab_title = f"{os.path.basename(file_path)} - {command_name}"
        new_tab = ttk.Frame(self.parent.tab_control)
        self.parent.tab_control.add(new_tab, text=tab_title)
        self.command_tabs[tab_title] = new_tab

        if command_name == 'windows.pslist':
            pslist_frame = PslistOutputFrame(new_tab)
            pslist_frame.pack(expand=True, fill='both')
            pslist_frame.populate(findings)

        elif command_name == 'windows.pstree':
            pstree_frame = PstreeOutputFrame(new_tab)
            pstree_frame.pack(expand=True, fill='both')
            pstree_frame.populate(findings)
        
        elif command_name == 'windows.filescan':
            pstree_frame = FilescanOutputFrame(new_tab)
            pstree_frame.pack(expand=True, fill='both')
            pstree_frame.populate(findings)

        elif command_name == 'windows.dlllist':
            pstree_frame = DllListOutputFrame(new_tab)
            pstree_frame.pack(expand=True, fill='both')
            pstree_frame.populate(findings)

        elif command_name == 'windows.netscan':
            pstree_frame = NetstatOutputFrame(new_tab)
            pstree_frame.pack(expand=True, fill='both')
            pstree_frame.populate(findings)
        
        elif command_name == 'windows.modules':
            pstree_frame = ModulesOutputFrame(new_tab)
            pstree_frame.pack(expand=True, fill='both')
            pstree_frame.populate(findings)

        elif command_name == 'windows.handles':
            pstree_frame = HandlesOutputFrame(new_tab)
            pstree_frame.pack(expand=True, fill='both')
            pstree_frame.populate(findings)

        elif command_name == 'windows.cmdline':
            pstree_frame = CmdLineOutputFrame(new_tab)
            pstree_frame.pack(expand=True, fill='both')
            pstree_frame.populate(findings)


        else:
            text_widget = CustomText(new_tab, wrap='word')
            text_widget.insert('1.0', findings)
            text_widget.config(state='disabled')
            text_widget.pack(expand=True, fill='both')

        self.show_close_button(new_tab)

    def execute_command(self, full_command):
        process = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, encoding='utf-8', errors='ignore')
        stdout, stderr = process.communicate()

        findings = stdout if stdout else "No output received."
        if stderr:
            findings += "\nError:\n" + stderr

        return full_command, findings

    def check_all_commands_finished(self):
        if all(f.done() for f in self.futures):
            print("All commands have finished executing.")
            self.parent.run_command_button.config(state=tk.NORMAL)  # Re-enable button
            self.parent.config(cursor="")

    def show_close_button(self, tab):
        close_button = ttk.Button(tab, text="Close", command=lambda: self.close_tab(tab))
        close_button.pack(side=tk.RIGHT, padx=5, pady=5)

    def close_tab(self, tab):
        self.parent.tab_control.forget(tab)
        del self.command_tabs[tab]