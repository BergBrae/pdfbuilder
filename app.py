import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import os
import json

from sorting import SortKeyDialog
from build import build_pdf

class PDFBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title('PDF Builder')
        self.root.geometry("1000x600")
        self.root.iconbitmap('pdficon.ico')

        self.tree_items = set()
        self.num_files = 0
        self.sorter = SortKeyDialog(self.root)

        self.create_toolbar()
        self.create_treeview()
        self.create_scrollbar()
        self.create_bottom_buttons()
        self.create_status_bar()

    def create_toolbar(self):
        self.toolbar_frame = tk.Frame(self.root)
        self.toolbar_frame.pack(fill=tk.X)

        toolbar_buttons = [
            ('Clear', self.clear_files),
            ('Remove Selected', self.remove_selected),
            ('Load', self.load_state),
            ('Save', self.save_state),
            ('Add Files', self.add_files),
            ('Add Directory', self.add_directory),
            ('Sort Key', self.sort_key),
            ('Settings', self.open_settings)
        ]

        for button_text, command in toolbar_buttons:
            button = tk.Button(self.toolbar_frame, text=button_text, command=command)
            button.pack(side=tk.LEFT, padx=2, pady=2)

    def create_treeview(self):
        self.tree = ttk.Treeview(self.root, columns=('File Name', 'Path'), show='headings')
        self.tree.heading('File Name', text='File Name')
        self.tree.heading('Path', text='Path')
        self.tree.column('File Name', width=200)
        self.tree.column('Path', width=200)
        self.tree.bind('<Double-1>', self.open_file)
        self.tree.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

    def create_scrollbar(self):
        self.scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=self.scrollbar.set)

    def create_bottom_buttons(self):
        bottom_buttons = [
            ('Build PDF', self.build_pdf),
            ('Auto Sort', self.auto_sort),
            ('Move File ↓', self.move_file_down),
            ('Move File ↑', self.move_file_up)
        ]

        for button_text, command in bottom_buttons:
            button = tk.Button(self.root, text=button_text, command=command)
            button.pack(side=tk.BOTTOM, fill=tk.X)

    def create_status_bar(self):
        self.status_bar = tk.Label(self.root, text=f'Total Files: {self.num_files}', bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def clear_files(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree_items.clear()
        self.update_num_files()

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if files:
            pdf_files = [f for f in files if f.lower().endswith('.pdf')]
            for file in pdf_files:
                normalized_file = os.path.normpath(file)
                values = (os.path.basename(normalized_file), normalized_file)
                self.add_item_to_tree(values)
        self.update_num_files()

    def remove_selected(self):
        selected_items = self.tree.selection()
        for item in selected_items:
            self.tree_items.remove(self.tree.item(item)['values'][1])
            self.tree.delete(item)
        self.update_num_files()

    def add_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
            for file in pdf_files:
                full_path = os.path.join(directory, file)
                normalized_path = os.path.normpath(full_path)
                values = (os.path.basename(normalized_path), normalized_path)
                self.add_item_to_tree(values)
        self.update_num_files()

    def update_num_files(self):
        items = self.tree.get_children('')
        self.num_files = len(items)
        self.status_bar.config(text=f'Total Files: {self.num_files}')

    def sort_key(self):
        pass

    def open_settings(self):
        new_window = Toplevel(None)
        new_window.title("Settings")
        # save button
        save_button = tk.Button(new_window, text="Save")
        save_button.pack(side=tk.BOTTOM)

    def save_state(self):
        items = self.tree.get_children()
        file_paths = [self.tree.item(item)['values'][1] for item in items]
        output_path = filedialog.asksaveasfilename(defaultextension=".json")

        with open(output_path, 'w') as f:
            json.dump(file_paths, f)

    def load_state(self):
        input_path = filedialog.askopenfilename(filetypes=[("PDF Builder Saves", "*.json")])

        with open(input_path, 'r') as f:
            file_paths = json.load(f)

        does_not_exist = []

        self.clear_files()
        for file_path in file_paths:
            values = (os.path.basename(file_path), file_path)
            try:
                self.add_item_to_tree(values, check_if_exists=True)
            except FileNotFoundError as e:
                does_not_exist.append(file_path)

        if does_not_exist:
            paths_text = '\n'.join(does_not_exist)
            messagebox.showwarning('Warning', f'The following files do not exist:\n{paths_text}')

    def build_pdf(self):
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if output_path:
                items = self.tree.get_children()
                paths = [self.tree.item(item)['values'][1] for item in items]
                build_pdf(paths, output_path)
                messagebox.showinfo('PDF Builder', 'PDF has been built successfully.')

    def auto_sort(self):
        items = self.tree.get_children('')
        values = [self.tree.item(item)['values'] for item in items]

        sorted_items = self.sorter.sort(values)
        
        self.clear_files()
        for values in sorted_items:
            self.add_item_to_tree(values)

    def move_file_down(self):
        selected_items = self.tree.selection()
        for selected_item in reversed(selected_items):
            item_index = self.tree.index(selected_item)
            if item_index < len(self.tree.get_children()) - 1:
                self.tree.move(selected_item, '', item_index + 1)

    def move_file_up(self):
        selected_items = self.tree.selection()
        for selected_item in selected_items:
            item_index = self.tree.index(selected_item)
            if item_index > 0:
                self.tree.move(selected_item, '', item_index - 1)

    def open_file(self, event):
        item = self.tree.focus()
        file_path = self.tree.item(item)['values'][1]
        os.startfile(file_path)

    def add_item_to_tree(self, item, check_if_exists=False):
        if check_if_exists and not os.path.exists(item[1]):
            raise FileNotFoundError(f"The file '{item[1]}' does not exist.")

        if item[1] not in self.tree_items:
            self.tree.insert('', 'end', values=item)
            self.tree_items.add(item[1])

        self.update_num_files()


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFBuilder(root)
    root.mainloop()
