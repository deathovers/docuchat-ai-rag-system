# DocuChat AI

DocuChat AI is a Multi-Document RAG (Retrieval-Augmented Generation) Assistant that allows users to upload multiple PDF documents and have a conversational interaction with their content. The system ensures strict grounding, meaning it only answers based on the provided documents and provides precise citations (Filename and Page Number).

## 🚀 Features

- **Multi-PDF Ingestion**: Upload and process multiple PDF files simultaneously.
- **Session Isolation**: Your documents and chats are isolated using unique session IDs.
- **Strict Grounding**: The AI is instructed to only use the provided context to prevent hallucinations.
- **Verifiable Citations**: Every claim made by the AI includes a reference to the source document and page number.
- **Real-time Chat**: Responsive React-based interface with Markdown support.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.9+)
- **Frontend**: React, Tailwind CSS, TypeScript
- **LLM & Embeddings**: Google Gemini 1.5 (Flash/Pro)
- **Vector Database**: FAISS (Local persistence per session)
- **PDF Processing**: PyMuPDF (fitz)

## 📋 Prerequisites

- Python 3.9 or higher
- Node.js 18+ and npm
- Google AI Studio API Key (for Gemini)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/docuchat-ai.git
cd docuchat-ai
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

Run the server:
```bash
uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

Run the development server:
```bash
npm run dev
```

## 🏗️ Architecture

1.  **Ingestion Layer**: PDFs are parsed using PyMuPDF. Text is extracted page-by-page to preserve metadata.
2.  **Vector Store**: Text chunks are converted into embeddings using Gemini and stored in a session-specific FAISS index.
3.  **Retrieval**: When a user asks a question, the system performs a similarity search against the session's FAISS index.
4.  **Generation**: The retrieved context and the user's query are sent to Gemini with a strict system prompt to generate a grounded response.

## ⚠️ Limitations
- **No OCR**: Scanned images or PDFs without a text layer cannot be read.
- **PDF Only**: Currently only supports `.pdf` files.
- **Stateless MVP**: Vector indices are stored locally; clearing the `storage/` directory or changing session IDs will reset the context.
