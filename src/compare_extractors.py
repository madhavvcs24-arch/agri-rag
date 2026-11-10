
import fitz
from langchain_community.document_loaders import PyPDFLoader

PDF_PATH = "data/raw/icar_kharif_2025_english.pdf"

SAMPLE_PAGES = [50, 150, 250]


def inspect_pymupdf():
    results = {}

    with fitz.open(PDF_PATH) as pdf:
        for page_index in SAMPLE_PAGES:
            results[page_index] = pdf[page_index].get_text("text")

    return results


def inspect_pypdfloader():
    results = {}

    loader = PyPDFLoader(PDF_PATH)

    for doc in loader.lazy_load():
        page_index = int(doc.metadata["page"])

        if page_index in SAMPLE_PAGES:
            results[page_index] = doc.page_content

    return results


def main():
    pymupdf_results = inspect_pymupdf()
    pypdf_results = inspect_pypdfloader()

    for page_index in SAMPLE_PAGES:

        text1 = pymupdf_results.get(page_index, "")
        text2 = pypdf_results.get(page_index, "")

        print("\n" + "=" * 70)
        print(f"PDF PAGE INDEX: {page_index}")
        print("=" * 70)

        print("\n--- PyMuPDF ---")
        print("Characters:", len(text1))
        print(text1[:1200])

        print("\n--- PyPDFLoader ---")
        print("Characters:", len(text2))
        print(text2[:1200])

        print("\n--- Comparison ---")
        print("Character difference:", abs(len(text1) - len(text2)))
        print("Both empty:", not text1.strip() and not text2.strip())


if __name__ == "__main__":
    main()
