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

    def signal_handler(sig, frame):
        print("Ctrl-C pressed, stopping the subprocess...")
        proc.terminate()  # or proc.kill() if terminate doesn't work
        sys.exit(0)

    # Setup signal handler to handle Ctrl-C
    signal.signal(signal.SIGINT, signal_handler)

    # Start the executable as a subprocess
    port = "3456"
    find_and_kill_process_by_port(port)
    proc = subprocess.Popen(
        [
            r"llamafiles\Phi-3-mini-4k-instruct.Q4_1.llamafile.exe",
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
        proc.kill()
        proc.wait()

        find_and_kill_process_by_port(port)

        print("Subprocess terminated.")
