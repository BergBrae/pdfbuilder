# PDF Builder: A Tkinter Application for Managing PDF Files

PDF Builder is a comprehensive desktop application designed to facilitate the management, sorting, and combining of PDF files. It is built using Python's Tkinter library and provides an interactive GUI for users to efficiently handle PDF documents. The application offers functionalities such as adding bookmarks, sorting PDFs based on custom criteria, merging multiple PDFs into a single document, and adding page numbers to PDFs.

## Features:
- **Load and Save Project State**: Users can save their current project state, including loaded PDFs and sort keys, and reload them later.
- **Add Files and Directories**: Users can add individual PDF files or entire directories containing PDF files.
- **Sorting Mechanism**: Users can define custom sort keys using regular expressions to automatically sort PDFs based on filename, directory, or content.
- **Bookmark Management**: Users can add, edit, and remove bookmarks from PDF files to help organize documents.
- **PDF Merging**: Merge multiple PDF files into a single document with options to add page numbers and manage bookmarks.
- **View PDF Text**: View text extracted from PDF files directly within the application.
- **Regular Expression Assistance**: An integrated Regex Generator helps users create regular expressions based on natural language inputs.

## Installation
To use PDF Builder, you need Python installed on your system along with the necessary libraries. Here’s how to get started:

1. **Install Python**: Ensure Python 3.x is installed on your machine.
2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```
3. **Run the Application**: Navigate to the application's directory in your terminal and run:
```bash
python main.py
```

## Usage
### Managing PDF Files
- Add Files: Click on "Add Files" to select PDFs to load.
Add Directory: Use "Add Directory" to load all PDF files within a specific directory.
- Remove Selected: Select files in the list and click "Remove Selected" to delete them from the project.
### Sorting and Bookmarks
- Sort Key: Define sort keys that determine how files should be organized. This can include regular expressions for matching and sorting based on the content or names of files.
- Edit Bookmarks: Double-click on the bookmark column of a file to edit its bookmark.
### Merging and Exporting PDFs
- Build PDF: Click "Build PDF" to combine the selected PDFs into a single document. This feature includes options for adding page numbers and managing bookmarks during the merge process.
### Saving and Loading State
- Save State: Save the current state of your project, including loaded PDFs and configured sort keys, into a .pdfbuilder.json file.
- Load State: Load a previously saved state from a .pdfbuilder.json file to resume work.
### Additional Features
- View PDF Text: Right-click on a PDF file and select "Show Text" to view its contents.
- Regex Generator: Use the Regex Generator to create regular expressions based on natural language descriptions.

## Compatibility
This application was devloped and tested on Windows. Compatibility with other systems may be limited.