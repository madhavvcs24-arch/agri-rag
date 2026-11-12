
import json
import re
import csv
import time

from pathlib import Path


INPUT_PATH = Path("data/processed/pages_raw_v2.jsonl")
OUTPUT_PATH = Path("data/processed/pages_v2.jsonl")
REPORT_PATH = Path("data/processed/cleaning_report_v2.csv")

REPEATED_HEADER = "ICAR Kharif Agro-Advisory 2025"

LIGATURES = {
    "ϐ": "f",
    "ﬀ": "ff",
    "ﬁ": "fi",
    "ﬂ": "fl",
    "ﬃ": "ffi",
    "ﬄ": "ffl",
    "ﬅ": "st",
    "ﬆ": "st",
}


def clean_text(text):
    replacement_count = 0
    header_count = 0

    # Fix known PDF character-mapping issues.
    for old, new in LIGATURES.items():
        count = text.count(old)
        replacement_count += count
        text = text.replace(old, new)

    cleaned_lines = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            cleaned_lines.append("")
            continue

        if line == REPEATED_HEADER:
            header_count += 1
            continue

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # Keep paragraph boundaries, but remove excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip(), replacement_count, header_count


def main():
    start_time = time.time()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    cleaned_pages = []
    report_rows = []

    with open(INPUT_PATH, "r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)

            cleaned_text, replacements, headers = clean_text(
                record["text"]
            )

            updated_record = record.copy()
            updated_record["text"] = cleaned_text
            updated_record["character_count"] = len(cleaned_text)

            cleaned_pages.append(updated_record)

            report_rows.append({
                "pdf_page": record["pdf_page"],
                "original_characters": len(record["text"]),
                "cleaned_characters": len(cleaned_text),
                "ligature_replacements": replacements,
                "headers_removed": headers,
            })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        for record in cleaned_pages:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    with open(REPORT_PATH, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "pdf_page",
                "original_characters",
                "cleaned_characters",
                "ligature_replacements",
                "headers_removed",
            ],
        )
        writer.writeheader()
        writer.writerows(report_rows)

    elapsed = time.time() - start_time

    total_replacements = sum(
        row["ligature_replacements"] for row in report_rows
    )

    total_headers = sum(
        row["headers_removed"] for row in report_rows
    )

    print("\nCLEANING SUMMARY")
    print("=" * 50)
    print(f"Pages processed: {len(cleaned_pages)}")
    print(f"Ligature replacements: {total_replacements}")
    print(f"Repeated headers removed: {total_headers}")
    print(f"Time taken: {elapsed:.2f} seconds")
    print(f"\nOutput: {OUTPUT_PATH}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
