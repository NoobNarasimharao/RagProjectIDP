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
