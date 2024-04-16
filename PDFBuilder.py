import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import os
import json
from PyPDF2 import PdfMerger, PdfReader

from sorting import SortKeyDialog
from PDFFile import PDFFile
from PDFCollection import PDFCollection


class PDFBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Builder")
        self.root.geometry("1000x600")
        # self.root.iconbitmap("pdficon.ico")

        self.tree_items = set()
        self.num_files = 0
        self.sorter = SortKeyDialog(self.root)
        self.pdfs = PDFCollection()

        self.create_toolbar()
        self.create_treeview()
        self.create_scrollbar()
        self.create_bottom_buttons()
        self.create_status_bar()

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
            ("Sort Key", self.sort_key),
            ("Settings", self.open_settings),
        ]

        for button_text, command in toolbar_buttons:
            button = tk.Button(self.toolbar_frame, text=button_text, command=command)
            button.pack(side=tk.LEFT, padx=2, pady=2)

    def create_treeview(self):
        self.tree = ttk.Treeview(
            self.root, columns=("File Name", "Path", "Primary Sort"), show="headings"
        )
        self.tree.heading("File Name", text="File Name")
        self.tree.heading("Path", text="Path")
        self.tree.heading("Primary Sort", text="Primary Sort")
        self.tree.column("File Name", width=200)
        self.tree.column("Path", width=200)
        self.tree.column("Primary Sort", width=200)
        self.tree.bind("<Double-1>", self.open_file)
        self.tree.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

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

    def clear_files(self):
        self.pdfs.clear_files()
        self.update_tree()

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if files:
            pdf_files = [f for f in files if f.lower().endswith(".pdf")]
            for filepath in pdf_files:
                self.pdfs.add_file(PDFFile(filepath))
            self.update_tree()

    def remove_selected(self):
        selected_items = self.tree.selection()
        for item in selected_items:
            filepath = self.tree.item(item)["values"][1]
            self.pdfs.remove_by_path(filepath)
        self.update_tree()

    def add_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            pdf_files = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith(".pdf"):
                        pdf_files.append(os.path.join(root, file))
            for file in pdf_files:
                full_path = os.path.join(directory, file)
                self.pdfs.add_file(PDFFile(full_path))
            self.update_tree()

    def sort_key(self):
        self.sort_dialog = SortKeyDialog(self.root)
        self.sort_dialog.open_dialog()
        self.root.wait_window(self.sort_dialog.dialog)
        self.sorter._sort_key = self.sort_dialog.sort_key

    def open_settings(self):
        new_window = Toplevel(None)
        new_window.title("Settings")
        # save button
        save_button = tk.Button(new_window, text="Save")
        save_button.pack(side=tk.BOTTOM)

    def save_state(self):
        file_paths = [pdf.path for pdf in self.pdfs.files]
        output_path = filedialog.asksaveasfilename(defaultextension=".json")

        with open(output_path, "w") as f:
            json.dump(file_paths, f)

    def load_state(self):
        input_path = filedialog.askopenfilename(
            filetypes=[("PDF Builder Saves", "*.json")]
        )

        with open(input_path, "r") as f:
            file_paths = json.load(f)

        does_not_exist = []

        for file_path in file_paths:
            try:
                pdf = PDFFile(file_path, check_exists=True)
                self.pdfs.add_file(pdf)
            except FileNotFoundError as e:
                does_not_exist.append(file_path)

        self.update_tree()

        if does_not_exist:
            paths_text = "\n".join(does_not_exist)
            messagebox.showwarning(
                "Warning", f"The following files do not exist:\n{paths_text}"
            )

    def build_pdf(self):
        # Create a new dialog window
        new_window = tk.Toplevel(self.root)
        new_window.title("Export Options")
        new_window.geometry("300x200")  # Set window size

        # Add "Add Page Numbers" option
        add_page_numbers_var = tk.BooleanVar()
        add_page_numbers_check = tk.Checkbutton(
            new_window, text="Add Page Numbers", variable=add_page_numbers_var
        )
        add_page_numbers_check.select()  # Set default to checked
        add_page_numbers_check.pack()

        # Add "Padding" option
        padding_var = tk.StringVar()
        padding_var.set("20")  # Set default padding
        padding_label = tk.Label(new_window, text="Page Number Padding:")
        padding_label.pack()
        padding_entry = tk.Entry(
            new_window, textvariable=padding_var, width=2
        )  # Set the width of the entry widget
        padding_entry.pack()

        # Add "Export" button
        export_button = tk.Button(
            new_window,
            text="Export",
            command=lambda: self.export_pdf(
                new_window, add_page_numbers_var.get(), int(padding_var.get())
            ),
        )
        export_button.pack()

    def export_pdf(self, window, add_page_numbers, padding):
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if output_path:
            try:
                self.pdfs.build_pdf(
                    output_path=output_path,
                    page_numbers=add_page_numbers,
                    padding=padding,
                )
                messagebox.showinfo("PDF Builder", "PDF has been built successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        window.destroy()

    def auto_sort(self):
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
                f"{num_not_matched} files did not match the sort key:\n\n{'\n'.join([pdf.filename for pdf in not_matched])}",
            )

    def get_item_id_from_value(self, tree, column, value):
        for item_id in self.tree.get_children():
            if tree.item(item_id)["values"][column] == value:
                return item_id
        return None

    def move_file_down(self):
        selected_items = self.tree.selection()
        selected_ids = [self.tree.item(item)["values"][0] for item in selected_items]
        for selected_item in reversed(selected_items):
            item_index = self.tree.index(selected_item)
            self.pdfs.move_file_down(item_index)
        self.update_tree()
        for id in selected_ids:
            item_id = self.get_item_id_from_value(self.tree, 0, id)
            self.tree.selection_add(item_id)

    def move_file_up(self):
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
        os.startfile(file_path)

    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        for pdf in self.pdfs.files:
            item_id = self.tree.insert("", "end", values=pdf.values)

        self.status_bar.config(text=f"Total Files: {self.pdfs.num_files}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFBuilder(root)
    root.mainloop()
