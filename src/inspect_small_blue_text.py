
import fitz

PDF_PATH = "data/raw/icar_kharif_2025_english.pdf"

TARGET_COLOR = 13209
TARGET_FONT = "Cambria-Bold"
TARGET_SIZE = 8.1

MAX_RESULTS = 40


def inspect_small_blue_text():

    count = 0

    with fitz.open(PDF_PATH) as pdf:

        for page_number, page in enumerate(pdf, start=1):

            data = page.get_text("dict")

            for block in data["blocks"]:

                if "lines" not in block:
                    continue

                for line in block["lines"]:

                    for span in line["spans"]:

                        if (
                            span["font"] == TARGET_FONT
                            and round(span["size"], 1) == TARGET_SIZE
                            and span["color"] == TARGET_COLOR
                        ):

                            text = span["text"].strip()

                            if not text:
                                continue

                            count += 1

                            print(
                                f"Page {page_number:3} | "
                                f"{text[:100]}"
                            )

                            if count >= MAX_RESULTS:
                                print("\nReached inspection limit.")
                                print(f"Matches inspected: {count}")
                                return

    print(f"\nTotal matches inspected: {count}")


if __name__ == "__main__":
    inspect_small_blue_text()
