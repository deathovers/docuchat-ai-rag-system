# DocuChat AI API Documentation

The DocuChat AI API provides endpoints for managing PDF documents and querying them using a RAG-based chat system.

## Base URL
`http://localhost:8000/v1`

---

## Endpoints

### 1. Upload Documents
Upload one or more PDF files to the current session.

- **URL:** `/upload`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Payload:**
  - `files`: List of PDF files (Max 10).
- **Success Response:**
  - **Code:** 200 OK
  - **Content:**
    ```json
    {
      "status": "success",
      "processed_files": [
        {
          "id": "uuid-string",
          "filename": "report.pdf",
          "total_pages": 15
        }
      ]
    }
    ```

### 2. Chat / Query
Ask a question based on the uploaded documents.

- **URL:** `/chat`
- **Method:** `POST`
- **Content-Type:** `application/json`
- **Payload:**
    ```json
    {
      "message": "What is the termination clause in the contract?",
      "session_id": "user-session-id"
    }
    ```
- **Success Response:**
  - **Code:** 200 OK
  - **Content:**
    ```json
    {
      "answer": "The termination clause states that either party may terminate the agreement with 30 days written notice.",
      "sources": [
        {
          "file_name": "contract_v2.pdf",
          "page": 12
        }
      ]
    }
    ```
- **Error Response:**
  - **Code:** 404 Not Found (If no documents are uploaded)
  - **Code:** 200 OK (If answer not found in context)
    ```json
    {
      "answer": "The answer was not found in the uploaded documents.",
      "sources": []
    }
    ```

### 3. Delete Document
Remove a specific document from the session index.

- **URL:** `/documents/{file_id}`
- **Method:** `DELETE`
- **Success Response:**
  - **Code:** 200 OK
  - **Content:** `{"message": "Document deleted successfully"}`

---

## Data Models

### RAGResponse (Internal Schema)
The system uses Pydantic to enforce structured outputs from the LLM.
- `answer`: (string) The generated response.
- `used_chunk_ids`: (list[int]) IDs of the context blocks used for the answer.
