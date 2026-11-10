
import json
import csv
import re
import time
from pathlib import Path


INPUT_FILE = Path("data/processed/pages_raw.jsonl")
OUTPUT_FILE = Path("data/processed/pages.jsonl")
REPORT_FILE = Path("data/processed/cleaning_report.csv")

REPEATED_HEADER = "ICAR Kharif Agro-Advisory 2025"


def clean_text(text):
    # Fix the incorrectly extracted fi ligature.
    text = text.replace("ϐ", "f")

    # Process each line separately.
    lines = []

    for line in text.splitlines():
        line = line.strip()

        # Remove the repeated header only when it is a full line.
        if line == REPEATED_HEADER:
            continue

        lines.append(line)

    # Preserve paragraph boundaries, but remove excessive blank lines.
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_pages():
    start_time = time.time()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    total_pages = 0
    cleaned_pages = 0
    skipped_pages = 0
    total_replacements = 0
    total_headers_removed = 0

    report_rows = []

    with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

        for line in infile:
            record = json.loads(line)
            total_pages += 1

            original_text = record["text"]

            replacement_count = original_text.count("ϐ")
            header_count = sum(
                1 for item in original_text.splitlines()
                if item.strip() == REPEATED_HEADER
            )

            cleaned = clean_text(original_text)

            total_replacements += replacement_count
            total_headers_removed += header_count

            if not cleaned:
                skipped_pages += 1
                status = "skipped_empty"

            else:
                cleaned_record = {
                    **record,
                    "text": cleaned,
                    "character_count": len(cleaned),
                    "cleaning_status": "cleaned"
                }

                outfile.write(
                    json.dumps(cleaned_record, ensure_ascii=False) + "\n"
                )

                cleaned_pages += 1
                status = "cleaned"

            report_rows.append({
                "pdf_page": record["pdf_page"] + 1,
                "original_characters": len(original_text),
                "cleaned_characters": len(cleaned),
                "fi_replacements": replacement_count,
                "headers_removed": header_count,
                "status": status
            })

    with open(REPORT_FILE, "w", newline="", encoding="utf-8") as report:
        writer = csv.DictWriter(
            report,
            fieldnames=[
                "pdf_page",
                "original_characters",
                "cleaned_characters",
                "fi_replacements",
                "headers_removed",
                "status"
            ]
        )

        writer.writeheader()
        writer.writerows(report_rows)

    elapsed = time.time() - start_time

    print("\nCLEANING COMPLETED")
    print("-------------------------")
    print("Total pages:", total_pages)
    print("Cleaned pages:", cleaned_pages)
    print("Skipped empty pages:", skipped_pages)
    print("fi replacements:", total_replacements)
    print("Repeated headers removed:", total_headers_removed)
    print("Time taken: {:.2f} seconds".format(elapsed))
    print("\nOutput:", OUTPUT_FILE)
    print("Report:", REPORT_FILE)


if __name__ == "__main__":
    clean_pages()
