
import fitz

PDF_PATH = "data/raw/icar_kharif_2025_english.pdf"

CATEGORIES = {
    "CEREAL CROPS",
    "PULSE CROPS",
    "OILSEED CROPS",
    "FRUIT CROPS",
    "VEGETABLE CROPS",
    "COMMERCIAL CROPS",
    "SPICE CROPS",
}

PAGES_TO_INSPECT = [210, 216, 228, 249, 257, 287, 299]


def inspect_categories():

    with fitz.open(PDF_PATH) as pdf:

        for page_number in PAGES_TO_INSPECT:

            page = pdf[page_number - 1]
            page_data = page.get_text("dict")

            for block in page_data["blocks"]:

                if "lines" not in block:
                    continue

                for line in block["lines"]:

                    for span in line["spans"]:

                        text = span["text"].strip()

                        if text.upper() not in CATEGORIES:
                            continue

                        print("\n" + "=" * 65)
                        print(f"PDF PAGE: {page_number}")
                        print(f"CATEGORY: {text}")
                        print(f"FONT: {span['font']}")
                        print(f"SIZE: {span['size']}")
                        print(f"COLOR: {span['color']}")
                        print(f"FLAGS: {span['flags']}")
                        print(f"POSITION: {span['bbox']}")


if __name__ == "__main__":
    inspect_categories()
