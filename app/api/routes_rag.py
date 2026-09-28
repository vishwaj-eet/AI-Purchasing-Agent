from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.rag.vector_store import vector_store
from app.schemas.rag import QueryRequest, QueryResponse, SearchResult, KnowledgeDocSchema

router = APIRouter(prefix="/api/rag", tags=["RAG & Knowledge Retrieval"])

@router.get("/docs", response_model=List[KnowledgeDocSchema])
def list_knowledge_documents():
    """Lists all enterprise policy, MSA, and compliance documents in the vector knowledge base."""
    docs = vector_store.get_all_documents()
    return docs

@router.post("/search", response_model=QueryResponse)
def search_knowledge_base(query_in: QueryRequest):
    """Performs hybrid semantic and keyword retrieval against enterprise procurement SOPs and contracts."""
    raw_results = vector_store.search(
        query=query_in.query,
        top_k=query_in.top_k,
        category_filter=query_in.category
    )

    results = [
        SearchResult(
            doc_id=r["doc_id"],
            title=r["title"],
            category=r["category"],
            content=r["content"],
            similarity_score=r["similarity_score"],
            metadata=r["metadata"]
        )
        for r in raw_results
    ]

    return QueryResponse(
        query=query_in.query,
        results=results,
        total_found=len(results)
    )

@router.post("/docs", status_code=201)
def add_knowledge_document(doc_in: KnowledgeDocSchema):
    """Dynamically indexes a new SOP, MSA, or vendor policy into the hybrid vector store."""
    doc_id = doc_in.id or f"DOC-{len(vector_store.documents) + 1}"
    vector_store.add_document(
        doc_id=doc_id,
        title=doc_in.title,
        category=doc_in.category,
        content=doc_in.content,
        metadata=doc_in.metadata
    )
    return {"message": f"Document '{doc_in.title}' indexed successfully.", "doc_id": doc_id}
