"""
Ola API integration for fetching ride prices.
Uses the category-fare endpoint from book.olacabs.com.
"""
import os
import re
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
            # Check for error
            if response_data.get('error'):
                return rides
            
            # Get data from response (silent=true format)
            data = response_data.get('data', {})
            p2p = data.get('p2p', {})
            categories = p2p.get('categories', {})
            
            # Map category IDs to display names
            category_names = {
                'auto': 'Ola Auto',
                'mini': 'Ola Mini',
                'prime': 'Ola Prime Sedan',
                'suv': 'Ola Prime SUV',
                'bike': 'Ola Bike',
                'lux': 'Ola Lux'
            }
            
            # Map category to capacity
            category_capacity = {
                'auto': 3,
                'mini': 4,
                'prime': 4,
                'suv': 6,
                'bike': 1,
                'lux': 4
            }
            
            for category_id, category_data in categories.items():
                if not category_data:
                    continue
                
                # Extract price
                price_str = category_data.get('price', '₹0')
                # Remove currency symbol and parse
                price_match = re.search(r'[\d,]+\.?\d*', price_str.replace(',', ''))
                price = float(price_match.group()) if price_match else 0.0
                
                if price == 0.0:
                    continue
                
                # Get fare ID
                fare_id = category_data.get('fareId', '')
                
                # Build ride info
                ride = {
                    'name': category_names.get(category_id, category_id.title()),
                    'category_id': category_id,
                    'description': f'Ola {category_names.get(category_id, category_id.title())}',
                    'price': price,
                    'currency': '₹',
                    'eta': 'N/A',  # Not provided in silent response
                    'eta_seconds': 0,
                    'capacity': category_capacity.get(category_id, 4),
                    'distance_meters': 0,  # Not provided in silent response
                    'has_surge': False,
                    'surge_multiplier': None,
                    'fare_id': fare_id,
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
