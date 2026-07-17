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
