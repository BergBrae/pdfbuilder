import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import os
import json
from PyPDF2 import PdfMerger, PdfReader
import pickle as pkl
from copy import deepcopy
from glob import glob
import ttkbootstrap as ttk

from PDFFile import PDFFile
from PDFCollection import PDFCollection
from open_file import open_file
from PDFSortKey import PDFSortKey


def _exit(event=None):
    root.quit()


class PDFBuilder:

    def __init__(self, root):
        self.root = root
        self.root.title("PDF Builder")
        self.root.geometry("1000x600")
        # self.root.iconbitmap("pdficon.ico")

        self.tree_items = set()
        self.num_files = 0
        self.pdfs = PDFCollection()

        self.sorter = PDFSortKey(self.root)

        self.create_toolbar()
        self.create_treeview()
        self.create_scrollbar()
        self.create_bottom_buttons()
        self.create_status_bar()
        self.root.bind("<Control-b>", self.build_pdf)
        self.root.bind("<Control-s>", self.sorter.open_dialog)
        self.root.bind("<Control-d>", self.add_directory)
        self.root.bind("<Control-Shift-S>", self.auto_sort)
        self.root.bind("<BackSpace>", self.remove_selected)
        self.root.bind("<Control-q>", _exit)
        self.root.bind("<Control-c>", self.clear_files)
        self.tree.bind("<Return>", self.edit_bookmark)

        self.style = ttk.Style()
        self.style.theme_use("flatly")

    def create_toolbar(self):
        self.toolbar_frame = tk.Frame(self.root)
        self.toolbar_frame.pack(fill=tk.X)

        toolbar_buttons = [
            ("Clear", self.clear_files),
            ("Remove Selected", self.remove_selected),
            ("Load", self.load_state),
            ("Save", self.save_state),
            ("Add Files", self.add_files),
            ("Add Directory", self.add_directory),
            ("Sort Key", self.sorter.open_dialog),
            # ("Settings", self.open_settings), # Not yet implemented
        ]

        for button_text, command in toolbar_buttons:
            button = tk.Button(self.toolbar_frame, text=button_text, command=command)
            button.pack(side=tk.LEFT, padx=2, pady=2)

    def create_treeview(self):
        self.tree = ttk.Treeview(
            self.root,
            columns=("File Name", "Path", "Sort Queries", "Bookmark"),
            show="headings",
        )
        self.tree.heading("File Name", text="File Name")
        self.tree.heading("Path", text="Path")
        self.tree.heading("Sort Queries", text="Sort Queries")
        self.tree.heading("Bookmark", text="Bookmark")
        self.tree.column("File Name", width=200)
        self.tree.column("Path", width=200)
        self.tree.column("Sort Queries", width=200)
        self.tree.column("Bookmark", width=200)
        self.tree.bind("<Double-1>", self.double_click)
        self.tree.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

    def double_click(self, event):
        column = self.tree.identify_column(event.x)
        if column == "#4":
            self.edit_bookmark(event)
        else:
            self.open_file(event)

    def edit_bookmark(self, event):
        row_id = self.tree.focus()
        column = "#4"
        column_idx = int(column[1]) - 1

        # We only want to edit if we're on an item
        if row_id:
            x, y, width, height = self.tree.bbox(row_id, column)
            pady = height // 2

            # create and position entry
            text = self.tree.item(row_id, "values")[column_idx]
            entry = tk.Entry(self.tree)
            entry.insert(0, text)
            entry.place(x=x, y=y + pady, anchor="w")
            # set focus and selection
            entry.focus_set()
            # unbind double click to prevent re-entry
            self.root.unbind("<BackSpace>")

            def save_edit(event):
                try:
                    filepath = self.tree.item(row_id).get("values")[1]
                    pdf = self.pdfs.get_file_by_path(filepath)
                    self.pdfs.bookmarks[pdf] = entry.get()
                    entry.destroy()
                    self.update_tree()
                except Exception as e:
                    raise e
                finally:
                    entry.destroy()
                    self.root.bind("<BackSpace>", self.remove_selected)

            entry.bind("<Return>", save_edit)
            entry.bind("<FocusOut>", save_edit)

    def create_scrollbar(self):
        self.scrollbar = ttk.Scrollbar(
            self.root, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=self.scrollbar.set)

    def create_bottom_buttons(self):
        bottom_buttons = [
            ("Build PDF", self.build_pdf),
            ("Auto Sort", self.auto_sort),
            ("Move File ↓", self.move_file_down),
            ("Move File ↑", self.move_file_up),
        ]

        for button_text, command in bottom_buttons:
            button = tk.Button(self.root, text=button_text, command=command)
            button.pack(side=tk.BOTTOM, fill=tk.X)

    def create_status_bar(self):
        self.status_bar = tk.Label(
            self.root,
            text=f"Total Files: {self.num_files}",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def clear_files(self, event=None):
        self.pdfs.clear_files()
        self.update_tree()

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if files:
            pdf_files = [f for f in files if f.lower().endswith(".pdf")]
            for filepath in pdf_files:
                self.pdfs.add_file(PDFFile(filepath))
            self.update_tree()

    def remove_selected(self, event=None):
        selected_items = self.tree.selection()
        for item in selected_items:
            filepath = self.tree.item(item)["values"][1]
            self.pdfs.remove_by_path(filepath)
        self.update_tree()

    def add_directory(self, event=None):
        directory = filedialog.askdirectory()
        if directory:
            pdf_files = glob(
                os.path.join(directory, "**/*.pdf"), recursive=True
            ) + glob(os.path.join(directory, "**/*.PDF"), recursive=True)
            for file in pdf_files:
                try:
                    self.pdfs.add_file(PDFFile(file))
                except Exception as e:
                    print(f"Error adding file: {file}")
            self.update_tree()

    def save_state(self):
        output_path = filedialog.asksaveasfilename(defaultextension=".pdfbuilder.json")
        # readers cannot be pickled
        self.pdfs.clear_readers()
        to_save = (self.pdfs, self.sorter.sort_key)

        if output_path:
            pdf_collection = self.pdfs.to_dict()
            sort_key = self.sorter.to_dict()
            to_save = json.dumps({"pdfs": pdf_collection, "sort_key": sort_key})
            with open(output_path, "w") as f:
                f.write(to_save)
            messagebox.showinfo("PDF Builder", "State has been saved successfully.")

    def load_state(self):
        input_path = filedialog.askopenfilename(
            filetypes=[("PDF Builder Saves", "*.pdfbuilder.json")]
        )

        with open(input_path, "r") as f:
            data = json.load(f)
        pdf_collection = data["pdfs"]
        sort_key = data["sort_key"]

        self.pdfs = PDFCollection.from_dict(pdf_collection)
        del self.sorter
        self.sorter = PDFSortKey.from_dict(sort_key, self.root)

        self.update_tree()

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
            try:
                progress_object, progress_window = self.export_progress_window()
                for progress in self.pdfs.build_pdf(
                    output_path=output_path,
                    page_numbers=add_page_numbers,
                    y_padding=y_padding,
                    font_size=font_size,
                ):
                    progress_object["value"] = progress
                    progress_object.update()

                window.destroy()
                progress_window.destroy()

                messagebox.showinfo("PDF Builder", "PDF has been built successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                raise e

    def export_progress_window(self):
        progress_window = Toplevel(self.root)
        progress_window.title("Building PDF")
        progress_window.geometry("300x50")
        progress = ttk.Progressbar(progress_window, length=200, mode="determinate")
        progress.pack()
        return progress, progress_window

    def auto_sort(self, event=None):
        not_matched = self.pdfs.sort(self.sorter.sort_key)
        self.update_tree()
        num_not_matched = len(not_matched)

        # Highlight and notify of files that did not match the sort key
        non_matched_ids = []
        for pdf in not_matched:
            item_id = self.get_item_id_from_value(self.tree, 1, pdf.path)
            non_matched_ids.append(item_id)

        if num_not_matched > 0:
            self.tree.selection_set(non_matched_ids)

            messagebox.showinfo(
                "PDF Builder",
                f"{num_not_matched} files did not match the sort key",
            )

    def get_item_id_from_value(self, tree, column, value):
        for item_id in self.tree.get_children():
            if tree.item(item_id)["values"][column] == value:
                return item_id
        return None

    def move_file_down(self, event=None):
        selected_items = self.tree.selection()
        selected_ids = [self.tree.item(item)["values"][0] for item in selected_items]
        for selected_item in reversed(selected_items):
            item_index = self.tree.index(selected_item)
            self.pdfs.move_file_down(item_index)
        self.update_tree()
        for id in selected_ids:
            item_id = self.get_item_id_from_value(self.tree, 0, id)
            self.tree.selection_add(item_id)

    def move_file_up(self, event=None):
        selected_items = self.tree.selection()
        selected_ids = [self.tree.item(item)["values"][0] for item in selected_items]
        for selected_item in selected_items:
            item_index = self.tree.index(selected_item)
            self.pdfs.move_file_up(item_index)
        self.update_tree()
        for id in selected_ids:
            item_id = self.get_item_id_from_value(self.tree, 0, id)
            self.tree.selection_add(item_id)

    def open_file(self, event):
        item = self.tree.focus()
        file_path = self.tree.item(item)["values"][1]
        open_file(file_path)

    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        table_values = self.pdfs.get_tkinter_table_data()
        for values in table_values:
            item_id = self.tree.insert("", "end", values=values)

        self.status_bar.config(text=f"Total Files: {self.pdfs.num_files}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFBuilder(root)
    root.mainloop()
