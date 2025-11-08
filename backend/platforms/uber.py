"""Uber provider with mock data."""
from __future__ import annotations

from typing import List

from models.ride import RideRequest, RideResult
from platforms.base import MockDataProvider


class UberProvider(MockDataProvider):
    provider_id = "uber"
    provider_name = "Uber"

    _SERVICES = [
        {
            "service_type": "Uber Moto",
            "vehicle_type": "bike",
            "base_fare": 28.0,
            "per_km": 8.0,
            "deep_link": "https://m.uber.com/ul/?action=setPickup",
            "confidence": 0.92,
            "vehicle_capacity": 1,
            "rating": 4.6,
            "co2_per_km": 60,
        },
        {
            "service_type": "Uber Go",
            "vehicle_type": "car",
            "base_fare": 55.0,
            "per_km": 12.0,
            "deep_link": "https://m.uber.com/ul/?action=setPickup",
            "confidence": 0.94,
            "vehicle_capacity": 4,
            "rating": 4.8,
            "co2_per_km": 170,
        },
        {
            "service_type": "Uber Premier",
            "vehicle_type": "car",
            "base_fare": 75.0,
            "per_km": 16.0,
            "deep_link": "https://m.uber.com/ul/?action=setPickup",
            "confidence": 0.9,
            "vehicle_capacity": 4,
            "rating": 4.9,
            "co2_per_km": 185,
        },
        {
            "service_type": "Uber XL",
            "vehicle_type": "car",
            "base_fare": 90.0,
            "per_km": 19.0,
            "deep_link": "https://m.uber.com/ul/?action=setPickup",
            "confidence": 0.88,
            "vehicle_capacity": 6,
            "rating": 4.85,
            "co2_per_km": 210,
        },
    ]

    def fetch_quotes(self, request: RideRequest) -> List[RideResult]:
        return self.build_mock_quotes(
            request=request,
            provider=self.provider_id,
            provider_name=self.provider_name,
            service_variants=self._SERVICES,
        )
