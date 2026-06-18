"""
Embedding Engine for RAG support.
Uses sentence-transformers for multilingual embeddings.
"""


class TAIFEmbeddingEngine:
    def __init__(self):
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(
                'paraphrase-multilingual-MiniLM-L12-v2')
        return self._model

    def get_vector(self, text):
        """Returns 384-dim embedding vector."""
        model = self._load()
        return model.encode([text])[0]
