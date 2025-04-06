import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text.strip()

# Example Usage
if __name__ == "__main__":
    text = extract_text_from_pdf("sample.pdf")
    print(text)
