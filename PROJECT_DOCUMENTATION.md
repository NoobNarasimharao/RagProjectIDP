# Complete Repository Documentation

> Automatically generated repository documentation.
> Source code and repository structure are included below.

## Repository Information

**Git Remote:** `origin	https://github.com/NoobNarasimharao/RagProjectIDP.git (fetch)
origin	https://github.com/NoobNarasimharao/RagProjectIDP.git (push)`
**Branch:** `main`
**Latest Commit:** `ee75a46030159ac3c70f3dee0cc1cf856cb17278`
**Latest Commit Message:** `Project main Base is completed`

## Dependency / Configuration Files

No common dependency files detected.

## Repository Structure

```text
📁 frontend/
    📄 .env.example
    📄 app.py
    📄 README.md
    📄 requirements.txt
📁 server/
    📄 .env.example
    📄 doc_processor.py
    📄 llm_service.py
    📄 main.py
    📄 README.md
    📄 requirements.txt
    📄 test_ingestion.py
    📄 test_qa.py
    📄 vector_store.py
📄 test.py
```

# File-by-File Documentation

## `frontend\.env.example`

> Binary or unsupported file type skipped.

## `frontend\app.py`

**File type:** `.py`
**Size:** `5,588 bytes`

### Imports
- `dotenv.load_dotenv`
- `os`
- `requests`
- `streamlit`
- `uuid`

### Source Code

```python
import streamlit as st
import requests
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Interactive Textbook Q&A", layout="wide")

# Session State Initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar: Session Info & Settings
with st.sidebar:
    st.title("Settings")
    st.markdown(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

st.title("📚 Interactive Textbook Q&A")
st.markdown("Upload your textbooks and ask questions grounded in the content.")

# Layout: Two columns (Upload/List and Chat)
col_upload, col_chat = st.columns([1, 2])

with col_upload:
    st.subheader("Documents")

    # File Uploader
    uploaded_files = st.file_uploader(
        "Upload PDFs, DOCX or PPTX",
        type=["pdf", "docx", "pptx"],
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            if st.button(f"Upload {uploaded_file.name}"):
                with st.spinner(f"Indexing {uploaded_file.name}..."):
                    try:
                        # Prepare file for request
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        params = {"session_id": st.session_state.session_id}

                        response = requests.post(f"{BACKEND_URL}/ingest", files=files, params=params)

                        if response.status_code == 200:
                            data = response.json()
                            st.success(f"Indexed {data['chunks_indexed']} chunks!")
                        else:
                            st.error(f"Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection failed: {e}")

    st.divider()

    # List of PDFs in this session
    st.subheader("Your Library")
    try:
        params = {"session_id": st.session_state.session_id}
        res = requests.get(f"{BACKEND_URL}/pdfs", params=params)
        if res.status_code == 200:
            pdfs = res.json()
            if not pdfs:
                st.info("No documents uploaded in this session.")
            else:
                for pdf in pdfs:
                    col_name, col_del = st.columns([0.8, 0.2])
                    with col_name:
                        st.write(f"📄 **{pdf['filename']}** ({pdf['chunk_count']} chunks)")
                    with col_del:
                        if st.button("🗑️", key=f"del_{pdf['filename']}"):
                            try:
                                del_params = {"session_id": st.session_state.session_id}
                                del_res = requests.delete(f"{BACKEND_URL}/pdfs/{pdf['filename']}", params=del_params)
                                if del_res.status_code == 200:
                                    st.success("Deleted")
                                    st.rerun()
                                else:
                                    st.error("Failed")
                            except Exception as e:
                                st.error("Error")
        else:
            st.error("Could not fetch PDF list.")
    except Exception as e:
        st.error(f"Backend unreachable: {e}")

with col_chat:
    st.subheader("Q&A")

    # Chat Display
    chat_container = st.container()
    with chat_container:
        for chat in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(chat["question"])
            with st.chat_message("assistant"):
                st.write(chat["answer"])
                if chat["sources"]:
                    with st.expander("View Sources"):
                        for src in chat["sources"]:
                            st.markdown(f"**{src['pdf']} (Page {src['page']})**")
                            st.caption(src['text'])

    # Question Input
    if prompt := st.chat_input("Ask a question about your textbooks..."):
        # Add to history immediately for UI responsiveness
        st.session_state.chat_history.append({"question": prompt, "answer": "...", "sources": []})

        with st.spinner("Searching textbooks..."):
            try:
                payload = {
                    "question": prompt,
                    "session_id": st.session_state.session_id
                }
                response = requests.post(f"{BACKEND_URL}/ask", json=payload)

                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    sources = data["sources"]

                    # Update last history item
                    st.session_state.chat_history[-1]["answer"] = answer
                    st.session_state.chat_history[-1]["sources"] = sources
                else:
                    st.error(f"Error: {response.text}")
                    st.session_state.chat_history.pop() # remove failed query
            except Exception as e:
                st.error(f"Connection failed: {e}")
                st.session_state.chat_history.pop()

        st.rerun()

```

## `frontend\README.md`

**File type:** `.md`
**Size:** `1,285 bytes`

### Source Code

```markdown
# Interactive Textbook Q&A Frontend

This is a minimal Streamlit frontend for the RAG backend.

## Installation

1. **Prerequisites:**
   - The backend server must be running.
   - Python 3.9+ installed.

2. **Setup:**
   ```bash
   cd frontend
   pip install -r requirements.txt
   ```

3. **Configuration:**
   Create a `.env` file in the `/frontend` directory:
   ```text
   BACKEND_URL=http://localhost:8000
   ```

## Running the Frontend

```bash
streamlit run app.py
```

## Features
- **Session-based Isolation:** Generates a random `session_id` upon loading. All uploads and queries are scoped to this ID.
- **Multi-format Support:** Upload PDFs, DOCX, and PPTX files.
- **Source Attribution:** Answers include expandable source sections with page numbers and text excerpts.
- **Chat History:** Maintains a local history of questions and answers for the current session.

## Known Limitations
- **Ephemeral Sessions:** The `session_id` is stored in the browser's session memory. Refreshing the page or closing the tab will start a new session, meaning you will lose access to documents uploaded in the previous session (though they remain on the server).
- **Single-user focused:** Designed for individual sessions without authentication.

```

## `frontend\requirements.txt`

**File type:** `.txt`
**Size:** `36 bytes`

### Source Code

```text
streamlit
requests
python-dotenv

```

## `server\.env.example`

> Binary or unsupported file type skipped.

## `server\doc_processor.py`

**File type:** `.py`
**Size:** `3,199 bytes`

### Imports
- `docx.Document`
- `fitz`
- `langchain_text_splitters.RecursiveCharacterTextSplitter`
- `os`
- `pptx.Presentation`
- `re`

### Functions
#### `extract_text_from_pdf(pdf_path)`
- Line: `8`
- Description: Extracts text from a PDF file and keeps track of page numbers.

#### `extract_text_from_pptx(pptx_path)`
- Line: `23`
- Description: Extracts text from a PPTX file. Each slide is treated as a page.

#### `extract_text_from_docx(docx_path)`
- Line: `38`
- Description: Extracts text from a DOCX file. Treat as single page.

#### `extract_text_with_pages(file_path)`
- Line: `47`
- Description: Generic extractor that handles PDF, PPTX, and DOCX.
Returns a list of (page_number, text) tuples.

#### `chunk_text_with_metadata(pages_content, source_doc)`
- Line: `62`
- Description: Chunks the extracted text and associates each chunk with its page number and index.

### Source Code

```python
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
import os
from pptx import Presentation
from docx import Document

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file and keeps track of page numbers."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

    doc = fitz.open(pdf_path)
    pages_content = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip() and not re.match(r'^\d+$', line.strip())]
        pages_content.append((page_num, "\n".join(cleaned_lines)))
    doc.close()
    return pages_content

def extract_text_from_pptx(pptx_path):
    """Extracts text from a PPTX file. Each slide is treated as a page."""
    if not os.path.exists(pptx_path):
        raise FileNotFoundError(f"PPTX file not found at: {pptx_path}")

    prs = Presentation(pptx_path)
    pages_content = []
    for i, slide in enumerate(prs.slides, start=1):
        slide_text = []
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                slide_text.append(shape.text)
        pages_content.append((i, "\n".join(slide_text)))
    return pages_content

def extract_text_from_docx(docx_path):
    """Extracts text from a DOCX file. Treat as single page."""
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"DOCX file not found at: {docx_path}")

    doc = Document(docx_path)
    full_text = "\n".join([p.text for p in doc.paragraphs])
    return [(1, full_text)]

def extract_text_with_pages(file_path):
    """
    Generic extractor that handles PDF, PPTX, and DOCX.
    Returns a list of (page_number, text) tuples.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".pptx":
        return extract_text_from_pptx(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

def chunk_text_with_metadata(pages_content, source_doc):
    """
    Chunks the extracted text and associates each chunk with its page number and index.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        length_function=len,
        is_separator_regex=False,
    )

    all_chunks = []
    chunk_count = 0

    for page_num, text in pages_content:
        if not text.strip():
            continue
        page_chunks = text_splitter.split_text(text)
        for chunk in page_chunks:
            all_chunks.append({
                "text": chunk,
                "metadata": {
                    "source_pdf": source_doc, # Keep key as source_pdf for consistency with vector_store
                    "page_number": page_num,
                    "chunk_index": chunk_count
                }
            })
            chunk_count += 1

    return all_chunks

```

## `server\llm_service.py`

**File type:** `.py`
**Size:** `1,611 bytes`

### Imports
- `dotenv.load_dotenv`
- `ollama`
- `os`

### Classes
#### `LLMService`
- Line: `11`
- Methods:
  - `__init__()`
  - `generate_answer()`

### Functions
#### `__init__(self)`
- Line: `12`

#### `generate_answer(self, question, context_chunks)`
- Line: `16`
- Description: Generates a grounded answer using Ollama (local LLM).
context_chunks: List of dicts with 'text' and 'metadata'

### Source Code

```python
import os
import ollama
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
# Use the user's requested model
OLLAMA_GEN_MODEL = "gemma4:31b-cloud"

class LLMService:
    def __init__(self):
        # Configure Ollama client
        self.client = ollama.Client(host=OLLAMA_BASE_URL)

    def generate_answer(self, question, context_chunks):
        """
        Generates a grounded answer using Ollama (local LLM).
        context_chunks: List of dicts with 'text' and 'metadata'
        """
        # Build context string
        context_text = ""
        for i, chunk in enumerate(context_chunks):
            meta = chunk['metadata']
            source = meta.get('source_pdf', 'Unknown')
            page = meta.get('page_number', 'Unknown')
            context_text += f"--- Source: {source} (Page {page}) ---\n{chunk['text']}\n\n"

        prompt = (
            "You are a textbook assistant. Answer the user's question using ONLY the "
            "context below. If the context doesn't fully answer it, say what's missing. "
            "Cite which section/page each part of your answer comes from.\n\n"
            f"CONTEXT:\n{context_text}\n\n"
            f"QUESTION: {question}\n\n"
            "ANSWER:"
        )

        # Generate response using Ollama
        response = self.client.generate(
            model=OLLAMA_GEN_MODEL,
            prompt=prompt,
            options={"num_predict": 1024} # Roughly equivalent to max_tokens
        )

        return response['response']

```

## `server\main.py`

**File type:** `.py`
**Size:** `6,314 bytes`

### Imports
- `datetime.datetime`
- `doc_processor.chunk_text_with_metadata`
- `doc_processor.extract_text_with_pages`
- `dotenv.load_dotenv`
- `fastapi.Depends`
- `fastapi.FastAPI`
- `fastapi.File`
- `fastapi.HTTPException`
- `fastapi.Query`
- `fastapi.UploadFile`
- `fastapi.middleware.cors.CORSMiddleware`
- `fastapi.responses.FileResponse`
- `llm_service.LLMService`
- `os`
- `pydantic.BaseModel`
- `shutil`
- `typing.List`
- `typing.Optional`
- `uuid`
- `vector_store.VectorStore`

### Classes
#### `AskRequest`
- Line: `39`

#### `PDFInfo`
- Line: `44`

### Functions
#### `sanitize_filename(filename)`
- Line: `49`
- Description: Prevents path traversal and handles duplicates.

#### `ingest_document(file, session_id)`
- Line: `68`

#### `ask_question(req)`
- Line: `100`

#### `list_pdfs(session_id)`
- Line: `135`

#### `download_pdf(pdf_name)`
- Line: `158`

#### `delete_pdf(pdf_name, session_id)`
- Line: `166`

#### `health_check()`
- Line: `186`

### Source Code

```python
import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from doc_processor import extract_text_with_pages, chunk_text_with_metadata
from vector_store import VectorStore
from llm_service import LLMService

# Load config
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Interactive Textbook Q&A Server")

# CORS
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:8501")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencies
vs = VectorStore()
llm = LLMService()

PDF_STORAGE_DIR = "pdfs"
os.makedirs(PDF_STORAGE_DIR, exist_ok=True)

# Models
class AskRequest(BaseModel):
    question: str
    session_id: str
    pdf_name: Optional[str] = None

class PDFInfo(BaseModel):
    filename: str
    chunk_count: int
    ingest_date: str

def sanitize_filename(filename: str) -> str:
    """Prevents path traversal and handles duplicates."""
    base_name = os.path.basename(filename)
    name, ext = os.path.splitext(base_name)
    # Simple alphanumeric sanitization
    clean_name = "".join([c for c in name if c.isalnum() or c in (' ', '_', '-')]).strip()
    if not clean_name:
        clean_name = "uploaded_file"

    # Handle duplicates by adding short hash
    final_name = f"{clean_name}{ext}"
    path = os.path.join(PDF_STORAGE_DIR, final_name)
    if os.path.exists(path):
        unique_id = uuid.uuid4().hex[:6]
        final_name = f"{clean_name}_{unique_id}{ext}"

    return final_name

@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...), session_id: str = Query(...)):
    ext = file.filename.lower()
    if not (ext.endswith(".pdf") or ext.endswith(".pptx") or ext.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Only PDF, PPTX, and DOCX files are allowed.")

    # 1. Save file
    safe_name = sanitize_filename(file.filename)
    save_path = os.path.join(PDF_STORAGE_DIR, safe_name)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Process Document
    try:
        pages_content = extract_text_with_pages(save_path)
        chunks = chunk_text_with_metadata(pages_content, safe_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

    # 3. Ingest into Vector Store
    if vs.is_pdf_ingested(safe_name, session_id):
        return {"status": "skipped", "message": f"Document {safe_name} already indexed for this session", "pdf_name": safe_name}

    vs.ingest_chunks(chunks, session_id)

    return {
        "status": "success",
        "chunks_indexed": len(chunks),
        "pdf_name": safe_name
    }

@app.post("/ask")
async def ask_question(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # 1. Retrieve chunks
    chunks = vs.retrieve(req.question, session_id=req.session_id)

    # Filter by pdf_name if requested
    if req.pdf_name:
        chunks = [c for c in chunks if c['metadata']['source_pdf'] == req.pdf_name]

    if not chunks:
        return {
            "answer": "This isn't covered in the textbook.",
            "sources": []
        }

    # 2. Generate answer
    answer = llm.generate_answer(req.question, chunks)

    # 3. Format sources
    sources = []
    for c in chunks:
        sources.append({
            "pdf": c['metadata']['source_pdf'],
            "page": c['metadata']['page_number'],
            "text": c['text']
        })

    return {
        "answer": answer,
        "sources": sources
    }

@app.get("/pdfs", response_model=List[PDFInfo])
async def list_pdfs(session_id: str = Query(...)):
    files = os.listdir(PDF_STORAGE_DIR)
    pdf_list = []
    for f in files:
        if f.lower().endswith((".pdf", ".pptx", ".docx")):
            # Get chunk count from Chroma for this session
            res = vs.collection.get(
                where={"$and": [{"source_pdf": f}, {"session_id": session_id}]}
            )
            count = len(res['ids'])

            if count == 0:
                continue

            # Get ingest date from file metadata
            mtime = os.path.getmtime(os.path.join(PDF_STORAGE_DIR, f))
            date = datetime.fromtimestamp(mtime).isoformat()

            pdf_list.append(PDFInfo(filename=f, chunk_count=count, ingest_date=date))

    return pdf_list

@app.get("/pdfs/{pdf_name}")
async def download_pdf(pdf_name: str):
    safe_name = os.path.basename(pdf_name)
    path = os.path.join(PDF_STORAGE_DIR, safe_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(path)

@app.delete("/pdfs/{pdf_name}")
async def delete_pdf(pdf_name: str, session_id: str = Query(...)):
    safe_name = os.path.basename(pdf_name)
    path = os.path.join(PDF_STORAGE_DIR, safe_name)

    # 1. Remove from vector store
    try:
        vs.delete_pdf(safe_name, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove from vector store: {e}")

    # 2. Remove file from disk
    if os.path.exists(path):
        os.remove(path)
    else:
        # If file is already gone but embeddings exist, we still return success
        pass

    return {"status": "success", "message": f"Removed {safe_name} from session {session_id}"}

@app.get("/health")
async def health_check():
    status = {"ollama": "unreachable", "chroma": "unreachable"}
    try:
        # Check Ollama
        vs.ollama_client.list()
        status["ollama"] = "reachable"
    except Exception:
        pass

    try:
        # Check Chroma
        vs.client.heartbeat()
        status["chroma"] = "reachable"
    except Exception:
        pass

    return status

```

## `server\README.md`

**File type:** `.md`
**Size:** `2,070 bytes`

### Source Code

```markdown
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

```

## `server\requirements.txt`

**File type:** `.txt`
**Size:** `141 bytes`

### Source Code

```text
fastapi
uvicorn
python-multipart
pymupdf
langchain-text-splitters
chromadb
ollama
anthropic
python-dotenv
python-pptx
python-docx

```

## `server\test_ingestion.py`

**File type:** `.py`
**Size:** `1,793 bytes`

### Imports
- `dotenv.load_dotenv`
- `os`
- `vector_store.VectorStore`

### Functions
#### `test_pipeline()`
- Line: `7`

### Source Code

```python
import os
from vector_store import VectorStore
from dotenv import load_dotenv

load_dotenv()

def test_pipeline():
    print("Starting Ingestion Pipeline Test...")
    vs = VectorStore()

    # Mock chunks from pdf_processor
    mock_chunks = [
        {
            "text": "The capital of France is Paris. It is known for the Eiffel Tower.",
            "metadata": {"source_pdf": "test_book.pdf", "page_number": 1, "chunk_index": 0}
        },
        {
            "text": "The Great Wall of China is one of the largest building projects ever completed.",
            "metadata": {"source_pdf": "test_book.pdf", "page_number": 2, "chunk_index": 0}
        },
        {
            "text": "Python is a versatile programming language used for AI and Data Science.",
            "metadata": {"source_pdf": "python_guide.pdf", "page_number": 10, "chunk_index": 5}
        }
    ]

    print("\nIngesting mock chunks...")
    vs.ingest_chunks(mock_chunks)

    print("\nTesting Retrieval...")
    queries = [
        "What is the capital of France?",
        "Tell me about Python",
        "Who is the president of Mars?" # Should be below threshold
    ]

    for q in queries:
        print(f"\nQuery: {q}")
        results = vs.retrieve(q, top_k=2)
        if not results:
            print("  -> Result: Not found in textbook (Correct for unrelated queries)")
        else:
            for res in results:
                print(f"  -> Found: {res['text']} (Page: {res['metadata']['page_number']}, Distance: {res['distance']:.4f})")

if __name__ == "__main__":
    try:
        test_pipeline()
    except Exception as e:
        print(f"Test failed: {e}")
        print("Note: Ensure Ollama is running and 'nomic-embed-text' is pulled.")

```

## `server\test_qa.py`

**File type:** `.py`
**Size:** `1,454 bytes`

### Imports
- `dotenv.load_dotenv`
- `llm_service.LLMService`
- `os`
- `vector_store.VectorStore`

### Functions
#### `test_qa_flow()`
- Line: `8`

### Source Code

```python
import os
from vector_store import VectorStore
from llm_service import LLMService
from dotenv import load_dotenv

load_dotenv()

def test_qa_flow():
    print("Starting QA Flow Test...")
    vs = VectorStore()
    llm = LLMService()

    # Ensure we have some data to test with
    mock_chunks = [
        {
            "text": "The photosynthesis process allows plants to convert light energy into chemical energy. This primarily happens in the leaves.",
            "metadata": {"source_pdf": "biology_101.pdf", "page_number": 42, "chunk_index": 0}
        },
        {
            "text": "Mitochondria are the powerhouses of the cell, generating most of the cell's supply of ATP.",
            "metadata": {"source_pdf": "biology_101.pdf", "page_number": 15, "chunk_index": 12}
        }
    ]
    vs.ingest_chunks(mock_chunks)

    question = "How do plants get energy and where does it happen?"
    print(f"\nQuestion: {question}")

    # 1. Retrieve
    chunks = vs.retrieve(question, top_k=3)
    if not chunks:
        print("No relevant chunks found. (Expected behavior if threshold too high)")
        return

    print(f"Retrieved {len(chunks)} relevant chunks.")

    # 2. Generate
    answer = llm.generate_answer(question, chunks)
    print(f"\nLLM Answer:\n{answer}")

if __name__ == "__main__":
    try:
        test_qa_flow()
    except Exception as e:
        print(f"QA Test failed: {e}")

```

## `server\vector_store.py`

**File type:** `.py`
**Size:** `4,147 bytes`

### Imports
- `chromadb`
- `chromadb.config.Settings`
- `dotenv.load_dotenv`
- `ollama`
- `os`

### Classes
#### `VectorStore`
- Line: `13`
- Methods:
  - `__init__()`
  - `get_embedding()`
  - `is_pdf_ingested()`
  - `ingest_chunks()`
  - `retrieve()`
  - `delete_pdf()`

### Functions
#### `__init__(self)`
- Line: `14`

#### `get_embedding(self, text)`
- Line: `26`
- Description: Gets embedding for a piece of text from Ollama.

#### `is_pdf_ingested(self, source_pdf, session_id)`
- Line: `34`
- Description: Checks if the given PDF is already in the vector store for a specific session.

#### `ingest_chunks(self, chunks, session_id)`
- Line: `42`
- Description: Embeds and stores chunks in ChromaDB.
chunks: List of {'text': ..., 'metadata': {...}}

#### `retrieve(self, query_text, session_id, top_k, threshold)`
- Line: `77`
- Description: Retrieves top_k similar chunks from ChromaDB scoped to a session.

#### `delete_pdf(self, source_pdf, session_id)`
- Line: `106`
- Description: Removes all chunks of a specific PDF for a specific session from the vector store.

### Source Code

```python
import os
import chromadb
from chromadb.config import Settings
import ollama
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

class VectorStore:
    def __init__(self):
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        # Create or get the collection with cosine distance
        self.collection = self.client.get_or_create_collection(
            name="textbook_collection",
            metadata={"hnsw:space": "cosine"}
        )

        # Configure Ollama client
        self.ollama_client = ollama.Client(host=OLLAMA_BASE_URL)

    def get_embedding(self, text):
        """Gets embedding for a piece of text from Ollama."""
        response = self.ollama_client.embeddings(
            model=OLLAMA_EMBED_MODEL,
            prompt=text
        )
        return response['embedding']

    def is_pdf_ingested(self, source_pdf, session_id):
        """Checks if the given PDF is already in the vector store for a specific session."""
        results = self.collection.get(
            where={"$and": [{"source_pdf": source_pdf}, {"session_id": session_id}]},
            limit=1
        )
        return len(results['ids']) > 0

    def ingest_chunks(self, chunks, session_id):
        """
        Embeds and stores chunks in ChromaDB.
        chunks: List of {'text': ..., 'metadata': {...}}
        """
        texts = [c['text'] for c in chunks]
        metadatas = [c['metadata'].copy() for c in chunks]

        # Add session_id to metadata for scoping
        for meta in metadatas:
            meta['session_id'] = session_id

        # Generate unique IDs for chunks
        ids = [f"{m['source_pdf']}_{m['page_number']}_{m['chunk_index']}_{session_id}" for m in metadatas]

        # Embeddings can be large, batch them
        batch_size = 100
        total = len(texts)

        for i in range(0, total, batch_size):
            batch_texts = texts[i : i + batch_size]
            batch_metadatas = metadatas[i : i + batch_size]
            batch_ids = ids[i : i + batch_size]

            batch_embeddings = [self.get_embedding(t) for t in batch_texts]

            self.collection.add(
                embeddings=batch_embeddings,
                documents=batch_texts,
                metadatas=batch_metadatas,
                ids=batch_ids
            )

            print(f"Ingested {min(i + batch_size, total)} / {total} chunks for session {session_id}...")

    def retrieve(self, query_text, session_id, top_k=5, threshold=0.3):
        """
        Retrieves top_k similar chunks from ChromaDB scoped to a session.
        """
        query_embedding = self.get_embedding(query_text)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"session_id": session_id},
            include=["documents", "metadatas", "distances"]
        )

        filtered_results = []
        if not results['ids'] or len(results['ids'][0]) == 0:
            return filtered_results

        for i in range(len(results['ids'][0])):
            distance = results['distances'][0][i]
            # DEBUG: print(f"Chunk {i} distance: {distance:.4f} (Threshold: {1-threshold:.4f})")
            if distance < (1 - threshold):
                filtered_results.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": distance
                })

        return filtered_results

    def delete_pdf(self, source_pdf, session_id):
        """
        Removes all chunks of a specific PDF for a specific session from the vector store.
        """
        self.collection.delete(
            where={"$and": [{"source_pdf": source_pdf}, {"session_id": session_id}]}
        )

```

## `test.py`

**File type:** `.py`
**Size:** `16,618 bytes`

### Imports
- `ast`
- `json`
- `markitdown.MarkItDown`
- `os`
- `pathlib.Path`
- `subprocess`

### Functions
#### `should_ignore(path)`
- Line: `116`
- Description: Decide whether a file/directory should be ignored.

#### `get_language(path)`
- Line: `135`

#### `read_text_file(path)`
- Line: `139`

#### `generate_tree(root)`
- Line: `170`

#### `analyze_python(path)`
- Line: `206`

#### `analyze_file(path, root)`
- Line: `288`

#### `convert_document(path)`
- Line: `423`

#### `get_git_info()`
- Line: `440`

#### `detect_dependencies(root)`
- Line: `496`

#### `generate_documentation()`
- Line: `530`

### Source Code

```python
from pathlib import Path
from markitdown import MarkItDown
import ast
import os
import subprocess
import json


# ============================================================
# CONFIG
# ============================================================

OUTPUT_FILE = "PROJECT_DOCUMENTATION.md"

# Directories that should NOT be documented
IGNORE_DIRS = {
    ".git",
    ".github",
    ".vscode",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".env",
    "dist",
    "build",
    ".next",
    ".idea",
    "coverage",
    "site-packages",
}

# Files that should NOT be included
IGNORE_FILES = {
    OUTPUT_FILE,
    ".gitignore",
    ".gitattributes",
}

# Binary / generated files
IGNORE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".exe",
    ".dll",
    ".so",
    ".bin",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".mp3",
    ".mp4",
    ".wav",
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
}


# ============================================================
# MARKITDOWN
# ============================================================

md_converter = MarkItDown()


# ============================================================
# LANGUAGE DETECTION
# ============================================================

LANGUAGES = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "jsx",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".php": "php",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".json": "json",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".sql": "sql",
    ".sh": "bash",
    ".bat": "bat",
    ".ps1": "powershell",
    ".md": "markdown",
    ".txt": "text",
    ".env": "dotenv",
}


# ============================================================
# FILE HELPERS
# ============================================================

def should_ignore(path: Path):
    """
    Decide whether a file/directory should be ignored.
    """

    for part in path.parts:

        if part in IGNORE_DIRS:
            return True

    if path.name in IGNORE_FILES:
        return True

    if path.suffix.lower() in IGNORE_EXTENSIONS:
        return True

    return False


def get_language(path: Path):
    return LANGUAGES.get(path.suffix.lower(), "")


def read_text_file(path: Path):

    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin-1",
    ]

    for encoding in encodings:

        try:

            return path.read_text(
                encoding=encoding,
                errors="strict"
            )

        except UnicodeDecodeError:
            continue

    return path.read_text(
        encoding="utf-8",
        errors="replace"
    )


# ============================================================
# TREE
# ============================================================

def generate_tree(root: Path):

    lines = []

    all_paths = sorted(root.rglob("*"))

    for path in all_paths:

        if should_ignore(path):
            continue

        relative = path.relative_to(root)

        depth = len(relative.parts) - 1

        prefix = "    " * depth

        if path.is_dir():

            lines.append(
                f"{prefix}📁 {path.name}/"
            )

        else:

            lines.append(
                f"{prefix}📄 {path.name}"
            )

    return "\n".join(lines)


# ============================================================
# PYTHON ANALYSIS
# ============================================================

def analyze_python(path: Path):

    result = {
        "imports": [],
        "functions": [],
        "classes": [],
        "variables": [],
    }

    try:

        source = read_text_file(path)

        tree = ast.parse(source)

    except Exception:

        return result

    for node in ast.walk(tree):

        # Imports
        if isinstance(node, ast.Import):

            for alias in node.names:

                result["imports"].append(alias.name)

        elif isinstance(node, ast.ImportFrom):

            module = node.module or ""

            for alias in node.names:

                result["imports"].append(
                    f"{module}.{alias.name}"
                )

        # Functions
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

            args = []

            for arg in node.args.args:

                args.append(arg.arg)

            result["functions"].append({
                "name": node.name,
                "line": node.lineno,
                "arguments": args,
                "docstring": ast.get_docstring(node),
            })

        # Classes
        elif isinstance(node, ast.ClassDef):

            methods = []

            for child in node.body:

                if isinstance(
                    child,
                    (ast.FunctionDef, ast.AsyncFunctionDef)
                ):

                    methods.append(child.name)

            result["classes"].append({
                "name": node.name,
                "line": node.lineno,
                "methods": methods,
                "docstring": ast.get_docstring(node),
            })

    return result


# ============================================================
# FILE ANALYSIS
# ============================================================

def analyze_file(path: Path, root: Path):

    relative = path.relative_to(root)

    output = []

    output.append(f"## `{relative}`")

    output.append("")

    output.append(
        f"**File type:** `{path.suffix or 'no extension'}`"
    )

    output.append(
        f"**Size:** `{path.stat().st_size:,} bytes`"
    )

    output.append("")

    # --------------------------------------------------------
    # Python analysis
    # --------------------------------------------------------

    if path.suffix.lower() == ".py":

        analysis = analyze_python(path)

        if analysis["imports"]:

            output.append("### Imports")

            for item in sorted(set(analysis["imports"])):

                output.append(
                    f"- `{item}`"
                )

            output.append("")

        if analysis["classes"]:

            output.append("### Classes")

            for cls in analysis["classes"]:

                output.append(
                    f"#### `{cls['name']}`"
                )

                output.append(
                    f"- Line: `{cls['line']}`"
                )

                if cls["methods"]:

                    output.append("- Methods:")

                    for method in cls["methods"]:

                        output.append(
                            f"  - `{method}()`"
                        )

                if cls["docstring"]:

                    output.append(
                        f"- Description: {cls['docstring']}"
                    )

                output.append("")

        if analysis["functions"]:

            output.append("### Functions")

            for func in analysis["functions"]:

                args = ", ".join(func["arguments"])

                output.append(
                    f"#### `{func['name']}({args})`"
                )

                output.append(
                    f"- Line: `{func['line']}`"
                )

                if func["docstring"]:

                    output.append(
                        f"- Description: {func['docstring']}"
                    )

                output.append("")

    # --------------------------------------------------------
    # Read source
    # --------------------------------------------------------

    try:

        content = read_text_file(path)

        language = get_language(path)

        output.append("### Source Code")

        output.append("")

        output.append(
            f"```{language}"
        )

        output.append(content)

        output.append("```")

        output.append("")

    except Exception as e:

        output.append(
            f"> Could not read this file: `{e}`"
        )

        output.append("")

    return "\n".join(output)


# ============================================================
# DOCUMENT CONVERSION
# ============================================================

def convert_document(path: Path):

    try:

        result = md_converter.convert(str(path))

        return result.text_content

    except Exception as e:

        return f"Conversion failed: {e}"


# ============================================================
# REPOSITORY METADATA
# ============================================================

def get_git_info():

    info = {}

    commands = {
        "remote": [
            "git",
            "remote",
            "-v",
        ],

        "branch": [
            "git",
            "branch",
            "--show-current",
        ],

        "commit": [
            "git",
            "log",
            "-1",
            "--pretty=%H",
        ],

        "commit_message": [
            "git",
            "log",
            "-1",
            "--pretty=%s",
        ],
    }

    for key, command in commands.items():

        try:

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10,
            )

            info[key] = result.stdout.strip()

        except Exception:

            info[key] = ""

    return info


# ============================================================
# DEPENDENCY DETECTION
# ============================================================

def detect_dependencies(root: Path):

    dependencies = []

    files = [
        "requirements.txt",
        "requirements-dev.txt",
        "pyproject.toml",
        "package.json",
        "package-lock.json",
        "Pipfile",
        "environment.yml",
        "pom.xml",
        "build.gradle",
        "Cargo.toml",
    ]

    for filename in files:

        path = root / filename

        if path.exists():

            dependencies.append(
                f"- `{filename}`"
            )

    return dependencies


# ============================================================
# MAIN GENERATOR
# ============================================================

def generate_documentation():

    root = Path.cwd()

    print("Scanning repository...")
    print(f"Root: {root}")

    git = get_git_info()

    output = []

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    output.append(
        "# Complete Repository Documentation"
    )

    output.append("")

    output.append(
        "> Automatically generated repository documentation."
    )

    output.append(
        "> Source code and repository structure are included below."
    )

    output.append("")

    # --------------------------------------------------------
    # Repository information
    # --------------------------------------------------------

    output.append(
        "## Repository Information"
    )

    output.append("")

    if git.get("remote"):

        output.append(
            f"**Git Remote:** `{git['remote']}`"
        )

    if git.get("branch"):

        output.append(
            f"**Branch:** `{git['branch']}`"
        )

    if git.get("commit"):

        output.append(
            f"**Latest Commit:** `{git['commit']}`"
        )

    if git.get("commit_message"):

        output.append(
            f"**Latest Commit Message:** `{git['commit_message']}`"
        )

    output.append("")

    # --------------------------------------------------------
    # Dependencies
    # --------------------------------------------------------

    output.append(
        "## Dependency / Configuration Files"
    )

    output.append("")

    dependencies = detect_dependencies(root)

    if dependencies:

        output.extend(dependencies)

    else:

        output.append(
            "No common dependency files detected."
        )

    output.append("")

    # --------------------------------------------------------
    # Repository tree
    # --------------------------------------------------------

    output.append(
        "## Repository Structure"
    )

    output.append("")

    output.append("```text")

    output.append(
        generate_tree(root)
    )

    output.append("```")

    output.append("")

    # --------------------------------------------------------
    # Files
    # --------------------------------------------------------

    output.append(
        "# File-by-File Documentation"
    )

    output.append("")

    files = []

    for path in root.rglob("*"):

        if not path.is_file():
            continue

        if should_ignore(path):
            continue

        files.append(path)

    files.sort(
        key=lambda x: str(x.relative_to(root)).lower()
    )

    print(
        f"Found {len(files)} files to document."
    )

    for index, path in enumerate(files, 1):

        print(
            f"[{index}/{len(files)}] {path.relative_to(root)}"
        )

        # ----------------------------------------------------
        # Standard source/document files
        # ----------------------------------------------------

        if path.suffix.lower() in {
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".java",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".cs",
            ".php",
            ".html",
            ".htm",
            ".css",
            ".scss",
            ".sass",
            ".json",
            ".xml",
            ".yaml",
            ".yml",
            ".sql",
            ".sh",
            ".bat",
            ".ps1",
            ".md",
            ".txt",
            ".env",
        }:

            output.append(
                analyze_file(path, root)
            )

        # ----------------------------------------------------
        # Documents supported by MarkItDown
        # ----------------------------------------------------

        elif path.suffix.lower() in {
            ".pdf",
            ".docx",
            ".pptx",
            ".xlsx",
            ".csv",
            ".html",
            ".xml",
        }:

            relative = path.relative_to(root)

            output.append(
                f"## `{relative}`"
            )

            output.append("")

            output.append(
                "### Converted Content"
            )

            output.append("")

            output.append(
                convert_document(path)
            )

            output.append("")

        # ----------------------------------------------------
        # Unknown files
        # ----------------------------------------------------

        else:

            relative = path.relative_to(root)

            output.append(
                f"## `{relative}`"
            )

            output.append("")

            output.append(
                "> Binary or unsupported file type skipped."
            )

            output.append("")

    # --------------------------------------------------------
    # Write output
    # --------------------------------------------------------

    output_path = root / OUTPUT_FILE

    output_path.write_text(
        "\n".join(output),
        encoding="utf-8",
    )

    print()
    print("=" * 60)
    print("DOCUMENTATION GENERATED")
    print("=" * 60)
    print()
    print(output_path)


if __name__ == "__main__":

    generate_documentation()
```
