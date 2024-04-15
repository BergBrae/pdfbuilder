import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import os
import json
from PyPDF2 import PdfMerger, PdfReader

from PDFFile import PDFFile


class PDFCollection:
    def __init__(self):
        self.files = []
        self.num_files = 0
        self.total_pages = 0

    def __len__(self):
        return self.num_files

    def __contains__(self, pdf: PDFFile):
        return pdf in self.files

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
                if key in pdf.filename:
                    sorted_files.append(pdf)
        not_matched = list(set(self.files) - set(sorted_files))
        self.files = sorted_files + not_matched
        return not_matched

    def get_tkinter_table_data(self):
        return [pdf.values for pdf in self.files]

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

    def build_pdf(self, output_path: str):
        # filepaths is a list of tuples (filename, path)
        merger = PdfMerger()
        for pdf in self.files:
            merger.append(pdf.path)

        merger.write(output_path)
        merger.close()
