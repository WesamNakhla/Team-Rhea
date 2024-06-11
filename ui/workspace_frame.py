import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from logic.workspace_logic import CustomDropdown, WorkspaceFrameLogic, ToolTip, ScrollingText, PslistOutputFrame
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from PIL import Image, ImageTk

class WorkspaceFrame(tk.Frame):
    def __init__(self, parent, app, file_handler, switch_to_export_frame):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.file_handler = file_handler
        self.switch_to_export_frame = switch_to_export_frame

        self.logic = WorkspaceFrameLogic(parent=self, file_handler=self.file_handler)


        self.init_ui()

        # Choose command label
        self.command_label = ttk.Label(self, text="Choose command:")
        self.command_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Command dropdown and input
        self.command_var = tk.StringVar()
        self.command_options = ["-choose command-", "Custom"] + [cmd['command'] for cmd in self.logic.commands]
        self.command_dropdown = ttk.Combobox(self, textvariable=self.command_var, values=self.command_options)
        self.command_dropdown.grid(row=1, column=0, padx=10, pady=5, sticky="we")
        self.command_dropdown.bind('<<ComboboxSelected>>', self.update_command_info)

        # Parameter input label and entry
        self.parameter_label = ttk.Label(self, text="Input Parameters:")
        self.parameter_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.parameter_entry = ttk.Entry(self)
        self.parameter_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        image_path = "img/run_arrow.png"
        img = Image.open(image_path)
        img = img.resize((20, 20), Image.LANCZOS)
        icon_image = ImageTk.PhotoImage(img)

        # Execute command button with icon
        self.run_command_button = ttk.Button(self, text="Run Command", command=self.run_command, image=icon_image, compound=tk.LEFT)
        self.run_command_button.image = icon_image
        self.run_command_button.grid(row=1, column=2, padx=10, pady=5, sticky="w")
        ToolTip(self.run_command_button, "Click to execute the selected command with specified parameters.")

        self.grid_rowconfigure(2, weight=1)
        self.tab_control = ttk.Notebook(self)
        self.tab_control.grid(row=2, column=0, columnspan=4, rowspan=4, padx=10, pady=10, sticky="nsew")

        # Highlight buttons
        self.highlight_frame = ttk.Frame(self)
        self.highlight_frame.grid(row=1, column=3, padx=10, pady=5, sticky="we")

        self.highlight_button = ttk.Button(self.highlight_frame, text="\U0001F58D Highlight", command=self.logic.choose_highlight_color)
        self.highlight_button.pack(side="right", padx=5, pady=5)
        ToolTip(self.highlight_button, "Highlight selected text with a chosen color.")

        self.remove_highlight_button = ttk.Button(self.highlight_frame, text="\U000025B1 Remove Highlight", command=self.logic.remove_highlight)
        self.remove_highlight_button.pack(side="left", padx=5, pady=5)
        ToolTip(self.remove_highlight_button, "Remove selected highlight")

        # Search bar
        self.search_frame = ttk.Frame(self, width=10)
        self.search_frame.grid_propagate(True)
        self.search_frame.grid(row=0, column=2, padx=10, pady=5, sticky="w")

        self.search_label = ttk.Label(self.search_frame, text="Search:")
        self.search_label.pack(side="left", padx=5, pady=5)

        self.search_entry = ttk.Entry(self.search_frame, width=20)
        self.search_entry.pack(side="left", padx=5, pady=5)

        self.search_button = ttk.Button(self.search_frame, text="Search", command=self.search_text)
        self.search_button.pack(side="left", padx=5, pady=5)
        ToolTip(self.search_button, "Search for specific strings in the output.")
        self.search_frame.grid_remove()

        # Sidebar to display loaded files (initially hidden)
        self.sidebar_frame = ttk.Frame(self, width=200)
        self.sidebar_frame.grid_propagate(False)

        self.selected_file_label = ScrollingText(self, text="No file selected", width=150, height=30)
        self.selected_file_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.selected_file_label.grid_propagate(False)
        self.sidebar_frame.grid_remove()

        self.sidebar_frame = ttk.Frame(self, width=200)
        self.sidebar_frame.grid_propagate(False)
        self.sidebar_frame.grid(row=1, column=4, rowspan=6, padx=10, pady=5, sticky="nsew")
        self.sidebar_frame.grid_remove()

        self.centered_frame = ttk.Frame(self.sidebar_frame)
        self.centered_frame.grid(row=1, column=0, padx=(20, 20), pady=5)  # Add padding to center
        self.centered_frame.grid_columnconfigure(0, weight=1)  # Center within the frame

        self.sidebar_listbox = tk.Listbox(self.centered_frame, selectmode=tk.SINGLE)
        self.sidebar_listbox.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.sidebar_listbox.bind("<<ListboxSelect>>", self.on_file_select)

        self.select_all_button = ttk.Button(self.sidebar_frame, text="\U0001F5F9 Select All", command=self.select_all_files)
        self.select_all_button.grid(row=2, column=0, columnspan=2, pady=5)
        self.close_file_button = ttk.Button(self.sidebar_frame, text="\U0001F5F5 Close File", command=self.close_file)
        self.close_file_button.grid(row=3, column=0, columnspan=2, pady=5)
        self.add_file_button = ttk.Button(self.sidebar_frame, text="\U0001F5C0 Open File", command=self.add_file)
        self.add_file_button.grid(row=4, column=0, columnspan=2, pady=5)

        self.toggle_terminal_button = ttk.Button(self.sidebar_frame, text="\U0001F5D4 Show Terminal", command=self.toggle_terminal)
        self.toggle_terminal_button.grid(row=5, column=0, columnspan=2, pady=5)

        self.sidebar_frame.grid(row=1, column=4, rowspan=6, padx=10, pady=5, sticky="nsew")
        self.sidebar_frame.grid_remove()

        self.terminal_frame = tk.Frame(self.sidebar_frame, height=200, width=200)
        self.terminal_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.terminal_output = tk.Text(self.terminal_frame, state='disabled', height=8, width=25, bg='black', fg='white')
        self.terminal_output.pack(expand=True, fill='both')

        self.terminal_frame.grid_remove()

        self.toggle_sidebar_button = ttk.Button(self, text="\U000025E8 Toggle Sidebar", command=self.toggle_sidebar)
        self.toggle_sidebar_button.grid(row=0, column=3, padx=10, pady=5, sticky="w")

        

    def select_first_file_in_sidebar(self):
        if self.sidebar_listbox.size() > 0:
            self.sidebar_listbox.selection_set(0)
            self.sidebar_listbox.event_generate("<<ListboxSelect>>")

    def toggle_terminal(self):
        if self.terminal_frame.winfo_viewable():
            self.terminal_frame.grid_remove()
            self.toggle_terminal_button.configure(text="\U0001F5D4 Show Terminal")
        else:
            self.terminal_frame.grid()
            self.toggle_terminal_button.configure(text="\U0001F5F5 Hide Terminal")

    def set_selected_file(self, file):
        self.file_handler.selected_file = file
        self.update_selected_file_label(file)

    def update_command_dropdown(self, command_options):
        self.command_dropdown['values'] = command_options

    def show_sidebar(self, files):
        self.sidebar_listbox.delete(0, tk.END)
        for file in files:
            self.sidebar_listbox.insert(tk.END, file)
        if len(files) >= 1:
            self.sidebar_frame.grid()
        else:
            self.sidebar_frame.grid_remove()

    def hide_sidebar(self):
        self.sidebar_frame.grid_remove()

    def toggle_sidebar(self):
        if self.sidebar_frame.winfo_viewable():
            self.sidebar_frame.grid_remove()
        else:
            self.sidebar_frame.grid()

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
        filename_only = self.file_handler.remove_path(file)
        new_text = f"Selected file: {filename_only}"
        self.selected_file_label.update_text(new_text)

    def add_file(self):
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            self.file_handler.load_files(file_paths)
            self.show_sidebar(self.file_handler.loaded_files)

    def close_file(self):
        selected_indices = self.sidebar_listbox.curselection()
        if selected_indices:
            selected_file_index = selected_indices[0]
            selected_file = self.file_handler.loaded_files[selected_file_index]
            self.file_handler.loaded_files.remove(selected_file)
            self.show_sidebar(self.file_handler.loaded_files)
            if self.file_handler.loaded_files:
                self.update_selected_file_label(self.file_handler.loaded_files[0])
            else:
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
        self.logic.update_command_info(event)

    def init_ui(self):
        self.configure(bg="#ffffff")
        for row in range(5):
            for col in range(4):
                cell_frame = tk.Frame(self, width=100, height=30)
                cell_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                cell_frame.grid_propagate(False)
                cell_frame.config(height=30)

        for row in range(5):
            self.grid_rowconfigure(row, weight=0)

        for col in range(4):
            self.grid_columnconfigure(col, weight=1)
