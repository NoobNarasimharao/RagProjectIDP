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
