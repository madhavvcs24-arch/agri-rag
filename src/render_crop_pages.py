
import fitz
from pathlib import Path

PDF_PATH = "data/raw/icar_kharif_2025_english.pdf"
OUTPUT_DIR = Path("data/processed/crop_page_images")

PAGES_TO_RENDER = [210, 216, 228, 249]

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with fitz.open(PDF_PATH) as pdf:

    for page_number in PAGES_TO_RENDER:

        # Convert PDF page number to zero-based index.
        page = pdf[page_number - 1]

        # Render at 1.5x resolution.
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))

        output_path = OUTPUT_DIR / f"page_{page_number}.png"

        pix.save(output_path)

        print(f"Rendered PDF page {page_number}: {output_path}")

print("\nAll selected pages rendered successfully!")
