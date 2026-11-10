
import fitz
import csv
from pathlib import Path

PDF_PATH = "data/raw/icar_kharif_2025_english.pdf"
REPORT_PATH = "data/processed/extraction_report.csv"

OUTPUT_DIR = Path("data/processed/flagged_pages")


def render_flagged_pages():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(REPORT_PATH, encoding="utf-8") as file:
        report = list(csv.DictReader(file))

    flagged_pages = [
        int(row["pdf_page"])
        for row in report
        if row["status"] != "extracted"
    ]

    with fitz.open(PDF_PATH) as pdf:

        for page_index in flagged_pages:

            page = pdf[page_index]

            # Render at 1.5x resolution for inspection.
            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(1.5, 1.5),
                alpha=False
            )

            output_path = OUTPUT_DIR / f"page_{page_index + 1}.png"

            pixmap.save(output_path)

            print(f"Saved: {output_path}")

    print("\nVisual inspection images generated!")


if __name__ == "__main__":
    render_flagged_pages()
