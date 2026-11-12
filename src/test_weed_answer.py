from src.answer_generator import AgriculturalRAG, display_result


def main():
    rag = AgriculturalRAG()

    question = "How can weeds be controlled in paddy fields in Karnataka?"

    result = rag.ask(
        question=question,
        state="Karnataka",
        crop="Paddy",
        top_k=1
    )

    display_result(result)


if __name__ == "__main__":
    main()