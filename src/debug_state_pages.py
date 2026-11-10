
import json

INPUT_FILE = "data/processed/pages_with_state.jsonl"

PAGES_TO_CHECK = [119, 120, 121, 125, 126, 127, 135, 136, 137]


def inspect():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)
            page = record["pdf_page"] + 1

            if page not in PAGES_TO_CHECK:
                continue

            lines = [
                item.strip()
                for item in record["text"].splitlines()
                if item.strip()
            ]

            print("\n" + "=" * 55)
            print("PDF PAGE:", page)
            print("Assigned state:", record["state"])
            print(
                "State detected on this page:",
                record["state_detected_on_page"]
            )
            print("=" * 55)

            for item in lines[:10]:
                print(item)


if __name__ == "__main__":
    inspect()
