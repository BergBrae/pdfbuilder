### README for PDF Builder Repository

#### Introduction
The PDF Builder repository contains a set of Python scripts that facilitate the creation, manipulation, and organization of PDF files. It includes functionality for adding bookmarks, merging PDFs, adding page numbers, and sorting PDF files based on customizable sort keys.

#### Repository Contents
- **PDFBuilder.py**: Main application script for the PDF Builder GUI, enabling PDF file management and operations.
- **PDFCollection.py**: Manages a collection of PDF files, including adding, removing, and sorting functionalities.
- **PDFFile.py**: Represents a single PDF file, handling file-specific operations like reading and classifying.
- **classify_pdf.py**: Stub for a function to classify PDF files based on their content.
- **add_page_numers.py**: Script to add page numbers to a PDF file.
- **open_file.py**: Utility script to open a file using the default application based on the operating system.
- **sorting.py**: Contains a dialog for setting and saving a sort key used for organizing PDF files.
- **state.json**: Stores paths to example PDF files for testing or demonstration.
- **todo.txt**: Text file listing tasks or bugs to fix.
- **PDFBuilder.spec**: Configuration file for PyInstaller to build an executable from the PDFBuilder script.
- **run_with_python.bat** and **build_exe.bat**: Batch scripts for setting up the environment and building an executable, respectively.
- **requirements.txt**: Lists dependencies needed to run the scripts.
- **sort_key.txt**: Text file storing user-defined sort keys for PDF organization.

#### Installation and Setup
1. **Install Python**: Ensure Python is installed on your system. Python 3.8 or higher is recommended.
2. **Clone the Repository**: Download or clone this repository to your local machine.
3. **Install Dependencies**: Navigate to the repository directory and run:

`pip install -r requirements.txt`

4. **Run PDFBuilder**: Start the application by running:

`python PDFBuilder.py`


#### Usage
- **Adding PDFs**: Use the "Add Files" or "Add Directory" buttons to load PDF files into the application.
- **Organizing PDFs**: Sort PDF files using customizable sort keys via the "Sort Key" button. Files can be manually moved up and down in the list.
- **Editing Bookmarks**: Double-click on the bookmark column to add or edit bookmarks for individual PDF files.
- **Building PDFs**: Compile selected PDF files into a single document with optional page numbers, bookmarks, and specified page settings.
- **Exporting PDFs**: After arranging and optionally merging files, use the "Build PDF" button to save the final PDF to a desired location.

#### Development
- **Modify Code**: Scripts like `classify_pdf.py` and `PDFClassifier.py` are stubs or skeletons that can be further developed to add additional functionality such as PDF content classification.
- **Add Features**: Implement features listed in `todo.txt` or enhance existing functionalities.

This repository provides a robust tool for PDF file management and is ideal for users needing customizable, scriptable PDF processing capabilities.
