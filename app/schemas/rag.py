from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class KnowledgeDocSchema(BaseModel):
    id: Optional[str] = None
    title: str
    category: str  # "SOP", "CONTRACT", "COMPLIANCE", "SUPPLIER_GUIDE"
    content: str
    metadata: Dict[str, Any] = {}

class QueryRequest(BaseModel):
    query: str
    top_k: int = 4
    category: Optional[str] = None

class SearchResult(BaseModel):
    doc_id: str
    title: str
    category: str
    content: str
    similarity_score: float
    metadata: Dict[str, Any] = {}

class QueryResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_found: int
