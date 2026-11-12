
import fitz
from collections import Counter, defaultdict

PDF_PATH = "data/raw/icar_kharif_2025_english.pdf"

RED_COLOR = 10027008
TARGET_FONT = "Cambria-Bold"
TARGET_SIZE = 10.0

heading_counts = Counter()
heading_pages = defaultdict(list)


def inspect_red_headings():

    with fitz.open(PDF_PATH) as pdf:

        for page_number, page in enumerate(pdf, start=1):

            data = page.get_text("dict")

            for block in data["blocks"]:

                if "lines" not in block:
                    continue

                for line in block["lines"]:

                    for span in line["spans"]:

                        if (
                            span["font"] != TARGET_FONT
                            or round(span["size"], 1) != TARGET_SIZE
                            or span["color"] != RED_COLOR
                        ):
                            continue

                        text = " ".join(span["text"].split())

                        if not text:
                            continue

                        heading_counts[text] += 1
                        heading_pages[text].append(page_number)

    print("\nRED HEADING INVENTORY")
    print("=" * 75)

    for heading, count in heading_counts.most_common():

        pages = heading_pages[heading][:8]

        print(
            f"{count:3} times | "
            f"{heading[:65]:65} | "
            f"Pages: {pages}"
        )

    print(f"\nUnique red heading texts: {len(heading_counts)}")


if __name__ == "__main__":
    inspect_red_headings()
