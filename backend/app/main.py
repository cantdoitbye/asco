from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.v1 import auth, dashboard, stakeholders, anganwadi, supply_chain, agents, grievances, trust_score, offline, recommendations, compliance, network, websocket

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["dashboard"])
app.include_router(stakeholders.router, prefix=f"{settings.API_V1_STR}/stakeholders", tags=["stakeholders"])
app.include_router(anganwadi.router, prefix=f"{settings.API_V1_STR}/anganwadi", tags=["anganwadi"])
app.include_router(supply_chain.router, prefix=f"{settings.API_V1_STR}/supply-chain", tags=["supply-chain"])
app.include_router(agents.router, prefix=f"{settings.API_V1_STR}/agents", tags=["agents"])
app.include_router(grievances.router, prefix=f"{settings.API_V1_STR}/grievances", tags=["grievances"])
app.include_router(trust_score.router, prefix=f"{settings.API_V1_STR}/trust-scores", tags=["trust-scores"])
app.include_router(offline.router, prefix=f"{settings.API_V1_STR}/offline", tags=["offline"])
app.include_router(recommendations.router, prefix=f"{settings.API_V1_STR}/recommendations", tags=["recommendations"])
app.include_router(compliance.router, prefix=f"{settings.API_V1_STR}/compliance", tags=["compliance"])
app.include_router(network.router, prefix=f"{settings.API_V1_STR}/network", tags=["network"])
app.include_router(websocket.router, tags=["websocket"])


@app.get("/")
def root():
    return {
        "message": "Welcome to Ooumph SHAKTI API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
