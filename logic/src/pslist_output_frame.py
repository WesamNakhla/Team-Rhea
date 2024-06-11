import tkinter as tk
from tkinter import ttk

class PslistOutputFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.tree = ttk.Treeview(self, columns=("Name", "PID", "PPID"), show='headings')
        self.tree.heading("Name", text="Name")
        self.tree.heading("PID", text="PID")
        self.tree.heading("PPID", text="PPID")
        self.tree.pack(fill=tk.BOTH, expand=True)

    def populate(self, data):
        for item in data:
            if isinstance(item, dict) and 'name' in item and 'pid' in item and 'ppid' in item:
                self.tree.insert('', tk.END, values=(item['name'], item['pid'], item['ppid']))
            else:
                print(f"Invalid item format: {item}")
