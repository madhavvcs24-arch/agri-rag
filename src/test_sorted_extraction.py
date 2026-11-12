
import fitz
from pathlib import Path

PDF_PATH = Path("data/raw/icar_kharif_2025_english.pdf")


def main():
    pdf = fitz.open(PDF_PATH)

    # PDF page 127: zero-based index 126.
    page = pdf[126]

    print("=" * 70)
    print("DEFAULT EXTRACTION")
    print("=" * 70)

    print(page.get_text("text"))

    print("\n" + "=" * 70)
    print("SORTED EXTRACTION")
    print("=" * 70)

    print(page.get_text("text", sort=True))


if __name__ == "__main__":
    main()
