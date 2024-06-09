import tkinter as tk
from tkinter import ttk
from logic.workspace_logic import CustomDropdown, WorkspaceFrameLogic, ToolTip

class WorkspaceFrame(tk.Frame):
    def __init__(self, parent, app, file_handler, switch_to_export_frame):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.file_handler = file_handler
        self.switch_to_export_frame = switch_to_export_frame

        self.logic = WorkspaceFrameLogic(parent=self, file_handler=self.file_handler)

        self.init_ui()

    def init_ui(self):
        # Using grid layout for better control
        # Choose command label
        self.command_label = ttk.Label(self, text="Choose command:")
        self.command_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        

        # Command dropdown
        # Command dropdown and input
        self.command_var = tk.StringVar()
        self.command_options = ["-choose command-", "Custom"] + [cmd['command'] for cmd in self.logic.commands]
        self.dropdown = CustomDropdown(self, self.command_options, self.command_var)
        self.dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="we")
        self.bind('<<MenuSelect>>', self.update_command_info)


        # Parameter input label and entry
        self.parameter_label = ttk.Label(self, text="Input Parameters:")
        self.parameter_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.parameter_entry = ttk.Entry(self)
        self.parameter_entry.grid(row=2, column=1, padx=10, pady=5, sticky="we")

        # Execute command button
        self.run_command_button = ttk.Button(self, text="Execute Command", command=self.run_command)
        self.run_command_button.grid(row=1, column=2, padx=10, pady=5, sticky="w")
        ToolTip(self.run_command_button, "Click to execute the selected command with specified parameters.")

        # Add Custom Plugin button
        self.add_custom_plugin_button = ttk.Button(self, text="Add Custom Plugin", command=self.logic.add_custom_plugin)
        self.add_custom_plugin_button.grid(row=2, column=2, padx=10, pady=5, sticky="we")
        ToolTip(self.add_custom_plugin_button, "Add a custom plugin to the application.")

        # Command description label
        self.command_info_label = ttk.Label(self, text="Select a command to see the description and type.", width=50, anchor="w", wraplength=400)
        self.command_info_label.grid(row=1, column=3, padx=10, pady=5, sticky="w")

        # Custom command label and entry
        self.custom_command_label = ttk.Label(self, text="Custom command:")
        self.custom_command_entry = ttk.Entry(self)

        # Initially hide the custom command entry
        self.custom_command_label.grid_forget()
        self.custom_command_entry.grid_forget()

        # OutputFrame OUTPUT REAL STUFF HERE from vol <--------
        self.tab_control = ttk.Notebook(self)
        self.tab_control.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        # Highlight buttons
        self.highlight_frame = tk.Frame(self)
        self.highlight_frame.grid(row=5, column=0, columnspan=4, pady=5, sticky="we")

        # Single highlight button with color chooser
        self.highlight_button = ttk.Button(self.highlight_frame, text="\U0001F58D Highlight", command=self.logic.choose_highlight_color)
        self.highlight_button.pack(side="left", padx=5, pady=5)
        ToolTip(self.highlight_button, "Highlight selected text with a chosen color.")

        self.remove_highlight_button = ttk.Button(self.highlight_frame, text="Remove Highlight", command=self.logic.remove_highlight)
        self.remove_highlight_button.pack(side="left", padx=5, pady=5)
        ToolTip(self.remove_highlight_button, "Remove selected highlight")

        # Export button with unicode icon
        self.export_button = ttk.Button(self.highlight_frame, text="\u23CF Export", command=self.logic.export_results)
        self.export_button.pack(side="right", padx=5, pady=5)
        ToolTip(self.export_button, "Export the results and data to a file.")

        # Configure grid to expand correctly
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(3, weight=1)

        # Search bar
        self.search_frame = tk.Frame(self)
        self.search_frame.grid(row=5, column=3, columnspan=1, pady=5, sticky="we")
        self.search_label = ttk.Label(self.search_frame, text="Search:")
        self.search_label.pack(side="left", padx=5, pady=5)
        self.search_entry = ttk.Entry(self.search_frame)
        self.search_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.search_button = ttk.Button(self.search_frame, text="Search", command=self.search_text)
        self.search_button.pack(side="left", padx=5, pady=5)
        ToolTip(self.search_button, "Search for specific strings in the output.")

        # Sidebar to display loaded files (initially hidden)
        self.sidebar_frame = ttk.Frame(self, width=200)
        self.sidebar_frame.grid_propagate(False)
        # Label to display the selected file
        self.selected_file_label = ttk.Label(self, text="No file selected", anchor="w", font=('Arial', 12, 'bold'))
        self.selected_file_label.grid(row=0, column=0, sticky="wew", padx=10, pady=5)

        self.close_tab_button = ttk.Button(self.sidebar_frame, text="Close Tab")
        self.close_tab_button.grid(row=0, column=1, sticky="e", pady=5)

        self.sidebar_listbox = tk.Listbox(self.sidebar_frame, selectmode=tk.SINGLE)
        self.sidebar_listbox.grid(row=1, column=0, columnspan=2, sticky="we")
        self.sidebar_listbox.bind("<<ListboxSelect>>", self.on_file_select)

        self.select_all_button = ttk.Button(self.sidebar_frame, text="Select All", command=self.select_all_files)
        self.select_all_button.grid(row=2, column=0, columnspan=2, pady=5)
        self.close_file_button = ttk.Button(self.sidebar_frame, text="Close File", command=self.close_file)
        self.close_file_button.grid(row=3, column=0, columnspan=2, pady=5)
        self.add_file_button = ttk.Button(self.sidebar_frame, text="Add File", command=self.add_file)
        self.add_file_button.grid(row=4, column=0, columnspan=2, pady=5)

        self.sidebar_frame.grid(row=0, column=4, rowspan=6, padx=10, pady=5, sticky="nsew")
        self.sidebar_frame.grid_remove()

        self.grid_rowconfigure(3, weight=1)  # Makes the row where terminal_frame will be placed expandable
        self.grid_columnconfigure(4, weight=1)  # Makes the column where terminal_frame will be placed expandable

        # Terminal Frame
        self.terminal_frame = tk.Frame(self, height=350, width=200)
        self.terminal_frame.grid(row=6, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")
        self.terminal_output = tk.Text(self.terminal_frame, state='disabled', height=8, width=25, bg='black', fg='white')
        self.terminal_output.pack(expand=True, fill='both')

        self.terminal_frame.grid_remove()  # Hide the terminal frame after redirection

        self.hide_terminal_button = ttk.Button(self, text="Show Terminal", command=self.toggle_terminal)
        self.hide_terminal_button.grid(row=5, column=4, padx=10, pady=5, sticky="w")

    def select_first_file_in_sidebar(self):
        if self.sidebar_listbox.size() > 0:  # Check if the listbox is not empty
            self.sidebar_listbox.selection_set(0)  # Select the first item
            self.sidebar_listbox.event_generate("<<ListboxSelect>>")  # Trigger the listbox select event

    def toggle_terminal(self):
        if self.terminal_frame.winfo_viewable():
            self.terminal_frame.grid_remove()
            self.hide_terminal_button.configure(text="Show Terminal")  # Change the button text to indicate action
        else:
            self.terminal_frame.grid()
            self.hide_terminal_button.configure(text="Hide Terminal")  # Change back the button text

    def set_selected_file(self, file):
        self.file_handler.selected_file = file
        self.update_selected_file_label(file)

    def update_command_dropdown(self, command_options):
        self.command_dropdown['values'] = command_options

    def show_sidebar(self, files):
        self.sidebar_listbox.delete(0, tk.END)
        for file in files:
            self.sidebar_listbox.insert(tk.END, file)
        self.sidebar_frame.grid()

    def hide_sidebar(self):
        self.sidebar_frame.grid_remove()

    def select_all_files(self):
        self.sidebar_listbox.select_set(0, tk.END)

    def on_file_select(self, event):
        selected_indices = self.sidebar_listbox.curselection()
        if selected_indices:
            selected_file_index = selected_indices[0]
            self.file_handler.selected_file = selected_file_index
            selected_file = self.file_handler.get_selected_file()
            self.update_selected_file_label(selected_file)

    def update_selected_file_label(self, file):
        # Use the remove_path method from file_handler to get the file name without the path
        filename_only = self.file_handler.remove_path(file)
        self.selected_file_label.config(text=f"Selected file: {filename_only}")


    def add_file(self):
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            self.file_handler.loaded_files.extend(file_paths)
            self.show_sidebar(self.file_handler.loaded_files)

    def close_file(self):
        selected_indices = self.sidebar_listbox.curselection()
        if selected_indices:
            selected_file = self.sidebar_listbox.get(selected_indices[0])
            self.file_handler.loaded_files.remove(selected_file)
            self.show_sidebar(self.file_handler.loaded_files)
            self.update_selected_file_label("No file selected")

    def show_search_box(self):
        self.search_frame.grid()
        self.search_entry.focus_set()

    def search_text(self):
        if not self.search_frame.winfo_ismapped():
            self.show_search_box()
            return

        search_term = self.search_entry.get().strip()
        if not search_term:
            return

        for tab_id in self.tab_control.tabs():
            tab = self.tab_control.nametowidget(tab_id)
            text_widget = tab.winfo_children()[0]
            text_widget.tag_remove('search_highlight', '1.0', tk.END)
            start_pos = '1.0'
            while True:
                start_pos = text_widget.search(search_term, start_pos, stopindex=tk.END, nocase=True)
                if not start_pos:
                    break
                end_pos = f'{start_pos}+{len(search_term)}c'
                text_widget.tag_add('search_highlight', start_pos, end_pos)
                start_pos = end_pos
            text_widget.tag_config('search_highlight', background='yellow')

    def search_command(self, event=None):
        search_term = self.command_var.get().strip().lower()
        filtered_options = [option for option in self.command_options if search_term in option.lower()]
        self.command_dropdown['values'] = filtered_options
        if filtered_options:
            self.command_dropdown.event_generate('<Down>')

    def show_combobox(self):
        self.command_button.grid_remove()
        self.command_dropdown.grid()
        self.command_dropdown.focus_set()
        self.command_dropdown.event_generate('<Button-1>')

    def run_command(self):
        self.logic.run_command()

    def update_command_info(self, event):
        self.logic.update_command_info(event)

    def update_loaded_file_label(self):
        self.logic.update_loaded_file_label()

    def update_command_info(self, event=None):
        # Update based on selected command
        selected_command = self.command_var.get()
        print(f"Command selected: {selected_command}")
        # Logic to update UI or perform actions based on the selected command    