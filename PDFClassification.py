from tkinter import simpledialog, Text, Button, Toplevel
import tkinter as tk


class PDFClassification:
    def __init__(
        self,
        regex: str = "",
        applies_to_directory: bool = False,
        applies_to_filename: bool = False,
        applies_to_document: bool = False,
        Bookmark: str = "",
    ):
        self.applies_to_directory = applies_to_directory
        self.applies_to_filename = applies_to_filename
        self.applies_to_document = applies_to_document
        self.regex = regex
        self.Bookmark = Bookmark

        self.directory_var = tk.BooleanVar()
        self.filename_var = tk.BooleanVar()
        self.document_var = tk.BooleanVar()
        self.bookmark_var = tk.StringVar()
        self.regex_var = tk.StringVar()

        self.directory_var.set(self.applies_to_directory)
        self.filename_var.set(self.applies_to_filename)
        self.document_var.set(self.applies_to_document)
        self.bookmark_var.set(self.Bookmark)
        self.regex_var.set(self.regex)

    def to_frame(self, root: tk.Tk):
        frame = tk.Frame(root)

        self.directory_checkbox = tk.Checkbutton(
            frame, text="Directory", variable=self.directory_var
        )
        self.directory_checkbox.pack(side=tk.LEFT)

        self.filename_checkbox = tk.Checkbutton(
            frame, text="Filename", variable=self.filename_var
        )
        self.filename_checkbox.pack(side=tk.LEFT)

        self.document_checkbox = tk.Checkbutton(
            frame, text="Document", variable=self.document_var
        )
        self.document_checkbox.pack(side=tk.LEFT)

        self.bookmark_entry = tk.Entry(frame, textvariable=self.bookmark_var)
        self.bookmark_entry.pack(side=tk.LEFT)

        self.regex_entry = tk.Entry(frame, textvariable=self.regex_var)
        self.regex_entry.pack(side=tk.LEFT)

        return frame

    def save_state(self):
        self.applies_to_directory = self.directory_var.get()
        self.applies_to_filename = self.filename_var.get()
        self.applies_to_document = self.document_var.get()
        self.Bookmark = self.bookmark_var.get()
        self.regex = self.regex_var.get()
