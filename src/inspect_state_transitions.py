
import json

INPUT_FILE = "data/processed/pages_with_state.jsonl"


def inspect_transitions():
    records = []

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        for line in file:
            records.append(json.loads(line))

    previous_state = None

    print("\nSTATE SECTION TRANSITIONS")
    print("=" * 60)

    for record in records:
        state = record["state"]

        if state != previous_state:
            page = record["pdf_page"] + 1

            print(
                f"\nPDF Page {page}: {previous_state} -> {state}"
            )

            lines = [
                item.strip()
                for item in record["text"].splitlines()
                if item.strip()
            ]

            print("First lines:")
            for item in lines[:5]:
                print("  ", item)

            previous_state = state


if __name__ == "__main__":
    inspect_transitions()
