
import fitz
import json
import csv
import time
from pathlib import Path

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

PDF_PATH = Path("data/raw/icar_kharif_2025_english.pdf")

OUTPUT_DIR = Path("data/processed")

RAW_OUTPUT = OUTPUT_DIR / "pages_raw.jsonl"
REPORT_OUTPUT = OUTPUT_DIR / "extraction_report.csv"

SOURCE_NAME = "ICAR Kharif Agro-Advisories for Farmers 2025"

# Pages with fewer than 100 characters need inspection.
MIN_CHARACTERS = 100


# --------------------------------------------------
# MAIN INGESTION FUNCTION
# --------------------------------------------------

def ingest_pdf():

    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    start_time = time.perf_counter()

    extraction_report = []

    total_pages = 0
    successful_pages = 0
    flagged_pages = 0

    with fitz.open(PDF_PATH) as pdf:

        total_pages = len(pdf)

        with open(RAW_OUTPUT, "w", encoding="utf-8") as output_file:

            for page_index, page in enumerate(pdf):

                # Extract original text without cleaning it.
                raw_text = page.get_text("text")

                character_count = len(raw_text.strip())

                # Determine basic extraction status.
                if character_count == 0:
                    status = "empty"
                    flagged_pages += 1

                elif character_count < MIN_CHARACTERS:
                    status = "needs_review"
                    flagged_pages += 1

                else:
                    status = "extracted"
                    successful_pages += 1

                # Preserve original extraction and metadata.
                page_record = {
                    "source": SOURCE_NAME,
                    "pdf_page": page_index,
                    "printed_page": None,
                    "text": raw_text,
                    "character_count": character_count,
                    "extraction_status": status
                }

                # Save one JSON object per line.
                output_file.write(
                    json.dumps(page_record, ensure_ascii=False) + "\n"
                )

                # Record page-level extraction statistics.
                extraction_report.append({
                    "pdf_page": page_index,
                    "character_count": character_count,
                    "status": status
                })

                # Display progress every 25 pages.
                if (page_index + 1) % 25 == 0:
                    print(
                        f"Processed {page_index + 1}/{total_pages} pages"
                    )

    # Save extraction report.
    with open(
        REPORT_OUTPUT,
        "w",
        newline="",
        encoding="utf-8"
    ) as report_file:

        writer = csv.DictWriter(
            report_file,
            fieldnames=[
                "pdf_page",
                "character_count",
                "status"
            ]
        )

        writer.writeheader()
        writer.writerows(extraction_report)

    elapsed_time = time.perf_counter() - start_time

    # Final summary.
    print("\n" + "=" * 55)
    print("ICAR PDF INGESTION COMPLETE")
    print("=" * 55)

    print(f"Total PDF pages: {total_pages}")
    print(f"Successfully extracted: {successful_pages}")
    print(f"Flagged for inspection: {flagged_pages}")
    print(f"Time taken: {elapsed_time:.2f} seconds")

    print("\nGenerated files:")
    print(RAW_OUTPUT)
    print(REPORT_OUTPUT)


# --------------------------------------------------
# PROGRAM ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    ingest_pdf()
