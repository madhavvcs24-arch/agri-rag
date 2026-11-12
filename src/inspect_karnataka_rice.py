
import json
import re
from pathlib import Path


CHUNKS_PATH = Path("data/processed/chunks.jsonl")


def main():

    chunks = []

    with CHUNKS_PATH.open("r", encoding="utf-8") as file:

        for line in file:

            if line.strip():
                chunks.append(json.loads(line))

    print(f"Total chunks: {len(chunks)}")

    karnataka_chunks = [
        chunk for chunk in chunks
        if chunk["state"].lower() == "karnataka"
    ]

    print(f"Karnataka chunks: {len(karnataka_chunks)}")

    pattern = re.compile(
        r"rice|paddy|variet|cultivar|sowing",
        re.IGNORECASE
    )

    print("\nKARNATAKA RICE-RELATED CHUNKS")
    print("=" * 70)

    matches = 0

    for chunk in karnataka_chunks:

        if pattern.search(chunk["text"]):

            matches += 1

            print("\n" + "-" * 70)
            print(f"Chunk ID: {chunk['chunk_id']}")
            print(f"PDF page: {chunk['pdf_page']}")
            print(f"Text:\n{chunk['text']}")

    print("\n" + "=" * 70)
    print(f"Total matching chunks: {matches}")


if __name__ == "__main__":
    main()
