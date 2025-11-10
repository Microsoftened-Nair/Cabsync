"""Rapido provider with real-time API integration."""
from __future__ import annotations

from typing import List
import logging

from models.ride import RideRequest, RideResult
from platforms.base import MockDataProvider

try:
    from platforms.rapido_graphql import RapidoAPIClient
    HAS_RAPIDO_API = True
except ImportError:
    HAS_RAPIDO_API = False
    logging.warning("RapidoAPIClient not available, using mock data")


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

    def __init__(self):
        """Initialize Rapido provider with optional real-time API client."""
        super().__init__()
        self.api_client = RapidoAPIClient() if HAS_RAPIDO_API else None
        self.use_real_api = HAS_RAPIDO_API

    def fetch_quotes(self, request: RideRequest) -> List[RideResult]:
        """
        Fetch ride quotes from Rapido.
        
        Args:
            request: Ride request with pickup and dropoff coordinates
            
        Returns:
            List of ride results with prices and details
        """
        # Try real-time API first if available
        if self.use_real_api and self.api_client:
            try:
                return self._fetch_realtime_quotes(request)
            except Exception as e:
                logging.warning(f"Rapido real-time API failed: {e}, falling back to mock data")
        
        # Fallback to mock data
        return self.build_mock_quotes(
            request=request,
            provider=self.provider_id,
            provider_name=self.provider_name,
            service_variants=self._SERVICES,
        )

    def _fetch_realtime_quotes(self, request: RideRequest) -> List[RideResult]:
        """
        Fetch real-time quotes from Rapido API.
        
        Args:
            request: Ride request with pickup and dropoff coordinates
            
        Returns:
            List of ride results with real prices from Rapido
        """
        # Get ride prices from API
        rides = self.api_client.get_and_parse_prices(
            pickup_lat=request.pickup.lat,
            pickup_lng=request.pickup.lng,
            pickup_name=request.pickup.address,
            dropoff_lat=request.dropoff.lat,
            dropoff_lng=request.dropoff.lng,
            dropoff_name=request.dropoff.address
        )
        
        # Calculate distance
        distance_meters = self._distance_meters(request)
        
        # Map vehicle types and metadata
        vehicle_capacity_map = {
            'bike': 1,
            'auto': 3,
            'car': 4,
        }
        
        rating_map = {
            'bike': 4.3,
            'auto': 4.2,
            'car': 4.4,
        }
        
        co2_per_km_map = {
            'bike': 55,
            'auto': 90,
            'car': 120,
        }
        
        # Convert to RideResult objects with filtering
        results = []
        for ride in rides:
            vehicle_type = ride.get('vehicle_type', 'unknown')
            vehicle_capacity = vehicle_capacity_map.get(vehicle_type, 2)
            
            # Apply vehicle type filter if requested
            if request.vehicle_type:
                requested_type = request.vehicle_type.lower()
                if vehicle_type.lower() != requested_type:
                    continue
            
            # Apply seater capacity filter if requested
            if request.seater_capacity:
                if vehicle_capacity != request.seater_capacity:
                    continue
            
            price_min = ride.get('price_min', 0.0)
            price_max = ride.get('price_max', price_min)
            
            # Use average price
            avg_price = (price_min + price_max) / 2 if price_max > 0 else price_min
            
            # Calculate CO2 estimate
            co2_per_km = co2_per_km_map.get(vehicle_type, 90)
            co2_estimate = co2_per_km * (distance_meters / 1000)
            
            # Create meta with additional info
            from models.ride import cabsync, Price, Eta
            meta = cabsync(
                vehicle_capacity=vehicle_capacity,
                rating=rating_map.get(vehicle_type, 4.3),
                co2_estimate=co2_estimate,
            )
            
            # Estimate ETA (rough estimate: 30 km/h average speed)
            eta_minutes = max((distance_meters / 1000) / 30 * 60, 10)
            eta = Eta(
                seconds=int(eta_minutes * 60),
                text=f"{int(eta_minutes)} min"
            )
            
            result = RideResult(
                provider=self.provider_id,
                service_type=ride.get('name', 'Rapido Ride'),
                price=Price(
                    value=round(avg_price, 2),
                    currency=ride.get('currency', '₹'),
                    confidence=0.95,  # High confidence for real-time data
                ),
                eta=eta,
                distance=distance_meters,
                deep_link="https://rapido.bike/book/ride",
                meta=meta,
            )
            results.append(result)
        
        return results
