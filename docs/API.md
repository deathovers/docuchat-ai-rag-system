# API Documentation - DocuChat AI

The DocuChat AI API provides endpoints for document management and conversational AI retrieval.

## Base URL
`http://localhost:8000`

---

## 1. Document Management

### Upload Document
Uploads a PDF file and indexes it for the current session.

- **Endpoint:** `POST /upload`
- **Content-Type:** `multipart/form-data`
- **Payload:**
    - `file`: Binary (PDF)
    - `session_id`: String (UUID recommended)
- **Success Response:**
    - **Code:** 200
    - **Content:** `{ "status": "success", "file_name": "contract.pdf" }`

### List Files
Returns a list of all files uploaded for a specific session.

- **Endpoint:** `GET /files/{session_id}`
- **Success Response:**
    - **Code:** 200
    - **Content:** `[{ "file_name": "contract.pdf", "upload_time": "..." }]`

### Delete File
Removes a specific document from the vector store and session.

- **Endpoint:** `DELETE /files/{file_id}`
- **Success Response:**
    - **Code:** 200
    - **Content:** `{ "message": "File deleted successfully" }`

---

## 2. Chat Interface

### Query Documents
Ask questions based on the uploaded documents in the session.

- **Endpoint:** `POST /chat`
- **Payload:**
  ```json
  {
    "session_id": "uuid-v4-string",
    "message": "What is the termination clause in the contract?",
    "history": [
      {"role": "user", "content": "Hello"},
      {"role": "assistant", "content": "Hi! How can I help with your docs?"}
    ]
  }
  ```
- **Success Response:**
  - **Code:** 200
  - **Content:**
    ```json
    {
      "answer": "The termination clause is found on page 12... [contract.pdf - Page 12]",
      "sources": [
        { "file_name": "contract.pdf", "page": 12 }
      ]
    }
    ```

---

## Error Handling

| Code | Description |
| :--- | :--- |
| 400 | Bad Request (Missing file or session_id) |
| 404 | Session not found (No documents uploaded) |
| 500 | Internal Server Error (Gemini API failure or processing error) |
