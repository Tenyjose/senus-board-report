
import io

from pypdf import PdfReader, PdfWriter


def extract_pages(pdf_path: str, page_indices: list[int]) -> bytes:
    """
    Take a PDF and a list of 0-based page indices, and return the raw
    bytes of a new PDF containing only those pages.
    """
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for index in page_indices:
        writer.add_page(reader.pages[index])

    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()