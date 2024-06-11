import concurrent.futures
import json
import os
import subprocess
import textwrap
import re
from tkinter import ttk
import tkinter as tk
import csv
import seaborn as sns
import pandas as pd
import numpy as np
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

class WindowsRegistryHiveList(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.columns = ["Hive", "Offset", "Name", "Root", "Subkeys", "Values", "LastWriteTime"]
        
        # Create Treeview widget
        self.tree = ttk.Treeview(self, columns=self.columns, show='headings')
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        
        # Add scrollbars
        self.scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscroll=self.scrollbar_y.set)
        
        self.scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.scrollbar_x.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscroll=self.scrollbar_x.set)
        
        # Bind right-click for context menu
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Export to CSV", command=self.export_to_csv)
        self.context_menu.add_command(label="Show Tree View", command=self.visualize_tree_view)
        self.context_menu.add_command(label="Show Heat Map", command=self.visualize_heat_map)
        
    def populate(self, findings):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        lines = findings.strip().split("\n")
        filtered_lines = []
        for line in lines:
            if line.strip() and not self.is_unwanted_line(line):
                filtered_lines.append(line)
        
        for line in filtered_lines:
            values = re.split(r'\s+', line.strip(), maxsplit=len(self.columns)-1)
            values = self.adjust_columns(values)
            if len(values) == len(self.columns):
                self.tree.insert("", "end", values=values)
    
    def adjust_columns(self, values):
        if len(values) < len(self.columns):
            values += [''] * (len(self.columns) - len(values))
        return values
    
    def is_unwanted_line(self, line):
        unwanted_keywords = ["Progress", "Scanning", "Error", "Finished"]
        return any(keyword in line for keyword in unwanted_keywords)
    
    def show_context_menu(self, event):
        try:
            row_id = self.tree.identify_row(event.y)
            self.tree.selection_set(row_id)
            self.context_menu.post(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(self.columns)
                    for row in self.tree.get_children():
                        row_values = self.tree.item(row, 'values')
                        writer.writerow(row_values)
                messagebox.showinfo("Export to CSV", f"Data successfully exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export to CSV", f"Error exporting to CSV: {e}")
    
    def visualize_tree_view(self):
        data = self.get_tree_data()
        if not data:
            messagebox.showwarning("No Data", "No data available to visualize.")
            return
        
        tree_window = tk.Toplevel(self)
        tree_window.title("Registry Hive Tree View")
        tree_tree = ttk.Treeview(tree_window, columns=["Key", "Value"], show='tree headings')
        tree_tree.pack(expand=True, fill='both')
        
        for root, branches in data.items():
            root_id = tree_tree.insert("", "end", text=root, values=(root, ""))
            self.add_subkeys(tree_tree, root_id, branches)
        
        tree_tree.column("#0", width=300)
        tree_tree.heading("#0", text="Registry Hive Structure")
    
    def get_tree_data(self):
        data = {}
        for row in self.tree.get_children():
            values = self.tree.item(row, "values")
            hive = values[0]
            subkeys = values[4]
            key_path = values[3]
            self.add_key_to_tree(data, hive, key_path, subkeys)
        return data
    
    def add_key_to_tree(self, tree, hive, path, subkeys):
        parts = path.split("\\")
        current = tree.setdefault(hive, {})
        for part in parts:
            current = current.setdefault(part, {})
        current["_subkeys"] = subkeys
    
    def add_subkeys(self, tree_tree, parent_id, branches):
        for key, sub in branches.items():
            if key == "_subkeys":
                continue
            key_id = tree_tree.insert(parent_id, "end", text=key, values=(key, ""))
            if sub:
                self.add_subkeys(tree_tree, key_id, sub)
    
    def visualize_heat_map(self):
        data = self.get_heatmap_data()
        if not data:
            messagebox.showwarning("No Data", "No data available to visualize.")
            return
        
        heatmap_window = tk.Toplevel(self)
        heatmap_window.title("Registry Hive Heat Map")
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        sns.heatmap(data, annot=True, fmt="d", cmap="YlGnBu", ax=ax)
        ax.set_title("Registry Hive Activity Heat Map")
        
        canvas = FigureCanvasTkAgg(fig, master=heatmap_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def get_heatmap_data(self):
        keys = []
        subkeys_counts = []
        for row in self.tree.get_children():
            values = self.tree.item(row, "values")
            key_path = values[3]
            subkeys = int(values[4]) if values[4].isdigit() else 0
            keys.append(key_path)
            subkeys_counts.append(subkeys)
        
        df = pd.DataFrame({
            "Key": keys,
            "Subkeys": subkeys_counts
        })
        df_pivot = df.pivot_table(index="Key", values="Subkeys", aggfunc=np.sum)
        return df_pivot

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
        command_options = ["-choose command-"] + [cmd['command'] for cmd in self.commands]
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

        elif command_name == 'windows.registry.hivelist':
            pstree_frame = WindowsRegistryHiveList(new_tab)
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
