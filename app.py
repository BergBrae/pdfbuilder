import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import os
import json
from PyPDF2 import PdfMerger, PdfReader

from sorting import SortKeyDialog
from build import build_pdf


class PDFFile:
    def __init__(self, path: str, num_pages=None, open_file=True, check_exists=True):
        if check_exists and not os.path.exists(path):
            raise FileNotFoundError(f"The file '{path}' does not exist.")
        self.path = os.path.normpath(path)
        self.filename = os.path.basename(path)
        if open_file:
            self.reader = PdfReader(open(self.path, "rb"), strict=False)
            self.num_pages = len(self.reader.pages)
        else:
            self.num_pages, self.reader = None, None

    def __hash__(self):
        return hash(self.path)

    def __repr__(self) -> str:
        return f"PDFFile({self.filename})"

    def __eq__(self, other) -> bool:
        return self.path == other.path

    @property
    def values(self):
        return (self.filename, self.path, self.num_pages)


class PDFCollection:
    def __init__(self):
        self.files = []
        self.num_files = 0
        self.total_pages = 0

    def __len__(self):
        return self.num_files

    def __contains__(self, pdf: PDFFile):
        return pdf in self.files

    def add_file(self, pdf: PDFFile):
        if pdf not in self:
            self.files.append(pdf)
            self.num_files += 1

    def remove_file(self, pdf: PDFFile):
        self.files.remove(pdf)
        self.num_files -= 1

    def remove_by_path(self, path: str):
        for pdf in self.files:
            if pdf.path == path:
                self.files.remove(pdf)
                self.num_files -= 1

    def clear_files(self):
        self.files.clear()
        self.num_files = 0

    def get_file_by_path(self, path: str):
        for pdf in self.files:
            if pdf.path == path:
                return pdf

    def sort(self, sort_key: list[str]):
        sorted_files = []
        for key in sort_key:
            for pdf in self.files:
                if key in pdf.filename:
                    sorted_files.append(pdf)
        not_matched = list(set(self.files) - set(sorted_files))
        self.files = sorted_files + not_matched
        return not_matched

    def get_tkinter_table_data(self):
        return [pdf.values for pdf in self.files]

    def move_file_up(self, index):
        if index > 0:
            self.files[index], self.files[index - 1] = (
                self.files[index - 1],
                self.files[index],
            )

    def move_file_down(self, index):
        if index < len(self.files) - 1:
            self.files[index], self.files[index + 1] = (
                self.files[index + 1],
                self.files[index],
            )

    def build_pdf(self, output_path: str):
        # filepaths is a list of tuples (filename, path)
        merger = PdfMerger()
        for pdf in self.files:
            merger.append(pdf.path)

        merger.write(output_path)
        merger.close()


class PDFBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Builder")
        self.root.geometry("1000x600")
        self.root.iconbitmap("pdficon.ico")

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

        self.show_pages_var = tk.BooleanVar(value=True)
        self.show_pages_check = tk.Checkbutton(
            self.toolbar_frame, text="Show # Pages", variable=self.show_pages_var
        )
        self.show_pages_check.pack(side=tk.LEFT, padx=2, pady=2)

    def create_treeview(self):
        self.tree = ttk.Treeview(
            self.root, columns=("File Name", "Path", "# Pages"), show="headings"
        )
        self.tree.heading("File Name", text="File Name")
        self.tree.heading("Path", text="Path")
        self.tree.heading("# Pages", text="# Pages")
        self.tree.column("File Name", width=200)
        self.tree.column("Path", width=200)
        self.tree.column("# Pages", width=10)
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
                self.pdfs.add_file(
                    PDFFile(filepath, open_file=self.show_pages_var.get())
                )
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
            pdf_files = [f for f in os.listdir(directory) if f.lower().endswith(".pdf")]
            for file in pdf_files:
                full_path = os.path.join(directory, file)
                self.pdfs.add_file(
                    PDFFile(full_path, open_file=self.show_pages_var.get())
                )
            self.update_tree()

    def sort_key(self):
        self.sort_dialog = SortKeyDialog(self.root)
        self.sort_dialog.open_dialog()
        self.root.wait_window(self.sort_dialog.dialog)

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
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if output_path:
            try:
                self.pdfs.build_pdf(output_path)
                messagebox.showinfo("PDF Builder", "PDF has been built successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def auto_sort(self):
        not_matched = self.pdfs.sort(self.sorter.sort_key)
        self.update_tree()
        num_not_matched = len(not_matched)

        non_matched_ids = []
        for pdfs in not_matched:
            item_id = self.get_item_id_from_value(self.tree, 1, pdfs.path)
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
