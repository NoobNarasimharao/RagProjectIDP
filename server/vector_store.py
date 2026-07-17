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
