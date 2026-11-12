
import json
from pathlib import Path

OLD_PATH = Path("data/processed/pages_raw.jsonl")
NEW_PATH = Path("data/processed/pages_raw_v2.jsonl")

TEST_PAGES = [126, 150, 200, 215, 227, 250]


def load_pages(path):
    pages = {}

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)
            pages[record["pdf_page"]] = record

    return pages


def main():
    old_pages = load_pages(OLD_PATH)
    new_pages = load_pages(NEW_PATH)

    print("EXTRACTION COMPARISON")
    print("=" * 60)

    for page_number in TEST_PAGES:
        old_text = old_pages[page_number]["text"]
        new_text = new_pages[page_number]["text"]

        print(f"\nPDF PAGE {page_number + 1}")
        print("-" * 60)

        print(f"Old character count: {len(old_text)}")
        print(f"New character count: {len(new_text)}")

        print("\nNEW EXTRACTION PREVIEW:")
        print(new_text[:1000])

        print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
