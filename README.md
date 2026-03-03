# DocuChat AI

DocuChat AI is a robust Multi-Document Retrieval-Augmented Generation (RAG) system designed to provide accurate, grounded answers from uploaded PDF documents. Leveraging Google's Gemini 1.5 Pro for reasoning and `text-embedding-004` for high-dimensional vector search, it ensures high-quality responses with mandatory source citations.

## 🚀 Features

- **Multi-PDF Ingestion:** Upload and query multiple documents simultaneously.
- **Session Isolation:** Documents are tied to a specific `session_id`, ensuring data privacy between users.
- **Smart Chunking:** Uses `RecursiveCharacterTextSplitter` with metadata tagging (filename, page number).
- **Grounded Reasoning:** Strict system prompts prevent hallucinations by forcing the model to answer only based on provided context.
- **Automatic Memory Management:** Uses `TTLCache` to automatically clear session data after 1 hour of inactivity, preventing memory leaks.
- **Concurrency Handling:** Built-in `SessionLockManager` to prevent race conditions during document processing.

## 🛠️ Tech Stack

- **LLM:** Google Gemini 1.5 Pro
- **Embeddings:** Google `text-embedding-004`
- **Backend:** Python 3.10+, FastAPI
- **Vector Store:** FAISS (In-memory with session-based TTL)
- **PDF Processing:** PyMuPDF (fitz)
- **Orchestration:** LangChain

## 📋 Prerequisites

- Python 3.10 or higher
- A Google Cloud Project with Vertex AI enabled or a Google AI Studio API Key.

## ⚙️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/docuchat-ai.git
   cd docuchat-ai
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```

4. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```

## 🏗️ Architecture

1. **Ingestion Pipeline:**
   - PDF is uploaded via `/upload`.
   - `PyMuPDF` extracts text per page.
   - `RecursiveCharacterTextSplitter` breaks text into 1000-token chunks.
   - `text-embedding-004` generates vectors.
   - Vectors are stored in a session-specific FAISS index.

2. **RAG Query Pipeline:**
   - User sends a query via `/chat`.
   - The system performs a similarity search in the session's FAISS index.
   - Top-k relevant chunks are retrieved.
   - Gemini 1.5 Pro generates a response using the chunks as context, citing sources in `[Filename - Page X]` format.

## 🛡️ Safety & Reliability

- **Safety Filters:** The system validates Gemini response candidates to handle blocked content gracefully.
- **Race Condition Prevention:** Async locks ensure that multiple uploads to the same session are processed sequentially.
- **Memory Safety:** Session data is automatically evicted after 1 hour of inactivity.
