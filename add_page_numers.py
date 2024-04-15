import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO


def add_page_number(input_pdf, output_pdf, padding=20):
    # Create a new PDF, but just with page numbers.
    packet = BytesIO()
    can = canvas.Canvas(packet)
    can.setFont("Times-Roman", 12)
    # Other available fonts: Times-Roman, Courier, Symbol, ZapfDingbats, etc.
    pdf = PyPDF2.PdfReader(input_pdf)
    for page_num in range(len(pdf.pages)):
        page = pdf.pages[page_num]
        page_width = page.mediabox[2]  # Get the actual page width
        text_width = can.stringWidth(str(page_num + 1), "Times-Roman", 12)
        can.setPageSize((page_width, page.mediabox[3]))  # Set the actual page size
        can.drawString(page_width - text_width - padding, padding, str(page_num + 1))
        can.showPage()
    can.save()

    # Combine the original PDF with the page numbers.
    packet.seek(0)
    new_pdf = PyPDF2.PdfReader(packet)
    pdf_writer = PyPDF2.PdfWriter()
    for page_num in range(len(pdf.pages)):
        page = pdf.pages[page_num]
        page.merge_page(new_pdf.pages[page_num])
        pdf_writer.add_page(page)
    with open(output_pdf, "wb") as f:
        pdf_writer.write(f)


# Run the function, and your PDF will have page numbers!
add_page_number(
    "C:/Users/guest2/Downloads/test_pdf.pdf",
    "C:/Users/guest2/Downloads/test_pdf_numbers.pdf",
)
