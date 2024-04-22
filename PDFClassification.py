from tkinter import simpledialog, Text, Button, Toplevel
import tkinter as tk


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
        self.bookmark_entry.pack(side=tk.LEFT)

        self.regex_entry = tk.Entry(frame, textvariable=self.regex)
        self.regex_entry.pack(side=tk.LEFT)

        return frame
