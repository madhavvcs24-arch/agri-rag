
import json
import csv
import time
from pathlib import Path
from collections import Counter

from langchain_text_splitters import RecursiveCharacterTextSplitter


INPUT_PATH = Path("data/processed/pages_with_state_v2.jsonl")
OUTPUT_PATH = Path("data/processed/chunks_v2.jsonl")
REPORT_PATH = Path("data/processed/chunk_report_v2.csv")

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120


# --------------------------------------------------
# 1. CROP HEADINGS
# --------------------------------------------------

CROP_HEADINGS = {
    "paddy": "Paddy",
    "rice": "Paddy",

    "maize": "Maize",

    "finger millet": "Finger Millet",
    "ragi": "Finger Millet",

    "groundnut": "Groundnut",

    "sunflower": "Sunflower",

    "sorghum": "Sorghum",
    "jowar": "Sorghum",

    "pearl millet": "Pearl Millet",
    "bajra": "Pearl Millet",

    "wheat": "Wheat",

    "cotton": "Cotton",
    "sugarcane": "Sugarcane",

    "soybean": "Soybean",
    "soyabean": "Soybean",

    "chickpea": "Chickpea",
    "gram": "Chickpea",

    "pigeonpea": "Pigeonpea",
    "redgram": "Pigeonpea",
    "red gram": "Pigeonpea",

    "greengram": "Greengram",
    "green gram": "Greengram",

    "blackgram": "Blackgram",
    "black gram": "Blackgram",

    "mustard": "Mustard",
    "sesame": "Sesame",
    "castor": "Castor",

    "mango": "Mango",
    "banana": "Banana",
    "coconut": "Coconut",
    "arecanut": "Arecanut",
    "cashew": "Cashew",
    "pomegranate": "Pomegranate",
    "grape": "Grape",
    "papaya": "Papaya",
    "pineapple": "Pineapple",

    "tomato": "Tomato",
    "onion": "Onion",
    "potato": "Potato",
    "chilli": "Chilli",
    "chili": "Chilli",

    "turmeric": "Turmeric",
    "ginger": "Ginger",

    "black pepper": "Black Pepper",
    "cinnamon": "Cinnamon",
    "clove": "Clove",
    "nutmeg": "Nutmeg",

    "elephant foot yam": "Elephant Foot Yam",
}


# --------------------------------------------------
# 2. SECTION HEADINGS
# --------------------------------------------------

# These headings clear the previous crop.
# They are not themselves searchable advice.

SECTION_HEADINGS = {
    "cereal crops",
    "cereals crops",

    "millet crops",

    "oilseed crops",

    "pulse crops",
    "pulses",

    "commercial crops",

    "fibre crops",
    "fiber crops",

    "fruit crops",
    "vegetable crops",
    "vegetables crops",

    "fruit and vegetable crops",

    "spice crops",
    "plantation crops",
    "fodder crops",
    "horticultural crops",

    "livestock",
    "animal husbandry",
    "dairy",
    "poultry",
    "fisheries",
}


# --------------------------------------------------
# 3. STATE NAME RECOGNITION
# --------------------------------------------------

# Keys are normalized state headings.
# Values are the standard state names used in metadata.

STATE_HEADINGS = {
    "andaman and nicobar islands": "Andaman & Nicobar Islands",
    "andhra pradesh": "Andhra Pradesh",
    "arunachal pradesh": "Arunachal Pradesh",
    "assam": "Assam",
    "bihar": "Bihar",
    "chhattisgarh": "Chhattisgarh",
    "chhatisgarh": "Chhattisgarh",
    "goa": "Goa",
    "gujarat": "Gujarat",
    "haryana and delhi": "Haryana & Delhi",
    "himachal pradesh": "Himachal Pradesh",
    "jharkhand": "Jharkhand",
    "karnataka": "Karnataka",
    "kerala": "Kerala",
    "ladakh": "Ladakh",
    "jammu and kashmir": "Jammu & Kashmir",
    "madhya pradesh": "Madhya Pradesh",
    "maharashtra": "Maharashtra",
    "manipur": "Manipur",
    "meghalaya": "Meghalaya",
    "mizoram": "Mizoram",
    "nagaland": "Nagaland",
    "odisha": "Odisha",
    "orissa": "Odisha",
    "punjab": "Punjab",
    "rajasthan": "Rajasthan",
    "sikkim": "Sikkim",
    "tamil nadu and puducherry": "Tamil Nadu & Puducherry",
    "telangana": "Telangana",
    "tripura": "Tripura",
    "uttar pradesh": "Uttar Pradesh",
    "uttarakhand": "Uttarakhand",
    "west bengal": "West Bengal",

    "chandigarh": "Chandigarh",
    "dadra and nagar haveli and daman and diu":
        "Dadra and Nagar Haveli and Daman and Diu",
    "delhi": "Delhi",
    "puducherry": "Puducherry",
    "lakshadweep": "Lakshadweep",
}


# --------------------------------------------------
# 4. TEXT NORMALIZATION
# --------------------------------------------------

def normalize_heading(line):
    """
    Normalize a line before comparing it with
    known crop, section and state headings.
    """

    normalized = line.strip().lower()

    normalized = normalized.replace("&", "and")

    normalized = " ".join(normalized.split())

    return normalized.rstrip(":.")


# --------------------------------------------------
# 5. LOAD SOURCE PAGES
# --------------------------------------------------

def load_pages():
    """Load cleaned pages containing state metadata."""

    pages = []

    with INPUT_PATH.open("r", encoding="utf-8") as file:

        for line in file:

            if line.strip():
                pages.append(json.loads(line))

    return pages


# --------------------------------------------------
# 6. CLASSIFY HEADINGS
# --------------------------------------------------

def classify_heading(line):
    """
    Identify standalone crop, section or state headings.

    Returns:
        ("crop", crop_name)
        ("section", None)
        ("state", standard_state_name)
        (None, None)
    """

    normalized = normalize_heading(line)

    if normalized in CROP_HEADINGS:

        return "crop", CROP_HEADINGS[normalized]

    if normalized in SECTION_HEADINGS:

        return "section", None

    if normalized in STATE_HEADINGS:

        return "state", STATE_HEADINGS[normalized]

    return None, None


# --------------------------------------------------
# 7. CHUNK GENERATION
# --------------------------------------------------

def create_chunks(pages):
    """
    Split pages into meaningful chunks.

    State headings update state metadata.
    Crop headings update crop metadata.
    Section headings clear crop metadata.

    Recognized headings are excluded from chunk text.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
        add_start_index=True
    )

    chunks = []

    active_crop = None
    active_state = None

    for page in pages:

        text = page["text"]

        if not text.strip():
            continue

        page_state = page["state"]

        # Reset crop when the page metadata indicates
        # that we have entered another state.
        if active_state != page_state:

            active_state = page_state
            active_crop = None

        current_lines = []

        section_start = 0
        current_position = 0

        section_crop = active_crop
        section_state = active_state

        sections = []

        for line in text.splitlines(keepends=True):

            line_content = line.rstrip("\r\n")

            heading_type, heading_value = classify_heading(
                line_content
            )

            if heading_type is not None:

                # Save the content before this heading.
                section_text = "".join(current_lines)

                if section_text.strip():

                    sections.append((
                        section_text,
                        section_start,
                        section_state,
                        section_crop
                    ))

                # The heading is excluded from chunk text.
                current_lines = []

                section_start = current_position + len(line)

                if heading_type == "crop":

                    section_crop = heading_value

                elif heading_type == "section":

                    section_crop = None

                elif heading_type == "state":

                    # A repeated state header should NOT
                    # reset the crop metadata.

                    if heading_value != active_state:

                        active_state = heading_value
                        section_state = heading_value
                        section_crop = None

                    else:

                        # Same state repeated in PDF header.
                        # Preserve the existing crop.
                        section_state = active_state

                current_position += len(line)

                continue

            current_lines.append(line)

            current_position += len(line)

        # Save remaining content on the page.
        remaining_text = "".join(current_lines)

        if remaining_text.strip():

            sections.append((
                remaining_text,
                section_start,
                section_state,
                section_crop
            ))

        # Split each section independently.
        for section_text, section_offset, state, crop in sections:

            documents = splitter.create_documents(
                texts=[section_text],
                metadatas=[{
                    "source": page["source"],
                    "state": state,
                    "pdf_page": page["pdf_page"],
                    "printed_page": page.get("printed_page")
                }]
            )

            for document in documents:

                chunk_text = document.page_content.strip()

                if not chunk_text:
                    continue

                local_start = document.metadata["start_index"]

                chunk = {
                    "chunk_id": len(chunks),
                    "text": chunk_text,
                    "source": document.metadata["source"],
                    "state": document.metadata["state"],
                    "crop": crop,
                    "pdf_page": document.metadata["pdf_page"],
                    "printed_page": document.metadata["printed_page"],
                    "start_index": section_offset + local_start,
                    "character_count": len(chunk_text)
                }

                chunks.append(chunk)

        # Carry the final crop and state into the next page.
        active_crop = section_crop
        active_state = section_state

    return chunks


# --------------------------------------------------
# 8. SAVE CHUNKS
# --------------------------------------------------

def save_chunks(chunks):
    """Save generated chunks as JSON Lines."""

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:

        for chunk in chunks:

            file.write(
                json.dumps(chunk, ensure_ascii=False) + "\n"
            )


# --------------------------------------------------
# 9. SAVE CSV REPORT
# --------------------------------------------------

def save_report(chunks):
    """Save chunk metadata for inspection."""

    fieldnames = [
        "chunk_id",
        "state",
        "crop",
        "pdf_page",
        "character_count",
        "start_index"
    ]

    with REPORT_PATH.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for chunk in chunks:

            writer.writerow({
                "chunk_id": chunk["chunk_id"],
                "state": chunk["state"],
                "crop": chunk["crop"],
                "pdf_page": chunk["pdf_page"],
                "character_count": chunk["character_count"],
                "start_index": chunk["start_index"]
            })


# --------------------------------------------------
# 10. PRINT SUMMARY
# --------------------------------------------------

def print_summary(chunks, pages):

    state_counts = Counter(
        chunk["state"] for chunk in chunks
    )

    crop_counts = Counter(
        chunk["crop"] if chunk["crop"] else "Unclassified"
        for chunk in chunks
    )

    lengths = [
        chunk["character_count"] for chunk in chunks
    ]

    short_chunks = [
        chunk for chunk in chunks
        if chunk["character_count"] < 100
    ]

    print("\nCHUNKING SUMMARY")
    print("=" * 45)

    print(f"Input pages: {len(pages)}")
    print(f"Total chunks: {len(chunks)}")

    if lengths:

        print(
            f"Average chunk length: "
            f"{sum(lengths) / len(lengths):.2f}"
        )

        print(f"Shortest chunk: {min(lengths)}")
        print(f"Longest chunk: {max(lengths)}")

    print(f"Chunks below 100 characters: {len(short_chunks)}")

    print("\nChunks by state:")

    for state, count in sorted(state_counts.items()):

        print(f"{state}: {count}")

    print("\nChunks by crop:")

    for crop, count in sorted(crop_counts.items()):

        print(f"{crop}: {count}")

    print("\nFiles saved:")
    print(OUTPUT_PATH)
    print(REPORT_PATH)


# --------------------------------------------------
# 11. MAIN
# --------------------------------------------------

def main():

    start_time = time.time()

    print("Loading cleaned pages...")

    pages = load_pages()

    print(f"Pages loaded: {len(pages)}")

    print("Creating improved crop-aware chunks...")

    chunks = create_chunks(pages)

    if not chunks:

        raise RuntimeError(
            "No chunks were generated. Check the input dataset."
        )

    save_chunks(chunks)

    save_report(chunks)

    print_summary(chunks, pages)

    print(
        f"\nTime taken: {time.time() - start_time:.2f} seconds"
    )


if __name__ == "__main__":
    main()
