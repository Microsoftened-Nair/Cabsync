"""Sample provider and service configuration for RideMeta backend."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

RideService = Dict[str, Any]
RideProvider = Dict[str, Any]


def eta_range(min_minutes: int, max_minutes: int) -> Tuple[int, int]:
    """Helper to make ETA ranges a little easier to read."""
    return (min_minutes, max_minutes)


SAMPLE_PROVIDER_DATA: List[RideProvider] = [
    {
        "id": "uber",
        "display_name": "Uber",
        "base_deep_link": (
            "https://m.uber.com/ul/?action=setPickup&pickup[latitude]={pickup_lat}"
            "&pickup[longitude]={pickup_lng}&dropoff[latitude]={dropoff_lat}"
            "&dropoff[longitude]={dropoff_lng}&productType={service_slug}"
        ),
        "services": [
            {
                "service_type": "Uber Go",
                "vehicle_type": "car",
                "base_fare": 55,
                "per_km": 11.8,
                "per_min": 1.6,
                "min_fare": 120,
                "avg_speed_kmph": 30,
                "eta_range_minutes": eta_range(5, 12),
                "vehicle_capacity": 4,
                "rating": 4.82,
                "co2_per_km": 165,
                "confidence": 0.95,
                "surge_chance": 0.3,
                "surge_range": (1.2, 1.7),
            },
            {
                "service_type": "Uber Premier",
                "vehicle_type": "car",
                "base_fare": 85,
                "per_km": 16.5,
                "per_min": 2.4,
                "min_fare": 190,
                "avg_speed_kmph": 32,
                "eta_range_minutes": eta_range(6, 14),
                "vehicle_capacity": 4,
                "rating": 4.9,
                "co2_per_km": 175,
                "confidence": 0.97,
                "surge_chance": 0.35,
                "surge_range": (1.2, 1.6),
            },
            {
                "service_type": "Uber Auto",
                "vehicle_type": "auto",
                "base_fare": 38,
                "per_km": 9.2,
                "per_min": 1.15,
                "min_fare": 85,
                "avg_speed_kmph": 25,
                "eta_range_minutes": eta_range(4, 10),
                "vehicle_capacity": 3,
                "rating": 4.65,
                "co2_per_km": 95,
                "confidence": 0.93,
                "surge_chance": 0.25,
                "surge_range": (1.1, 1.4),
            },
        ],
    },
    {
        "id": "ola",
        "display_name": "Ola",
        "base_deep_link": (
            "https://book.olacabs.com/?pickup_lat={pickup_lat}&pickup_lng={pickup_lng}"
            "&drop_lat={dropoff_lat}&drop_lng={dropoff_lng}&category={service_slug}"
        ),
        "services": [
            {
                "service_type": "Ola Auto",
                "vehicle_type": "auto",
                "base_fare": 34,
                "per_km": 9.0,
                "per_min": 1.05,
                "min_fare": 80,
                "avg_speed_kmph": 24,
                "eta_range_minutes": eta_range(4, 11),
                "vehicle_capacity": 3,
                "rating": 4.52,
                "co2_per_km": 90,
                "confidence": 0.91,
                "surge_chance": 0.28,
                "surge_range": (1.1, 1.5),
            },
            {
                "service_type": "Ola Bike",
                "vehicle_type": "bike",
                "base_fare": 28,
                "per_km": 7.1,
                "per_min": 0.85,
                "min_fare": 65,
                "avg_speed_kmph": 32,
                "eta_range_minutes": eta_range(3, 9),
                "vehicle_capacity": 1,
                "rating": 4.48,
                "co2_per_km": 55,
                "confidence": 0.88,
                "surge_chance": 0.18,
                "surge_range": (1.05, 1.25),
            },
            {
                "service_type": "Ola Prime Sedan",
                "vehicle_type": "car",
                "base_fare": 72,
                "per_km": 14.8,
                "per_min": 2.1,
                "min_fare": 170,
                "avg_speed_kmph": 30,
                "eta_range_minutes": eta_range(6, 15),
                "vehicle_capacity": 4,
                "rating": 4.7,
                "co2_per_km": 170,
                "confidence": 0.92,
                "surge_chance": 0.32,
                "surge_range": (1.15, 1.55),
            },
        ],
    },
    {
        "id": "rapido",
        "display_name": "Rapido",
        "base_deep_link": (
            "https://rapido.bike/book/ride?pickup_lat={pickup_lat}&pickup_lng={pickup_lng}"
            "&drop_lat={dropoff_lat}&drop_lng={dropoff_lng}&variant={service_slug}"
        ),
        "services": [
            {
                "service_type": "Rapido Bike",
                "vehicle_type": "bike",
                "base_fare": 25,
                "per_km": 6.4,
                "per_min": 0.76,
                "min_fare": 60,
                "avg_speed_kmph": 34,
                "eta_range_minutes": eta_range(3, 8),
                "vehicle_capacity": 1,
                "rating": 4.35,
                "co2_per_km": 50,
                "confidence": 0.78,
                "surge_chance": 0.16,
                "surge_range": (1.05, 1.2),
            },
            {
                "service_type": "Rapido Auto",
                "vehicle_type": "auto",
                "base_fare": 30,
                "per_km": 8.4,
                "per_min": 1.0,
                "min_fare": 70,
                "avg_speed_kmph": 24,
                "eta_range_minutes": eta_range(4, 10),
                "vehicle_capacity": 3,
                "rating": 4.28,
                "co2_per_km": 88,
                "confidence": 0.8,
                "surge_chance": 0.22,
                "surge_range": (1.05, 1.35),
            },
        ],
    },
    {
        "id": "indrive",
        "display_name": "inDrive",
        "base_deep_link": (
            "https://indrive.com/ride?pickup_lat={pickup_lat}&pickup_lng={pickup_lng}"
            "&drop_lat={dropoff_lat}&drop_lng={dropoff_lng}&tariff={service_slug}"
        ),
        "services": [
            {
                "service_type": "inDrive Saver",
                "vehicle_type": "car",
                "base_fare": 60,
                "per_km": 12.2,
                "per_min": 1.8,
                "min_fare": 150,
                "avg_speed_kmph": 29,
                "eta_range_minutes": eta_range(6, 13),
                "vehicle_capacity": 4,
                "rating": 4.6,
                "co2_per_km": 160,
                "confidence": 0.86,
                "surge_chance": 0.27,
                "surge_range": (1.1, 1.45),
            },
            {
                "service_type": "inDrive Plus",
                "vehicle_type": "car",
                "base_fare": 82,
                "per_km": 15.8,
                "per_min": 2.35,
                "min_fare": 200,
                "avg_speed_kmph": 31,
                "eta_range_minutes": eta_range(7, 14),
                "vehicle_capacity": 4,
                "rating": 4.74,
                "co2_per_km": 175,
                "confidence": 0.9,
                "surge_chance": 0.3,
                "surge_range": (1.15, 1.5),
            },
            {
                "service_type": "inDrive XL",
                "vehicle_type": "suv",
                "base_fare": 105,
                "per_km": 18.5,
                "per_min": 2.8,
                "min_fare": 260,
                "avg_speed_kmph": 28,
                "eta_range_minutes": eta_range(8, 16),
                "vehicle_capacity": 6,
                "rating": 4.68,
                "co2_per_km": 210,
                "confidence": 0.89,
                "surge_chance": 0.32,
                "surge_range": (1.15, 1.55),
            },
        ],
    },
]
"""Structured sample data used to derive deterministic ride comparisons."""
