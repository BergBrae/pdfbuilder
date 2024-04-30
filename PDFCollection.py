import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import os
import json
from PyPDF2 import PdfWriter, PdfReader
from io import BytesIO

from PDFFile import PDFFile
from add_page_numbers import add_page_number
from open_file import open_file
from PDFClassification import PDFClassification
from PDFSortKey import PDFSortKey


class PDFCollection:
    captured_keyword = "_"

    def __init__(self):
        self.files = []
        self.bookmarks = {}  # {PDFFile: bookmark_title: str}
        self.num_files = 0
        self.failed_files = set()

    def __len__(self):
        return self.num_files

    def __contains__(self, pdf: PDFFile):
        return pdf in self.files

    def __iter__(self):
        return iter(self.files)

    def failed_open(self, pdf: PDFFile):
        if pdf.opened_successfully is None:
            return None
        if pdf.opened_successfully is False:
            self.failed_files.add(pdf)
            return pdf  # returned pdf so that it can be removed from self.files outside of a loop iterating over self.files
        return False

    def add_bookmark(self, pdf: PDFFile, title: str):
        if title:
            self.bookmarks[pdf] = title

    def remove_bookmark(self, pdf: PDFFile):
        if pdf in self.bookmarks:
            del self.bookmarks[pdf]

    def add_file(self, pdf: PDFFile):
        if pdf not in self:
            self.files.append(pdf)
            self.num_files += 1

    def remove_file(self, pdf: PDFFile):
        if pdf in self:
            self.files.remove(pdf)
            self.num_files -= 1
            self.remove_bookmark(pdf)

    def remove_by_path(self, path: str):
        for pdf in self.files:
            if pdf.path == path:
                self.files.remove(pdf)
                self.num_files -= 1
                self.remove_bookmark(pdf)

    def clear_files(self):
        self.files.clear()
        self.num_files = 0
        self.bookmarks.clear()

    def get_file_by_path(self, path: str):
        for pdf in self.files:
            if pdf.path == path:
                return pdf

    def sort(self, sort_key: PDFSortKey):
        sorted_files = []
        files_to_remove = []
        for classification in sort_key:
            for pdf in self.files:
                match = classification.applies_to(pdf)
                pdf_if_failed = self.failed_open(
                    pdf
                )  # PDFFile when faield, False when not failed
                if (
                    pdf_if_failed is False or pdf_if_failed is None
                ):  # self.failed_open removes the files from self.files and adds it to self.failed_files
                    if match and pdf not in sorted_files:
                        sorted_files.append(pdf)

                        bookmark = classification.bookmark.get().strip()
                        if bookmark:
                            for i, group in enumerate(match.groups()):
                                if i == 0:
                                    bookmark = bookmark.replace(
                                        f"{PDFCollection.captured_keyword}", group
                                    )
                            self.bookmarks[pdf] = bookmark
                elif isinstance(pdf_if_failed, PDFFile):
                    files_to_remove.append(pdf_if_failed)

        for pdf in files_to_remove:
            self.remove_file(pdf)
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

    def clear_readers(self):
        for pdf in self.files:
            pdf._reader = None

    def build_pdf(
        self,
        output_path: str,
        page_numbers=True,
        y_padding=20,
        font_size=12,
    ):
        writer = PdfWriter()
        current_page = 0
        bookmarks = []  # [(page_number, title),]
        files_to_remove = []
        for i, pdf in enumerate(self):
            pdf.text  # will open file if not already opened
            pdf_or_failed = self.failed_open(pdf)
            if isinstance(
                pdf_or_failed, PDFFile
            ):  # Issue: failed_open changes self.files
                files_to_remove.append(pdf_or_failed)
                continue
            progress = (i + 1) / len(self.files) * 70
            yield progress  # Yield progress value
            for page in pdf.reader.pages:
                writer.add_page(page)
                current_page += 1

            if pdf in self.bookmarks and self.bookmarks[pdf].strip():
                bookmarks.append((current_page - pdf.num_pages, self.bookmarks[pdf]))

        if page_numbers:
            packet = BytesIO()
            writer.write(packet)
            packet.seek(0)
            packet = add_page_number(packet, y_padding=y_padding, font_size=font_size)
            reader = PdfReader(packet)
            writer = PdfWriter()
            current_page = 0
            for page in reader.pages:
                writer.add_page(page)
                current_page += 1

        progress = 95
        yield progress

        for page_number, title in bookmarks:
            writer.add_outline_item(title, page_number, parent=None)

        for file in files_to_remove:
            self.remove_file(file)

        writer.write(output_path)

        progress = 100
        yield progress

        open_file(output_path)

    def to_dict(self):
        return {
            "files": [pdf.to_dict() for pdf in self],
            "bookmarks": {pdf.path: title for pdf, title in self.bookmarks.items()},
        }

    @classmethod
    def from_dict(cls, data: dict):
        pdf_collection = cls()
        for pdf_data in data["files"]:
            pdf = PDFFile.from_dict(pdf_data)
            pdf_collection.add_file(pdf)
        for path, title in data["bookmarks"].items():
            pdf = pdf_collection.get_file_by_path(path)
            pdf_collection.add_bookmark(pdf, title)
        return pdf_collection
