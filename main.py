import tkinter as tk

from RegexGenerator import find_and_kill_process_by_port
from PDFBuilder import PDFBuilder


def main():
    root = tk.Tk()
    app = PDFBuilder(root)
    root.mainloop()


if __name__ == "__main__":
    import subprocess
    import signal
    import sys
    import os

    def resource_path(relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    llamafile_path = resource_path(
        r"llamafiles\Phi-3-mini-4k-instruct.Q4_1.llamafile.exe"
    )
    llamafile_exists = os.path.exists(llamafile_path)

    def signal_handler(sig, frame):
        print("Ctrl-C pressed, stopping the subprocess...")
        proc.terminate()  # or proc.kill() if terminate doesn't work
        sys.exit(0)

    # Setup signal handler to handle Ctrl-C
    signal.signal(signal.SIGINT, signal_handler)

    # Start the executable as a subprocess
    if llamafile_exists:
        port = "3456"
        find_and_kill_process_by_port(port)
        proc = subprocess.Popen(
            [
                llamafile_path,
                "--nobrowser",
                "--port",
                port,
            ],
            shell=True,
        )

    try:
        # Keep the main program running; you can do your other tasks in this block
        print("Running, press Ctrl-C to stop.")
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure the subprocess is terminated when the Python script ends
        if llamafile_exists:
            proc.kill()
            proc.wait()

            find_and_kill_process_by_port(port)

            print("Subprocess terminated.")
