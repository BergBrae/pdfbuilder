import os
from PyPDF2 import PdfReader
import re


class PDFFile:
    def __init__(self, path: str, keep_open=False, check_exists=True):
        if check_exists and not os.path.exists(path):
            raise FileNotFoundError(f"The file '{path}' does not exist.")
        self.path = os.path.normpath(path)
        self.filename = os.path.basename(path)
        self.directory = os.path.dirname(path)

        self._reader = None
        self._num_pages = None
        self.keep_open = keep_open
        self.opened_successfully = None
        self.error = None

        self._text: list[str] = None

    def __hash__(self):
        return hash(self.path)

    def __repr__(self) -> str:
        return f"PDFFile({self.filename})"

    def __eq__(self, other) -> bool:
        return self.path == other.path

    @property
    def values(self):
        return (self.filename, self.path)

    @property
    def reader(self):
        try:
            if self._reader is None:
                if self.keep_open:
                    self._reader = PdfReader(open(self.path, "rb"), strict=False)
                    self.opened_successfully = True
                    return self._reader
                else:
                    reader = PdfReader(open(self.path, "rb"), strict=False)
                    self.opened_successfully = True
                    return reader
            return self._reader
        except Exception as e:
            self.opened_successfully = False
            self.error = e
            return None

    @property
    def num_pages(self):
        reader = self.reader
        if reader and self._num_pages is None:
            self._num_pages = len(self.reader.pages)

        return self._num_pages

    @property
    def text(self) -> list[str]:
        reader = self.reader
        if reader is not None:
            if self._text is None:
                self._text = []
                for page in self.reader.pages:
                    self._text.append(page.extract_text())
            return self._text
        else:
            return []

    def to_dict(self):

        return {
            "filename": self.filename,
            "path": self.path,
            "directory": self.directory,
            "num_pages": self._num_pages,
            "text": self._text,
        }

    @classmethod
    def from_dict(cls, data: dict):
        pdf = cls(data["path"], check_exists=False)
        pdf.filename = data["filename"]
        pdf.directory = data["directory"]
        pdf._num_pages = data["num_pages"]
        pdf._text = data["text"]
        return pdf
