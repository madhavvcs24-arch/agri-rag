
import fitz
from langchain_community.document_loaders import PyPDFLoader

PDF_PATH = "data/raw/icar_kharif_2025_english.pdf"
PAGE_INDEX = 50

# Extract using PyMuPDF
with fitz.open(PDF_PATH) as pdf:
    pymupdf_text = pdf[PAGE_INDEX].get_text("text")

# Extract using PyPDFLoader
loader = PyPDFLoader(PDF_PATH)
pypdf_documents = loader.load()
pypdf_text = pypdf_documents[PAGE_INDEX].page_content

# Save both complete outputs
with open("pymupdf_page51.txt", "w", encoding="utf-8") as f:
    f.write(pymupdf_text)

with open("pypdf_page51.txt", "w", encoding="utf-8") as f:
    f.write(pypdf_text)

print("Both complete page extractions saved!")
print("PyMuPDF characters:", len(pymupdf_text))
print("PyPDFLoader characters:", len(pypdf_text))
