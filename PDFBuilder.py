import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import os
import json
from PyPDF2 import PdfMerger, PdfReader
import pickle as pkl
from copy import deepcopy
from glob import glob
import ttkbootstrap as ttk
import tkinter as tk
from tkinter import messagebox, filedialog

from PDFFile import PDFFile
from PDFCollection import PDFCollection
from open_file import open_file
from PDFSortKey import PDFSortKey
from RegexGenerator import find_and_kill_process_by_port
from PDFTreeView import PDFTreeView


def _exit(root, event=None):
    root.quit()


class PDFBuilder:

    def __init__(self, root):
        self.root = root
        self.root.title("PDF Builder")
        self.root.geometry("1000x600")
        self.root.iconbitmap("pdficon.ico")

        self.table = PDFTreeView(
            self.root,
            update_num_files=lambda x: self.status_bar.config(text=f"Total Files: {x}"),
        )

        self.create_toolbar()
        self.table.create_treeview()
        self.create_scrollbar()
        self.create_bottom_buttons()
        self.create_status_bar()
        self.root.bind("<Control-b>", self.build_pdf)
        self.root.bind("<Control-s>", lambda e: self.table.sorter.open_dialog())
        self.root.bind("<Control-d>", self.table.add_directory)
        self.root.bind("<Control-Shift-S>", self.table.auto_sort)
        self.root.bind("<BackSpace>", self.table.remove_selected)
        self.root.bind("<Control-q>", lambda x: _exit(self.root, x))
        self.root.bind("<Control-c>", self.table.clear_files)

        self.style = ttk.Style()
        self.style.theme_use("flatly")

    def create_toolbar(self):
        self.toolbar_frame = tk.Frame(self.root)
        self.toolbar_frame.pack(fill=tk.X)

        default_spacing = 4
        large_spacing = 100
        toolbar_buttons = [
            ("Clear", self.table.clear_files, default_spacing),
            ("Remove Selected", self.table.remove_selected, default_spacing),
            ("Load", self.load_state, large_spacing),
            ("Save", self.save_state, default_spacing),
            ("Add Files", self.table.add_files, large_spacing),
            ("Add Directory", self.table.add_directory, default_spacing),
            (
                "Sort Key",
                lambda: self.table.sorter.open_dialog(),
                large_spacing,
            ),  # Need lambda to avoid calling an out of date sorter
            (
                "Remove Selected Bookmarks",
                self.table.remove_selected_bookmarks,
                default_spacing,
            ),
        ]

        for button_text, command, spacing in toolbar_buttons:
            button = tk.Button(self.toolbar_frame, text=button_text, command=command)
            button.pack(side=tk.LEFT, padx=(spacing, 0), pady=2)

    def create_scrollbar(self):
        self.scrollbar = ttk.Scrollbar(
            self.root, orient=tk.VERTICAL, command=self.table.tree.yview
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.tree.configure(yscroll=self.scrollbar.set)

    def create_bottom_buttons(self):
        bottom_buttons = [
            ("Build PDF", self.build_pdf),
            ("Auto Sort", self.table.auto_sort),
            ("Move File ↓", self.table.move_file_down),
            ("Move File ↑", self.table.move_file_up),
        ]

        for button_text, command in bottom_buttons:
            button = tk.Button(self.root, text=button_text, command=command)
            button.pack(side=tk.BOTTOM, fill=tk.X)

    def create_status_bar(self):
        self.status_bar = tk.Label(
            self.root,
            text=f"Total Files: {self.table.num_files}",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def save_state(self):
        output_path = filedialog.asksaveasfilename(defaultextension=".pdfbuilder.json")
        if not output_path:
            return

        # Create a new window
        window = Toplevel(self.root)
        window.title("PDF Builder")

        # Variables for checkboxes
        save_files = tk.BooleanVar()
        save_sort_key = tk.BooleanVar()

        # Checkboxes
        tk.Checkbutton(window, text="Save files", variable=save_files).pack()
        tk.Checkbutton(window, text="Save sort key", variable=save_sort_key).pack()

        # Save button
        def save():
            if save_files.get():
                pdf_collection = self.table.pdfs.to_dict()
            else:
                pdf_collection = None

            if save_sort_key.get():
                sort_key = self.table.sorter.to_dict()
            else:
                sort_key = None

            to_save = json.dumps({"pdfs": pdf_collection, "sort_key": sort_key})

            with open(output_path, "w") as f:
                f.write(to_save)

            messagebox.showinfo("PDF Builder", "State has been saved successfully.")
            window.destroy()

        tk.Button(window, text="Save", command=save).pack()

    def load_state(self):
        input_path = filedialog.askopenfilename(
            filetypes=[("PDF Builder Saves", "*.pdfbuilder.json")]
        )

        with open(input_path, "r") as f:
            data = json.load(f)

        pdf_collection = data.get("pdfs")
        sort_key = data.get("sort_key")

        if (pdf_collection is None) != (sort_key is None):  # if only one is None
            if pdf_collection is not None:
                self.table.pdfs = PDFCollection.from_dict(pdf_collection)
            if sort_key is not None:
                self.table.sorter = PDFSortKey.from_dict(sort_key, self.root)
                self.table.sorter.open_dialog()

            self.table.update_tree()
            messagebox.showinfo("PDF Builder", "State has been loaded successfully.")
            return

        # Create a new window
        window = Toplevel(self.root)
        window.title("PDF Builder")

        # Variables for checkboxes
        load_files = tk.BooleanVar()
        load_sort_key = tk.BooleanVar()

        # Checkboxes
        if pdf_collection:
            tk.Checkbutton(window, text="Load files", variable=load_files).pack()
        if sort_key:
            tk.Checkbutton(window, text="Load sort key", variable=load_sort_key).pack()

        # Load button
        def load():
            if load_files.get() and pdf_collection:
                self.table.pdfs = PDFCollection.from_dict(pdf_collection)
            if load_sort_key.get() and sort_key:
                self.table.sorter = PDFSortKey.from_dict(sort_key, self.root)
                self.table.sorter.open_dialog()

            self.table.update_tree()
            messagebox.showinfo("PDF Builder", "State has been loaded successfully.")
            window.destroy()

        tk.Button(window, text="Load", command=load).pack()

        window.mainloop()

    def build_pdf(self, event=None):
        # Create a new dialog window
        new_window = tk.Toplevel(self.root)
        new_window.title("Export Options")
        new_window.geometry("300x200")  # Set window size

        # create a container for each line
        lines = []
        for _ in range(4):
            line = tk.Frame(new_window)
            line.pack(pady=10)  # fill=tk.X
            lines.append(line)

        # Add "Add Page Numbers" option
        add_page_numbers_var = tk.BooleanVar(lines[0])
        add_page_numbers_check = tk.Checkbutton(
            new_window, text="Add Page Numbers", variable=add_page_numbers_var
        )
        add_page_numbers_check.select()  # Set default to checked
        add_page_numbers_check.pack(in_=lines[0])

        # Add "Padding" option
        padding_var = tk.StringVar(lines[1])
        padding_var.set("20")  # Set default padding
        padding_label = tk.Label(new_window, text="Page Number Bottom Padding:")
        padding_label.pack(in_=lines[1], side=tk.LEFT)
        padding_entry = tk.Entry(
            new_window, textvariable=padding_var, width=2
        )  # Set the width of the entry widget
        padding_entry.pack(in_=lines[1], side=tk.LEFT, padx=5)

        # Add "Font Size" option
        font_size_var = tk.StringVar(lines[2])
        font_size_var.set("10")  # Set default font size
        font_size_label = tk.Label(new_window, text="Font Size:")
        font_size_label.pack(in_=lines[2], side=tk.LEFT)
        font_size_entry = tk.Entry(
            new_window, textvariable=font_size_var, width=2
        )  # Set the width of the entry widget
        font_size_entry.pack(in_=lines[2], side=tk.LEFT, padx=5)

        # Add "Export" button
        export_button = tk.Button(
            new_window,
            text="Export",
            command=lambda: self.export_pdf(
                new_window,
                add_page_numbers_var.get(),
                int(padding_var.get()),
                int(font_size_var.get()),
            ),
        )
        export_button.pack()
        new_window.bind("<Return>", lambda e: export_button.invoke())
        new_window.focus_set()

    def export_pdf(self, window, add_page_numbers, y_padding, font_size):
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if output_path:
            window.destroy()
            try:
                progress_object, progress_window = self.export_progress_window()
                for progress in self.table.pdfs.build_pdf(
                    output_path=output_path,
                    page_numbers=add_page_numbers,
                    y_padding=y_padding,
                    font_size=font_size,
                ):
                    progress_object["value"] = progress
                    progress_object.update()

                self.table.update_tree()

                progress_window.destroy()

                self.table.alert_failed_files()
                messagebox.showinfo("PDF Builder", "PDF has been built successfully.")
            except Exception as e:
                window.destroy()
                progress_window.destroy()
                messagebox.showerror("Error", str(e))
                raise e

    def export_progress_window(self):
        progress_window = Toplevel(self.root)
        progress_window.title("Building PDF")
        progress_window.geometry("300x50")
        progress = ttk.Progressbar(progress_window, length=200, mode="determinate")
        progress.pack()
        return progress, progress_window
