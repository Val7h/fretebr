from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.fretes import router as fretes_router
from app.api.matches import router as matches_router
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
    FreteTracking, FreteCurrentLocation, TrackingSession
)

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
app.include_router(fretes_router)
app.include_router(matches_router)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
