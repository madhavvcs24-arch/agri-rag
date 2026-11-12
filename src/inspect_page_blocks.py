
import fitz

PDF_PATH = "data/raw/icar_kharif_2025_english.pdf"
PAGE_NUMBER = 216

def inspect_page_blocks():
    with fitz.open(PDF_PATH) as pdf:
        page = pdf[PAGE_NUMBER - 1]
        blocks = page.get_text("dict")["blocks"]

        print(f"PDF page: {PAGE_NUMBER}")
        print(f"Total blocks: {len(blocks)}")
        print("=" * 80)

        for index, block in enumerate(blocks):
            if "lines" not in block:
                continue

            x0, y0, x1, y1 = block["bbox"]

            text_parts = []

            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        text_parts.append(text)

            text = " ".join(text_parts)

            if text:
                print(
                    f"\nBlock {index} | "
                    f"Y: {y0:.1f}-{y1:.1f} | "
                    f"X: {x0:.1f}-{x1:.1f}"
                )
                print(text[:300])

if __name__ == "__main__":
    inspect_page_blocks()
