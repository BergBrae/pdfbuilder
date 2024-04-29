from tkinter import simpledialog, Text, Button, Toplevel
import tkinter as tk
import ollama
import re
import webbrowser


def open_link(url):
    webbrowser.open_new(url)


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
        message = f"Please convert the following natural language description into a regular expression. Your response should consist solely of the regex pattern itself, without enclosing it in code blocks, providing any additional explanations, or including any supplementary text. The goal is to receive a clean, direct regex pattern that corresponds exactly to the described criteria.\nDescription: {nat_lang_str}\nExpected output: "
        response = ollama.generate(
            model=modelname,
            prompt=message,
        )
        response = response["response"]
        print(response)
        regex_expression = re.sub(
            "[`r\"'\n\r\\s]*(?:\\^*|\\^*(?:regex|python))?\\s*([^`$]+)[\\s`$\"']*",
            r"\1",
            response,
        )  # clean the expression of code blocks, quotes etc.
        return regex_expression

    def open_dialog(self, insert_into, event=None):
        self.insert_into = insert_into

        if not self.dialog.winfo_exists():
            self.dialog = Toplevel(self.root)
            self.dialog.geometry("400x250")
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
        self.submit_button.bind("<Control-Return>", self.submit)

        self.output = Text(self.dialog_frame, height=1, width=50)
        self.output.pack()

        self.help_link = tk.Label(
            self.dialog_frame,
            text="You can test the regex here",
            fg="blue",
            cursor="hand2",
            underline=True,
        )
        self.help_link.bind("<Button-1>", lambda e: open_link("https://regex101.com/"))
        self.help_link.pack()

        self.accept_button = Button(
            self.dialog_frame, text="Accept", command=self.accept
        )
        self.accept_button.pack(pady=10)

        self.dialog_frame.pack()

    def submit(self):
        self.output.delete(1.0, tk.END)
        input_str = self.text.get(1.0, tk.END)
        self.output_str = self.nl_to_regex(input_str)
        if not re.match(self.output_str, r"\(.+\)"):
            self.output_str = f"({self.output_str})"
        self.output.insert(tk.END, self.output_str)

    def accept(self):
        self.dialog.destroy()
        if self.insert_into:
            self.insert_into.delete(0, tk.END)
            self.insert_into.insert(tk.END, self.output_str)
        return self.output_str


if __name__ == "__main__":
    root = tk.Tk()
    pdf_sort_key = RegexGenerator(root)
    open_button = Button(root, text="Open", command=pdf_sort_key.open_dialog)
    open_button.pack()
    root.mainloop()
