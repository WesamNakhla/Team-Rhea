import tkinter as tk

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
