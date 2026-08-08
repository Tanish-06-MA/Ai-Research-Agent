import pdfplumber


def load_pdf(filepath: str) -> str:
    """
    Reads the pdf file text
    """

    text = " "

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"
    return text
