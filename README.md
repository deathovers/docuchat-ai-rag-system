# DocuChat AI

DocuChat AI is a high-performance Retrieval-Augmented Generation (RAG) application that allows users to upload multiple PDF documents and interact with them through a conversational interface. The system is designed for accuracy, providing context-grounded answers with precise page-level citations.

## 🚀 Features

- **Multi-Document Support:** Upload up to 10 PDFs per session.
- **Context-Grounded RAG:** Answers are strictly derived from the uploaded content to prevent hallucinations.
- **Page-Level Citations:** Every response includes the specific file name and page number used to generate the answer.
- **High-Performance Retrieval:** Utilizes **FAISS** (Facebook AI Similarity Search) for lightning-fast document indexing and search.
- **Robust Processing:** Implements document-level truncation and structured LLM outputs for reliable performance.
- **Session-Based Privacy:** All data is stored in-memory and cleared upon session termination.

## 🛠️ Tech Stack

- **Backend:** Python 3.9+, FastAPI
- **Orchestration:** LangChain
- **LLM:** OpenAI GPT-4o
- **Embeddings:** OpenAI `text-embedding-3-small`
- **Vector Database:** FAISS
- **PDF Parsing:** PyMuPDF (fitz) / PDFPlumber
- **Token Management:** Tiktoken

## 🏗️ Architecture

The system follows a standard RAG pipeline with enhanced reliability features:

1.  **Ingestion:** PDFs are uploaded via a FastAPI endpoint.
2.  **Extraction & Chunking:** Text is extracted with page metadata and split into chunks (500-1000 tokens) using recursive character splitting with 10% overlap.
3.  **Vectorization:** Chunks are converted into embeddings and stored in a session-specific FAISS index.
4.  **Retrieval:** User queries are embedded and used to find the top-k relevant chunks (relevance threshold: 0.5).
5.  **Context Construction:** Chunks are assembled into a prompt, ensuring no "destructive truncation" occurs by calculating tokens at the document level.
6.  **Structured Generation:** The LLM uses OpenAI Structured Outputs to return a JSON response containing the answer and the IDs of the chunks used.
7.  **Source Mapping:** The system maps chunk IDs back to metadata to provide citations.

## 💻 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/docuchat-ai.git
    cd docuchat-ai
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    Create a `.env` file in the root directory:
    ```env
    OPENAI_API_KEY=your_openai_api_key_here
    ```

## 🏃 Usage

1.  **Start the server:**
    ```bash
    uvicorn app.main:app --reload
    ```

2.  **Access the API:**
    The API will be available at `http://127.0.0.1:8000`.
    You can view the interactive Swagger documentation at `http://127.0.0.1:8000/docs`.

## 🛡️ Limitations

- **No OCR:** Only selectable text PDFs are supported.
- **Volatile Storage:** FAISS indices and chat history are cleared when the session ends.
- **Token Limit:** Context is capped at 4,000 tokens to manage LLM costs and performance.
