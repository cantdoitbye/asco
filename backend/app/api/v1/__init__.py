from .auth import router as auth_router
from .dashboard import router as dashboard_router
from .stakeholders import router as stakeholders_router
from .anganwadi import router as anganwadi_router
from .supply_chain import router as supply_chain_router

__all__ = [
    "auth_router",
    "dashboard_router",
    "stakeholders_router",
    "anganwadi_router",
    "supply_chain_router"
]
