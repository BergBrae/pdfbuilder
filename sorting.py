from tkinter import simpledialog

class SortKeyDialog:
    def __init__(self, parent):
        # self.parent = parent
        # self.dialog = simpledialog.askstring('Sort Key', 'Enter a sort key')
        # self.parent.focus_set()
        # self.parent.grab_set()
        pass

    def sort(self, items: list[(str, str)]): # [(filename, path)]
        # items is a list of tuples (filename, path)
        return sorted(items)