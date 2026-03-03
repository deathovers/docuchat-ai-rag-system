# DocuChat AI - API Documentation

The DocuChat AI API provides endpoints for document management and conversational RAG.

**Base URL**: `http://localhost:8000`

## 1. Document Management

### Upload Documents
`POST /v1/upload`

Uploads one or more PDF files to a specific session.

**Request Body**: `multipart/form-data`
- `files`: List of files (PDF only).
- `session_id`: A unique string identifying the user session.

**Response**:
```json
[
  {
    "file_id": "string",
    "status": "processing"
  }
]
```

### List Documents
`GET /v1/documents`

Retrieves a list of all processed documents for the given session.

**Query Parameters**:
- `session_id`: (string) Required.

**Response**:
```json
[
  {
    "doc_name": "Contract.pdf",
    "page_count": 12
  }
]
```

## 2. Chat Interface

### Send Message
`POST /v1/chat`

Sends a query to the AI based on the uploaded documents.

**Request Body**:
```json
{
  "query": "What is the termination clause?",
  "session_id": "uuid-string",
  "history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi, how can I help with your documents?"}
  ]
}
```

**Response**:
```json
{
  "answer": "The termination clause is located in section 4.2... [Contract.pdf - Page 5]",
  "sources": [
    {
      "doc_name": "Contract.pdf",
      "page_number": 5
    }
  ]
}
```

## 3. Error Codes
- `400 Bad Request`: Unsupported file format or missing parameters.
- `404 Not Found`: Session ID or document not found.
- `500 Internal Server Error`: LLM or Vector Store processing failure.
