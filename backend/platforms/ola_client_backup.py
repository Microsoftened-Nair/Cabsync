"""
Ola API integration for fetching ride prices.
Uses the category-fare endpoint from book.olacabs.com.
"""
import os
import requests
from typing import Dict, List, Optional, Any


class OlaAPIClient:
    """Client for Ola's category-fare API to fetch ride prices."""
    
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
        dropoff_lng: float
    ) -> Dict[str, Any]:
        """
        Get ride prices from pickup to dropoff location.
        
        Args:
            pickup_lat: Pickup latitude
            pickup_lng: Pickup longitude
            dropoff_lat: Dropoff latitude
            dropoff_lng: Dropoff longitude
            
        Returns:
            Dictionary containing ride options with prices and ETAs
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.5',
            'content-type': 'application/json',
            'x-requested-with': 'XMLHttpRequest',
            'Referer': 'https://book.olacabs.com/',
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
        
        try:
            response = requests.get(
                self.BASE_URL,
                headers=headers,
                params=params,
                cookies=self.cookies,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Ola prices: {e}")
            return {}
    
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
            # Check for error responses
            if response_data.get('status') == 'FAILURE':
                return rides
            
            # Get categories from response
            categories = response_data.get('categories', [])
            
            for category in categories:
                # Skip unavailable categories
                if not category.get('available', False):
                    continue
                
                # Extract basic info
                display_name = category.get('display_name', 'Unknown')
                category_id = category.get('id', '')
                
                # Extract pricing info
                fare_breakup = category.get('fare_breakup', {})
                total_fare = fare_breakup.get('total_fare', 0)
                currency = fare_breakup.get('currency_symbol', '₹')
                
                # Extract ETA info
                eta = category.get('eta', {})
                eta_text = eta.get('short_text', 'N/A')
                eta_seconds = eta.get('value', 0)
                
                # Extract capacity
                capacity = category.get('capacity', 0)
                
                # Extract distance
                distance_km = category.get('distance', 0)
                distance_meters = int(distance_km * 1000) if distance_km else 0
                
                # Extract additional info
                description = category.get('description', '')
                
                # Check for surge pricing
                surge_info = category.get('surge', {})
                has_surge = surge_info.get('is_surge', False)
                surge_multiplier = surge_info.get('multiplier', 1.0) if has_surge else None
                
                ride = {
                    'name': display_name,
                    'category_id': category_id,
                    'description': description,
                    'price': total_fare,
                    'currency': currency,
                    'eta': eta_text,
                    'eta_seconds': eta_seconds,
                    'capacity': capacity,
                    'distance_meters': distance_meters,
                    'has_surge': has_surge,
                    'surge_multiplier': surge_multiplier,
                    'fare_breakup': fare_breakup,
                }
                
                rides.append(ride)
        except (KeyError, TypeError, ValueError) as e:
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
    # Try to load cookies from environment or file
    cookie_string = os.environ.get('OLA_COOKIES', '')
    
    if not cookie_string:
        cookie_file = os.path.join(os.path.dirname(__file__), '..', 'ola_cookies.txt')
        try:
            with open(cookie_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        cookie_string = line
                        break
        except FileNotFoundError:
            pass
    
    cookies = {}
    if cookie_string and 'REPLACE_ME' not in cookie_string:
        cookies = OlaAPIClient.cookies_from_string(cookie_string)
    
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
        
        print(f"\n{'='*60}")
        print(f"Ola Ride Options from ({pickup_lat}, {pickup_lng}) to ({dropoff_lat}, {dropoff_lng})")
        print(f"{'='*60}\n")
        
        if not rides:
            print("No rides available.")
            if not cookies:
                print("\nNote: Cookies not configured. Set OLA_COOKIES env var or create ola_cookies.txt")
        else:
            for ride in rides:
                surge_text = f" (SURGE {ride['surge_multiplier']}x)" if ride['has_surge'] else ""
                print(f"{ride['name']:15} | {ride['currency']}{ride['price']:7.2f}{surge_text}")
                print(f"                  ETA: {ride['eta']} | Capacity: {ride['capacity']} | {ride['description']}")
                print()
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

    
    def get_ride_prices(
        self,
        pickup_lat: float,
        pickup_lng: float,
        dropoff_lat: float,
        dropoff_lng: float
    ) -> Dict[str, Any]:
        """
        Get ride prices from pickup to dropoff location.
        
        Args:
            pickup_lat: Pickup latitude
            pickup_lng: Pickup longitude
            dropoff_lat: Dropoff latitude
            dropoff_lng: Dropoff longitude
            
        Returns:
            Dictionary containing ride options with prices and ETAs
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.5',
            'content-type': 'application/json',
            'x-requested-with': 'XMLHttpRequest',
            'Referer': 'https://book.olacabs.com/',
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
        
        try:
            response = requests.get(
                self.BASE_URL,
                headers=headers,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Ola prices: {e}")
            return {}
    
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
            # Check for error responses
            if response_data.get('status') == 'FAILURE':
                return rides
            
            # Get categories from response
            categories = response_data.get('categories', [])
            
            for category in categories:
                # Skip unavailable categories
                if not category.get('available', False):
                    continue
                
                # Extract basic info
                display_name = category.get('display_name', 'Unknown')
                category_id = category.get('id', '')
                
                # Extract pricing info
                fare_breakup = category.get('fare_breakup', {})
                total_fare = fare_breakup.get('total_fare', 0)
                currency = fare_breakup.get('currency_symbol', '₹')
                
                # Extract ETA info
                eta = category.get('eta', {})
                eta_text = eta.get('short_text', 'N/A')
                eta_seconds = eta.get('value', 0)
                
                # Extract capacity
                capacity = category.get('capacity', 0)
                
                # Extract distance
                distance_km = category.get('distance', 0)
                distance_meters = int(distance_km * 1000) if distance_km else 0
                
                # Extract additional info
                description = category.get('description', '')
                
                # Check for surge pricing
                surge_info = category.get('surge', {})
                has_surge = surge_info.get('is_surge', False)
                surge_multiplier = surge_info.get('multiplier', 1.0) if has_surge else None
                
                ride = {
                    'name': display_name,
                    'category_id': category_id,
                    'description': description,
                    'price': total_fare,
                    'currency': currency,
                    'eta': eta_text,
                    'eta_seconds': eta_seconds,
                    'capacity': capacity,
                    'distance_meters': distance_meters,
                    'has_surge': has_surge,
                    'surge_multiplier': surge_multiplier,
                    'fare_breakup': fare_breakup,
                }
                
                rides.append(ride)
        except (KeyError, TypeError, ValueError) as e:
            print(f"Error parsing Ola ride options: {e}")
            
        return rides


def main():
    """Example usage of the Ola API client."""
    client = OlaAPIClient()
    
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
        
        print(f"\n{'='*60}")
        print(f"Ola Ride Options from ({pickup_lat}, {pickup_lng}) to ({dropoff_lat}, {dropoff_lng})")
        print(f"{'='*60}\n")
        
        if not rides:
            print("No rides available or service not operational in this area.")
        else:
            for ride in rides:
                surge_text = f" (SURGE {ride['surge_multiplier']}x)" if ride['has_surge'] else ""
                print(f"{ride['name']:15} | {ride['currency']}{ride['price']:7.2f}{surge_text}")
                print(f"                  ETA: {ride['eta']} | Capacity: {ride['capacity']} | {ride['description']}")
                print()
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
