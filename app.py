import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PyPDF2 import PdfMerger
import os
import json

num_files = 0

def clear_files():
    # Clear the tree
    for item in tree.get_children():
        tree.delete(item)
    # Clear the set of items
    tree_items.clear()
    update_num_files()

def add_files():
    files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    if files:
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        for file in pdf_files:
            values = (os.path.basename(file), file)
            add_item_to_tree(values)
    update_num_files()

# Create a function to remove selected items
def remove_selected():
    selected_items = tree.selection()
    for item in selected_items:
        tree_items.remove(tree.item(item)['values'][1])
        tree.delete(item)
    update_num_files()

def add_directory():
    directory = filedialog.askdirectory()
    if directory:
        pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
        for file in pdf_files:
            values = (os.path.basename(file), os.path.join(directory, file))
            add_item_to_tree(values)
    update_num_files()

def update_num_files():
    items = tree.get_children('')
    num_files = len(items)
    status_bar.config(text=f'Total Files: {num_files}')

def sort_key():
    pass  # Add functionality here

def open_settings():
    pass  # Add functionality here

def save_state():
    # Get all items in the tree
    items = tree.get_children()

    # Get the file paths of the items
    file_paths = [tree.item(item)['values'][1] for item in items]

    output_path = filedialog.asksaveasfilename(defaultextension=".json")

    # Write the file paths to a JSON file
    with open(output_path, 'w') as f:
        json.dump(file_paths, f)

def load_state():
    # Clear the tree
    tree.delete(*tree.get_children())

    input_path = filedialog.askopenfilename(filetypes=[("PDF Builder Saves", "*.json")])

    # Read the file paths from the JSON file
    with open(input_path, 'r') as f:
        file_paths = json.load(f)

    does_not_exist = []

    # Add the items to the tree
    for file_path in file_paths:
        values = (os.path.basename(file_path), file_path)
        try:
            add_item_to_tree(values, check_if_exists=True)
        except FileNotFoundError as e:
            does_not_exist.append(file_path)

    if does_not_exist:
        paths_text = '\n'.join(does_not_exist)
        messagebox.showwarning('Warning', f'The following files do not exist:\n{paths_text}')

def build_pdf():
    # Ask the user where they want to save the combined PDF
    output_path = filedialog.asksaveasfilename(defaultextension=".pdf")

    if output_path:
        # Create a PdfMerger object
        merger = PdfMerger()

        # Get all items in the tree
        items = tree.get_children()

        # Loop through the items and merge the PDFs
        for item in items:
            file_path = tree.item(item)['values'][1]
            merger.append(file_path)

        # Write the merged PDF to the output file
        merger.write(output_path)
        merger.close()

        # Inform the user that the PDF has been built
        messagebox.showinfo('PDF Builder', 'PDF has been built successfully.')

def auto_sort():
    items = tree.get_children('')
    sorted_items = sorted((tree.item(item)['values'], item) for item in items)
    tree.delete(*items)
    tree_items.clear()
    for values, item in sorted_items:
        add_item_to_tree(values)

def move_file_down():
    selected_items = tree.selection()  # get selected items
    for selected_item in reversed(selected_items):
        item_index = tree.index(selected_item)  # get index of selected item
        if item_index < len(tree.get_children()) - 1:  # if not the last item
            tree.move(selected_item, '', item_index + 1)  # move item down

def move_file_up():
    selected_items = tree.selection()  # get selected items
    for selected_item in selected_items:
        item_index = tree.index(selected_item)  # get index of selected item
        if item_index > 0:  # if not the first item
            tree.move(selected_item, '', item_index - 1)  # move item up

def open_file(event):
    item = tree.focus()
    file_path = tree.item(item)['values'][1]
    os.startfile(file_path)

# Initialize the main window
root = tk.Tk()
root.title('PDF Builder')
root.geometry("800x600")
root.iconbitmap('pdficon.ico')

# Create the toolbar frame
toolbar_frame = tk.Frame(root)
toolbar_frame.pack(fill=tk.X)

# Add buttons to the toolbar
toolbar_buttons = [
    ('Clear', clear_files),
    ('Remove Selected', remove_selected),
    ('Load', load_state), 
    ('Save', save_state),
    ('Add Files', add_files),
    ('Add Directory', add_directory),
    ('Sort Key', sort_key),
    ('Settings', open_settings)
]

for button_text, command in toolbar_buttons:
    button = tk.Button(toolbar_frame, text=button_text, command=command)
    button.pack(side=tk.LEFT, padx=2, pady=2)

# Create the file display area
tree = ttk.Treeview(root, columns=('File Name', 'Path'), show='headings')
tree.heading('File Name', text='File Name')
tree.heading('Path', text='Path')
tree.column('File Name', width=200)
tree.column('Path', width=200)

# Bind the double click event to the tree
tree.bind('<Double-1>', open_file)

# Create a set to store the items in the tree
tree_items = set()

# Function to add items to the tree
def add_item_to_tree(item, check_if_exists=False):
    # Check if the file exists
    if check_if_exists and not os.path.exists(item[1]):
        raise FileNotFoundError(f"The file '{item[1]}' does not exist.")

    # Only add the item if it's not already in the set
    if item[1] not in tree_items:
        tree.insert('', 'end', values=item)
        tree_items.add(item[1])

    update_num_files()

tree.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

# Add scrollbar for the treeview
scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscroll=scrollbar.set)

# Add additional buttons at the bottom
bottom_buttons = [
    ('Build PDF', build_pdf),
    ('Auto Sort', auto_sort),
    ('Move File ↓', move_file_down),
    ('Move File ↑', move_file_up)
]

for button_text, command in bottom_buttons:
    button = tk.Button(root, text=button_text, command=command)
    button.pack(side=tk.BOTTOM, fill=tk.X)

# Status bar at the bottom
status_bar = tk.Label(root, text=f'Total Files: {num_files}', bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Start the Tkinter event loop
root.mainloop()
