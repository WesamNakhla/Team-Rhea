import tkinter as tk

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
