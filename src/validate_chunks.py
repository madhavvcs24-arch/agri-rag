
import json
from pathlib import Path
from collections import Counter

CHUNKS_PATH = Path("data/processed/chunks.jsonl")

REQUIRED_FIELDS = [
    "chunk_id",
    "text",
    "source",
    "state",
    "pdf_page",
    "printed_page",
    "start_index",
    "character_count"
]


def validate_chunks():

    chunks = []

    with CHUNKS_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))

    errors = []

    # 1. Check total chunks
    print(f"Total chunks loaded: {len(chunks)}")

    # 2. Check required metadata
    for index, chunk in enumerate(chunks):

        for field in REQUIRED_FIELDS:
            if field not in chunk:
                errors.append(
                    f"Chunk {index}: missing field {field}"
                )

    # 3. Check chunk IDs
    ids = [chunk["chunk_id"] for chunk in chunks]

    if ids != list(range(len(chunks))):
        errors.append("Chunk IDs are not sequential.")

    # 4. Check character counts
    for chunk in chunks:

        actual_length = len(chunk["text"])

        if actual_length != chunk["character_count"]:
            errors.append(
                f"Chunk {chunk['chunk_id']}: incorrect character count."
            )

        if actual_length > 800:
            errors.append(
                f"Chunk {chunk['chunk_id']}: exceeds 800 characters."
            )

        if actual_length == 0:
            errors.append(
                f"Chunk {chunk['chunk_id']}: empty text."
            )

    # 5. Check metadata
    for chunk in chunks:

        if not chunk["state"]:
            errors.append(
                f"Chunk {chunk['chunk_id']}: missing state."
            )

        if chunk["pdf_page"] is None:
            errors.append(
                f"Chunk {chunk['chunk_id']}: missing PDF page."
            )

    # 6. Count chunks per state
    state_counts = Counter(
        chunk["state"] for chunk in chunks
    )

    print("\nChunks per state:")
    for state, count in sorted(state_counts.items()):
        print(f"{state}: {count}")

    # 7. Display one example
    print("\nSAMPLE CHUNK")
    print("=" * 60)

    sample = chunks[0]

    for field, value in sample.items():
        print(f"{field}: {value}")

    # 8. Final result
    print("\nVALIDATION RESULT")
    print("=" * 60)

    if errors:
        print(f"Validation failed: {len(errors)} errors")

        for error in errors[:20]:
            print(error)

    else:
        print("All validation checks passed!")


if __name__ == "__main__":
    validate_chunks()
