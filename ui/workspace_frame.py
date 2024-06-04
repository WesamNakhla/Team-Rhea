import tkinter as tk
from tkinter import ttk
import os
from logic.workspace_frame import WorkspaceFrameLogic

class WorkspaceFrame(tk.Frame, WorkspaceFrameLogic):
    def __init__(self, parent, switch_to_export_frame):
        tk.Frame.__init__(self, parent)
        WorkspaceFrameLogic.__init__(self, parent)
        self.switch_to_export_frame = switch_to_export_frame
        self.init_ui()

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
        self.highlight_frame.grid(row=5, column=0, columnspan=4, pady=5, sticky="we")

        # Single highlight button with color chooser
        self.highlight_button = ttk.Button(self.highlight_frame, text="\U0001F58D Highlight", command=self.choose_highlight_color)
        self.highlight_button.pack(side="left", padx=5, pady=5)

        self.remove_highlight_button = ttk.Button(self.highlight_frame, text="Remove Highlight", command=self.remove_highlight)
        self.remove_highlight_button.pack(side="left", padx=5, pady=5)

        # Export button with unicode icon
        self.export_button = ttk.Button(self.highlight_frame, text="\u23CF Export", command=self.export_results)
        self.export_button.pack(side="right", padx=5, pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=100, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=4, padx=10, pady=5, sticky="we")

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

        # Sidebar to display loaded files (initially hidden)
        self.sidebar_frame = ttk.Frame(self)
        self.sidebar_title = ttk.Label(self.sidebar_frame, text="Selected Files:", font=('Arial', 12, 'bold'))
        self.sidebar_title.grid(row=0, column=0, sticky="w", pady=5)
        self.close_sidebar_button = ttk.Button(self.sidebar_frame, text="Close", command=self.hide_sidebar)
        self.close_sidebar_button.grid(row=0, column=1, sticky="e", pady=5)
        self.sidebar_listbox = tk.Listbox(self.sidebar_frame, selectmode=tk.SINGLE)
        self.sidebar_listbox.grid(row=1, column=0, columnspan=2, sticky="we")
        self.sidebar_listbox.bind("<<ListboxSelect>>", self.on_file_select)
        self.select_all_button = ttk.Button(self.sidebar_frame, text="Select All", command=self.select_all_files)
        self.select_all_button.grid(row=2, column=0, columnspan=2, pady=5)
        self.sidebar_frame.grid(row=0, column=4, rowspan=6, padx=10, pady=5, sticky="nsew")
        self.sidebar_frame.grid_remove()

        # Label to display the selected file
        self.selected_file_label = ttk.Label(self, text="No file selected", anchor="w")
        self.selected_file_label.grid(row=6, column=0, sticky="wew", padx=10, pady=5)

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
            selected_file = self.sidebar_listbox.get(selected_indices[0])
            self.parent.set_selected_file(selected_file)

    def update_selected_file_label(self, file):
        self.selected_file_label.config(text=f"Selected file: {file}")
