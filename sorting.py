from tkinter import simpledialog, Text, Button, Toplevel
import os


class SortKeyDialog:
    def __init__(self, parent):
        self.parent = parent
        self.sort_key = []
        self.load_sort_key()

    def load_sort_key(self):
        # Load sort key from file
        if os.path.exists("sort_key.txt"):
            with open("sort_key.txt", "r") as f:
                self.sort_key = [line.rstrip() for line in f]

    def open_dialog(self):
        self.dialog = Toplevel(self.parent)
        self.dialog.title("Sort Key")
        self.text = Text(self.dialog)
        self.text.pack()
        self.button = Button(self.dialog, text="Save", command=self.save)
        self.button.pack()

        self.text.insert("1.0", "\n".join(self.sort_key))

    def save(self):
        self.sort_key = self.text.get("1.0", "end-1c").split("\n")
        with open("sort_key.txt", "w") as f:
            for item in self.sort_key:
                f.write("%s\n" % item)
        self.dialog.destroy()

    def sort(self, items: list[(str, str)]) -> list[str]:  # [(filename, path)]
        # sort alphabetically before applying sort key
        items.sort(key=lambda x: x[0])

        sorted_items = []
        self.load_sort_key()
        for key in self.sort_key:
            for item in items:
                if key in item[0]:  # if key in filename
                    sorted_items.append(item)  # append path

        not_matched = list(set(items) - set(sorted_items))
        return sorted_items, not_matched
