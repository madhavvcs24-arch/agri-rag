
import json
from pathlib import Path

OLD_PATH = Path("data/processed/pages_with_state.jsonl")
NEW_PATH = Path("data/processed/pages_with_state_v2.jsonl")
CLEAN_PATH = Path("data/processed/pages_v2.jsonl")

MISMATCHED_PAGES = [
    40, 48, 62, 84, 120, 126, 136,
    178, 184, 188, 194, 266, 280, 296
]


def load_jsonl(path):
    records = {}

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)
            records[record["pdf_page"] + 1] = record

    return records


def print_first_lines(text, count=8):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines[:count]:
        print("  ", line[:180])


def main():
    old_records = load_jsonl(OLD_PATH)
    new_records = load_jsonl(NEW_PATH)
    clean_records = load_jsonl(CLEAN_PATH)

    for page in MISMATCHED_PAGES:
        old = old_records[page]
        new = new_records[page]
        clean = clean_records[page]

        print("\n" + "=" * 75)
        print(f"PDF PAGE {page}")
        print("=" * 75)

        print(f"OLD STATE: {old['state']}")
        print(f"NEW STATE: {new['state']}")
        print(
            "New state detected on this page:",
            new["state_detected_on_page"]
        )

        print("\nNEW CLEANED TEXT — FIRST 8 NON-EMPTY LINES")
        print("-" * 75)
        print_first_lines(clean["text"])

        print("\nPREVIOUS PAGE — NEW STATE")
        print("-" * 75)

        if page - 1 in new_records:
            print("State:", new_records[page - 1]["state"])
            print_first_lines(
                clean_records[page - 1]["text"],
                count=3
            )

        print("\nNEXT PAGE — NEW STATE")
        print("-" * 75)

        if page + 1 in new_records:
            print("State:", new_records[page + 1]["state"])
            print_first_lines(
                clean_records[page + 1]["text"],
                count=3
            )


if __name__ == "__main__":
    main()
