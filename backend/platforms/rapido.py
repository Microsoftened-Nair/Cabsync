"""Rapido provider with mock data."""
from __future__ import annotations

from typing import List

from models.ride import RideRequest, RideResult
from platforms.base import MockDataProvider


class RapidoProvider(MockDataProvider):
    provider_id = "rapido"
    provider_name = "Rapido"

    _SERVICES = [
        {
            "service_type": "Rapido Bike",
            "vehicle_type": "bike",
            "base_fare": 25.0,
            "per_km": 7.0,
            "deep_link": "https://rapido.bike/book/ride",
            "confidence": 0.8,
            "vehicle_capacity": 1,
            "rating": 4.3,
            "co2_per_km": 55,
        },
        {
            "service_type": "Rapido Auto",
            "vehicle_type": "auto",
            "base_fare": 35.0,
            "per_km": 9.0,
            "deep_link": "https://rapido.bike/book/ride",
            "confidence": 0.8,
            "vehicle_capacity": 3,
            "rating": 4.2,
            "co2_per_km": 90,
        },
    ]

    def fetch_quotes(self, request: RideRequest) -> List[RideResult]:
        return self.build_mock_quotes(
            request=request,
            provider=self.provider_id,
            provider_name=self.provider_name,
            service_variants=self._SERVICES,
        )
