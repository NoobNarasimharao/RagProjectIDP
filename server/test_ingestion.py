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
