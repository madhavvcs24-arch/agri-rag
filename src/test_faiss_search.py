
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
# 2. LOAD THE SAVED INDEX AND METADATA
# --------------------------------------------------

def load_index():

    print("Loading FAISS index...")

    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"Index not found: {INDEX_PATH}")

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Metadata not found: {METADATA_PATH}"
        )

    index = faiss.read_index(str(INDEX_PATH))

    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    chunks = metadata["chunks"]

    if index.ntotal != len(chunks):
        raise ValueError(
            "FAISS index and metadata have different sizes."
        )

    print(f"Vectors loaded: {index.ntotal}")
    print(f"Metadata chunks loaded: {len(chunks)}")

    return index, metadata


# --------------------------------------------------
# 3. LOAD THE EMBEDDING MODEL
# --------------------------------------------------

def load_model():

    print("\nLoading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )

    return model


# --------------------------------------------------
# 4. SEARCH THE INDEX
# --------------------------------------------------

def search(query, model, index, metadata):

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

    print("Searching FAISS...")

    top_k = min(TOP_K, index.ntotal)

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    chunks = metadata["chunks"]

    print("\n" + "=" * 80)
    print("SEARCH QUERY:", query)
    print("=" * 80)

    for rank, (score, idx) in enumerate(
        zip(scores[0], indices[0]),
        start=1
    ):

        if idx == -1:
            continue

        chunk = chunks[idx]

        print(f"\nRANK: {rank}")
        print(f"FAISS POSITION: {idx}")
        print(f"CHUNK ID: {chunk['chunk_id']}")
        print(f"STATE: {chunk['state']}")
        print(f"CROP: {chunk['crop']}")
        print(f"PDF PAGE: {chunk['pdf_page']}")
        print(f"COSINE SIMILARITY SCORE: {score:.4f}")

        print("\nCHUNK TEXT:")
        print(chunk["text"])

        print("\n" + "-" * 80)


# --------------------------------------------------
# 5. MAIN
# --------------------------------------------------

def main():

    print("=" * 80)
    print("AGRICULTURAL RAG - FAISS SEMANTIC SEARCH TEST")
    print("=" * 80)

    index, metadata = load_index()

    model = load_model()

    query = (
        "How can I control weeds in paddy fields "
        "in Karnataka?"
    )

    search(
        query,
        model,
        index,
        metadata
    )


if __name__ == "__main__":
    main()
