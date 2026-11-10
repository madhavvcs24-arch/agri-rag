
import json
from collections import Counter

INPUT_FILE = "data/processed/pages_raw.jsonl"

def inspect_patterns():

    all_text = []
    first_lines = Counter()
    last_lines = Counter()

    with open(INPUT_FILE, encoding="utf-8") as file:

        for line in file:

            record = json.loads(line)
            text = record["text"]

            all_text.append(text)

            lines = [
                line.strip()
                for line in text.splitlines()
                if line.strip()
            ]

            if lines:
                first_lines[lines[0]] += 1
                last_lines[lines[-1]] += 1

    combined_text = "\n".join(all_text)

    print("=" * 60)
    print("TEXT CLEANING DIAGNOSTICS")
    print("=" * 60)

    # Character corruption
    print("\n1. Suspected corrupted character: ϐ")

    occurrences = combined_text.count("ϐ")

    print("Total occurrences:", occurrences)

    if occurrences:
        print("\nExamples:")

        for text in all_text:
            for word in text.split():
                if "ϐ" in word:
                    print(word)

                    if occurrences > 0:
                        occurrences -= 1

                    if occurrences <= 0:
                        break

            if occurrences <= 0:
                break

    # Repeated first lines
    print("\n2. Most common first lines")

    for line, count in first_lines.most_common(15):
        print(f"{count:3} times | {line}")

    # Repeated last lines
    print("\n3. Most common last lines")

    for line, count in last_lines.most_common(15):
        print(f"{count:3} times | {line}")


if __name__ == "__main__":
    inspect_patterns()
