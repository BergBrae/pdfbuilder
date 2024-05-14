from tkinter import simpledialog, Text, Button, Toplevel
import tkinter as tk
import re
import webbrowser
import tkinter.ttk as ttk

from PDFClassification import PDFClassification


class PDFSortKey:
    def __init__(self, root, llamafile_exists: bool):
        self.root = root
        self.dialog = Toplevel(self.root)
        self.dialog.title("Sort Key")
        self.dialog.destroy()
        self.llamafile_exists = llamafile_exists

        self.sort_key: list[PDFClassification] = [PDFClassification(regex="")]
        if self.llamafile_exists:
            from RegexGenerator import RegexGenerator

            self.regex_generator = RegexGenerator(self.root)

    def __iter__(self):
        for key in self.sort_key:
            if not key.is_empty():
                yield key

    def open_dialog(self, event=None):
        if not self.dialog.winfo_exists():
            self.dialog = Toplevel(self.root)
            self.dialog.geometry("850x200")  # Adjusted for demonstration
            self.dialog.title("Sort Key")

        self.dialog.focus_set()

        # Clear dialog
        for widget in self.dialog.winfo_children():
            widget.destroy()

        # Create a canvas and a scrollbar
        self.canvas = tk.Canvas(self.dialog)
        scrollbar = tk.Scrollbar(
            self.dialog, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Pack the scrollbar to the right of the dialog and the canvas on the left
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a frame inside the canvas to hold the content
        self.dialog_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.dialog_frame, anchor="nw")

        # add a vertical line to the right side of the canvas
        sperator = ttk.Separator(self.canvas, orient="vertical")
        sperator.pack(side=tk.RIGHT, fill=tk.Y)

        header_text = (
            f"Applies to: {' '*60} Bookmark Title: {' '*19} Text Pattern: {' '*85}"
        )
        containers = [tk.Label(self.dialog_frame, text=header_text)]
        containers[0].pack(fill=tk.X)

        for i, key in enumerate(self.sort_key):
            frame = key.to_frame(self.dialog_frame)
            delete_key = Button(
                frame,
                text="Delete",
                command=lambda i=i, frame=frame: self.delete_key(i, frame),
            )

            move_up = Button(frame, text="Move Up", command=lambda i=i: self.move_up(i))
            move_up.pack(side=tk.RIGHT, padx=5)

            move_down = Button(
                frame, text="Move Down", command=lambda i=i: self.move_down(i)
            )
            move_down.pack(side=tk.RIGHT, padx=5)

            delete_key.pack(side=tk.RIGHT, padx=5)

            containers.append(frame)
            containers[-1].pack(pady=5, fill=tk.X)

        self.dialog_frame.update_idletasks()  # Update inner frame size
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        buttons_frame = tk.Frame(self.dialog)
        self.add_key_button = Button(
            buttons_frame, text="Add Key", command=self.add_key
        )
        self.add_key_button.pack(side=tk.TOP, pady=5)

        if self.llamafile_exists:
            self.generate_regex_button = Button(
                buttons_frame,
                text="Generate\nText Pattern",
                command=self.generate_regex,
            )
            self.generate_regex_button.pack(side=tk.TOP, pady=5)

        buttons_frame.pack(padx=5, pady=10, anchor="se")
        self.help_button = Button(buttons_frame, text="Help", command=self.help_dialog)
        self.help_button.pack(side=tk.BOTTOM, pady=10)

        # Configure canvas to expand the scrollbar dynamically
        self.dialog_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.dialog_frame.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def help_dialog(self):
        def open_link(event):
            webbrowser.open_new("https://en.wikipedia.org/wiki/Regular_expression")

        # Create the main window
        root = tk.Tk()
        root.title("Help")

        # Create a text widget to display information
        text_info = f"""A regular expression (regex) is a sequence of characters that define a search pattern.
    In its simplest form, a regex can be used to match a single character or word.
    For example, the regex 'merit' will simply find the word 'merit' in text.
    However, regexes can be much more complex and powerful. For example, the regex {r'\w\d{5}\.\d{2}\(\d{2}\)'} will match any of Merit's sample IDs like 'S17535.01(01)'.
    For help with more complex regexes, you can use the 'Generate Text Pattern' button to create a regex that matches the text you want. Please test your regexes before using them.
    The matching text can be used in the bookmark name. Use "_" to insert the matched text into the bookmark name.
    For more information on regexes, see the link below."""

        text_info = re.sub("\\n\\s*", "\\n\\n", text_info)

        label_info = tk.Label(root, text=text_info, justify=tk.LEFT)
        label_info.pack(padx=10, pady=10)

        # Create a label that acts like a hyperlink
        link = tk.Label(
            root, text="More about regular expressions", fg="blue", cursor="hand2"
        )
        link.pack()
        link.bind("<Button-1>", open_link)

        root.mainloop()

    def move_down(self, i):
        num_keys = len(self.sort_key)
        self.sort_key[i], self.sort_key[(i + 1) % num_keys] = (
            self.sort_key[(i + 1) % num_keys],
            self.sort_key[i],
        )
        self.open_dialog()

    def move_up(self, i):
        num_keys = len(self.sort_key)
        self.sort_key[i], self.sort_key[(i - 1) % num_keys] = (
            self.sort_key[(i - 1) % num_keys],
            self.sort_key[i],
        )
        self.open_dialog()

    def get_insert_function(self):

        def insert_into_existing_box(box, regex):
            box.delete(0, tk.END)
            box.insert(tk.END, regex)

        box = self.root.focus_get()
        if isinstance(box, Text):
            return insert_into_existing_box

        def new_key(regex):
            self.sort_key.append(PDFClassification(regex=regex))

        return new_key

    def generate_regex(self):
        self.regex_generator.open_dialog(insert_into=self.get_insert_function())
        self.regex_generator.dialog.wait_window()
        self.open_dialog()

    def add_key(self):
        self.sort_key.append(PDFClassification())
        self.open_dialog()

    def delete_key(self, i, frame):
        self.sort_key.pop(i)
        frame.destroy()
        self.open_dialog()

    def to_dict(self):
        return [key.to_dict() for key in self.sort_key]

    @classmethod
    def from_dict(cls, data: list[dict], root, llamafile_exists: bool):
        sort_key = cls(root, llamafile_exists=llamafile_exists)
        sort_key.sort_key = [PDFClassification.from_dict(d) for d in data]
        return sort_key


if __name__ == "__main__":
    root = tk.Tk()
    pdf_sort_key = PDFSortKey(root)
    open_button = Button(root, text="Open", command=pdf_sort_key.open_dialog)
    open_button.pack()
    root.mainloop()
