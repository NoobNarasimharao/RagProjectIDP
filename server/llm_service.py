import os
import ollama
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_GEN_MODEL = os.getenv("OLLAMA_GEN_MODEL", "gemma4:31b-cloud")

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
            "You are a helpful, knowledgeable assistant. Answer the user's question "
            "directly and naturally using your general knowledge. The retrieved textbook "
            "context is optional supporting information, not a restriction: use it when "
            "relevant, and correct or supplement it when needed. Do not say that a question "
            "is not covered just because the context is empty or incomplete. When you use "
            "a claim from the context, cite its source and page; do not invent citations.\n\n"
            f"RETRIEVED TEXTBOOK CONTEXT:\n{context_text or '(No relevant textbook context was found.)'}\n\n"
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
