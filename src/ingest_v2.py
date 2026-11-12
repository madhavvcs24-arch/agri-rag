
import fitz
import json
import csv
import time

from pathlib import Path


PDF_PATH = Path("data/raw/icar_kharif_2025_english.pdf")

OUTPUT_PATH = Path("data/processed/pages_raw_v2.jsonl")
REPORT_PATH = Path("data/processed/extraction_report_v2.csv")

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
    start_time = time.time()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    pdf = fitz.open(PDF_PATH)

    total_pages = len(pdf)
    extracted_pages = 0
    empty_pages = 0

    with open(OUTPUT_PATH, "w", encoding="utf-8") as output_file, \
         open(REPORT_PATH, "w", newline="", encoding="utf-8") as report_file:

        writer = csv.writer(report_file)

        writer.writerow([
            "pdf_page",
            "character_count",
            "status"
        ])

        for page_number, page in enumerate(pdf):

            text = reconstruct_page(page)

            character_count = len(text.strip())

            if character_count == 0:
                status = "empty"
                empty_pages += 1
            elif character_count < 100:
                status = "needs_review"
            else:
                status = "extracted"
                extracted_pages += 1

            record = {
                "source": "ICAR Kharif Agro-Advisories for Farmers 2025",
                "pdf_page": page_number,
                "printed_page": None,
                "text": text,
                "character_count": character_count,
                "extraction_status": status
            }

            output_file.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )

            writer.writerow([
                page_number,
                character_count,
                status
            ])

    elapsed = time.time() - start_time

    print("\nEXTRACTION SUMMARY")
    print("=" * 50)
    print(f"Total PDF pages: {total_pages}")
    print(f"Successfully extracted: {extracted_pages}")
    print(f"Empty pages: {empty_pages}")
    print(f"Time taken: {elapsed:.2f} seconds")
    print(f"\nOutput: {OUTPUT_PATH}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
