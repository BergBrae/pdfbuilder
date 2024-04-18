import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import os
import json
from PyPDF2 import PdfMerger, PdfReader
from io import BytesIO

from PDFFile import PDFFile
from add_page_numers import add_page_number


class PDFCollection:
    def __init__(self):
        self.files = []
        self.bookmarks = {}  # {PDFFile: bookmark_title: str}
        self.num_files = 0

    def __len__(self):
        return self.num_files

    def __contains__(self, pdf: PDFFile):
        return pdf in self.files

    def __iter__(self):
        return iter(self.files)

    def add_bookmark(self, pdf: PDFFile, title: str):
        if title:
            self.bookmarks[pdf] = title

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
                if key in pdf.filename_parts and pdf not in sorted_files:
                    sorted_files.append(pdf)
        not_matched = [pdf for pdf in self.files if pdf not in sorted_files]
        self.files = sorted_files + not_matched
        return not_matched

    def get_tkinter_table_data(self):
        table_values = []

        for pdf in self.files:
            if pdf in self.bookmarks:
                bookmark = self.bookmarks[pdf]
            else:
                bookmark = ""
            table_values.append(pdf.values + (bookmark,))
        return table_values

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

    def build_pdf(self, output_path: str, page_numbers=True, padding=20):
        merger = PdfMerger()  # Can add bookmarks with PdfMerger
        start_page_number = 0
        total_pages = sum(pdf.num_pages for pdf in self)
        for pdf in self.files:
            with open(pdf.path, "rb") as f:
                input_pdf_bytes = BytesIO(f.read())

            if page_numbers:
                output_pdf_bytes, num_pages = add_page_number(
                    input_pdf_bytes, total_pages, start_page_number + 1, padding
                )
                merger.append(output_pdf_bytes)
                start_page_number += num_pages
            else:
                merger.append(input_pdf_bytes)

            # Add bookmark if it exists for the current PDF
            if pdf in self.bookmarks:
                merger.add_outline_item(
                    self.bookmarks[pdf], start_page_number - num_pages
                )  # total_pages -1 may be wrong

        with open(output_path, "wb") as f:
            merger.write(f)
        merger.close()
