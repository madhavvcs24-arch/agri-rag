
import fitz
from pathlib import Path

PDF_PATH = Path("data/raw/icar_kharif_2025_english.pdf")


def main():
    pdf = fitz.open(PDF_PATH)

    # PDF page 127 is zero-based index 126.
    page = pdf[126]

    # Render the page as an image.
    output_path = Path("data/processed/karnataka_page127.png")

    pix = page.get_pixmap(
        matrix=fitz.Matrix(2, 2),
        alpha=False
    )

    pix.save(output_path)

    print(f"Rendered page saved to: {output_path}")

    # Inspect text blocks and their coordinates.
    blocks = page.get_text("dict")["blocks"]

    for block_number, block in enumerate(blocks):
        if "lines" not in block:
            continue

        print("\n" + "=" * 70)
        print(f"BLOCK {block_number}")
        print(f"Bounding box: {block['bbox']}")

        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()

                if text:
                    print(
                        f"Text: {text[:150]}"
                        f" | Font: {span['font']}"
                        f" | Size: {span['size']}"
                        f" | Color: {span['color']}"
                    )


if __name__ == "__main__":
    main()
