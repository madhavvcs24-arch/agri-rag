
import json
from pathlib import Path

OLD_PATH = Path("data/processed/pages_with_state.jsonl")
NEW_PATH = Path("data/processed/pages_with_state_v2.jsonl")


def load_states(path):
    states = {}

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)
            states[record["pdf_page"]] = record["state"]

    return states


def main():
    old_states = load_states(OLD_PATH)
    new_states = load_states(NEW_PATH)

    print("STATE METADATA COMPARISON")
    print("=" * 60)

    differences = []

    for page in sorted(set(old_states) | set(new_states)):
        old_state = old_states.get(page)
        new_state = new_states.get(page)

        if old_state != new_state:
            differences.append((page + 1, old_state, new_state))

    print(f"Old assigned pages: {len(old_states)}")
    print(f"New assigned pages: {len(new_states)}")
    print(f"Pages with different assignments: {len(differences)}")

    if differences:
        print("\nDIFFERENCES")
        print("-" * 60)

        for page, old, new in differences:
            print(
                f"PDF page {page}: "
                f"Old = {old} | New = {new}"
            )
    else:
        print("\nAll state assignments match!")


if __name__ == "__main__":
    main()
