from app.api.routes_inventory import router as inventory_router
from app.api.routes_suppliers import router as suppliers_router
from app.api.routes_orders import router as orders_router
from app.api.routes_emails import router as emails_router
from app.api.routes_approvals import router as approvals_router
from app.api.routes_rag import router as rag_router
from app.api.routes_workflow import router as workflow_router
from app.api.routes_audit import router as audit_router

__all__ = [
    "inventory_router",
    "suppliers_router",
    "orders_router",
    "emails_router",
    "approvals_router",
    "rag_router",
    "workflow_router",
    "audit_router"
]
