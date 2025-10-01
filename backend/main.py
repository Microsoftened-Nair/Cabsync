from __future__ import annotations

import hashlib
import logging
import os
import random
from datetime import datetime
from math import atan2, cos, radians, sin, sqrt
from typing import List, Optional, Sequence, Tuple
from urllib.parse import quote_plus

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from sample_data import SAMPLE_PROVIDER_DATA

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RideMeta API",
    description="A ride aggregator API that compares prices across multiple providers",
    version="1.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models & helpers
def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(  # type: ignore[call-arg]
        populate_by_name=True,
        alias_generator=to_camel,
        extra="ignore",
    )


class Location(CamelModel):
    lat: float
    lng: float
    address: str
    place_id: Optional[str] = None


class RideRequest(CamelModel):
    pickup: Location
    dropoff: Location
    when: Optional[datetime] = None
    vehicle_type: Optional[str] = "auto"


class Price(CamelModel):
    value: float
    currency: str
    confidence: float


class Eta(CamelModel):
    seconds: int
    text: str


class RideMetaDetail(CamelModel):
    vehicle_capacity: Optional[int] = None
    rating: Optional[float] = None
    co2_estimate: Optional[float] = None


class RideResult(CamelModel):
    provider: str
    service_type: str
    price: Price
    eta: Eta
    distance: int
    surge: Optional[float] = None
    deep_link: str
    meta: Optional[RideMetaDetail] = None


class ResponseMeta(CamelModel):
    queried_at: str
    cache_key: str
    total_providers: int
    failed_providers: List[str]


class CompareResponse(CamelModel):
    results: List[RideResult]
    meta: ResponseMeta


def _haversine_distance_km(pickup: Location, dropoff: Location) -> float:
    radius = 6371.0
    lat1, lon1, lat2, lon2 = map(
        radians, [pickup.lat, pickup.lng, dropoff.lat, dropoff.lng]
    )
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = radius * c
    return max(distance, 0.75)


def _traffic_multiplier(when: datetime) -> float:
    multiplier = 1.0
    hour = when.hour

    if 7 <= hour < 10 or 17 <= hour < 21:
        multiplier += 0.35
    elif 22 <= hour or hour < 5:
        multiplier -= 0.15

    if when.weekday() >= 5:
        multiplier += 0.1

    return max(0.8, min(multiplier, 1.6))


def _select_services(
    services: Sequence[dict], vehicle_type: Optional[str]
) -> List[dict]:
    if not vehicle_type:
        return list(services)

    requested = vehicle_type.lower()
    exact_matches = [
        service for service in services if service.get("vehicle_type") == requested
    ]
    if exact_matches:
        return exact_matches

    fallback_map = {
        "auto": {"auto", "car"},
        "car": {"car", "suv"},
        "bike": {"bike", "scooter"},
    }
    relaxed_types = fallback_map.get(requested, {requested})
    relaxed_matches = [
        service
        for service in services
        if service.get("vehicle_type") in relaxed_types
    ]
    if relaxed_matches:
        return relaxed_matches

    return list(services)


def _format_eta(minutes: float) -> str:
    if minutes <= 1:
        return "Now"
    rounded = max(1, int(round(minutes)))
    return f"{rounded} min" if rounded == 1 else f"{rounded} mins"


def _build_seed(
    provider_id: str, service_type: str, request: RideRequest, when: datetime
) -> int:
    fingerprint = (
        provider_id,
        service_type,
        round(request.pickup.lat, 3),
        round(request.pickup.lng, 3),
        round(request.dropoff.lat, 3),
        round(request.dropoff.lng, 3),
        when.date().isoformat(),
    )
    digest = hashlib.sha1(str(fingerprint).encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _build_deep_link(
    provider: dict, service: dict, request: RideRequest
) -> str:
    template = service.get("deep_link_template") or provider.get("base_deep_link")
    if not template:
        return ""

    context = {
        "pickup_lat": f"{request.pickup.lat:.6f}",
        "pickup_lng": f"{request.pickup.lng:.6f}",
        "dropoff_lat": f"{request.dropoff.lat:.6f}",
        "dropoff_lng": f"{request.dropoff.lng:.6f}",
        "pickup_address": quote_plus(request.pickup.address),
        "dropoff_address": quote_plus(request.dropoff.address),
        "service_slug": quote_plus(
            service["service_type"].lower().replace(" ", "-")
        ),
    }

    try:
        return template.format(**context)
    except KeyError:
        return template


def _estimate_trip_minutes(
    distance_km: float, service: dict, traffic_multiplier: float, rng: random.Random
) -> float:
    base_speed = max(service.get("avg_speed_kmph", 28), 10)
    minutes = max(distance_km / base_speed * 60, 6)
    minutes *= traffic_multiplier
    minutes *= rng.uniform(0.9, 1.15)
    return minutes


def _build_cache_key(request: RideRequest) -> str:
    base = (
        f"{request.pickup.lat:.3f}:{request.pickup.lng:.3f}:"
        f"{request.dropoff.lat:.3f}:{request.dropoff.lng:.3f}:"
        f"{(request.vehicle_type or 'any').lower()}"
    )
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]
    return f"sample_{digest}"


def generate_sample_results(
    request: RideRequest,
) -> Tuple[List[RideResult], List[str]]:
    when = request.when or datetime.utcnow()
    distance_km = _haversine_distance_km(request.pickup, request.dropoff)
    traffic_multiplier = _traffic_multiplier(when)

    results: List[RideResult] = []
    failed_providers: List[str] = []

    for provider in SAMPLE_PROVIDER_DATA:
        services = provider.get("services", [])
        selected_services = _select_services(services, request.vehicle_type)

        if not selected_services:
            failed_providers.append(provider.get("id", "unknown"))
            continue

        for service in selected_services:
            rng = random.Random(
                _build_seed(
                    provider.get("id", "unknown"),
                    service["service_type"],
                    request,
                    when,
                )
            )

            trip_minutes = _estimate_trip_minutes(
                distance_km, service, traffic_multiplier, rng
            )
            demand_factor = 0.6 + traffic_multiplier * 0.5
            price_value = (
                service["base_fare"]
                + distance_km * service["per_km"] * demand_factor
                + trip_minutes * service["per_min"] * (0.4 + traffic_multiplier * 0.3)
            )
            price_value = max(service["min_fare"], price_value)
            price_value *= rng.uniform(0.96, 1.08)

            surge = None
            if traffic_multiplier > 1.1 and "surge_range" in service:
                surge_probability = min(
                    0.9, service.get("surge_chance", 0.25) * traffic_multiplier
                )
                if rng.random() < surge_probability:
                    surge = round(rng.uniform(*service["surge_range"]), 2)
                    price_value *= surge

            price_value = round(price_value / 5) * 5

            eta_range = service.get("eta_range_minutes", (5, 12))
            eta_min, eta_max = (
                tuple(eta_range) if isinstance(eta_range, (list, tuple)) else (5, 12)
            )
            eta_minutes = rng.uniform(eta_min, eta_max) * (
                0.85 + (traffic_multiplier - 1) * 0.5
            )
            eta_minutes = max(0.5, eta_minutes)
            eta_seconds = max(20, int(eta_minutes * 60))

            results.append(
                RideResult(
                    provider=provider["id"],
                    service_type=service["service_type"],
                    price=Price(
                        value=float(price_value),
                        currency="₹",
                        confidence=service.get("confidence", 0.85),
                    ),
                    eta=Eta(seconds=eta_seconds, text=_format_eta(eta_minutes)),
                    distance=int(distance_km * 1000),
                    surge=surge,
                    deep_link=_build_deep_link(provider, service, request),
                    meta=RideMetaDetail(
                        vehicle_capacity=service.get("vehicle_capacity"),
                        rating=service.get("rating"),
                        co2_estimate=round(
                            distance_km * service.get("co2_per_km", 0)
                        ),
                    ),
                )
            )

    results.sort(key=lambda ride: (ride.price.value, ride.eta.seconds, ride.provider))
    return results, failed_providers

# API Routes
@app.get("/")
async def root():
    return {
        "message": "RideMeta API",
        "version": "1.1.0",
        "mode": os.getenv("MODE", "MOCK"),
        "providers": [provider["id"] for provider in SAMPLE_PROVIDER_DATA],
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "providers": len(SAMPLE_PROVIDER_DATA),
    }

@app.post("/api/compare", response_model=CompareResponse, response_model_by_alias=True)
async def compare_rides(request: RideRequest):
    """Compare ride prices across Uber, Ola, Rapido, and inDrive using sample data."""
    try:
        logger.info(
            "Ride request received: %s -> %s",
            request.pickup.address,
            request.dropoff.address,
        )

        results, failed_providers = generate_sample_results(request)

        response = CompareResponse(
            results=results,
            meta=ResponseMeta(
                queried_at=datetime.utcnow().isoformat() + "Z",
                cache_key=_build_cache_key(request),
                total_providers=len(SAMPLE_PROVIDER_DATA),
                failed_providers=failed_providers,
            ),
        )

        return response

    except Exception as exc:  # pragma: no cover - defensive safeguard
        logger.exception("Error comparing rides")
        raise HTTPException(status_code=500, detail="Failed to compare rides") from exc


@app.get("/api/providers")
async def list_providers():
    """Expose the available providers and their configured services."""
    return {
        "providers": [
            {
                "id": provider["id"],
                "displayName": provider.get("display_name", provider["id"].title()),
                "services": [
                    {
                        "serviceType": service["service_type"],
                        "vehicleType": service.get("vehicle_type"),
                        "baseFare": service.get("base_fare"),
                        "perKm": service.get("per_km"),
                        "perMin": service.get("per_min"),
                    }
                    for service in provider.get("services", [])
                ],
            }
            for provider in SAMPLE_PROVIDER_DATA
        ]
    }

@app.get("/api/auth/uber")
async def initiate_uber_auth():
    """Initiate Uber OAuth flow (placeholder)"""
    # This would redirect to Uber's OAuth URL in a real implementation
    uber_client_id = os.getenv("UBER_CLIENT_ID")
    redirect_uri = os.getenv("UBER_REDIRECT_URI")
    
    if not uber_client_id:
        raise HTTPException(status_code=501, detail="Uber OAuth not configured")
    
    auth_url = f"https://login.uber.com/oauth/v2/authorize?client_id={uber_client_id}&response_type=code&redirect_uri={redirect_uri}&scope=rides.read"
    
    return {"auth_url": auth_url}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.status_code, "message": exc.detail}}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
