import os
from PyPDF2 import PdfReader
import re


class PDFFile:
    def __init__(self, path: str, keep_open=False, check_exists=True):
        if check_exists and not os.path.exists(path):
            raise FileNotFoundError(f"The file '{path}' does not exist.")
        self.path = os.path.normpath(path)
        self.filename = os.path.basename(path)

        filename_without_extension, _ = os.path.splitext(self.filename)
        filename_parts = re.split(r"[\s_.-]+", filename_without_extension)
        self.filename_parts = [part.upper() for part in filename_parts]

        self._reader = None
        self._num_pages = None
        self.keep_open = keep_open

    def __hash__(self):
        return hash(self.path)

    def __repr__(self) -> str:
        return f"PDFFile({self.filename})"

    def __eq__(self, other) -> bool:
        return self.path == other.path

    @property
    def values(self):
        return (self.filename, self.path, self.filename_parts)

    @property
    def reader(self):
        if self._reader is None:
            if self.keep_open:
                self._reader = PdfReader(open(self.path, "rb"), strict=False)
                return self._reader
            else:
                return PdfReader(open(self.path, "rb"), strict=False)
        return self._reader

    @property
    def num_pages(self):
        if self._num_pages is None:
            self._num_pages = len(self.reader.pages)

        return self._num_pages