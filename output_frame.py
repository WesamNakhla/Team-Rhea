import tkinter as tk
from tkinter import ttk

class OutputFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.text_output = tk.Text(self, height=15, width=50)
        self.text_output.insert(tk.END, "Dummy command output...")
        self.text_output.pack(pady=20)
        
        self.highlight_button = ttk.Button(self, text="Highlight Text", command=self.highlight_text)
        self.highlight_button.pack()

    def highlight_text(self):
        # Dummy function to highlight text
        print("Text highlighted successfully!")
