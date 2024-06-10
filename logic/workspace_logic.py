import concurrent.futures
import json
import os
import subprocess
import textwrap
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
    def __init__(self, widget, text, delay=300):
        self.widget = widget
        self.tipwindow = None
        self.text = text
        self.delay = delay
        self.after_id = None
        self.widget.bind("<Enter>", self.schedule_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def schedule_tip(self, event=None):
        """Schedule the tooltip to display after a delay."""
        self.cancel_tip()  # Cancel existing tooltip schedule if any
        self.after_id = self.widget.after(self.delay, self.show_tip)

    def show_tip(self):
        """Display text in tooltip window, this function gets called after a delay."""
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", foreground="#000000",
                         relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1, fill=tk.BOTH, expand=True)

    def hide_tip(self, event=None):
        """Hide the tooltip and cancel any pending tooltip display."""
        self.cancel_tip()
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

    def cancel_tip(self):
        """Cancel any scheduled tooltip from appearing."""
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None

class RedirectOutput:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.config(state='normal')
        self.text_widget.insert(tk.END, string)
        self.text_widget.config(state='disabled')
        self.text_widget.see(tk.END)

    def flush(self):
        pass

class ScrollingText(tk.Canvas):
    def __init__(self, parent, text, **kwargs):
        super().__init__(parent, **kwargs)
        self.text_id = self.create_text(0, 0, anchor="w", text=text, font=('Arial', 12, 'bold'))
        self.bind("<Configure>", self.on_configure)
        self.start_scrolling()

    def on_configure(self, event):
        bbox = self.bbox(self.text_id)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        self.config(scrollregion=(0, 0, width, height))
        self.coords(self.text_id, self.winfo_width(), height // 2)

    def start_scrolling(self):
        x, y = self.coords(self.text_id)
        if x < -self.bbox(self.text_id)[2]:
            self.coords(self.text_id, self.winfo_width(), y)
        else:
            self.move(self.text_id, -2, 0)  # Move text left by 2 pixels
        self.after(50, self.start_scrolling)  # Repeat every 50 ms

    def update_text(self, new_text):
        self.itemconfig(self.text_id, text=new_text)
        self.on_configure(None)  # Reconfigure to adjust the new text

class CustomDropdown(tk.Frame):
    def __init__(self, parent, options, var, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.variable = var
        self.original_options = options
        self.filtered_options = options
        self.selected_index = -1  # Initialize selected index

        # Entry for input
        self.entry = tk.Entry(self, textvariable=self.variable)
        self.entry.pack(side="top", fill="x")
        self.entry.bind("<KeyRelease>", self.handle_key_release)
        self.entry.bind("<FocusIn>", self.on_focus_in)
        self.entry.bind("<FocusOut>", self.on_focus_out)

        # Toplevel window for dropdown options
        self.dropdown_window = None
        self.listbox = None

        # Button to toggle dropdown visibility
        self.toggle_button = tk.Button(self, text="▼", command=self.toggle_menu_visibility)
        self.toggle_button.pack(side="right", fill="y")

    def handle_key_release(self, event):
        print(f"Key released: {event.keysym} (code: {event.keycode})")
        self.update_menu()

        if self.variable.get().strip() and self.filtered_options:
            self.show_menu()
        else:
            self.hide_menu()
        self.entry.after(1, self.refocus_entry)
        self.confirm_focus()

    def update_menu(self):
        search_term = self.variable.get().strip().lower()
        self.filtered_options = [option for option in self.original_options if search_term in option.lower()]
        if self.listbox:
            self.listbox.delete(0, tk.END)
            for option in self.filtered_options:
                self.listbox.insert(tk.END, option)
        print(f"Filtered options: {self.filtered_options}")

    def show_menu(self):
        if not self.dropdown_window:
            self.dropdown_window = tk.Toplevel(self)
            self.dropdown_window.overrideredirect(True)
            self.dropdown_window.geometry(f"+{self.winfo_rootx()}+{self.winfo_rooty() + self.entry.winfo_height()}")
            self.dropdown_window.bind("<FocusOut>", lambda e: self.hide_menu())

            self.listbox = tk.Listbox(self.dropdown_window, selectmode=tk.SINGLE)
            self.listbox.pack(fill=tk.BOTH, expand=True)
            self.listbox.bind("<ButtonRelease-1>", self.on_listbox_select)
            self.listbox.bind("<KeyRelease>", self.on_listbox_key)

        # Adjust the dropdown window position and size
        self.dropdown_window.geometry(f"{self.entry.winfo_width()}x{min(100, len(self.filtered_options) * 20)}+{self.winfo_rootx()}+{self.winfo_rooty() + self.entry.winfo_height()}")
        self.dropdown_window.deiconify()
        self.update_menu()
        self.entry.after(1, self.refocus_entry)
        print("Menu shown.")

    def hide_menu(self):
        if self.dropdown_window:
            self.dropdown_window.withdraw()
            print("Menu hidden.")
        self.entry.after(1, self.refocus_entry)
        self.confirm_focus()

    def toggle_menu_visibility(self):
        if self.dropdown_window and self.dropdown_window.winfo_viewable():
            self.hide_menu()
        else:
            self.show_menu()

    def on_listbox_select(self, event):
        if self.listbox.curselection():
            index = self.listbox.curselection()[0]
            value = self.listbox.get(index)
            self.set_value(value)
            self.selected_index = index  # Set the selected index

    def on_listbox_key(self, event):
        if event.keysym == 'Return':
            self.on_listbox_select(event)

    def set_value(self, value):
        print(f"Value selected: {value}")
        self.variable.set(value)
        self.hide_menu()
        self.entry.after(1, self.refocus_entry)
        self.event_generate('<<MenuSelect>>')
        self.confirm_focus()

    def get_selected_index(self):
        return self.selected_index

    def refocus_entry(self):
        self.entry.focus_set()
        self.entry.icursor(tk.END)
        print("Refocused entry.")

    def on_focus_in(self, event):
        print("Entry gained focus.")

    def on_focus_out(self, event):
        print("Entry lost focus.")

    def confirm_focus(self):
        if self.entry.focus_get() == self.entry:
            print("Entry widget is focused.")
        else:
            print("Entry widget is not focused.")




class WorkspaceFrameLogic:
    def __init__(self, parent, file_handler):
        self.parent = parent
        self.file_handler = file_handler
        self.command_tabs = {}  # Dictionary to store command titles and corresponding tabs
        self.commands = self.load_commands()  # Load commands from JSON
        self.command_details = {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)  # Initialize ThreadPoolExecutor
        self.running_process = None  # Store the running process
        self.futures = []  # Initialize the futures list
       
        
       


    def update_loaded_file_label(self, loaded_files=None):
        if loaded_files is None:
            loaded_files = self.file_handler.get_loaded_files()
        
        # Remove paths from the loaded files
        filenames_only = [self.file_handler.remove_path(full_path) for full_path in loaded_files]
        
        if filenames_only:
            self.parent.show_sidebar(filenames_only)  # Show sidebar if files exist
            self.parent.select_first_file_in_sidebar()  # Select the first file in the sidebar
        else:
            self.parent.hide_sidebar()  # Hide sidebar if no files exist

    def show_search_box(self):
        self.search_entry.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        self.search_entry.focus_set()

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
                plugin_name = plugin_name[:-3]  # Remove the .py extension

            # Check for duplicates
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
        self.update_command_dropdown(command_options)

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

    def command_finished(self, future, command_name, file_path):
        try:
            if future.done():
                command_result, findings = future.result()
                self.parent.after(0, self.add_tab, file_path, command_name, findings)
                tab_title = f"{command_name} ({os.path.basename(file_path)})"
                self.command_details[tab_title] = {
                    "command": command_name,
                    "output": findings,
                    "highlights": []  # Placeholder for any highlights data
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

        text_widget = CustomText(new_tab, wrap='word')
        text_widget.insert('1.0', findings)
        text_widget.config(state='disabled')
        text_widget.pack(expand=True, fill='both')

        self.show_close_button(new_tab)

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

    def run_command(self):
        print("Running command")
        selected_file = self.file_handler.get_selected_file()
        print(f"Selected file: {selected_file}")
        if not selected_file:
            messagebox.showerror("Error", "No file selected.")
            return

        selected_index = self.parent.command_dropdown.get_selected_index()
        command = None
        command_name = None
        if selected_index == 1:  # Custom command
            command = self.parent.custom_command_entry.get().strip()
            command_name = "Custom"
        elif selected_index > 1:  # Predefined command selected
            command_index = selected_index - 2  # Adjust index for 'Choose command...' and 'Custom'
            if command_index < len(self.commands):
                command = self.commands[command_index]['command']
                command_name = self.commands[command_index]['command']  # Use the command from the list

        if not command:
            messagebox.showerror("Error", "Please select a command or enter a custom command.")
            return

        command_parameters = self.parent.parameter_entry.get().strip()  # Retrieve parameters from the user input
        vol_path = self.get_volatility_path()

        # Combine the volatility script, file path, command, and user-entered parameters
        full_command = f"python {vol_path} -f {selected_file} {command} {command_parameters}"
        print(f"Running command: {full_command}")

        # Execute the command in a separate thread using ThreadPoolExecutor
        future = self.executor.submit(self.execute_command, full_command)  # Pass the full command to execution
        future.add_done_callback(lambda f, cmd=command_name, fp=selected_file: self.command_finished(f, cmd, fp))

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

    def prepare_export_data(self):
        print("Preparing export data...")
        selected_file = self.file_handler.get_selected_file()
        if selected_file:
            export_data = {
                "memory_dump_file": selected_file,  # Use the selected file
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
