import concurrent.futures
import json
import os
import subprocess
import textwrap
import re
from tkinter import ttk
import tkinter as tk
import csv
import seaborn as sns
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog, messagebox, colorchooser



class PslistOutputFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.columns = ["PID", "PPID", "ImageFileName", "Offset", "Threads", "Handles",
                        "SessionId", "Wow64", "CreateTime", "ExitTime", "FileOutput"]

        self.tree = ttk.Treeview(self, columns=self.columns, show='headings')
        self.tree.grid(row=0, column=0, columnspan=2, sticky="nsew")

        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False))
            self.tree.column(col, width=100, anchor="center")

        self.scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar_y.grid(row=0, column=2, sticky="ns")
        self.tree.configure(yscroll=self.scrollbar_y.set)

        self.scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.scrollbar_x.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.tree.configure(xscroll=self.scrollbar_x.set)

        self.style = ttk.Style()
        self.style.configure("Treeview", font=("Helvetica", 10), rowheight=25)
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        self.tree.tag_configure('oddrow', background='#f0f0f0')
        self.tree.tag_configure('evenrow', background='#ffffff')

        self.tree.bind("<Button-1>", self.start_selection)
        self.tree.bind("<B1-Motion>", self.drag_selection)
        self.tree.bind("<Button-3>", self.show_context_menu)

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_selected)
        self.context_menu.add_command(label="Export to CSV", command=self.export_to_csv)

        # Add buttons for Export to CSV and Show Bar Chart
        self.export_button = ttk.Button(self, text="Export to CSV", command=self.export_to_csv)
        self.export_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")


        self.tree_button = ttk.Button(self, text="Show Process Tree", command=self.show_process_tree)
        self.tree_button.grid(row=2, column=2, padx=10, pady=5, sticky="ew")


    def sort_treeview(self, col, reverse):
        def convert(data):
            try:
                return int(data)
            except ValueError:
                try:
                    return float(data)
                except ValueError:
                    return data

        data_list = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        data_list.sort(key=lambda t: convert(t[0]), reverse=reverse)

        for index, (_, item) in enumerate(data_list):
            self.tree.move(item, '', index)

        self.tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))

    def populate(self, findings):
        for i in self.tree.get_children():
            self.tree.delete(i)

        lines = findings.strip().split("\n")
        filtered_lines = []
        for line in lines[1:]:
            if line.strip() and not self.is_unwanted_line(line):
                filtered_lines.append(line)

        for line in filtered_lines:
            values = re.split(r'\s+', line.strip())
            values = self.adjust_columns(values)
            if len(values) == len(self.columns):
                self.tree.insert("", "end", values=values)

    def filter_lines(self, lines):
        filtered_lines = []
        for line in lines[4:]:
            if not self.is_unwanted_line(line) and self.contains_data(line):
                filtered_lines.append(line)
        return filtered_lines

    def is_unwanted_line(self, line):
        unwanted_keywords = ["Progress", "Scanning", "Error", "Stacking attempts", "PDB scanning finished"]
        return any(keyword in line for keyword in unwanted_keywords)

    def contains_data(self, line):
        return any(char.isdigit() for char in line)

    def adjust_columns(self, values):
        if len(values) > len(self.columns):
            values = values[:len(self.columns) - 1] + [' '.join(values[len(self.columns) - 1:])]
        elif len(values) < len(self.columns):
            values += [''] * (len(self.columns) - len(values))
        return values

    def show_context_menu(self, event):
        try:
            row_id = self.tree.identify_row(event.y)
            self.tree.selection_set(row_id)
            self.context_menu.post(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def copy_selected(self):
        try:
            selected_items = self.tree.selection()
            if not selected_items:
                return

            copied_text = ""
            for item in selected_items:
                row_values = self.tree.item(item, "values")
                copied_text += "\t".join(row_values) + "\n"

            self.clipboard_clear()
            self.clipboard_append(copied_text)
        except Exception as e:
            print(f"Error copying to clipboard: {e}")

    def start_selection(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)

    def drag_selection(self, event):
        self.tree.selection_set(self.tree.selection())
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_add(item)

    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(self.columns)
                    for row in self.tree.get_children():
                        row_values = self.tree.item(row, 'values')
                        writer.writerow(row_values)
                messagebox.showinfo("Export to CSV", f"Data successfully exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export to CSV", f"Error exporting to CSV: {e}")


    def show_process_tree(self):
        selected_items = self.tree.get_children()
        if not selected_items:
           messagebox.showwarning("No Data", "No data available to show process tree.")
           return

        process_data = []
        for item in selected_items:
           row_values = self.tree.item(item, "values")
           process_data.append(row_values)
 
        G = nx.DiGraph()

        for process in process_data:
            pid, ppid, image_name = process[0], process[1], process[2]
            G.add_node(pid, label=image_name)
            if ppid != '0':  # Typically, PID 0 is the root or system process
                G.add_edge(ppid, pid)

        pos = nx.spring_layout(G, k=0.5, iterations=50)
        labels = nx.get_node_attributes(G, 'label')

        fig, ax = plt.subplots(figsize=(12, 8))
        nx.draw(G, pos, with_labels=False, ax=ax, node_size=500, node_color='lightblue', linewidths=0.5, font_size=10)
        nx.draw_networkx_labels(G, pos, labels, font_size=8)

        plt.title("Process Tree")
        plt.show()
