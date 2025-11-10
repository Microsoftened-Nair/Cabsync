"""
Ola API integration for fetching ride prices.
Uses the book.olacabs.com data API endpoint.
"""
import requests
from typing import Dict, List, Optional, Any


class OlaAPIClient:
    """Client for Ola's data API to fetch ride prices."""
    
    BASE_URL = "https://book.olacabs.com/data-api/category-fare/p2p"
    
    def __init__(self, cookies: Optional[Dict[str, str]] = None):
        """
        Initialize the Ola API client.
        
        Args:
            cookies: Optional dictionary of cookie name-value pairs
        """
        self.cookies = cookies or {}
    
    def get_ride_prices(
        self,
        pickup_lat: float,
        pickup_lng: float,
        dropoff_lat: float,
        dropoff_lng: float,
        pickup_zone_id: Optional[str] = None,
        pickup_point_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get ride prices from pickup to dropoff location.
        
        Args:
            pickup_lat: Pickup latitude
            pickup_lng: Pickup longitude
            dropoff_lat: Dropoff latitude
            dropoff_lng: Dropoff longitude
            pickup_zone_id: Optional Ola zone ID for pickup
            pickup_point_id: Optional Ola pickup point ID
            
        Returns:
            Dictionary containing ride options with prices
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.5',
            'content-type': 'application/json',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        params = {
            'pickupLat': pickup_lat,
            'pickupLng': pickup_lng,
            'pickupMode': 'NOW',
            'leadSource': 'desktop_website',
            'dropLat': dropoff_lat,
            'dropLng': dropoff_lng,
            'silent': 'true',
        }
        
        # Add optional parameters if provided
        if pickup_zone_id:
            params['pickupZoneId'] = pickup_zone_id
        if pickup_point_id:
            params['defaultPickupPointId'] = pickup_point_id
        
        response = requests.get(
            self.BASE_URL,
            headers=headers,
            params=params,
            cookies=self.cookies
        )
        
        response.raise_for_status()
        return response.json()
    
    def parse_ride_options(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse the API response into simplified ride options.
        
        Args:
            response_data: Raw response from get_ride_prices()
            
        Returns:
            List of ride options with name, price, ETA, etc.
        """
        rides = []
        
        try:
            categories = response_data.get('categories', [])
            
            for category in categories:
                if not category.get('available', True):
                    continue
                
                ride = {
                    'id': category.get('id', ''),
                    'name': category.get('display_name', 'Unknown'),
                    'category_type': category.get('category_type', ''),
                    'price': category.get('fare', {}).get('total_fare', 0),
                    'currency': 'INR',
                    'eta': category.get('eta', 0),  # in minutes
                    'eta_text': f"{category.get('eta', 0)} mins",
                    'min_fare': category.get('fare', {}).get('minimum_fare', 0),
                    'capacity': category.get('capacity', 0),
                    'available': category.get('available', True),
                    'surge': category.get('is_surge', False),
                    'surge_factor': category.get('surge_factor', 1.0),
                    'fare_breakdown': {
                        'base_fare': category.get('fare', {}).get('base_fare', 0),
                        'ride_fare': category.get('fare', {}).get('ride_fare', 0),
                        'service_charge': category.get('fare', {}).get('service_charge', 0),
                        'total_fare': category.get('fare', {}).get('total_fare', 0),
                    },
                    'vehicle_image': category.get('vehicle_image', ''),
                    'display_text': category.get('display_text', ''),
                }
                
                rides.append(ride)
        except (KeyError, TypeError, IndexError) as e:
            print(f"Error parsing Ola ride options: {e}")
            
        return rides
    
    @staticmethod
    def cookies_from_string(cookie_string: str) -> Dict[str, str]:
        """
        Convert cookie string (from browser) to dictionary.
        
        Args:
            cookie_string: Cookie header string (e.g., "key1=value1; key2=value2")
            
        Returns:
            Dictionary of cookie name-value pairs
        """
        cookies = {}
        for cookie in cookie_string.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies[key] = value
        return cookies


def main():
    """Example usage of the Ola API client."""
    # Example cookie string - Ola API works without cookies too!
    cookie_string = """
    OSRN_v1=o3P15tX3wfqgXFY5F4oOOyZl; 
    _csrf=UYnV4DGzSHHTV1NU02s2UXIf; 
    XSRF-TOKEN=TEOSRwln-2lRzt3ecqOJ_TAQ2-RbZjOi-zOA
    """
    
    # Parse cookies (optional for Ola)
    cookies = OlaAPIClient.cookies_from_string(cookie_string)
    
    # Create client (can work without cookies)
    client = OlaAPIClient(cookies=cookies)
    
    # Example: Get prices from Pune Railway Station to Loni Kalbhor
    pickup_lat = 18.52862
    pickup_lng = 73.87467
    dropoff_lat = 18.4866
    dropoff_lng = 74.0251
    
    try:
        # Fetch prices
        response = client.get_ride_prices(
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            dropoff_lat=dropoff_lat,
            dropoff_lng=dropoff_lng
        )
        
        # Parse and display results
        rides = client.parse_ride_options(response)
        
        print(f"\n{'='*70}")
        print(f"Ola Ride Options from ({pickup_lat}, {pickup_lng}) to ({dropoff_lat}, {dropoff_lng})")
        print(f"{'='*70}\n")
        
        if not rides:
            print("No rides available")
        else:
            for ride in rides:
                surge_marker = " 🔥 SURGE" if ride['surge'] else ""
                print(f"{ride['name']:20} | Rs {ride['price']:7.2f} | ETA: {ride['eta_text']:8}{surge_marker}")
                print(f"                       Min Fare: Rs {ride['min_fare']:.2f} | Capacity: {ride['capacity']}")
                if ride['surge']:
                    print(f"                       Surge Factor: {ride['surge_factor']:.2f}x")
                print()
            
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print("Ola API request failed")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
