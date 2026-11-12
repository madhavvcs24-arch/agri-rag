from answer_generator import AgriculturalRAG, display_result


def main():

    rag = AgriculturalRAG()

    question = "What is the current market price of tomatoes in Bengaluru today?"

    result = rag.ask(
        question=question,
        state="Karnataka",
        crop="Tomato",
        top_k=5
    )

    display_result(result)


if __name__ == "__main__":
    main()