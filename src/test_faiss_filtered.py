
import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# 1. PATHS AND CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INDEX_PATH = PROJECT_ROOT / "indexes" / "faiss_index.bin"
METADATA_PATH = PROJECT_ROOT / "indexes" / "chunks_metadata.json"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

TOP_K = 5


# --------------------------------------------------
# 2. LOAD INDEX AND METADATA
# --------------------------------------------------

def load_index():

    print("Loading FAISS index and metadata...")

    index = faiss.read_index(str(INDEX_PATH))

    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    chunks = metadata["chunks"]

    if index.ntotal != len(chunks):
        raise ValueError("Index and metadata sizes do not match.")

    print(f"Total indexed chunks: {index.ntotal}")

    return index, metadata


# --------------------------------------------------
# 3. LOAD EMBEDDING MODEL
# --------------------------------------------------

def load_model():

    print("\nLoading embedding model...")

    return SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )


# --------------------------------------------------
# 4. FILTERED SEMANTIC SEARCH
# --------------------------------------------------

def search(query, required_state, required_crop, model, index, metadata):

    chunks = metadata["chunks"]

    print("\nGenerating query embedding...")

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype=np.float32
    )

    # Search all chunks, not just the global top five.
    print("\nSearching all FAISS vectors...")

    scores, indices = index.search(
        query_embedding,
        index.ntotal
    )

    # Apply metadata filters while preserving FAISS ranking.
    filtered_results = []

    for score, idx in zip(scores[0], indices[0]):

        if idx == -1:
            continue

        chunk = chunks[idx]

        state_matches = (
            chunk["state"].casefold() == required_state.casefold()
        )

        crop_matches = (
            (chunk["crop"] or "").casefold() == required_crop.casefold()
        )

        if state_matches and crop_matches:

            filtered_results.append(
                {
                    "score": float(score),
                    "chunk": chunk
                }
            )

    print("\n" + "=" * 80)
    print("FILTERED SEMANTIC SEARCH")
    print("=" * 80)

    print("Question:", query)
    print("Required state:", required_state)
    print("Required crop:", required_crop)
    print("Matching chunks:", len(filtered_results))

    if not filtered_results:
        print("\nNo matching chunks found.")
        return

    print(f"\nShowing top {min(TOP_K, len(filtered_results))} results.")

    for rank, result in enumerate(filtered_results[:TOP_K], start=1):

        chunk = result["chunk"]

        print("\n" + "-" * 80)
        print(f"RANK: {rank}")
        print(f"CHUNK ID: {chunk['chunk_id']}")
        print(f"STATE: {chunk['state']}")
        print(f"CROP: {chunk['crop']}")
        print(f"PDF PAGE: {chunk['pdf_page']}")
        print(f"COSINE SIMILARITY: {result['score']:.4f}")

        print("\nTEXT:")
        print(chunk["text"])


# --------------------------------------------------
# 5. MAIN
# --------------------------------------------------

def main():

    print("=" * 80)
    print("AGRICULTURAL RAG - METADATA FILTERED FAISS SEARCH")
    print("=" * 80)

    index, metadata = load_index()

    model = load_model()

    query = "How can I control weeds in paddy fields in Karnataka?"

    search(
        query=query,
        required_state="Karnataka",
        required_crop="Paddy",
        model=model,
        index=index,
        metadata=metadata
    )


if __name__ == "__main__":
    main()
