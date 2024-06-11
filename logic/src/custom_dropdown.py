import tkinter as tk

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
