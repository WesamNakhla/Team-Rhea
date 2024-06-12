import tkinter as tk
from tkinter import ttk, filedialog
from logic.workspace_logic import CustomDropdown, WorkspaceFrameLogic, ToolTip
from tkinter import PhotoImage
from PIL import Image, ImageTk
import json
import os

class WorkspaceFrame(tk.Frame):
    def __init__(self, parent, app, file_handler, switch_to_export_frame):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.file_handler = file_handler
        self.switch_to_export_frame = switch_to_export_frame

        self.logic = WorkspaceFrameLogic(parent=self, file_handler=self.file_handler)
        self.font_settings = self.load_font_settings()

        self.highlights = []  # Initialize the highlights attribute

        self.init_ui()

        

        # Command dropdown and input
        self.command_var = tk.StringVar()
        self.command_options = ["-choose command-", "Custom"] + [cmd['command'] for cmd in self.logic.commands]
        self.command_dropdown = ttk.Combobox(self, textvariable=self.command_var, values=self.command_options)
        self.command_dropdown.grid(row=1, column=0, padx=10, pady=5, sticky="we")
        self.command_dropdown.set("-choose command-")  # Default display value
        self.command_dropdown.bind('<<ComboboxSelected>>', self.update_command_info)
        self.command_dropdown.bind('<FocusIn>', self.on_focus_in)
        self.command_dropdown.bind('<FocusOut>', self.on_focus_out)
        ToolTip(self.command_dropdown, "Select a command from the list or search to find a specific command")

       

        self.placeholder_text = "Enter parameters here"
        self.parameter_entry = ttk.Entry(self)
        self.parameter_entry.insert(0, self.placeholder_text)
        self.parameter_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")
        self.parameter_entry.bind("<FocusIn>", self.on_entry_click)
        self.parameter_entry.bind("<FocusOut>", self.on_focusout)
        self.parameter_entry.config(foreground='grey')
        ToolTip(self.parameter_entry, "Enter parameters here, e.g., '--pid 1234' This field is used to specify additional options or arguments for the selected command.")

        # Command info label
        self.command_info_label = ttk.Label(self, text="Command Info:")
        self.command_info_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        image_path = "img/run_arrow.png"
        img = Image.open(image_path)
        img = img.resize((20, 20), Image.LANCZOS)
        icon_image = ImageTk.PhotoImage(img)

        # Execute command button with icon
        self.run_command_button = ttk.Button(self, text="Run Command", command=self.run_command, image=icon_image, compound=tk.LEFT)
        self.run_command_button.image = icon_image
        self.run_command_button.grid(row=1, column=2, padx=10, pady=5, sticky="w")
        ToolTip(self.run_command_button, "Click to run the selected command. Parameters are optional and can refine the command's behavior.")

        self.grid_rowconfigure(2, weight=1)
        self.tab_control = ttk.Notebook(self)
        self.tab_control.grid(row=2, column=0, columnspan=4, rowspan=4, padx=10, pady=10, sticky="nsew")

        

        self.highlight_frame = ttk.Frame(self)
        self.highlight_frame.grid(row=1, column=3, padx=10, pady=5, sticky="we")

        # Load icons for buttons
        base_directory = os.path.dirname(os.path.dirname(__file__))
        highlight_image = Image.open(os.path.join(base_directory, "img", "highlighter.png"))
        eraser_image = Image.open(os.path.join(base_directory, "img", "eraser.png"))
        highlight_image = highlight_image.resize((20, 20), Image.LANCZOS)  # Resize to 20x20 pixels
        eraser_image = eraser_image.resize((20, 20), Image.LANCZOS)

        self.highlight_icon = ImageTk.PhotoImage(highlight_image)
        self.remove_highlight_icon = ImageTk.PhotoImage(eraser_image)

        # Button for removing highlight
        self.remove_highlight_button = ttk.Button(self.highlight_frame, image=self.remove_highlight_icon, command=self.logic.remove_highlight)
        self.remove_highlight_button.pack(side="right", padx=5, pady=5)  # Swapped to 'right'
        ToolTip(self.remove_highlight_button, "Remove selected highlight")

        # Button for highlighting
        self.highlight_button = ttk.Button(self.highlight_frame, image=self.highlight_icon, command=self.logic.choose_highlight_color)
        self.highlight_button.pack(side="right", padx=5, pady=5)  # Also 'right', will appear to the left of remove button
        ToolTip(self.highlight_button, "Highlight selected text with a chosen color.\n\nTip: Use CTRL + H to quickly highlight text with a dark orange color.")


        # Ensure text_widget is defined before using it
        for tab_id in self.tab_control.tabs():
            tab = self.tab_control.nametowidget(tab_id)
            text_widget = tab.winfo_children()[0]
            text_widget.tag_config('search_highlight', foreground='black')

        # Search bar
        self.search_frame = ttk.Frame(self, width=10)
        self.search_frame.grid_propagate(True)
        self.search_frame.grid(row=0, column=2, padx=10, pady=5, sticky="w")

        self.search_label = ttk.Label(self.search_frame, text="Search:")
        self.search_label.pack(side="left", padx=5, pady=5)

        self.search_entry = ttk.Entry(self.search_frame, width=10)
        self.search_entry.pack(side="left", padx=5, pady=5)
        self.search_entry.bind("<Return>", self.search_text)
        self.search_entry.bind("<KeyRelease>", self.clear_search_highlight)

        self.search_button = ttk.Button(self.search_frame, text="Search", command=self.search_text)
        self.search_button.pack(side="left", padx=5, pady=5)
        ToolTip(self.search_button, "Search for specific strings in the output.")
        self.search_frame.grid_remove()

        # Bind Ctrl+F to show search bar
        self.bind_all('<Control-f>', self.show_search_box)
        self.search_entry.bind('<Return>', self.search_text)  # Bind Enter key to the search_text method

        # Sidebar to display loaded files (initially hidden)
        self.sidebar_frame = ttk.Frame(self, width=200)
        self.sidebar_frame.grid_propagate(False)

        self.selected_file_label = ttk.Label(self, text="No file selected", width=30)
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
        self.sidebar_listbox.bind("<Motion>", self.show_file_tooltip)

        self.select_all_button = ttk.Button(self.sidebar_frame, text="\U0001F5F9 Select All", command=self.select_all_files)
        self.select_all_button.grid(row=2, column=0, columnspan=2, pady=5)
        self.close_file_button = ttk.Button(self.sidebar_frame, text="\U0001F5F5 Close File", command=self.close_file)
        self.close_file_button.grid(row=3, column=0, columnspan=2, pady=5)
        self.add_file_button = ttk.Button(self.sidebar_frame, text="\U0001F5C0 Open File", command=self.add_file)
        self.add_file_button.grid(row=4, column=0, columnspan=2, pady=5)
        ToolTip(self.select_all_button, "Select all files listed in the sidebar.")
        ToolTip(self.close_file_button, "Close the selected file from the list.")
        ToolTip(self.add_file_button, "Open a new file and add it to the list in the sidebar.")

        self.sidebar_frame.grid(row=1, column=4, rowspan=6, padx=10, pady=5, sticky="nsew")
        self.sidebar_frame.grid_remove()

        self.toggle_sidebar_button = ttk.Button(self, text="\U000025E8 Toggle Sidebar", command=self.toggle_sidebar)
        self.toggle_sidebar_button.grid(row=0, column=3, padx=10, pady=5, sticky="e")
        ToolTip(self.toggle_sidebar_button, "Toggle the visibility of the sidebar to show or hide loaded files.")

        self.file_tooltip = ToolTip(self.sidebar_listbox, "")
        self.apply_font_settings()


    def show_file_tooltip(self, event):
        """Show the tooltip for the file currently under the cursor in the sidebar listbox."""
        index = self.sidebar_listbox.nearest(event.y)
        if index < 0 or index >= self.sidebar_listbox.size():
            self.file_tooltip.hide_tip()
            return

        file_name = self.sidebar_listbox.get(index)
        full_file_path = self.file_handler.loaded_files[index]
        self.file_tooltip.update_text(full_file_path)
        self.file_tooltip.schedule_tip()


    def on_entry_click(self, event):
        """Clear the entry on focus if it contains the placeholder."""
        if self.parameter_entry.get() == self.placeholder_text:
            self.parameter_entry.delete(0, tk.END)  # Delete all the text in the entry
            self.parameter_entry.config(foreground='white')  # Reset the text color

    def on_focusout(self, event):
        """Put placeholder text back if the entry is empty."""
        if not self.parameter_entry.get():
            self.parameter_entry.insert(0, self.placeholder_text)
            self.parameter_entry.config(foreground='grey')  # Change the text color to grey to indicate placeholder
    
    def select_first_file_in_sidebar(self):
        if self.sidebar_listbox.size() > 0:
            self.sidebar_listbox.selection_set(0)
            self.sidebar_listbox.event_generate("<<ListboxSelect>>")

    def set_selected_file(self, file):
        self.file_handler.selected_file = file
        self.update_selected_file_label(file)

    def update_command_dropdown(self, command_options):
        self.command_dropdown['values'] = command_options

    def update_command_info(self, event):
        """Handle the event when a command is selected."""
        selected_command = self.command_var.get()
        if selected_command == "-choose command-":
            self.command_var.set("")  # Clear the selection if the placeholder is selected
        else:
            # Update the interface or perform actions based on the command selected
            print(f"Command selected: {selected_command}")


    def update_command_info(self, event):
        """Handle the event when a command is selected."""
        selected_command = self.command_var.get()
        if selected_command == "-choose command-":
            self.command_var.set("")  # Clear the selection if the placeholder is selected

    def on_focus_in(self, event):
        """Clear the combobox text if it's the default prompt when focused."""
        if self.command_var.get() == "-choose command-":
            self.command_dropdown.set('')

    def on_focus_out(self, event):
        """Reset the default prompt if no valid command has been selected."""
        if not self.command_var.get().strip():  # Check if the field is empty
            self.command_dropdown.set('-choose command-')

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
        if file:
            filename_only = os.path.basename(file)  # Assuming you want just the file name, not the entire path
            display_text = f"Selected file:\n{filename_only}"
        else:
            display_text = "No file selected"
        
        self.selected_file_label.config(text=display_text)  # Use config to update the label's text

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

    
    
    def show_search_box(self, event=None):
        if self.search_frame.grid_info():  # Checks if search_frame is visible
            self.search_frame.grid_remove()  # Hide the search_frame
        else:
            self.search_frame.grid()  # Show the search_frame
            self.search_entry.focus_set()

    def clear_search_highlight(self, event):
        if not self.search_entry.get().strip():
            for tab_id in self.tab_control.tabs():
                tab = self.tab_control.nametowidget(tab_id)
                text_widget = tab.winfo_children()[0]
                text_widget.tag_remove('search_highlight', '1.0', tk.END)

    def search_text(self, event=None):
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
            text_widget.tag_config('search_highlight', background='yellow', foreground='black')

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

    def get_export_data(self):
        export_data = {
            "memory_dump_file": self.file_handler.get_selected_file(),
            "commands": []
        }
        for tab in self.tab_control.tabs():
            tab_widget = self.tab_control.nametowidget(tab)
            command = self.command_dropdown.get()
            if not command:
                command = "Custom Command"
            text_widget = tab_widget.winfo_children()[0]
            output = text_widget.get("1.0", tk.END)
            export_data["commands"].append({
                "command": command,
                "output": output
            })
        return export_data

    def load_font_settings(self):
        settings_file_path = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
        if os.path.exists(settings_file_path):
            with open(settings_file_path, 'r') as f:
                settings = json.load(f)
                return {
                    "font_size": settings.get("font_size", "12"),
                    "line_distance": settings.get("line_distance", "1"),
                    "letter_distance": settings.get("letter_distance", "1")
                }
        else:
            return {
                "font_size": "12",
                "line_distance": "1",
                "letter_distance": "1"
            }

    def apply_font_settings(self):
        font_size = int(self.font_settings.get("font_size", "12"))
        font_family = "Arial"
        for tab_id in self.tab_control.tabs():
            tab = self.tab_control.nametowidget(tab_id)
            text_widget = tab.winfo_children()[0]
            text_widget.config(font=(font_family, font_size))

    def apply_font_settings_to_console(self):
        self.font_settings = self.load_font_settings()
        self.apply_font_settings()