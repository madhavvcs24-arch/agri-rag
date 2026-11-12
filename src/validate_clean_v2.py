
import json
import re
from pathlib import Path

INPUT_PATH = Path("data/processed/pages_v2.jsonl")


def main():
    records = []

    with open(INPUT_PATH, "r", encoding="utf-8") as file:
        for line in file:
            records.append(json.loads(line))

    print("CLEANED DATA VALIDATION")
    print("=" * 50)

    # 1. Record count
    print(f"Total records: {len(records)}")
    assert len(records) == 310

    # 2. Page numbering
    page_numbers = [r["pdf_page"] for r in records]
    assert page_numbers == list(range(310))
    print("Page numbering: Correct")

    # 3. Empty pages
    empty_pages = [
        r["pdf_page"] + 1
        for r in records
        if not r["text"].strip()
    ]

    print(f"Empty pages: {empty_pages}")
    assert len(empty_pages) == 8

    # 4. Check corrupted characters and repeated headers
    all_text = "\n".join(r["text"] for r in records)

    assert "ϐ" not in all_text
    assert "ﬀ" not in all_text
    assert "ﬁ" not in all_text
    assert "ﬂ" not in all_text
    assert "ICAR Kharif Agro-Advisory 2025" not in all_text

    print("Known corrupted characters: None found")
    print("Repeated headers: None found")

    # 5. Character count validation
    for record in records:
        assert record["character_count"] == len(record["text"])

    print("Character counts: Correct")

    # 6. Inspect sample pages
    test_pages = [126, 150, 200, 215, 227, 250]

    print("\nSAMPLE CLEANED TEXT")
    print("=" * 50)

    for page_number in test_pages:
        record = records[page_number]

        print(f"\nPDF PAGE {page_number + 1}")
        print("-" * 50)
        print(record["text"][:500])

    print("\nAll cleaning validation checks passed!")


if __name__ == "__main__":
    main()
