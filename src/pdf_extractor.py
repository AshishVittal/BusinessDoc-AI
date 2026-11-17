
import pymupdf


def extract_text(pdf_bytes: bytes) -> str:
    """Extract readable text from a PDF file."""

    try:
        document = pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        if document.page_count == 0:
            raise ValueError("The PDF contains no pages.")

        extracted_pages = []

        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text()

            extracted_pages.append(
                f"--- Page {page_number} ---\n{page_text}"
            )

        document.close()

        extracted_text = "\n".join(extracted_pages).strip()

        if not extracted_text:
            raise ValueError(
                "No readable text found. "
                "This PDF may contain scanned images."
            )

        return extracted_text

    except Exception as error:
        raise ValueError(
            f"PDF extraction failed: {error}"
        ) from error
