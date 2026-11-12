
import fitz
from collections import Counter

PDF_PATH = "data/raw/icar_kharif_2025_english.pdf"


def analyze_styles():

    style_counts = Counter()

    with fitz.open(PDF_PATH) as pdf:

        for page_number, page in enumerate(pdf, start=1):

            data = page.get_text("dict")

            for block in data["blocks"]:

                if "lines" not in block:
                    continue

                for line in block["lines"]:

                    for span in line["spans"]:

                        text = span["text"].strip()

                        if not text:
                            continue

                        style = (
                            span["font"],
                            round(span["size"], 1),
                            span["color"],
                            span["flags"]
                        )

                        style_counts[style] += 1

    print("\nDOCUMENT FONT STYLE INVENTORY")
    print("=" * 85)

    for style, count in style_counts.most_common(30):

        font, size, color, flags = style

        print(
            f"Font: {font:25} | "
            f"Size: {size:5} | "
            f"Color: {color:10} | "
            f"Flags: {flags:3} | "
            f"Occurrences: {count}"
        )


if __name__ == "__main__":
    analyze_styles()
