import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox

class SettingsFrameLogic:
    def __init__(self, app):
        self.app = app
        self.original_settings = {}
        
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.volatility_path_entry.delete(0, tk.END)
            self.volatility_path_entry.insert(0, folder_path)

    def save_settings(self):
        settings = {
            'volatility_path': self.volatility_path_entry.get(),
            'font_size': self.font_size_spinbox.get(),
            'line_distance': self.line_distance_spinbox.get(),
            'letter_distance': self.letter_distance_spinbox.get()
        }
        with open('settings.json', 'w') as settings_file:
            json.dump(settings, settings_file)
        self.original_settings = settings.copy()
        messagebox.showinfo("Settings Saved", "Your settings have been saved.")

    def load_settings(self):
        try:
            with open('settings.json', 'r') as settings_file:
                settings = json.load(settings_file)
                self.volatility_path_entry.insert(0, settings.get('volatility_path', '../Volatility3'))
                self.font_size_spinbox.delete(0, tk.END)
                self.font_size_spinbox.insert(0, settings.get('font_size', 12))
                self.line_distance_spinbox.delete(0, tk.END)
                self.line_distance_spinbox.insert(0, settings.get('line_distance', 1))
                self.letter_distance_spinbox.delete(0, tk.END)
                self.letter_distance_spinbox.insert(0, settings.get('letter_distance', 1))
                self.original_settings = settings.copy()
        except FileNotFoundError:
            print("Settings file not found. Using defaults.")
            self.volatility_path_entry.insert(0, '../Volatility3')

    def revert_unsaved_changes(self):
        self.volatility_path_entry.delete(0, tk.END)
        self.volatility_path_entry.insert(0, self.original_settings.get('volatility_path', '../Volatility3'))
        self.font_size_spinbox.delete(0, tk.END)
        self.font_size_spinbox.insert(0, self.original_settings.get('font_size', 12))
        self.line_distance_spinbox.delete(0, tk.END)
        self.line_distance_spinbox.insert(0, self.original_settings.get('line_distance', 1))
        self.letter_distance_spinbox.delete(0, tk.END)
        self.letter_distance_spinbox.insert(0, self.original_settings.get('letter_distance', 1))

    def exit_settings(self):
        current_settings = {
            'volatility_path': self.volatility_path_entry.get(),
            'font_size': self.font_size_spinbox.get(),
            'line_distance': self.line_distance_spinbox.get(),
            'letter_distance': self.letter_distance_spinbox.get()
        }
        if current_settings != self.original_settings:
            if messagebox.askyesno("Exit Settings", "Are you sure you want to exit without saving your latest changes?"):
                self.app.switch_to_workspace_frame()
            else:
                self.revert_unsaved_changes()
        else:
            self.app.switch_to_workspace_frame()

    def apply_font_settings(self, font_size):
        for frame in self.app.frames.values():
            if hasattr(frame, 'apply_font_settings'):
                frame.apply_font_settings(font_size)
