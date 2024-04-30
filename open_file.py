import os, sys, subprocess


def open_file(filename):
    """
    Opens the specified file using the default application associated with its file type.

    Args:
        filename (str): The path of the file to be opened.

    Returns:
        None
    """
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])
