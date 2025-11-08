"""Ola provider with mock data."""
from __future__ import annotations

from typing import List

from models.ride import RideRequest, RideResult
from platforms.base import MockDataProvider


class OlaProvider(MockDataProvider):
    provider_id = "ola"
    provider_name = "Ola"

    _SERVICES = [
        {
            "service_type": "Ola Auto",
            "vehicle_type": "auto",
            "base_fare": 30.0,
            "per_km": 9.5,
            "deep_link": "https://book.olacabs.com/",
            "confidence": 0.9,
            "vehicle_capacity": 3,
            "rating": 4.5,
            "co2_per_km": 95,
        },
        {
            "service_type": "Ola Mini",
            "vehicle_type": "car",
            "base_fare": 45.0,
            "per_km": 11.5,
            "deep_link": "https://book.olacabs.com/",
            "confidence": 0.88,
            "vehicle_capacity": 4,
            "rating": 4.6,
            "co2_per_km": 165,
        },
        {
            "service_type": "Ola Prime",
            "vehicle_type": "car",
            "base_fare": 60.0,
            "per_km": 14.0,
            "deep_link": "https://book.olacabs.com/",
            "confidence": 0.86,
            "vehicle_capacity": 4,
            "rating": 4.7,
            "co2_per_km": 190,
        },
        {
            "service_type": "Ola SUV",
            "vehicle_type": "car",
            "base_fare": 85.0,
            "per_km": 18.0,
            "deep_link": "https://book.olacabs.com/",
            "confidence": 0.84,
            "vehicle_capacity": 6,
            "rating": 4.8,
            "co2_per_km": 220,
        },
    ]

    def fetch_quotes(self, request: RideRequest) -> List[RideResult]:
        return self.build_mock_quotes(
            request=request,
            provider=self.provider_id,
            provider_name=self.provider_name,
            service_variants=self._SERVICES,
        )
