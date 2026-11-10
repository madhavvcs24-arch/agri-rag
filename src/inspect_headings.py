
import json
import re
from collections import Counter, defaultdict

INPUT_FILE = "data/processed/pages.jsonl"

# Known Indian states and union territories.
STATES_AND_UTS = {
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
    "Chhattisgarh", "Goa", "Gujarat", "Haryana",
    "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
    "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi", "Jammu & Kashmir", "Ladakh",
    "Lakshadweep", "Puducherry"
}


def is_heading_candidate(line):
    line = line.strip()

    if not line or len(line) > 55:
        return False

    # Ignore lines that are mostly numbers or punctuation.
    if not re.search(r"[A-Za-z]", line):
        return False

    # Ignore ordinary sentence-like lines.
    if line.endswith((".", ",", ";", ":")):
        return False

    words = line.split()

    # Keep short title-case or uppercase lines.
    title_case = all(
        word[0].isupper() or word.isupper()
        for word in words
        if word
    )

    return title_case


def inspect_headings():
    first_line_counts = Counter()
    candidate_counts = Counter()
    candidate_pages = defaultdict(list)

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        for record_number, line in enumerate(file, start=1):
            record = json.loads(line)

            pdf_page = record["pdf_page"] + 1
            text = record["text"]

            lines = [
                item.strip()
                for item in text.splitlines()
                if item.strip()
            ]

            if not lines:
                continue

            first_line_counts[lines[0]] += 1

            for item in lines:
                if is_heading_candidate(item):
                    candidate_counts[item] += 1
                    candidate_pages[item].append(pdf_page)

    print("\n1. FIRST NON-EMPTY LINE ON EACH PAGE")
    print("------------------------------------")

    for heading, count in first_line_counts.most_common(40):
        print(f"{count:3} times | {heading}")

    print("\n2. KNOWN STATE / UT HEADINGS")
    print("----------------------------")

    for heading in sorted(STATES_AND_UTS):
        pages = [
            page for page_heading, page_list in candidate_pages.items()
            if page_heading.casefold() == heading.casefold()
            for page in page_list
        ]

        if pages:
            print(f"{heading}: pages {pages[:20]}")

    print("\n3. MOST COMMON HEADING CANDIDATES")
    print("---------------------------------")

    for heading, count in candidate_counts.most_common(100):
        pages = candidate_pages[heading][:10]
        print(f"{count:3} times | {heading} | pages: {pages}")


if __name__ == "__main__":
    inspect_headings()
