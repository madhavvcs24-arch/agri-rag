
import fitz

PDF_PATH = "data/raw/icar_kharif_2025_english.pdf"

PAGES_TO_INSPECT = [210, 228, 249]

CANDIDATES = {
    "Maize",
    "Rice",
    "Paddy",
    "Groundnut",
    "Turmeric",
    "Sesame",
    "Mango",
    "Litchi",
    "Pear",
}


def inspect_styles():

    with fitz.open(PDF_PATH) as pdf:

        for page_number in PAGES_TO_INSPECT:

            page = pdf[page_number - 1]
            page_data = page.get_text("dict")

            print("\n" + "=" * 75)
            print(f"PDF PAGE: {page_number}")
            print("=" * 75)

            for block in page_data["blocks"]:

                if "lines" not in block:
                    continue

                for line in block["lines"]:

                    for span in line["spans"]:

                        text = span["text"].strip()

                        if text not in CANDIDATES:
                            continue

                        print(f"\nHeading candidate: {text}")
                        print(f"Font: {span['font']}")
                        print(f"Size: {span['size']}")
                        print(f"Color: {span['color']}")
                        print(f"Flags: {span['flags']}")
                        print(f"Position: {span['bbox']}")


if __name__ == "__main__":
    inspect_styles()
