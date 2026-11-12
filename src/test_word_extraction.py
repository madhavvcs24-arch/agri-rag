
import fitz
from pathlib import Path

PDF_PATH = Path("data/raw/icar_kharif_2025_english.pdf")

Y_TOLERANCE = 1.5


def reconstruct_page(page):
    words = page.get_text("words", sort=True)
    lines = []

    for word in words:
        x0, y0, x1, y1, text = word[:5]

        center_y = (y0 + y1) / 2

        matched_line = None

        for line in lines:
            if abs(line["center_y"] - center_y) <= Y_TOLERANCE:
                matched_line = line
                break

        if matched_line is None:
            lines.append({
                "center_y": center_y,
                "words": [(x0, text)]
            })
        else:
            matched_line["words"].append((x0, text))

    lines.sort(key=lambda line: line["center_y"])

    reconstructed_lines = []

    for line in lines:
        line["words"].sort(key=lambda item: item[0])

        text = " ".join(
            word for _, word in line["words"]
        )

        reconstructed_lines.append(text)

    return "\n".join(reconstructed_lines)


def main():
    pdf = fitz.open(PDF_PATH)

    test_pages = [126, 150, 200, 215, 227, 250]

    for page_number in test_pages:
        page = pdf[page_number]

        text = reconstruct_page(page)

        print("\n" + "=" * 70)
        print(f"PDF PAGE: {page_number + 1}")
        print("=" * 70)
        print(text)


if __name__ == "__main__":
    main()
