from io import BytesIO
from reportlab.pdfgen import canvas
import PyPDF2


def add_page_number(input_pdf_bytes, y=20, font_size=12):
    # Create a new PDF, but just with page numbers.
    packet = BytesIO()
    can = canvas.Canvas(packet)
    font = "Times-Roman"
    # Other available fonts: Times-Roman, Courier, Symbol, ZapfDingbats, etc.
    pdf = PyPDF2.PdfReader(input_pdf_bytes)
    total_num_pages = len(pdf.pages)
    for page_num in range(total_num_pages):
        page = pdf.pages[page_num]
        rotation = page.get("/Rotate")  # Rotation is not None for scanned PDFs
        if rotation is None:
            page_width, page_height = (
                page.mediabox[2],
                page.mediabox[3],
            )  # Get the actual page width and height
            str_to_show = f"Page {page_num + 1} of {total_num_pages}"
            text_width = can.stringWidth(str_to_show, font, font_size)
            can.setPageSize((page_width, page_height))  # Set the actual page size
            can.setFont(font, font_size)
            can.drawString(
                (int(page_width) - int(text_width)) // 2,
                y,
                str_to_show,
            )
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

    output_pdf_bytes = BytesIO()
    pdf_writer.write(output_pdf_bytes)
    output_pdf_bytes.seek(0)
    return output_pdf_bytes


if __name__ == "__main__":
    with open("C:/Users/guest2/Downloads/test_pdf.pdf", "rb") as f:
        input_pdf_bytes = BytesIO(f.read())

    output_pdf_bytes = add_page_number(input_pdf_bytes)

    # If you want to write the output to a file, you can do it like this:
    with open("C:/Users/guest2/Downloads/test_pdf_numbers.pdf", "wb") as f:
        f.write(output_pdf_bytes.getvalue())
