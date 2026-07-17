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
