
import json
import csv
from pathlib import Path

JSON_PATH = Path("data/processed/pages_raw_v2.jsonl")
CSV_PATH = Path("data/processed/extraction_report_v2.csv")


def main():
    records = []

    with open(JSON_PATH, "r", encoding="utf-8") as file:
        for line in file:
            records.append(json.loads(line))

    with open(CSV_PATH, "r", encoding="utf-8") as file:
        report = list(csv.DictReader(file))

    print("INGESTION VALIDATION")
    print("=" * 50)

    print(f"JSON records: {len(records)}")
    print(f"CSV report rows: {len(report)}")

    # Check total records.
    assert len(records) == 310, "Incorrect number of JSON records!"
    assert len(report) == 310, "Incorrect number of CSV rows!"

    # Check page numbering.
    page_numbers = [record["pdf_page"] for record in records]

    assert page_numbers == list(range(310)), "Page numbering error!"

    # Check required fields.
    required_fields = {
        "source",
        "pdf_page",
        "printed_page",
        "text",
        "character_count",
        "extraction_status"
    }

    for record in records:
        assert required_fields.issubset(record.keys())

        assert record["character_count"] == len(record["text"])

    # Check empty pages.
    empty_pages = [
        record["pdf_page"] + 1
        for record in records
        if record["extraction_status"] == "empty"
    ]

    print(f"Empty PDF pages: {empty_pages}")

    # Inspect selected pages.
    test_pages = [126, 150, 200, 215, 227, 250]

    print("\nSAMPLE PAGE VALIDATION")
    print("=" * 50)

    for page_number in test_pages:
        record = records[page_number]

        print(
            f"PDF page {page_number + 1}: "
            f"{record['character_count']} characters, "
            f"status={record['extraction_status']}"
        )

        assert record["character_count"] > 0

    print("\nAll structural validation checks passed!")


if __name__ == "__main__":
    main()
