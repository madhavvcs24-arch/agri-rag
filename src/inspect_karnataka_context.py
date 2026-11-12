
import json
import fitz
from pathlib import Path

PDF_PATH = Path("data/raw/icar_kharif_2025_english.pdf")
CHUNKS_PATH = Path("data/processed/chunks.jsonl")

TARGET_CHUNK_IDS = {457, 458, 461, 503, 504}


def main():
    with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
        chunks = [json.loads(line) for line in file]

    pdf = fitz.open(PDF_PATH)

    for chunk in chunks:
        if chunk["chunk_id"] not in TARGET_CHUNK_IDS:
            continue

        page_number = chunk["pdf_page"]

        print("\n" + "=" * 75)
        print(f"CHUNK ID: {chunk['chunk_id']}")
        print(f"PDF PAGE: {page_number + 1}")
        print("=" * 75)

        page = pdf[page_number]

        # Print the complete extracted text of the original PDF page.
        print(page.get_text("text", sort=True))


if __name__ == "__main__":
    main()
