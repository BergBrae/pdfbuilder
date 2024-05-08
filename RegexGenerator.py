from tkinter import simpledialog, Text, Button, Toplevel, messagebox
import tkinter as tk
import ollama
import re
import webbrowser
from typing import Callable
from openai import OpenAI
import subprocess


LLAMAFILE_PATH = r".\Phi-3-mini-4k-instruct.Q4_1.llamafile.exe"

client = OpenAI(
    base_url="http://127.0.0.1:3456/v1",  # "http://<Your api-server IP>:port"
    api_key="sk-no-key-required",
)


def open_link(url):
    webbrowser.open_new(url)


def call_model(prompt):
    return client.chat.completions.create(
        model="NULL",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        stop=["\n"],
    )


class RegexGenerator:
    def __init__(self, root):
        self.root = root
        self.dialog = Toplevel(self.root)
        self.dialog.title("Regex Generator")
        self.dialog.destroy()

    def nl_to_regex(self, nat_lang_str: str, failed_attempts=None, event=None):
        try:
            nat_lang_str = self.convert_description_to_words(nat_lang_str)
            if failed_attempts:
                failed_attempts = set(failed_attempts)
                nat_lang_str += (
                    "\nThe following are previous attempts that failed. Do not generate these patterns.\n"
                    + "\n".join(failed_attempts)
                )
            message = f"Please convert the following natural language description into a regular expression. Your response should consist solely of the regex pattern itself, without enclosing it in code blocks, providing any additional explanations, or including any supplementary text. The goal is to receive a clean, direct regex pattern that corresponds exactly to the described criteria. Note: Make sure to escape charcters that need to be matched. \nDescription: {nat_lang_str}\nExpected output: "
            response = call_model(message)
            response = response.choices[0].message.content
            print(f"\n{response}\n")
            regex_expression = re.sub(
                "[`r\"'\n\r\\s]*(?:\\^*|\\^*(?:regex|python))?\\s*([^`$]+)[\\s`$\"']*",
                r"\1",
                response,
            )
            return regex_expression
        except Exception as e:
            # show message box with error
            messagebox.showerror("Error", f"An error occurred: {e}")

    def convert_description_to_words(self, nat_lang_str: str):
        def replace_and_format(quoted_text):
            # Define patterns and replacements
            replacements = [
                (r"[a-zA-Z]", "letter"),
                (r"\d", "digit"),
                (r"\(", "open parenthesis"),
                (r"\)", "close parenthesis"),
                (r"-", "dash"),
                (r"_", "underscore"),
                (r"\+", "plus"),
                (r"\*", "asterisk"),
                (r"\.", "period"),
                (r"\\", "backslash"),
                (r"`", "backtick"),
                (r";", "semicolon"),
                (r":", "colon"),
                (r"@", "at sign"),
                (r"#", "hash"),
                (r"%", "percent"),
                (r"\&", "ampersand"),
                (r"=", "equals"),
                (r"/", "forward slash"),
                (r"~", "tilde"),
                (r"\n", "newline"),
                (r"\r", "return"),
            ]

            # Apply the replacements
            for pattern, replacement in replacements:
                quoted_text = re.sub(pattern, replacement + " ", quoted_text)

            # Condense repeated words with counts
            quoted_text = re.sub(
                r"(\b\w+\s)(\1)+",
                lambda m: f"{m.group(1).strip()}({len(m.group(0).split())} of them) ",
                quoted_text,
            )

            return quoted_text.strip()

        # Apply the replace_and_format only to the text inside quotes
        modified_str = re.sub(
            r'"([^"]+)"|\'([^\']+)\'',
            lambda m: f"{m.group(0)} ({replace_and_format(m.group(0))})",
            nat_lang_str,
        )

        # Remove the quotes
        modified_str = re.sub(r'"|\'', "", modified_str)

        return modified_str

    def open_dialog(self, insert_into: Callable = None, event=None):
        # insert_into is a function that will insert the generated regex into the calling function
        self.insert_into = insert_into

        if not self.dialog.winfo_exists():
            self.dialog = Toplevel(self.root)
            self.dialog.geometry("400x400")
            self.dialog.title("Text Pattern Generator")

        self.dialog.focus_set()
        for widget in self.dialog.winfo_children():
            widget.destroy()

        self.dialog_frame = tk.Frame(self.dialog)

        label = tk.Label(
            self.dialog_frame, text="Describe What You Would Like To Match:"
        )
        label.pack()

        self.text = Text(self.dialog_frame, height=3, width=50)
        self.text.pack(pady=3)

        self.test_label = tk.Label(self.dialog_frame, text="Enter An Example To Test:")
        self.test_label.pack()
        self.test_input = Text(self.dialog_frame, height=1, width=50)
        self.test_input.pack()
        self.test_input.bind("<KeyRelease>", self.test_regex)

        self.submit_button = Button(
            self.dialog_frame, text="Submit", command=self.submit
        )
        self.submit_button.pack(pady=10)
        self.submit_button.bind("<Control-Return>", self.submit)

        self.progress_label = tk.Label(self.dialog_frame, text="")
        self.progress_label.pack()

        self.test_result = tk.Label(self.dialog_frame, text="")
        self.test_result.pack()

        self.output_label = tk.Label(self.dialog_frame, text="Generated Text Pattern:")
        self.output_label.pack(pady=(30, 5))
        self.output = Text(self.dialog_frame, height=1, width=50)
        self.output.pack()

        self.accept_button = Button(
            self.dialog_frame, text="Accept", command=self.accept
        )
        self.accept_button.pack(pady=5)

        self.dialog_frame.pack()

    def test_regex(self, event=None):
        regex = self.output.get(1.0, tk.END).strip()
        test_string = self.test_input.get(1.0, tk.END).strip()

        try:
            regex = re.compile(regex, re.IGNORECASE)
        except re.error:
            self.test_result.config(text="Invalid Pattern")
            return False

        if re.fullmatch(regex, test_string):
            self.test_result.config(text="Match")
            return True
        else:
            self.test_result.config(text="No match")
            return False

    def submit(self):
        input_str = self.text.get(1.0, tk.END).strip()
        test_string = self.test_input.get(1.0, tk.END).strip()
        max_tries = 10
        attempts = 0
        failed_attempts = []

        self.output.delete(1.0, tk.END)

        while attempts < max_tries:
            self.output_str = self.nl_to_regex(input_str, failed_attempts)
            try:
                if not re.match(self.output_str, r"\(.+\)"):
                    self.output_str = f"({self.output_str})"
            except re.error:
                pass
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, self.output_str)
            self.root.update()  # Force update the GUI

            if test_string:
                attempts += 1
                self.progress_label.config(text=f"Try {attempts} of {max_tries}")

                if self.test_regex():
                    break

                failed_attempts.append(self.output_str)
                self.root.update()  # Force update the GUI
            else:
                self.progress_label.config(text="")
                self.test_result.config(text="")
                self.root.update()
                break

    def accept(self):
        self.output_str = self.output.get(1.0, tk.END).strip()
        self.insert_into(self.output_str)
        self.dialog.destroy()
        return self.output_str


def find_and_kill_process_by_port(port):
    try:
        # Use netstat and findstr to find the PID of the process using the port
        netstat_output = subprocess.check_output(["netstat", "-a", "-n", "-o"]).decode(
            "utf-8"
        )
        lines = netstat_output.splitlines()
        for line in lines:
            if f"127.0.0.1:{port}" in line:
                parts = line.split()
                pid = parts[-1]
                subprocess.call(["taskkill", "/F", "/PID", pid])
                print(f"Killed process with PID {pid} using port {port}")
                return
    except Exception as e:
        print(f"Error while killing existing processes: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    pdf_sort_key = RegexGenerator(root)
    open_button = Button(root, text="Open", command=pdf_sort_key.open_dialog)
    open_button.pack()
    root.mainloop()
