import tkinter as tk

class ScrollingText(tk.Canvas):
    def __init__(self, parent, text, **kwargs):
        super().__init__(parent, **kwargs)
        self.text_id = self.create_text(0, 0, anchor="w", text=text, font=('Arial', 12, 'bold'), fill="red")
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
            self.coords(self.winfo_width(), y)
        else:
            self.move(self.text_id, -2, 0)  # Move text left by 2 pixels
        self.after(50, self.start_scrolling)  # Repeat every 50 ms

    def update_text(self, new_text):
        self.itemconfig(self.text_id, text=new_text)
        self.on_configure(None)  # Reconfigure to adjust the new text
