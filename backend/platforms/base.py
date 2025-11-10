"""Shared helpers for platform providers."""
from __future__ import annotations

from math import atan2, cos, radians, sin, sqrt
from random import Random
from typing import List

from models.ride import Eta, Price, cabsync, RideRequest, RideResult


class MockDataProvider:
    """Utility mixin to produce mock ride quotes with deterministic randomness."""

    seed_namespace = "cabsync"

    def _rng(self, *pieces: str) -> Random:
        seed = "::".join([self.seed_namespace, *pieces])
        return Random(seed)

    def _format_eta(self, minutes: float) -> Eta:
        seconds = int(minutes * 60)
        display_minutes = max(1, int(round(minutes)))
        return Eta(seconds=max(30, seconds), text=f"{display_minutes} min")

    def _distance_meters(self, request: RideRequest) -> int:
        radius_km = 6371.0
        lat1, lon1 = radians(request.pickup.lat), radians(request.pickup.lng)
        lat2, lon2 = radians(request.dropoff.lat), radians(request.dropoff.lng)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance_km = max(radius_km * c, 0.75)
        return int(distance_km * 1000)

    def build_mock_quotes(
        self,
        request: RideRequest,
        provider: str,
        provider_name: str,
        service_variants: List[dict],
    ) -> List[RideResult]:
        distance_meters = self._distance_meters(request)
        base_minutes = max(distance_meters / 1000 / 30 * 60, 10)
        quotes: List[RideResult] = []

        # Filter services by requested vehicle type
        filtered_variants = service_variants
        if request.vehicle_type:
            requested_type = request.vehicle_type.lower()
            filtered_variants = [
                v for v in service_variants 
                if v.get("vehicle_type", "").lower() == requested_type
            ]
            # If no exact matches, return empty (strict filtering)
            if not filtered_variants:
                return []
        
        # Further filter by seater capacity if specified
        if request.seater_capacity:
            filtered_variants = [
                v for v in filtered_variants
                if v.get("vehicle_capacity") == request.seater_capacity
            ]

        for variant in filtered_variants:
            rng = self._rng(provider, variant["service_type"], request.pickup.address)
            surge = variant.get("surge")
            if surge is None:
                surge = rng.uniform(0.9, 1.4)

            price = variant["base_fare"] + (distance_meters / 1000) * variant["per_km"]
            price *= surge
            eta_minutes = base_minutes * rng.uniform(0.7, 1.2)

            co2_per_km = variant.get("co2_per_km")
            co2_estimate = None
            if co2_per_km and co2_per_km > 0:
                co2_estimate = co2_per_km * (distance_meters / 1000)

            vehicle_capacity = variant.get("vehicle_capacity")
            rating = variant.get("rating")
            meta = None
            if any(value is not None for value in (vehicle_capacity, rating, co2_estimate)):
                meta = cabsync(
                    vehicle_capacity=vehicle_capacity,
                    rating=rating,
                    co2_estimate=co2_estimate,
                )

            quotes.append(
                RideResult(
                    provider=provider,
                    service_type=variant["service_type"],
                    price=Price(
                        value=round(price, 2),
                        currency=variant.get("currency", "₹"),
                        confidence=variant.get("confidence", 0.82),
                    ),
                    eta=self._format_eta(eta_minutes),
                    distance=distance_meters,
                    deep_link=variant.get("deep_link", ""),
                    surge=round(surge, 2) if surge > 1 else None,
                    meta=meta,
                )
            )

        return quotes
