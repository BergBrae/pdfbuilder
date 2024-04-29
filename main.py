import tkinter as tk

from PDFBuilder import PDFBuilder


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFBuilder(root)
    root.mainloop()
