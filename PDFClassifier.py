from tkinter import simpledialog, Text, Button, Toplevel
import tkinter as tk


class PDFClassification:
    def __init__(
        self,
        regex: str,
        applies_to_directory: bool = False,
        applies_to_filename: bool = False,
        applies_to_document: bool = False,
        Bookmark: str | None = None,
    ):
        self.applies_to_directory = applies_to_directory
        self.applies_to_filename = applies_to_filename
        self.applies_to_document = applies_to_document
        self.regex = regex
        self.Bookmark = Bookmark

    def to_frame(self, root: tk.Tk):
        frame = tk.Frame(root)
        self.directory_var = tk.BooleanVar()
        self.filename_var = tk.BooleanVar()
        self.document_var = tk.BooleanVar()
        self.bookmark_var = tk.StringVar()

        self.directory_var.set(self.applies_to_directory)
        self.filename_var.set(self.applies_to_filename)
        self.document_var.set(self.applies_to_document)
        self.bookmark_var.set(self.Bookmark)
        self.regex_var = tk.StringVar()

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


class PDFSortKey:
    def __init__(self, root):
        self.root = root

        self.sort_key: list[PDFClassification] = [PDFClassification(regex="")]

    def dialog_window(self):
        self.dialog = self.root
        self.dialog.title("Sort Key")
        self.dialog_frame = tk.Frame(self.dialog)
        containers = []
        for key in self.sort_key:
            frame = key.to_frame(self.dialog_frame)
            delete_key = Button(
                frame, text="Delete", command=lambda: containers.remove(frame)
            )
            delete_key.pack(side=tk.RIGHT)
            containers.append(frame)
            containers[-1].pack()
        self.dialog_frame.pack()

        # add save key button and add key button
        container = tk.Frame(self.dialog)
        self.save_button = Button(container, text="Save", command=self.save)
        self.add_key_button = Button(container, text="Add Key", command=self.add_key)
        self.save_button.pack(side=tk.LEFT)
        self.add_key_button.pack(side=tk.LEFT)
        container.pack()

    def add_key(self):
        self.sort_key.append(
            PDFClassification(
                regex="",
                applies_to_directory=False,
                applies_to_filename=False,
                applies_to_document=False,
                Bookmark=None,
            )
        )

    def save(self):
        new_sort_key = []
        for sort_key in self.sort_key:
            directory = sort_key.directory_var.get()
            filename = sort_key.filename_var.get()
            document = sort_key.document_var.get()
            bookmark = sort_key.bookmark_var.get()
            regex = sort_key.regex_var.get()
            new_sort_key.append(
                PDFClassification(
                    regex=regex,
                    applies_to_directory=directory,
                    applies_to_filename=filename,
                    applies_to_document=document,
                    Bookmark=bookmark,
                )
            )
        self.sort_key = new_sort_key
        self.dialog.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    pdf_sort_key = PDFSortKey(root)
    pdf_sort_key.dialog_window()
    root.mainloop()
