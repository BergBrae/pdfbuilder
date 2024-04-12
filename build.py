from PyPDF2 import PdfMerger

def build_pdf(filepaths: list[str], output_path: str):
    # filepaths is a list of tuples (filename, path)
    merger = PdfMerger()
    for filepath in filepaths:
        merger.append(filepath)
    
    merger.write(output_path)
    merger.close()