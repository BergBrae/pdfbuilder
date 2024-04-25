from tkinter import simpledialog, Text, Button, Toplevel
import tkinter as tk
import ollama
import re

modelname = "phi3"


class RegexGenerator:
    def __init__(self, root):
        self.root = root
        self.dialog = Toplevel(self.root)
        self.dialog.title("Regex Generator")
        self.dialog.destroy()

        try:
            ollama.list(modelname)
        except:
            ollama.pull(modelname)

    def nl_to_regex(self, nat_lang_str: str, event=None):
        message = f"You generate python compatible regular expressions that are directly used from within python. Your responses are 100% a python regex. Do not output anything that is not a regex string. Do not use code blocks or '`'. The expression to match is: {nat_lang_str}"
        response = ollama.chat(
            model=modelname,
            messages=[
                {
                    "role": "user",
                    "content": message,
                },
            ],
        )
        response = response["message"]["content"]
        print(response)
        regex_expression = re.sub(
            "`?(?:\\^|\\^?(?:regex|python))?\\s*([^`$]+)[\\s`$]*", r"\1", response
        )
        return regex_expression

    def open_dialog(self, event=None):
        if not self.dialog.winfo_exists():
            self.dialog = Toplevel(self.root)
            self.dialog.title("Regex Generator")

        self.dialog.focus_set()

        # clear dialog
        for widget in self.dialog.winfo_children():
            widget.destroy()

        self.dialog_frame = tk.Frame(self.dialog)

        label = tk.Label(
            self.dialog_frame, text="Describe what you would like to match:"
        )
        label.pack()

        self.text = Text(self.dialog_frame, height=3, width=50)
        self.text.pack(pady=3)

        self.submit_button = Button(
            self.dialog_frame, text="Submit", command=self.submit
        )
        self.submit_button.pack(pady=10)

        self.output = Text(self.dialog_frame, height=1, width=50)
        self.output.pack()

        self.accept_button = Button(
            self.dialog_frame, text="Accept", command=self.accept
        )
        self.accept_button.pack(pady=10)

        self.dialog_frame.pack()

    def submit(self):
        self.output.delete(1.0, tk.END)
        input_str = self.text.get(1.0, tk.END)
        self.output_str = self.nl_to_regex(input_str)
        self.output.insert(tk.END, self.output_str)

    def accept(self):
        self.dialog.destroy()
        return self.output_str


if __name__ == "__main__":
    root = tk.Tk()
    pdf_sort_key = RegexGenerator(root)
    open_button = Button(root, text="Open", command=pdf_sort_key.open_dialog)
    open_button.pack()
    root.mainloop()
