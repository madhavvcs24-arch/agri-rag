
import re

from ollama import chat

from src.retriever import AgriculturalRetriever


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

MODEL = "qwen2.5:3b-instruct"

TEMPERATURE = 0.1
MAX_RESPONSE_TOKENS = 350

REFUSAL_MESSAGE = (
    "The available ICAR document does not contain "
    "sufficient information to answer this question."
)

# Words that are usually not useful for checking
# whether a sentence is supported by a passage.
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were",
    "be", "been", "being", "and", "or", "but",
    "to", "of", "in", "on", "at", "by", "for",
    "from", "with", "as", "it", "its", "this",
    "that", "these", "those", "can", "could",
    "should", "would", "may", "might", "will",
    "while", "during", "such", "like", "also",
    "other", "others", "their", "they", "them",
    "you", "your", "we", "our", "if", "when",
    "which", "who", "what", "how", "where",
    "do", "does", "did", "not", "no", "yes",
    "than", "then", "into", "through", "after",
    "before", "per"
}

# A sentence must have enough matching content words
# before Python attaches a citation.
MIN_MATCHED_WORDS = 3
MIN_EVIDENCE_COVERAGE = 0.30


# --------------------------------------------------
# RAG ANSWER GENERATOR
# --------------------------------------------------

class AgriculturalRAG:

    def __init__(self):

        print("Initializing Agricultural RAG system...")

        self.retriever = AgriculturalRetriever()

        print("\nAgricultural RAG system is ready!")

    # --------------------------------------------------
    # BUILD CONTEXT
    # --------------------------------------------------

    def build_context(self, retrieved_chunks):

        context_parts = []

        for index, chunk in enumerate(retrieved_chunks, start=1):

            passage = (
                f"Passage {index}\n"
                f"Source: {chunk.get('source', 'Unknown source')}\n"
                f"PDF page: {chunk.get('pdf_page', 'Unknown')}\n"
                f"State: {chunk.get('state', 'Unknown')}\n"
                f"Crop: {chunk.get('crop', 'Unclassified')}\n"
                f"Information:\n{chunk.get('text', '')}\n"
            )

            context_parts.append(passage)

        return "\n".join(context_parts)

    # --------------------------------------------------
    # GENERATE ANSWER WITHOUT CITATIONS
    # --------------------------------------------------

    def generate_answer(self, question, context):

        system_prompt = """
You are an agricultural information assistant.

Answer the farmer's question using ONLY the supplied
retrieved ICAR passages.

STRICT RULES:

1. Use only information explicitly supported by the passages.

2. Never add agricultural facts, recommendations,
   quantities, pesticide names, fertilizer doses,
   or application methods from general knowledge.

3. If the passages do not contain sufficient information,
   respond exactly:

   "The available ICAR document does not contain
   sufficient information to answer this question."

4. Do NOT generate citation numbers.
   Python will assign citations separately.

5. Do not combine information from different states or crops.

6. Keep the answer simple and concise.

7. Write factual claims as short, separate sentences.
   Avoid combining unrelated recommendations into one sentence.

8. Do not invent source names, page numbers, or facts.

9. Do not add unrelated introductions or conclusions.

10. Do not present recommendations as independently verified
    or guarantee that they will work.

Return only the answer.
"""

        response = chat(
            model=MODEL,

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": (
                        f"QUESTION:\n{question}\n\n"
                        f"RETRIEVED ICAR CONTEXT:\n{context}\n\n"
                        "Answer only from the supplied passages. "
                        "Do not include citation numbers."
                    )
                }
            ],

            options={
                "temperature": TEMPERATURE,
                "num_predict": MAX_RESPONSE_TOKENS
            }
        )

        return response.message.content.strip()

    # --------------------------------------------------
    # TOKENIZE TEXT FOR EVIDENCE MATCHING
    # --------------------------------------------------

    @staticmethod
    def content_tokens(text):

        tokens = re.findall(
            r"[a-zA-Z0-9]+",
            text.lower()
        )

        return {
            token
            for token in tokens
            if token not in STOP_WORDS
        }

    # --------------------------------------------------
    # CHECK SENTENCE AGAINST RETRIEVED PASSAGES
    # --------------------------------------------------

    def find_supporting_passage(self, sentence, retrieved_chunks):

        sentence_tokens = self.content_tokens(sentence)

        if not sentence_tokens:
            return None

        best_position = None
        best_coverage = 0.0
        best_matches = 0

        for position, chunk in enumerate(retrieved_chunks):

            passage_tokens = self.content_tokens(
                chunk.get("text", "")
            )

            matched_tokens = sentence_tokens.intersection(
                passage_tokens
            )

            matched_count = len(matched_tokens)

            coverage = (
                matched_count / len(sentence_tokens)
            )

            if coverage > best_coverage:
                best_coverage = coverage
                best_matches = matched_count
                best_position = position

        if best_position is None:
            return None

        if best_matches < MIN_MATCHED_WORDS:
            return None

        if best_coverage < MIN_EVIDENCE_COVERAGE:
            return None

        return best_position

    # --------------------------------------------------
    # ASSIGN CITATIONS USING PYTHON
    # --------------------------------------------------

    def add_verified_citations(self, answer, retrieved_chunks):

        # Split the generated answer into sentences.
        # The prompt asks Qwen to keep factual claims separate.
        sentences = re.split(
            r"(?<=[.!?])\s+(?=[A-Z0-9])",
            answer.strip()
        )

        cited_sentences = []
        cited_positions = set()

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            # Remove any citation numbers Qwen may have
            # generated despite being instructed not to.
            sentence = re.sub(
                r"\s*\[\d+\]",
                "",
                sentence
            ).strip()

            supporting_position = self.find_supporting_passage(
                sentence,
                retrieved_chunks
            )

            # Do not display a factual sentence when
            # the retrieved text does not sufficiently match it.
            if supporting_position is None:

                print(
                    "\nEvidence check failed for sentence:"
                )
                print(sentence)

                return REFUSAL_MESSAGE, []

            citation_number = supporting_position + 1

            cited_sentences.append(
                f"{sentence} [{citation_number}]"
            )

            cited_positions.add(supporting_position)

        if not cited_sentences:
            return REFUSAL_MESSAGE, []

        final_answer = "\n\n".join(cited_sentences)

        return final_answer, sorted(cited_positions)

    # --------------------------------------------------
    # MAIN ASK METHOD
    # --------------------------------------------------

    def ask(self, question, state=None, crop=None, top_k=5):

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        print("\nSearching the ICAR knowledge base...")

        retrieved_chunks = self.retriever.search(
            query=question,
            state=state,
            crop=crop,
            top_k=top_k
        )

        if not retrieved_chunks:

            return {
                "answer": REFUSAL_MESSAGE,
                "sources": [],
                "retrieved_chunks": []
            }

        print(f"Retrieved {len(retrieved_chunks)} passages.")

        context = self.build_context(retrieved_chunks)

        print("\nGenerating answer using local Qwen model...")

        generated_answer = self.generate_answer(
            question=question,
            context=context
        )

        # Preserve the model's explicit refusal.
        if REFUSAL_MESSAGE in generated_answer:

            return {
                "answer": REFUSAL_MESSAGE,
                "sources": [],
                "retrieved_chunks": retrieved_chunks
            }

        print("\nChecking answer against retrieved ICAR passages...")

        final_answer, cited_positions = self.add_verified_citations(
            generated_answer,
            retrieved_chunks
        )

        sources = []

        for position in cited_positions:

            chunk = retrieved_chunks[position]

            sources.append({
                "citation": f"[{position + 1}]",
                "source": chunk.get("source", "Unknown source"),
                "pdf_page": chunk.get("pdf_page", "Unknown"),
                "state": chunk.get("state", "Unknown"),
                "crop": chunk.get("crop", "Unclassified")
            })

        return {
            "answer": final_answer,
            "sources": sources,
            "retrieved_chunks": retrieved_chunks
        }


# --------------------------------------------------
# DISPLAY HELPER
# --------------------------------------------------

def display_result(result):

    print("\n" + "=" * 80)
    print("AGRICULTURAL ADVISORY")
    print("=" * 80)

    print("\nANSWER:\n")
    print(result["answer"])

    print("\n" + "-" * 80)
    print("SOURCE DOCUMENTS")
    print("-" * 80)

    if not result["sources"]:

        print("No supporting passages were verified.")

    else:

        for source in result["sources"]:

            print(
                f'{source["citation"]} '
                f'{source["source"]} | '
                f'PDF page: {source["pdf_page"]} | '
                f'State: {source["state"]} | '
                f'Crop: {source["crop"]}'
            )

    print("\n" + "=" * 80)
