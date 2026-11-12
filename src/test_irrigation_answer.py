from src.answer_generator import AgriculturalRAG, display_result


def main():

    rag = AgriculturalRAG()

    question = (
        "What are the critical growth stages "
        "when paddy needs irrigation in Karnataka?"
    )

    result = rag.ask(
        question=question,
        state="Karnataka",
        crop="Paddy",
        top_k=2
    )

    display_result(result)


if __name__ == "__main__":
    main()