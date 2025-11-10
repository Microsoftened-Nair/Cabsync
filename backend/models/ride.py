"""Pydantic models shared across the backend."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


def _to_camel(name: str) -> str:
    first, *others = name.split("_")
    return first + "".join(part.capitalize() for part in others)


class CamelModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=_to_camel,
        extra="ignore",
    )


class Location(CamelModel):
    lat: float
    lng: float
    address: str
    place_id: Optional[str] = Field(default=None, alias="placeId")


class RideRequest(CamelModel):
    pickup: Location
    dropoff: Location
    when: Optional[datetime] = None
    vehicle_type: Optional[str] = Field(default=None, alias="vehicleType")
    seater_capacity: Optional[int] = Field(default=None, alias="seaterCapacity")


class Price(CamelModel):
    value: float
    currency: str = "₹"
    confidence: float = 0.85


class Eta(CamelModel):
    seconds: int
    text: str


class cabsync(CamelModel):
    vehicle_capacity: Optional[int] = None
    rating: Optional[float] = None
    co2_estimate: Optional[float] = None


class RideResult(CamelModel):
    provider: str
    service_type: str
    price: Price
    eta: Eta
    distance: int
    deep_link: str = Field(default="", alias="deepLink")
    surge: Optional[float] = None
    meta: Optional[cabsync] = None


class ResponseMeta(CamelModel):
    queried_at: str = Field(alias="queriedAt")
    cache_key: str = Field(alias="cacheKey")
    total_providers: int = Field(alias="totalProviders")
    failed_providers: List[str] = Field(default_factory=list, alias="failedProviders")


class CompareResponse(CamelModel):
    results: List[RideResult]
    meta: ResponseMeta


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class TransactionState(BaseModel):
    """State management for Beckn async transactions"""
    transaction_id: str
    request: RideRequest
    status: TransactionStatus = TransactionStatus.PENDING
    results: List[RideResult] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    callback_received_at: Optional[datetime] = None
    error: Optional[str] = None


class BecknCallback(BaseModel):
    """Beckn protocol callback payload"""
    context: Dict[str, Any]
    message: Dict[str, Any]
    error: Optional[Dict[str, Any]] = None


# In-memory transaction store (use Redis in production)
transaction_store: Dict[str, TransactionState] = {}
