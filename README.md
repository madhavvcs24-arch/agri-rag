# AgriSaarthi – Agricultural Advisory Chatbot using RAG

## 1. Project Overview

AgriSaarthi is a Retrieval-Augmented Generation (RAG) based agricultural advisory chatbot designed to provide farmers with information from trusted agricultural documents.

The project uses the **ICAR Kharif Agro-Advisories for Farmers 2025** as its initial knowledge source.

Instead of relying entirely on a language model's pre-trained knowledge, the chatbot retrieves relevant information from the ICAR document and uses that information to generate an answer.

The chatbot also provides source-document citations, including PDF page number, state, and crop information.

**Current implementation:** English text-based RAG prototype.

**Proposed full system:** Multilingual voice-enabled agricultural advisory chatbot supporting Indian languages.

---

## 2. Problem Statement

Farmers often need access to reliable agricultural information regarding crop cultivation, irrigation, pest management, weed control, and other farming practices.

Agricultural information may be spread across lengthy documents, making it difficult to locate relevant recommendations quickly.

AgriSaarthi aims to simplify access to this information by allowing users to ask natural-language questions and receive answers grounded in trusted agricultural documents.

---

## 3. Current Features

- Processes agricultural PDF documents.
- Extracts and cleans text from PDF pages.
- Identifies agricultural information using state and crop metadata.
- Divides document content into crop-aware text chunks.
- Generates semantic embeddings using Sentence Transformers.
- Performs vector similarity search using FAISS.
- Performs keyword-based retrieval using BM25.
- Combines retrieval results using Reciprocal Rank Fusion (RRF).
- Uses a Cross-Encoder to rerank retrieved passages.
- Generates answers using a locally running Qwen model through Ollama.
- Provides citations containing the source document, PDF page, state, and crop.
- Refuses to answer when the available document does not contain sufficient supporting information.
- Provides a Gradio web interface.

---

## 4. Knowledge Base

The initial knowledge source is:

**ICAR Kharif Agro-Advisories for Farmers 2025**

Document processing statistics:

| Processing stage | Result |
|---|---:|
| Total PDF pages | 310 |
| Pages with extracted text | 302 |
| Pages flagged without extractable text | 8 |
| Crop-aware chunks generated | 1,360 |

The extracted content is cleaned and enriched with metadata before being divided into chunks.

The metadata includes information such as:
- State
- Crop
- Source document
- PDF page number

The chatbot uses this metadata to retrieve relevant agricultural information.

---

## 5. System Architecture

The current system follows this pipeline:

1. **PDF Ingestion:** Extracts text from the ICAR PDF using PyMuPDF.
2. **Text Cleaning:** Removes repeated headers and corrects extraction-related text issues.
3. **Metadata Extraction:** Associates agricultural content with relevant states and crops.
4. **Chunking:** Divides the document into smaller crop-aware passages.
5. **Embedding Generation:** Converts text passages into numerical vectors using `sentence-transformers/all-MiniLM-L6-v2`.
6. **Vector Indexing:** Stores normalized embeddings in a FAISS index.
7. **Hybrid Retrieval:** Combines FAISS semantic retrieval and BM25 keyword retrieval.
8. **Result Fusion:** Uses Reciprocal Rank Fusion to combine retrieval results.
9. **Reranking:** Uses a Cross-Encoder to rank candidate passages by relevance.
10. **Answer Generation:** Sends retrieved passages and the question to a local Qwen model through Ollama.
11. **Citation Verification:** Applies a preliminary lexical evidence-matching check to associate generated sentences with retrieved passages.
12. **Response:** Displays the answer and its source information through Gradio.

---

## 6. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| PyMuPDF | PDF text extraction |
| FAISS | Vector similarity search |
| Sentence Transformers | Text embeddings |
| BM25 | Keyword-based retrieval |
| Reciprocal Rank Fusion | Combining retrieval results |
| Cross-Encoder | Reranking retrieved passages |
| Ollama | Running the local language model |
| Qwen 2.5 3B Instruct | Answer generation |
| Gradio | Web application interface |
| NumPy | Numerical operations |

---

## 7. Project Structure

```text
agri-rag/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── sources.csv
│
├── data/
│   ├── raw/
│   │   └── icar_kharif_2025_english.pdf
│   │
│   └── processed/
│       ├── pages_raw.jsonl
│       ├── pages.jsonl
│       ├── pages_with_state_v2.jsonl
│       └── chunks_v2.jsonl
│
├── indexes/
│   ├── faiss_index.bin
│   └── chunks_metadata.json
│
├── src/
│   ├── ingest.py
│   ├── ingest_v2.py
│   ├── clean.py
│   ├── clean_v2.py
│   ├── chunk.py
│   ├── build_index.py
│   ├── build_faiss.py
│   ├── build_bm25.py
│   ├── retriever.py
│   ├── hybrid_search.py
│   ├── answer_generator.py
│   └── test_*.py
│
└── eval/
```

*The structure above highlights the main project components. Additional inspection, validation, and diagnostic scripts are also present in `src/`.*

---

## 8. Requirements

- Python 3.12
- Ollama
- Qwen 2.5 3B Instruct model
- Required Python packages listed in `requirements.txt`

The current implementation runs the language model locally and does not require a paid LLM API.

---

## 9. Installation and Setup

### Step 1: Clone the repository

```bash
git clone https://github.com/madhavvcs24-arch/agri-rag.git
cd agri-rag
```

### Step 2: Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Install and configure Ollama

Install Ollama on your system.

Pull the required model:

```bash
ollama pull qwen2.5:3b-instruct
```

Make sure Ollama is running before starting the application.

### Step 5: Prepare the knowledge base

Place the ICAR Kharif Agro-Advisories for Farmers 2025 English PDF at:

```text
data/raw/icar_kharif_2025_english.pdf
```

The application also requires the generated processed data and FAISS index files to be available in their respective project directories.

### Step 6: Run the application

```bash
python app.py
```

Open the local Gradio application at:

```text
http://127.0.0.1:7860
```

---

## 10. Example Questions

The current prototype has been tested with questions such as:

**Irrigation**

"What are the critical growth stages when paddy needs irrigation in Karnataka?"

**Weed Management**

"How can weeds be controlled in paddy fields in Karnataka?"

**Seed Rate**

"What is the recommended seed rate for paddy in Karnataka?"

**Unsupported Question**

"What is the current market price of paddy in Karnataka?"

For questions not supported by the available document, the chatbot is designed to return:

> The available ICAR document does not contain sufficient information to answer this question.

---

## 11. Current Limitations

- The current knowledge base contains one ICAR English PDF.
- The current user interface supports English text questions and answers.
- Hindi, Kannada, Punjabi, and other language support is not yet implemented.
- Voice input and voice output are not yet implemented.
- The knowledge base does not provide live market prices or real-time agricultural information.
- The citation verification mechanism uses lexical overlap and is a preliminary evidence-matching safeguard, not a complete semantic fact-checker.
- Agricultural recommendations are based on the 2025 document and may not reflect later changes.

Users should verify recommendations with current local agricultural experts and follow current product labels before implementing pesticide or fertilizer advice.

---

## 12. Future Scope

- Multilingual question translation and answer generation.
- Support for Hindi, Kannada, Punjabi, and English.
- Speech-to-text for voice-based farmer queries.
- Text-to-speech for spoken agricultural responses.
- Integration of additional trusted ICAR documents.
- Expansion of the agricultural knowledge base.
- Improved semantic verification of generated answers.
- Evaluation using a larger agricultural question-answer dataset.

---

## 13. Project Objective

The long-term objective of AgriSaarthi is to make trusted agricultural information more accessible to Indian farmers through a multilingual, voice-enabled, document-grounded conversational system.

The current English RAG prototype establishes the document-processing, retrieval, answer-generation, and citation foundation for that larger system.

---

**Project:** Multilingual Voice-Enabled Agricultural Advisory Chatbot for Indian Farmers using Retrieval-Augmented Generation (RAG)

**Initial Knowledge Source:** ICAR Kharif Agro-Advisories for Farmers 2025
