from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.observability import (
    setup_logging, setup_sentry, request_id_middleware, metrics
)
from app.api.auth import router as auth_router

# Observabilidade (antes de tudo)
setup_logging()
setup_sentry()
from app.api.fretes import router as fretes_router
from app.api.matches import router as matches_router
from app.api.messages import router as messages_router
from app.api.notifications import router as notifications_router
from app.api.transactions import router as transactions_router
from app.api.payments import router as payments_router
from app.routes.referral import router as referral_router
from app.routes.fuel_station import router as fuel_station_router
from app.routes.rating import router as rating_router
from app.routes.tracking import router as tracking_router
from app.routes.agents import router as agents_router
from app.database import Base, engine
# Import all models to register them with Base
from app.models import (
    User, Frete, Match, Message, Transaction, Referral, ReferralWithdrawal,
    FuelStation, FuelStationAttendant, FuelReferralCode, FuelStationReferral,
    FuelDiscount, FuelAttendantWithdrawal,
    RatingMotorista, RatingShipper, UserReputation,
    FreteTracking, FreteCurrentLocation, TrackingSession, Notification
)

# Create tables
Base.metadata.create_all(bind=engine)

# Rate limiter (global - usado por endpoints sensiveis)
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="FreteBR API",
    description="Marketplace de fretes brasileiro",
    version="0.1.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware de request-id + metricas
app.middleware("http")(request_id_middleware)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3008",
        "http://localhost:3009",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(fretes_router)
app.include_router(matches_router)
app.include_router(messages_router)
app.include_router(notifications_router)
app.include_router(transactions_router)
app.include_router(payments_router)
app.include_router(referral_router)
app.include_router(fuel_station_router)
app.include_router(rating_router)
app.include_router(tracking_router)
app.include_router(agents_router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "FreteBR Backend"}


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics_prometheus():
    """Metricas no formato Prometheus."""
    return PlainTextResponse(content=metrics.render_prometheus(), media_type="text/plain")


@app.get("/metrics/summary")
async def metrics_summary():
    """Metricas em JSON (resumo legivel)."""
    return metrics.summary_json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
