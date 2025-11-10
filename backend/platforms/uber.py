"""Uber provider using GraphQL API."""
from __future__ import annotations

import os
import re
from typing import List, Optional

from models.ride import Eta, Price, RideRequest, RideResult, cabsync
from platforms.uber_graphql import UberGraphQLClient


class UberProvider:
    provider_id = "uber"
    provider_name = "Uber"

    def __init__(self):
        """Initialize Uber provider with GraphQL client."""
        self.client: Optional[UberGraphQLClient] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the GraphQL client with cookies from environment."""
        # Try to load cookies from environment variable
        cookie_string = os.environ.get('UBER_COOKIES', '')
        
        if not cookie_string:
            # Try to load from file
            cookie_file = os.path.join(
                os.path.dirname(__file__), 
                '..', 
                'uber_cookies.txt'
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
        if cookie_string and 'REPLACE_ME' not in cookie_string:
            cookies = UberGraphQLClient.cookies_from_string(cookie_string)
            self.client = UberGraphQLClient(
                cookies=cookies,
                city_id=os.environ.get('UBER_CITY_ID', '342')  # Default: Pune
            )

    def _parse_price(self, price_str: str) -> float:
        """Extract numeric value from price string like '₹301.06'."""
        if not price_str:
            return 0.0
        # Remove currency symbols and commas, extract number
        match = re.search(r'[\d,]+\.?\d*', price_str.replace(',', ''))
        if match:
            return float(match.group())
        return 0.0
    
    def _parse_eta_seconds(self, eta_str: str) -> int:
        """Convert ETA string like '2 mins' to seconds."""
        if not eta_str:
            return 0
        match = re.search(r'(\d+)', eta_str)
        if match:
            minutes = int(match.group(1))
            return minutes * 60
        return 0

    def _classify_vehicle_type(self, service_name: str) -> str:
        """
        Determine vehicle type from Uber service name.
        Returns: 'auto', 'bike', or 'car'
        """
        service_lower = service_name.lower()
        
        # Auto rickshaw detection
        if 'auto' in service_lower:
            return 'auto'
        
        # Bike/motorcycle detection
        if 'bike' in service_lower or 'moto' in service_lower:
            return 'bike'
        
        # Everything else is a car (Go, Premier, XL, etc.)
        return 'car'
    
    def _get_vehicle_capacity(self, service_name: str, api_capacity: int) -> int:
        """
        Determine vehicle capacity from service name and API data.
        """
        # If API provides capacity, use it
        if api_capacity and api_capacity > 0:
            return api_capacity
        
        # Otherwise infer from service name
        service_lower = service_name.lower()
        
        # Auto rickshaws typically seat 3
        if 'auto' in service_lower:
            return 3
        
        # Bikes seat 1 passenger
        if 'bike' in service_lower or 'moto' in service_lower:
            return 1
        
        # XL/SUV vehicles typically seat 6
        if 'xl' in service_lower or 'suv' in service_lower:
            return 6
        
        # Standard cars seat 4
        return 4

    def _build_deep_link(
        self, 
        request: RideRequest,
        product_id: Optional[str] = None
    ) -> str:
        """Generate Uber deep link for the ride."""
        base_url = "https://m.uber.com/ul/"
        params = [
            f"?action=setPickup",
            f"&pickup[latitude]={request.pickup.lat}",
            f"&pickup[longitude]={request.pickup.lng}",
            f"&dropoff[latitude]={request.dropoff.lat}",
            f"&dropoff[longitude]={request.dropoff.lng}",
        ]
        if product_id:
            params.append(f"&product_id={product_id}")
        
        return base_url + "".join(params)

    def fetch_quotes(self, request: RideRequest) -> List[RideResult]:
        """Fetch real-time ride quotes from Uber GraphQL API."""
        if not self.client:
            # Return empty list if client not initialized (no cookies available)
            return []
        
        try:
            # Call GraphQL API
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
                # Parse price
                price_value = self._parse_price(ride['price'])
                if price_value == 0.0:
                    continue  # Skip rides with invalid prices
                
                # Classify vehicle type and capacity
                service_name = ride['name']
                vehicle_type = self._classify_vehicle_type(service_name)
                api_capacity = ride.get('capacity', 0)
                vehicle_capacity = self._get_vehicle_capacity(service_name, api_capacity)
                
                # Apply vehicle type filter if requested
                if request.vehicle_type:
                    requested_type = request.vehicle_type.lower()
                    if vehicle_type != requested_type:
                        continue  # Skip rides that don't match vehicle type
                
                # Apply seater capacity filter if requested
                if request.seater_capacity:
                    if vehicle_capacity != request.seater_capacity:
                        continue  # Skip rides that don't match capacity
                
                # Parse ETA
                eta_seconds = self._parse_eta_seconds(ride['eta'])
                if eta_seconds == 0:
                    eta_seconds = ride.get('estimated_trip_time_seconds', 600)
                
                # Calculate distance (if available from metadata)
                distance_meters = 0
                try:
                    meta_str = ride.get('meta', {})
                    if isinstance(meta_str, str):
                        import json
                        meta_dict = json.loads(meta_str)
                        # Try to extract distance from upfrontFare
                        upfront = meta_dict.get('upfrontFare', {})
                        unmodified_distance = upfront.get('unmodifiedDistance', 0)
                        if unmodified_distance:
                            distance_meters = unmodified_distance
                except:
                    pass
                
                # Build result
                result = RideResult(
                    provider=self.provider_id,
                    service_type=service_name,
                    price=Price(
                        value=price_value,
                        currency="₹",
                        confidence=0.95  # High confidence for real API data
                    ),
                    eta=Eta(
                        seconds=eta_seconds,
                        text=ride['eta']
                    ),
                    distance=distance_meters,
                    deep_link=self._build_deep_link(request),
                    surge=None,  # Could extract from dynamicFareInfo if needed
                    meta=cabsync(
                        vehicle_capacity=vehicle_capacity,
                        rating=None,  # Not provided in this API response
                        co2_estimate=None
                    )
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error fetching Uber quotes: {e}")
            return []
