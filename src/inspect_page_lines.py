
import fitz

PDF_PATH = "data/raw/icar_kharif_2025_english.pdf"
PAGE_NUMBER = 216

def inspect_page_lines():
    with fitz.open(PDF_PATH) as pdf:
        page = pdf[PAGE_NUMBER - 1]
        blocks = page.get_text("dict")["blocks"]

        lines = []

        for block in blocks:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                spans = line["spans"]

                text = " ".join(
                    span["text"].strip()
                    for span in spans
                    if span["text"].strip()
                )

                if not text:
                    continue

                x0, y0, x1, y1 = line["bbox"]

                # Ignore the repeated document header
                if "ICAR Kharif Agro-Advisory" in text:
                    continue

                lines.append({
                    "y": y0,
                    "x": x0,
                    "text": text
                })

        # Sort lines from top to bottom
        lines.sort(key=lambda item: (item["y"], item["x"]))

        print(f"PDF page: {PAGE_NUMBER}")
        print("=" * 90)

        for line in lines:
            print(f"Y: {line['y']:7.2f} | X: {line['x']:7.2f}")
            print(line["text"])
            print("-" * 90)

if __name__ == "__main__":
    inspect_page_lines()
