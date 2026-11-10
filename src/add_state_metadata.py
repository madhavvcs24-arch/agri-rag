
import json
import csv
from pathlib import Path


INPUT_FILE = Path("data/processed/pages.jsonl")
OUTPUT_FILE = Path("data/processed/pages_with_state.jsonl")
REPORT_FILE = Path("data/processed/state_report.csv")

FIRST_ADVISORY_PAGE = 17
LAST_ADVISORY_PAGE = 307

STATE_ALIASES = {
    "andaman & nicobar islands": "Andaman & Nicobar Islands",
    "andaman and nicobar islands": "Andaman & Nicobar Islands",
    "andhra pradesh": "Andhra Pradesh",
    "arunachal pradesh": "Arunachal Pradesh",
    "assam": "Assam",
    "bihar": "Bihar",
    "chhattisgarh": "Chhattisgarh",
    "goa": "Goa",
    "gujarat": "Gujarat",
    "haryana & delhi": "Haryana & Delhi",
    "himachal pradesh": "Himachal Pradesh",
    "jammu & kashmir": "Jammu & Kashmir",
    "jharkhand": "Jharkhand",
    "karnataka": "Karnataka",
    "kerala": "Kerala",
    "ladakh": "Ladakh",
    "madhya pradesh": "Madhya Pradesh",
    "maharashtra": "Maharashtra",
    "manipur": "Manipur",
    "meghalaya": "Meghalaya",
    "mizoram": "Mizoram",
    "nagaland": "Nagaland",
    "odisha": "Odisha",
    "punjab": "Punjab",
    "rajasthan": "Rajasthan",
    "sikkim": "Sikkim",
    "tamil nadu & puducherry": "Tamil Nadu & Puducherry",
    "telengana": "Telangana",
    "telangana": "Telangana",
    "tripura": "Tripura",
    "uttar pradesh": "Uttar Pradesh",
    "uttarakhand": "Uttarakhand",
    "west bengal": "West Bengal",
}


def detect_state(text):
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # State heading may follow a page number.
    for line in lines[:3]:
        normalized = line.casefold()

        if normalized in STATE_ALIASES:
            return STATE_ALIASES[normalized]

    return None


def add_state_metadata():
    current_state = None
    total_pages = 0
    assigned_pages = 0
    unassigned_pages = []
    state_counts = {}

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

        for line in infile:
            record = json.loads(line)
            total_pages += 1

            pdf_page = record["pdf_page"] + 1

            if pdf_page < FIRST_ADVISORY_PAGE:
                continue

            if pdf_page > LAST_ADVISORY_PAGE:
                continue

            detected_state = detect_state(record["text"])

            if detected_state:
                current_state = detected_state

            if current_state is None:
                unassigned_pages.append(pdf_page)
                continue

            record["state"] = current_state
            record["state_detected_on_page"] = bool(detected_state)

            outfile.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )

            assigned_pages += 1
            state_counts[current_state] = (
                state_counts.get(current_state, 0) + 1
            )

    with open(REPORT_FILE, "w", newline="", encoding="utf-8") as report:
        writer = csv.writer(report)
        writer.writerow(["state", "number_of_pages"])

        for state, count in sorted(state_counts.items()):
            writer.writerow([state, count])

    print("\nSTATE METADATA EXTRACTION")
    print("-------------------------")
    print("Total input pages:", total_pages)
    print("Pages assigned a state:", assigned_pages)
    print("Pages without a state:", len(unassigned_pages))
    print("Unique states/UT sections:", len(state_counts))

    print("\nPages per state:")
    for state, count in sorted(state_counts.items()):
        print(f"{state}: {count}")

    print("\nUnassigned PDF pages:", unassigned_pages)
    print("\nOutput:", OUTPUT_FILE)
    print("Report:", REPORT_FILE)


if __name__ == "__main__":
    add_state_metadata()
