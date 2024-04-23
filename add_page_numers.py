from io import BytesIO
from reportlab.pdfgen import canvas
import PyPDF2


def add_page_number(input_pdf_bytes, y_padding=20, font_size=12):
    # Create a new PDF, but just with page numbers.
    packet = BytesIO()
    can = canvas.Canvas(packet)
    font = "Times-Roman"
    pdf = PyPDF2.PdfReader(input_pdf_bytes)
    total_num_pages = len(pdf.pages)

    for page_num in range(total_num_pages):
        page = pdf.pages[page_num]
        rotation = page.get("/Rotate") if page.get("/Rotate") else 0
        page_width, page_height = float(page.mediabox[2]), float(page.mediabox[3])
        str_to_show = f"Page {page_num + 1} of {total_num_pages}"
        text_width = can.stringWidth(str_to_show, font, font_size)
        can.setPageSize((page_width, page_height))
        can.setFont(font, font_size)

        # Adjust text position based on rotation
        if rotation == 90:
            can.rotate(90)
            x = y_padding
            y = -page_height + (page_width - text_width) / 2
        elif rotation == 180:
            can.rotate(180)
            x = -page_width + (page_width - text_width) / 2
            y = -page_height + y_padding
        elif rotation == 270:
            can.rotate(-90)  # Rotating -90 is equivalent to rotating 270 clockwise
            x = (-page_height - text_width) / 2
            y = y_padding
        else:  # rotation == 0 or None
            x = (page_width - text_width) / 2
            y = y_padding

        can.drawString(x, y, str_to_show)
        can.showPage()
        can.saveState()  # Save the state of the canvas to reset rotations for the next page
        can.restoreState()

    can.save()

    # Combine the original PDF with the page numbers.
    packet.seek(0)
    new_pdf = PyPDF2.PdfReader(packet)
    pdf_writer = PyPDF2.PdfWriter()
    for page_num in range(total_num_pages):
        page = pdf.pages[page_num]
        page.merge_page(new_pdf.pages[page_num])
        pdf_writer.add_page(page)

    output_pdf_bytes = BytesIO()
    pdf_writer.write(output_pdf_bytes)
    output_pdf_bytes.seek(0)
    return output_pdf_bytes
