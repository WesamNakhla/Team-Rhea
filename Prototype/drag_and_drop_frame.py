import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES

class DragAndDropFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app  # Store the reference to the MainApplication instance

        # Add text and button
        self.label = ttk.Label(self, text="Drag and drop your file here OR", padding=20)
        self.label.pack()

        # Create a canvas to display the image
        self.canvas = tk.Canvas(self, width=200, height=200)
        self.canvas.pack()

        # Load the image
        self.image = tk.PhotoImage(file="Drag.png")  # Replace "your_image.png" with the path to your image
        self.canvas.create_image(110, 80, anchor="center", image=self.image)  # Centering the image

        # Add text and button
        self.browse_label = ttk.Label(self, text="Browse for file", padding=20)
        self.browse_label.pack()

        self.browse_button = ttk.Button(self, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=5)  # Add padding between Browse button and label

        # Add more space between the Browse button and the Import button
        

        self.import_button = ttk.Button(self, text="Import dump package", command=self.import_file)
        self.import_button.pack()

        # Register this widget as a drop target
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop)

    def drop(self, event):
        files = event.data
        self.label.config(text=f"Files dropped: {files}")
        print("Files dropped:", files)
        self.app.switch_to_combined_frame()  # Use the stored reference to call the method
        
    def import_file(self):
        # Dummy function for file import
        print("File imported successfully!")
        self.app.switch_to_combined_frame()  # Use the stored reference to switch frames

    def browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            print("File selected:", filename)
            self.label.config(text=f"File selected: {filename}")

class MainApplication(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("Drag and Drop Example")
        self.geometry("400x400")

        self.frame = DragAndDropFrame(self, self)
        self.frame.pack(expand=True, fill=tk.BOTH)

    def switch_to_command_frame(self):
        print("Switching to command frame...")
        # Implement the logic to switch frames here self.app.switch_to_combined_frame()

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()