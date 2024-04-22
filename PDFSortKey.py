from tkinter import simpledialog, Text, Button, Toplevel
import tkinter as tk

from PDFClassification import PDFClassification


class PDFSortKey:
    def __init__(self, root):
        self.root = root
        self.dialog = Toplevel(self.root)
        self.dialog.title("Sort Key")

        self.sort_key: list[PDFClassification] = [PDFClassification(regex="")]

    def dialog_window(self):
        # clear dialog
        for widget in self.dialog.winfo_children():
            widget.destroy()

        self.dialog_frame = tk.Frame(self.dialog)
        containers = []
        for i, key in enumerate(self.sort_key):
            frame = key.to_frame(self.dialog_frame)
            delete_key = Button(
                frame, text="Delete", command=lambda i=i: self.delete_key(i, frame)
            )
            delete_key.pack(side=tk.RIGHT)
            containers.append(frame)
            containers[-1].pack(pady=5)
        self.dialog_frame.pack()

        # add save key button and add key button
        container = tk.Frame(self.dialog)
        self.save_button = Button(container, text="Save", command=self.save)
        self.add_key_button = Button(container, text="Add Key", command=self.add_key)
        self.save_button.pack(side=tk.LEFT)
        self.add_key_button.pack(side=tk.LEFT)
        container.pack()

    def add_key(self):
        self.sort_key.append(PDFClassification())
        self.dialog_window()

    def delete_key(self, i, frame):
        self.sort_key.pop(i)
        frame.destroy()
        self.dialog_window()

    def save(self):
        self.dialog.destroy()
        return self.sort_key


if __name__ == "__main__":
    root = tk.Tk()
    pdf_sort_key = PDFSortKey(root)
    open_button = Button(root, text="Open", command=pdf_sort_key.dialog_window)
    open_button.pack()
    root.mainloop()
