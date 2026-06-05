from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.database import Base, engine
# Import all models to register them with Base
from app.models import User, Frete

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FreteBR API",
    description="Marketplace de fretes brasileiro",
    version="0.1.0"
)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "FreteBR Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
