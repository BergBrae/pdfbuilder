import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import os
import ttkbootstrap as ttk
import tkinter as tk
from tkinter import messagebox, filedialog

from PDFFile import PDFFile
from PDFCollection import PDFCollection
from open_file import open_file
from PDFSortKey import PDFSortKey
from PDFSortKey import PDFSortKey


class PDFTreeView:
    def __init__(self, root, update_num_files: callable):
        self.style = ttk.Style()
        self.style.theme_use("flatly")

        self.root = root
        self.pdfs = PDFCollection()
        self.sorter = PDFSortKey(self.root)
        self.tree_items = set()
        self.alerted_failed_files = set()
        self.update_num_files = update_num_files

        self.tree = ttk.Treeview(
            self.root,
            columns=("File Name", "Path", "Bookmark"),
            show="headings",
        )

        self.tree.bind("<Return>", self.edit_bookmark)
        self.tree.bind("<Button-3>", self.show_file_text)
        self.tree.bind(
            "<Control-a>",
            lambda e: self.tree.selection_set(self.tree.get_children()),
        )
        self.tree.bind("<Control-Up>", self.move_file_up)
        self.tree.bind("<Control-Down>", self.move_file_down)

    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        table_values = self.pdfs.get_tkinter_table_data()
        for values in table_values:
            self.tree.insert("", "end", values=values)

        self.update_num_files(self.num_files)

    def create_treeview(self):
        self.tree.heading("File Name", text="File Name")
        self.tree.heading("Path", text="Path")
        self.tree.heading("Bookmark", text="Bookmark")
        self.tree.column("File Name", width=200)
        self.tree.column("Path", width=200)
        self.tree.column("Bookmark", width=200)
        self.tree.bind("<Double-1>", self.double_click)
        self.tree.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

    def double_click(self, event=None):
        column = self.tree.identify_column(event.x)
        if column == "#3":
            self.edit_bookmark(event)
        else:
            self.open_file(event)

    def edit_bookmark(self, event=None):
        row_id = self.tree.focus()
        column = "#3"
        column_idx = int(column[1]) - 1

        # We only want to edit if we're on an item
        if row_id:
            x, y, width, height = self.tree.bbox(row_id, column)
            pady = height // 2

            # create and position entry
            text = self.tree.item(row_id, "values")[column_idx]
            entry = tk.Entry(self.tree, width=40)  # Adjust the width as desired
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

    def open_file(self, event=None):
        item = self.tree.focus()
        file_path = self.tree.item(item)["values"][1]
        open_file(file_path)

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
            pdf_files = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith(".pdf"):
                        pdf_files.append(os.path.normpath(os.path.join(root, file)))
            for file in pdf_files:
                try:
                    self.pdfs.add_file(PDFFile(file))
                except Exception as e:
                    print(f"Error adding file: {file}")
            self.update_tree()

    def remove_selected_bookmarks(self, event=None):
        selected_items = self.tree.selection()
        for item in selected_items:
            filepath = self.tree.item(item)["values"][1]
            pdf = self.pdfs.get_file_by_path(filepath)
            self.pdfs.bookmarks[pdf] = ""
        self.update_tree()

    def show_file_text(self, event=None):
        if event is None:
            items = self.tree.selection()
        else:
            items = [self.tree.identify_row(event.y)]
        for item in items:
            filepath = self.tree.item(item)["values"][1]
            pdf = self.pdfs.get_file_by_path(filepath)
            text = "\n\n".join(pdf.text)
            text_window = Toplevel(self.root)
            text_window.title(pdf.filename)
            text_window.geometry("800x600")
            text_widget = tk.Text(text_window)
            text_widget.insert(tk.END, text)
            text_widget.pack(expand=True, fill=tk.BOTH)

    def move_file_down(self, event=None):
        selected_items = self.tree.selection()
        selected_ids = [self.tree.item(item)["values"][0] for item in selected_items]
        for selected_item in reversed(selected_items):
            item_index = self.tree.index(selected_item)
            self.pdfs.move_file_down(item_index)
        self.update_tree()
        for id in selected_ids:
            item_id = self.get_item_id_from_value(0, id)
            self.tree.selection_add(item_id)

    def move_file_up(self, event=None):
        selected_items = self.tree.selection()
        selected_ids = [self.tree.item(item)["values"][0] for item in selected_items]
        for selected_item in selected_items:
            item_index = self.tree.index(selected_item)
            self.pdfs.move_file_up(item_index)
        self.update_tree()
        for id in selected_ids:
            item_id = self.get_item_id_from_value(0, id)
            self.tree.selection_add(item_id)

    def get_item_id_from_value(self, column, value):
        for item_id in self.tree.get_children():
            if self.tree.item(item_id)["values"][column] == value:
                return item_id
        return None

    def auto_sort(self, event=None):
        not_matched = self.pdfs.sort(self.sorter.sort_key)
        self.update_tree()
        self.alert_failed_files()
        num_not_matched = len(not_matched)

        # Highlight and notify of files that did not match the sort key
        non_matched_ids = []
        for pdf in not_matched:
            item_id = self.get_item_id_from_value(1, pdf.path)
            non_matched_ids.append(item_id)

        if num_not_matched > 0:
            self.tree.selection_set(non_matched_ids)

            messagebox.showinfo(
                "PDF Builder",
                f"{num_not_matched} files did not match the sort key",
            )

    def alert_failed_files(self):
        to_alert = self.pdfs.failed_files - self.alerted_failed_files
        failed_files = [f"{pdf.filename}: {pdf.error}" for pdf in to_alert]
        if failed_files:
            num_failed = len(failed_files)
            failed_files = "\n\n".join(failed_files)
            self.alerted_failed_files = self.alerted_failed_files.union(to_alert)
            messagebox.showinfo(
                "PDF Builder",
                f"The following {num_failed} files were removed because they failed to open:\n\n{failed_files}",
            )

    @property
    def num_files(self):
        return len(self.pdfs)
