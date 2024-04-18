from tkinter import simpledialog, Text, Button, Toplevel
import os


class SortKeyDialog:
    def __init__(self, parent):
        self.parent = parent
        self._sort_key = None

    def load_sort_key(self):
        # Load sort key from file
        if not os.path.exists("sort_key.txt"):
            with open("sort_key.txt", "w") as f:
                f.write("")
        with open("sort_key.txt", "r") as f:
            self._sort_key = f.read().rstrip().splitlines()

    def open_dialog(self):
        self.dialog = Toplevel(self.parent)
        self.dialog.title("Sort Key")
        self.text = Text(self.dialog)
        self.text.pack()
        self.button = Button(self.dialog, text="Save", command=self.save)
        self.button.pack()

        self.text.insert("1.0", "\n".join(self.sort_key))
        self.dialog.bind("<Control-s>", lambda e: self.save())
        self.text.focus_set()

    def save(self):
        self._sort_key = self.text.get("1.0", "end-1c").strip().upper().split("\n")
        with open("sort_key.txt", "w") as f:
            for item in self.sort_key:
                f.write("%s\n" % item)
        self.dialog.destroy()

    @property
    def sort_key(self):
        if self._sort_key is None:
            self.load_sort_key()
        return self._sort_key
