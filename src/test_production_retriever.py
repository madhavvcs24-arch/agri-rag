
from retriever import AgriculturalRetriever


def display_results(question, results, expected_chunk_id):

    print("\n" + "=" * 100)
    print(f"QUESTION: {question}")
    print("=" * 100)

    if not results:
        print("No relevant chunks found.")
        return

    found_expected = False

    for rank, result in enumerate(results, start=1):

        print(f"\nRANK: {rank}")
        print(f"CHUNK ID: {result['chunk_id']}")
        print(f"STATE: {result['state']}")
        print(f"CROP: {result['crop']}")
        print(f"PDF PAGE: {result['pdf_page']}")
        print(f"RERANKER SCORE: {result['reranker_score']:.4f}")

        print("\nTEXT:")
        print(result["text"])

        print("-" * 100)

        if result["chunk_id"] == expected_chunk_id:
            found_expected = True
            expected_rank = rank

    actual_top_chunk = results[0]["chunk_id"]

    print("\nEXPECTED CHUNK:", expected_chunk_id)
    print("ACTUAL TOP CHUNK:", actual_top_chunk)

    if actual_top_chunk == expected_chunk_id:
        print("TEST PASSED: Expected chunk ranked first!")

    elif found_expected:
        print(
            f"EXPECTED CHUNK FOUND AT RANK {expected_rank}, "
            "BUT DID NOT RANK FIRST."
        )

    else:
        print("EXPECTED CHUNK NOT FOUND IN TOP RESULTS.")


def main():

    print("=" * 100)
    print("AGRICULTURAL RAG - PRODUCTION RETRIEVER TEST")
    print("=" * 100)

    retriever = AgriculturalRetriever()

    # TEST 1: Weed management

    question_1 = (
        "How can I control weeds in paddy fields in Karnataka?"
    )

    results_1 = retriever.search(
        query=question_1,
        state="Karnataka",
        crop="Paddy",
        top_k=5
    )

    display_results(
        question_1,
        results_1,
        expected_chunk_id=496
    )

    # TEST 2: Seed rate

    question_2 = (
        "What seed rate is recommended for paddy cultivation in Karnataka?"
    )

    results_2 = retriever.search(
        query=question_2,
        state="Karnataka",
        crop="Paddy",
        top_k=5
    )

    display_results(
        question_2,
        results_2,
        expected_chunk_id=495
    )

    # TEST 3: Irrigation

    question_3 = (
        "What irrigation practices are recommended for paddy in Karnataka?"
    )

    results_3 = retriever.search(
        query=question_3,
        state="Karnataka",
        crop="Paddy",
        top_k=5
    )

    display_results(
        question_3,
        results_3,
        expected_chunk_id=497
    )


if __name__ == "__main__":
    main()
