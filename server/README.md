# Interactive Textbook Q&A Server

This is the backend server for the RAG-based textbook question-answering system.

## Architecture
- **PDF Extraction:** PyMuPDF
- **Chunking:** RecursiveCharacterTextSplitter (800 chars, 150 overlap)
- **Embeddings:** Ollama (`nomic-embed-text`)
- **Vector Store:** ChromaDB (Persistent local storage)
- **Answer Generation:** Anthropic Claude (via API)
- **API Layer:** FastAPI

## Installation

1. **Prerequisites:**
   - Install [Ollama](https://ollama.ai/)
   - Pull the embedding model: `ollama pull nomic-embed-text`
   - Ensure Ollama is running at `http://localhost:11434`

2. **Environment Setup:**
   - Create a `.env` file in the `/server` directory based on `.env.example`.
   - Add your `ANTHROPIC_API_KEY`.

3. **Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

```bash
# From the /server directory
uvicorn main:app --reload --port 8000
```

## API Endpoints

### `POST /ingest`
- **Purpose:** Upload a PDF textbook to be indexed.
- **Request:** Multipart form-data (`file`: PDF file).
- **Response:** `{"status": "success", "chunks_indexed": 120, "pdf_name": "textbook_123.pdf"}`

### `POST /ask`
- **Purpose:** Ask a question based on the indexed textbooks.
- **Request Body:** 
  ```json
  {
    "question": "What is the primary function of mitochondria?",
    "pdf_name": "optional_filter_by_pdf_name.pdf"
  }
  ```
- **Response:** 
  ```json
  {
    "answer": "Mitochondria act as the powerhouses of the cell...",
    "sources": [
      {"pdf": "biology.pdf", "page": 15, "text": "..."}
    ]
  }
  ```

### `GET /pdfs`
- **Purpose:** List all indexed textbooks.
- **Response:** `[{"filename": "book.pdf", "chunk_count": 500, "ingest_date": "..."}]`

### `GET /pdfs/{pdf_name}`
- **Purpose:** Download the original PDF file.
- **Response:** PDF file stream.

### `GET /health`
- **Purpose:** Check connectivity to Ollama and ChromaDB.
- **Response:** `{"ollama": "reachable", "chroma": "reachable"}`
