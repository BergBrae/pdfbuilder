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
        input_regex = self.regex.get()
        if not re.match(r"^\(.+[^\\)]\)$", input_regex):
            input_regex = f"({input_regex})"
        expression = re.compile(input_regex, re.IGNORECASE)
        if self.applies_to_directory.get():
            directory_result = re.search(expression, pdf.path)
            if directory_result:
                return directory_result
        if self.applies_to_filename.get():
            filename_result = re.search(expression, pdf.filename)
            if filename_result:
                return filename_result
        if self.applies_to_document.get():
            pdf_text = "\n\n".join(pdf.text)
            document_result = re.search(expression, pdf_text)
            if document_result:
                return document_result
        return None

    def to_dict(self):
        return {
            "applies_to_directory": self.applies_to_directory.get(),
            "applies_to_filename": self.applies_to_filename.get(),
            "applies_to_document": self.applies_to_document.get(),
            "regex": self.regex.get(),
            "bookmark": self.bookmark.get(),
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["regex"],
            data["applies_to_directory"],
            data["applies_to_filename"],
            data["applies_to_document"],
            data["bookmark"],
        )
