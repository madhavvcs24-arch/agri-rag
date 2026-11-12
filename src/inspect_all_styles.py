
import fitz

PDF_PATH = "data/raw/icar_kharif_2025_english.pdf"

PAGES_TO_INSPECT = [216, 249, 257, 287, 299]


def inspect_styles():

    with fitz.open(PDF_PATH) as pdf:

        for page_number in PAGES_TO_INSPECT:

            page = pdf[page_number - 1]
            data = page.get_text("dict")

            print("\n" + "=" * 75)
            print(f"PDF PAGE: {page_number}")
            print("=" * 75)

            for block in data["blocks"]:

                if "lines" not in block:
                    continue

                for line in block["lines"]:

                    for span in line["spans"]:

                        text = span["text"].strip()

                        if not text:
                            continue

                        color = span["color"]
                        font = span["font"]

                        if font == "Cambria-Bold":
                            print(
                                f"Text: {text[:65]:65} | "
                                f"Color: {color}"
                            )


if __name__ == "__main__":
    inspect_styles()
