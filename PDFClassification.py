from tkinter import simpledialog, Text, Button, Toplevel
import tkinter as tk
import re


class PDFClassification:
    def __init__(
        self,
        regex: str = "",
        applies_to_directory: bool = False,
        applies_to_filename: bool = False,
        applies_to_document: bool = False,
        bookmark: str = "",
    ):
        self.applies_to_directory = tk.BooleanVar()
        self.applies_to_filename = tk.BooleanVar()
        self.applies_to_document = tk.BooleanVar()
        self.regex = tk.StringVar()
        self.bookmark = tk.StringVar()

        self.applies_to_directory.set(applies_to_directory)
        self.applies_to_filename.set(applies_to_filename)
        self.applies_to_document.set(applies_to_document)
        self.regex.set(regex)
        self.bookmark.set(bookmark)

    def is_empty(self):
        return not any(
            [
                self.applies_to_directory.get(),
                self.applies_to_filename.get(),
                self.applies_to_document.get(),
                self.regex.get(),
                self.bookmark.get(),
            ]
        )

    def to_frame(self, root: tk.Tk):
        frame = tk.Frame(root)

        self.directory_checkbox = tk.Checkbutton(
            frame, text="Directory", variable=self.applies_to_directory
        )
        self.directory_checkbox.pack(side=tk.LEFT)

        self.filename_checkbox = tk.Checkbutton(
            frame, text="Filename", variable=self.applies_to_filename
        )
        self.filename_checkbox.pack(side=tk.LEFT)

        self.document_checkbox = tk.Checkbutton(
            frame, text="Document", variable=self.applies_to_document
        )
        self.document_checkbox.pack(side=tk.LEFT)

        self.bookmark_entry = tk.Entry(frame, textvariable=self.bookmark)
        self.bookmark_entry.pack(side=tk.LEFT, padx=10)

        self.regex_entry = tk.Entry(frame, textvariable=self.regex)
        self.regex_entry.pack(side=tk.LEFT, padx=10)

        return frame

    def applies_to(self, pdf) -> bool:
        if self.applies_to_directory.get():
            directory_result = re.search(self.regex.get(), pdf.directory, re.IGNORECASE)
            if directory_result:
                return directory_result
        if self.applies_to_filename.get():
            filename_result = re.search(self.regex.get(), pdf.filename, re.IGNORECASE)
            if filename_result:
                return filename_result
        if self.applies_to_document.get():
            document_result = re.search(self.regex.get(), pdf.text, re.IGNORECASE)
            if document_result:
                return document_result
        return None
