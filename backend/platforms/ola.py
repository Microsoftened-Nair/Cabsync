"""Ola provider using real API."""
from __future__ import annotations

import os
from typing import List, Optional
from urllib.parse import urlencode

from models.ride import Eta, Price, RideRequest, RideResult, cabsync
from platforms.ola_client import OlaAPIClient


class OlaProvider:
    provider_id = "ola"
    provider_name = "Ola"

    def __init__(self):
        """Initialize Ola provider with API client."""
        self.client: Optional[OlaAPIClient] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the API client with cookies from environment or file."""
        # Try to load cookies from environment variable
        cookie_string = os.environ.get('OLA_COOKIES', '')
        
        if not cookie_string:
            # Try to load from file
            cookie_file = os.path.join(
                os.path.dirname(__file__), 
                '..', 
                'ola_cookies.txt'
            )
            try:
                with open(cookie_file, 'r') as f:
                    lines = f.readlines()
                    # Find the first non-comment, non-empty line
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            cookie_string = line
                            break
            except FileNotFoundError:
                pass
        
        # Check if cookies are valid (not placeholder)
        cookies = {}
        if cookie_string and 'REPLACE_ME' not in cookie_string:
            cookies = OlaAPIClient.cookies_from_string(cookie_string)
        
        self.client = OlaAPIClient(cookies=cookies)

    def _build_deep_link(self, request: RideRequest, category_id: str = None) -> str:
        """Generate Ola deep link for the ride."""
        base_url = "https://book.olacabs.com/"
        params = {
            'serviceType': 'p2p',
            'drop_lat': request.dropoff.lat,
            'drop_lng': request.dropoff.lng,
            'drop_name': request.dropoff.address,
            'lat': request.pickup.lat,
            'lng': request.pickup.lng,
            'pickup_name': request.pickup.address,
        }
        if category_id:
            params['category'] = category_id
        
        return base_url + '?' + urlencode(params)

    def _classify_vehicle_type(self, category_id: str) -> str:
        """
        Determine vehicle type from Ola category ID.
        Returns: 'auto', 'bike', or 'car'
        """
        category_lower = category_id.lower()
        
        # Auto rickshaw detection
        if category_lower == 'auto':
            return 'auto'
        
        # Bike/motorcycle detection
        if category_lower == 'bike':
            return 'bike'
        
        # Everything else is a car (mini, prime, suv, lux, etc.)
        return 'car'

    def fetch_quotes(self, request: RideRequest) -> List[RideResult]:
        """Fetch real-time ride quotes from Ola API."""
        if not self.client:
            return []
        
        try:
            # Call Ola API
            response = self.client.get_ride_prices(
                pickup_lat=request.pickup.lat,
                pickup_lng=request.pickup.lng,
                dropoff_lat=request.dropoff.lat,
                dropoff_lng=request.dropoff.lng
            )
            
            # Parse response
            rides_data = self.client.parse_ride_options(response)
            
            # Convert to RideResult objects
            results: List[RideResult] = []
            for ride in rides_data:
                # Classify vehicle type
                category_id = ride.get('category_id', '')
                vehicle_type = self._classify_vehicle_type(category_id)
                vehicle_capacity = ride['capacity']
                
                # Apply vehicle type filter if requested
                if request.vehicle_type:
                    requested_type = request.vehicle_type.lower()
                    if vehicle_type != requested_type:
                        continue  # Skip rides that don't match vehicle type
                
                # Apply seater capacity filter if requested
                if request.seater_capacity:
                    if vehicle_capacity != request.seater_capacity:
                        continue  # Skip rides that don't match capacity
                
                # Build result
                result = RideResult(
                    provider=self.provider_id,
                    service_type=ride['name'],
                    price=Price(
                        value=ride['price'],
                        currency=ride['currency'],
                        confidence=0.95  # High confidence for real API data
                    ),
                    eta=Eta(
                        seconds=ride['eta_seconds'],
                        text=ride['eta']
                    ),
                    distance=ride['distance_meters'],
                    deep_link=self._build_deep_link(request, ride.get('category_id')),
                    surge=ride['surge_multiplier'] if ride['has_surge'] else None,
                    meta=cabsync(
                        vehicle_capacity=vehicle_capacity,
                        rating=None,
                        co2_estimate=None
                    )
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error fetching Ola quotes: {e}")
            return []

