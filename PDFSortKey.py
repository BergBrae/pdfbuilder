from tkinter import simpledialog, Text, Button, Toplevel
import tkinter as tk

from PDFClassification import PDFClassification
from RegexGenerator import RegexGenerator


class PDFSortKey:
    def __init__(self, root):
        self.root = root
        self.dialog = Toplevel(self.root)
        self.dialog.title("Sort Key")
        self.dialog.destroy()

        self.sort_key: list[PDFClassification] = [PDFClassification(regex="")]
        self.regex_generator = RegexGenerator(self.root)

    def __iter__(self):
        for key in self.sort_key:
            if not key.is_empty():
                yield key

    def open_dialog(self, event=None):
        if not self.dialog.winfo_exists():
            self.dialog = Toplevel(self.root)
            self.dialog.title("Sort Key")

        self.dialog.focus_set()

        # clear dialog
        for widget in self.dialog.winfo_children():
            widget.destroy()

        self.dialog_frame = tk.Frame(self.dialog)

        header_text = (
            f"Applies to: {' '*60} Bookmark Title: {' '*19} Regex Expression: {' '*26}"
        )

        containers = [tk.Label(self.dialog_frame, text=header_text)]
        # pack with left justified
        containers[0].pack()
        for i, key in enumerate(self.sort_key):
            frame = key.to_frame(self.dialog_frame)
            delete_key = Button(
                frame, text="Delete", command=lambda i=i: self.delete_key(i, frame)
            )
            delete_key.pack(side=tk.RIGHT)
            containers.append(frame)
            containers[-1].pack(pady=5)
        self.dialog_frame.pack()

        buttons_frame = tk.Frame(self.dialog)

        self.add_key_button = Button(
            buttons_frame, text="Add Key", command=self.add_key
        )
        self.add_key_button.pack(side=tk.LEFT)
        self.generate_regex_button = Button(
            buttons_frame, text="Generate Regex", command=self.generate_regex
        )
        self.generate_regex_button.pack(side=tk.LEFT, padx=5)

        buttons_frame.pack()

    def generate_regex(self):
        self.regex_generator.open_dialog()
        self.regex_generator.dialog.wait_window()
        self.open_dialog()

    def add_key(self):
        self.sort_key.append(PDFClassification())
        self.open_dialog()

    def delete_key(self, i, frame):
        self.sort_key.pop(i)
        frame.destroy()
        self.open_dialog()

    def to_dict(self):
        return [key.to_dict() for key in self.sort_key]

    @classmethod
    def from_dict(cls, data: list[dict], root):
        sort_key = cls(root)
        sort_key.sort_key = [PDFClassification.from_dict(d) for d in data]
        return sort_key


if __name__ == "__main__":
    root = tk.Tk()
    pdf_sort_key = PDFSortKey(root)
    open_button = Button(root, text="Open", command=pdf_sort_key.open_dialog)
    open_button.pack()
    root.mainloop()
