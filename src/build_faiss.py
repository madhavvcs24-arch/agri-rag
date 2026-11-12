
import numpy as np
import faiss
import time

from pathlib import Path


EMBEDDINGS_PATH = Path("data/processed/embeddings_v2.npy")
INDEX_PATH = Path("data/processed/agri_faiss_v2.index")

DIMENSIONS = 384


def build_index():

    print("Loading embeddings...")

    embeddings = np.load(EMBEDDINGS_PATH)

    print(f"Embedding shape: {embeddings.shape}")

    # FAISS expects float32 vectors.
    # Make the array contiguous in memory.
    embeddings = np.ascontiguousarray(
        embeddings,
        dtype=np.float32
    )

    if embeddings.ndim != 2:
        raise ValueError("Embeddings must be a 2D array.")

    if embeddings.shape[1] != DIMENSIONS:
        raise ValueError("Unexpected embedding dimensions.")

    # Create exact inner-product index.
    index = faiss.IndexFlatIP(DIMENSIONS)

    print("\nAdding embeddings to FAISS...")

    index.add(embeddings)

    # Save the index.
    faiss.write_index(index, str(INDEX_PATH))

    print("\nFAISS INDEX SUMMARY")
    print("=" * 45)

    print(f"Total vectors indexed: {index.ntotal}")
    print(f"Vector dimensions: {index.d}")
    print(f"Index type: IndexFlatIP")
    print(f"Index saved at: {INDEX_PATH}")


def main():

    start_time = time.time()

    build_index()

    print(f"\nTime taken: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
