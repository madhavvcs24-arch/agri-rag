
import fitz

PDF_PATH = "data/raw/icar_kharif_2025_english.pdf"

PAGES = [210, 216, 228, 249]

RED_COLOR = 10027008
TARGET_FONT = "Cambria-Bold"
TARGET_SIZE = 10.0


def inspect_pages():

    with fitz.open(PDF_PATH) as pdf:

        for page_number in PAGES:

            page = pdf[page_number - 1]
            blocks = page.get_text("dict")["blocks"]

            headings = []
            text_blocks = []

            for block in blocks:

                if "lines" not in block:
                    continue

                block_text = []

                for line in block["lines"]:

                    for span in line["spans"]:

                        text = span["text"].strip()

                        if not text:
                            continue

                        if (
                            span["font"] == TARGET_FONT
                            and round(span["size"], 1) == TARGET_SIZE
                            and span["color"] == RED_COLOR
                        ):

                            headings.append({
                                "text": text,
                                "y": span["bbox"][1]
                            })

                        block_text.append(text)

                if block_text:

                    text_blocks.append({
                        "text": " ".join(block_text),
                        "y0": block["bbox"][1],
                        "y1": block["bbox"][3]
                    })

            print(f"\n{'=' * 75}")
            print(f"PDF PAGE {page_number}")
            print("=" * 75)

            for heading in sorted(
                headings,
                key=lambda item: item["y"]
            ):

                print(
                    f"\nHEADING: {heading['text']} "
                    f"(Y={heading['y']:.2f})"
                )

                matching_blocks = [
                    block for block in text_blocks
                    if block["y0"] <= heading["y"] <= block["y1"]
                ]

                if matching_blocks:

                    for block in matching_blocks:

                        print(
                            f"  OVERLAPPING BLOCK: "
                            f"Y={block['y0']:.2f}-"
                            f"{block['y1']:.2f}"
                        )

                        print(f"  {block['text'][:180]}")

                else:
                    print("  No overlapping text block found.")


if __name__ == "__main__":
    inspect_pages()
