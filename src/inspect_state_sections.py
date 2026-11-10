
import json

INPUT_FILE = "data/processed/pages.jsonl"


def inspect_pages(start_page, end_page):
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)

            page_number = record["pdf_page"] + 1

            if start_page <= page_number <= end_page:
                lines = [
                    item.strip()
                    for item in record["text"].splitlines()
                    if item.strip()
                ]

                print("\n" + "=" * 65)
                print(f"PDF PAGE: {page_number}")
                print("=" * 65)

                for item in lines[:8]:
                    print(item)


if __name__ == "__main__":
    # Inspect the beginning of the state-wise advisory section.
    inspect_pages(14, 40)
