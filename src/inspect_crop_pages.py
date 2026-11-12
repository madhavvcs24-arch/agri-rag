
import json

INPUT_FILE = "data/processed/pages_with_state.jsonl"

# PDF page numbers we want to inspect.
PAGES_TO_INSPECT = [210, 216, 228, 249]


def inspect_pages():
    selected_pages = set(PAGES_TO_INSPECT)

    with open(INPUT_FILE, "r", encoding="utf-8") as file:

        for line in file:
            record = json.loads(line)

            # Stored page numbers are zero-based.
            pdf_page = record["pdf_page"] + 1

            if pdf_page not in selected_pages:
                continue

            print("\n" + "=" * 80)
            print(f"PDF PAGE: {pdf_page}")
            print(f"STATE: {record.get('state', 'Unknown')}")
            print("=" * 80)

            print(record["text"])


if __name__ == "__main__":
    inspect_pages()
