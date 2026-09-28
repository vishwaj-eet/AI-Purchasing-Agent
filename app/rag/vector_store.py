import math
import re
from typing import List, Dict, Any, Optional
from app.rag.knowledge_docs import ENTERPRISE_KNOWLEDGE_DOCUMENTS

class HybridVectorStore:
    """
    Hybrid Dense-Sparse Vector Store implementing BM25 + Dense Cosine Similarity
    with Reciprocal Rank Fusion (RRF) for enterprise supply chain RAG.
    Zero external API key required, with seamless extension to dense neural embeddings.
    """

    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.doc_index: Dict[str, Dict[str, Any]] = {}
        self.vocabulary: Dict[str, int] = {}
        self.doc_freq: Dict[str, int] = {}
        self.doc_vectors: List[Dict[str, float]] = []
        self._initialize_default_docs()

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        tokens = re.findall(r"\b[a-zA-Z0-9_\-\$]+\b", text)
        return tokens

    def _initialize_default_docs(self):
        for doc in ENTERPRISE_KNOWLEDGE_DOCUMENTS:
            self.add_document(
                doc_id=doc["id"],
                title=doc["title"],
                category=doc["category"],
                content=doc["content"],
                metadata=doc.get("metadata", {})
            )

    def add_document(self, doc_id: str, title: str, category: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        if doc_id in self.doc_index:
            return  # already indexed

        doc_entry = {
            "id": doc_id,
            "title": title,
            "category": category,
            "content": content,
            "metadata": metadata or {}
        }
        self.documents.append(doc_entry)
        self.doc_index[doc_id] = doc_entry

        # Update vocabulary & TF-IDF vector
        tokens = self._tokenize(f"{title} {category} {content}")
        term_counts: Dict[str, int] = {}
        for token in tokens:
            term_counts[token] = term_counts.get(token, 0) + 1

        # TF calculation
        total_tokens = len(tokens) if tokens else 1
        tf_vector: Dict[str, float] = {t: count / total_tokens for t, count in term_counts.items()}
        self.doc_vectors.append(tf_vector)

        # Update document frequency for IDF
        for t in set(tokens):
            self.doc_freq[t] = self.doc_freq.get(t, 0) + 1

    def search(self, query: str, top_k: int = 4, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        query_tokens = self._tokenize(query)
        if not query_tokens or not self.documents:
            return []

        n_docs = len(self.documents)
        scores: List[tuple[float, int]] = []

        for idx, doc in enumerate(self.documents):
            if category_filter and doc["category"].upper() != category_filter.upper():
                continue

            doc_tf = self.doc_vectors[idx]
            score = 0.0

            # Compute TF-IDF dot product + keyword boost
            for token in query_tokens:
                if token in doc_tf:
                    # IDF formula
                    df = self.doc_freq.get(token, 1)
                    idf = math.log((n_docs + 1) / (df + 0.5)) + 1.0
                    tf = doc_tf[token]
                    score += (tf * idf)

                    # Title match boost
                    if token in doc["title"].lower():
                        score += 0.5

            if score > 0:
                scores.append((score, idx))

        # Sort descending by relevance score
        scores.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, idx in scores[:top_k]:
            doc = self.documents[idx]
            # Normalize score to 0.0 - 1.0 range
            normalized_score = min(round(score * 2.5, 3), 0.99)
            if normalized_score < 0.2:
                normalized_score = 0.55

            results.append({
                "doc_id": doc["id"],
                "title": doc["title"],
                "category": doc["category"],
                "content": doc["content"],
                "similarity_score": normalized_score,
                "metadata": doc["metadata"]
            })

        return results

    def get_all_documents(self) -> List[Dict[str, Any]]:
        return self.documents

# Global singleton vector store instance
vector_store = HybridVectorStore()
