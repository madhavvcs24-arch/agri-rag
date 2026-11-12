
import json
import re

INPUT_FILE = "data/processed/pages.jsonl"

CROP_CATEGORIES = {
    "CEREAL CROPS",
    "PULSE CROPS",
    "OILSEED CROPS",
    "FRUIT CROPS",
    "VEGETABLE CROPS",
    "COMMERCIAL CROPS",
    "FIBRE CROPS",
    "SPICE CROPS",
    "PLANTATION CROPS",
    "FLOWER CROPS",
    "MEDICINAL AND AROMATIC PLANTS",
    "LIVESTOCK",
    "POULTRY",
    "FISHERIES",
}

KNOWN_CROPS = {
    "Rice", "Paddy", "Maize", "Wheat", "Finger millet",
    "Ragi", "Jowar", "Bajra", "Sorghum", "Barley",
    "Groundnut", "Soybean", "Sunflower", "Sesame",
    "Mustard", "Pigeonpea", "Redgram", "Blackgram",
    "Greengram", "Chickpea", "Cotton", "Sugarcane",
    "Jute", "Banana", "Mango", "Coconut", "Arecanut",
    "Ginger", "Turmeric", "Tomato", "Brinjal",
    "Chilli", "Onion", "Potato",
}


def normalize(line):
    return re.sub(r"\s+", " ", line.strip()).casefold()


def inspect_candidates():
    category_lookup = {
        normalize(item): item for item in CROP_CATEGORIES
    }

    crop_lookup = {
        normalize(item): item for item in KNOWN_CROPS
    }

    print("\nCROP HEADING CANDIDATES")
    print("=======================")

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        for record_line in file:
            record = json.loads(record_line)

            pdf_page = record["pdf_page"] + 1

            lines = [
                line.strip()
                for line in record["text"].splitlines()
                if line.strip()
            ]

            for index, line in enumerate(lines):
                key = normalize(line)

                if key in category_lookup:
                    heading_type = "CATEGORY"
                    heading = category_lookup[key]

                elif key in crop_lookup:
                    heading_type = "CROP"
                    heading = crop_lookup[key]

                else:
                    continue

                previous_line = (
                    lines[index - 1] if index > 0 else "<PAGE START>"
                )

                next_line = (
                    lines[index + 1]
                    if index + 1 < len(lines)
                    else "<PAGE END>"
                )

                print(f"\nPDF page: {pdf_page}")
                print(f"Type: {heading_type}")
                print(f"Heading: {heading}")
                print(f"Previous: {previous_line[:100]}")
                print(f"Next: {next_line[:100]}")


if __name__ == "__main__":
    inspect_candidates()
