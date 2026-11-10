
import fitz
import csv

PDF_PATH = "data/raw/icar_kharif_2025_english.pdf"
REPORT_PATH = "data/processed/extraction_report.csv"

def inspect_pages():

    with open(REPORT_PATH, encoding="utf-8") as file:
        report = list(csv.DictReader(file))

    flagged_pages = [
        int(row["pdf_page"])
        for row in report
        if row["status"] != "extracted"
    ]

    with fitz.open(PDF_PATH) as pdf:

        print("=" * 65)
        print("INSPECTION OF FLAGGED PDF PAGES")
        print("=" * 65)

        for page_index in flagged_pages:

            page = pdf[page_index]

            images = page.get_images(full=True)
            drawings = page.get_drawings()
            blocks = page.get_text("blocks")

            print(f"\nPDF page: {page_index + 1}")
            print(f"Python index: {page_index}")
            print(f"Text blocks: {len(blocks)}")
            print(f"Images: {len(images)}")
            print(f"Drawings: {len(drawings)}")

            if images:
                print("Status: Contains images")

            elif drawings:
                print("Status: Contains graphical elements")

            else:
                print("Status: Possibly blank page")

            print("-" * 65)


if __name__ == "__main__":
    inspect_pages()
