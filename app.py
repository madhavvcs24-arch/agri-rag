
import gradio as gr

from src.answer_generator import AgriculturalRAG


# --------------------------------------------------
# INITIALIZE RAG SYSTEM
# --------------------------------------------------

print("Starting Agricultural Advisory Chatbot...")

rag = AgriculturalRAG()


# --------------------------------------------------
# CHATBOT FUNCTION
# --------------------------------------------------

def respond(question, state, crop):

    if not question or not question.strip():
        return (
            "Please enter an agricultural question.",
            "",
            ""
        )

    try:

        result = rag.ask(
            question=question,
            state=state if state != "All States" else None,
            crop=crop if crop != "All Crops" else None,
            top_k=2
        )

        answer = result["answer"]

        refusal_message = (
            "The available ICAR document does not contain "
            "sufficient information to answer this question."
        )

        # Do not display irrelevant sources for refused answers.
        if answer.strip().startswith(refusal_message):

            return (
                refusal_message,
                "No supporting information was found in the "
                "available ICAR document.",
                ""
            )

        # Format source information.
        source_text = ""

        if result["sources"]:

            source_text = "### ICAR Sources\n\n"

            for source in result["sources"]:

                source_text += (
                    f'{source["citation"]} '
                    f'**{source["source"]}**\n\n'
                    f'- PDF page: {source["pdf_page"]}\n'
                    f'- State: {source["state"]}\n'
                    f'- Crop: {source["crop"]}\n\n'
                )

        else:

            source_text = "No supporting passages were verified."

        return answer, source_text, ""

    except Exception as error:

        print("ERROR:", error)

        return (
            "Something went wrong while processing your question. "
            "Please try again.",
            "",
            question
        )


# --------------------------------------------------
# GRADIO INTERFACE
# --------------------------------------------------

custom_css = """
.gradio-container {
    max-width: 1050px !important;
    margin: auto !important;
}

#main-title {
    text-align: center;
}

#answer-box {
    border-radius: 12px;
}
"""


with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="green",
        secondary_hue="lime"
    ),
    css=custom_css,
    title="AgriSaarthi - Agricultural Advisory"
) as demo:

    gr.Markdown(
        """
        # 🌾 AgriSaarthi

        ### Multilingual Voice-Enabled Agricultural Advisory Chatbot

        Ask agricultural questions and receive answers grounded
        in trusted ICAR documents using Retrieval-Augmented Generation (RAG).

        **Current knowledge base:** ICAR Kharif Agro-Advisories for Farmers 2025

        **Current prototype:** English text-based agricultural advisory.
        """,
        elem_id="main-title"
    )

    gr.Markdown("---")

    with gr.Row():

        state_input = gr.Dropdown(
            choices=[
                "All States",
                "Andhra Pradesh",
                "Arunachal Pradesh",
                "Assam",
                "Bihar",
                "Chhattisgarh",
                "Goa",
                "Gujarat",
                "Haryana & Delhi",
                "Himachal Pradesh",
                "Jammu & Kashmir",
                "Jharkhand",
                "Karnataka",
                "Kerala",
                "Ladakh",
                "Madhya Pradesh",
                "Maharashtra",
                "Manipur",
                "Meghalaya",
                "Mizoram",
                "Nagaland",
                "Odisha",
                "Punjab",
                "Rajasthan",
                "Sikkim",
                "Tamil Nadu & Puducherry",
                "Telangana",
                "Tripura",
                "Uttar Pradesh",
                "Uttarakhand",
                "West Bengal",
                "Andaman & Nicobar Islands"
            ],
            value="All States",
            label="Select State",
            info="Choose the state relevant to your question."
        )

        crop_input = gr.Dropdown(
            choices=[
                "All Crops",
                "Paddy",
                "Maize",
                "Cotton",
                "Sugarcane",
                "Soybean",
                "Groundnut",
                "Wheat",
                "Tomato",
                "Onion",
                "Potato",
                "Banana",
                "Mango",
                "Chilli",
                "Finger Millet",
                "Pearl Millet",
                "Pigeonpea",
                "Greengram",
                "Blackgram",
                "Coconut",
                "Arecanut",
                "Grape",
                "Pomegranate",
                "Turmeric",
                "Ginger"
            ],
            value="All Crops",
            label="Select Crop",
            info="Choose the crop relevant to your question."
        )

    question_input = gr.Textbox(
        label="Ask your agricultural question",
        placeholder=(
            "Example: How can I control weeds in "
            "paddy fields in Karnataka?"
        ),
        lines=3
    )

    submit_button = gr.Button(
        "Get Agricultural Advisory 🌱",
        variant="primary"
    )

    gr.Markdown("## Agricultural Advisory")

    answer_output = gr.Markdown(
        label="Answer",
        elem_id="answer-box"
    )

    sources_output = gr.Markdown(
        label="Sources"
    )

    submit_button.click(
        fn=respond,
        inputs=[
            question_input,
            state_input,
            crop_input
        ],
        outputs=[
            answer_output,
            sources_output,
            question_input
        ],
        show_progress="full"
    )

    gr.Markdown(
        """
        ---

        **Disclaimer:** Responses are generated from the
        ICAR Kharif Agro-Advisories for Farmers 2025 document.
        They may not reflect subsequent changes in agricultural
        recommendations. Verify advice with current local
        agricultural experts and follow current product labels
        before implementing pesticide or fertilizer recommendations.

        **Technology:** Python, Gradio, FAISS, BM25,
        Sentence Transformers, Cross-Encoder and Ollama.
        """
    )


# --------------------------------------------------
# LAUNCH APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        inbrowser=True
    )
