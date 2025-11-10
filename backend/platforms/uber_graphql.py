"""
Uber GraphQL API integration for fetching ride prices.
Uses the mobile GraphQL endpoint with session cookies.
"""
import requests
import json
from typing import Dict, List, Optional, Any


class UberGraphQLClient:
    """Client for Uber's GraphQL API to fetch ride prices."""
    
    BASE_URL = "https://m.uber.com/go/graphql"
    
    # GraphQL query for fetching products/prices
    PRODUCTS_QUERY = """query Products($capacity: Int, $destinations: [InputCoordinate!]!, $includeRecommended: Boolean = false, $isRiderCurrentUser: Boolean, $payment: InputPayment, $paymentProfileUUID: String, $pickup: InputCoordinate!, $pickupFormattedTime: String, $profileType: String, $profileUUID: String, $returnByFormattedTime: String, $stuntID: String, $targetProductType: EnumRVWebCommonTargetProductType) {
  products(
    capacity: $capacity
    destinations: $destinations
    includeRecommended: $includeRecommended
    isRiderCurrentUser: $isRiderCurrentUser
    payment: $payment
    paymentProfileUUID: $paymentProfileUUID
    pickup: $pickup
    pickupFormattedTime: $pickupFormattedTime
    profileType: $profileType
    profileUUID: $profileUUID
    returnByFormattedTime: $returnByFormattedTime
    stuntID: $stuntID
    targetProductType: $targetProductType
  ) {
    ...ProductsFragment
    __typename
  }
}

fragment ProductsFragment on RVWebCommonProductsResponse {
  defaultVVID
  hourlyTiersWithMinimumFare {
    ...HourlyTierFragment
    __typename
  }
  intercity {
    ...IntercityFragment
    __typename
  }
  links {
    iFrame
    text
    url
    __typename
  }
  productsUnavailableMessage
  tiers {
    ...TierFragment
    __typename
  }
  __typename
}

fragment BadgesFragment on RVWebCommonProductBadge {
  backgroundColor
  color
  contentColor
  icon
  inactiveBackgroundColor
  inactiveContentColor
  text
  __typename
}

fragment HourlyTierFragment on RVWebCommonHourlyTier {
  description
  distance
  fare
  fareAmountE5
  farePerHour
  minutes
  packageVariantUUID
  preAdjustmentValue
  __typename
}

fragment IntercityFragment on RVWebCommonIntercityInfo {
  oneWayIntercityConfig(destinations: $destinations, pickup: $pickup) {
    ...IntercityConfigFragment
    __typename
  }
  roundTripIntercityConfig(destinations: $destinations, pickup: $pickup) {
    ...IntercityConfigFragment
    __typename
  }
  __typename
}

fragment IntercityConfigFragment on RVWebCommonIntercityConfig {
  description
  onDemandAllowed
  reservePickup {
    ...IntercityTimePickerFragment
    __typename
  }
  returnBy {
    ...IntercityTimePickerFragment
    __typename
  }
  __typename
}

fragment IntercityTimePickerFragment on RVWebCommonIntercityTimePicker {
  bookingRange {
    maximum
    minimum
    __typename
  }
  header {
    subTitle
    title
    __typename
  }
  __typename
}

fragment TierFragment on RVWebCommonProductTier {
  products {
    ...ProductFragment
    __typename
  }
  title
  __typename
}

fragment ProductFragment on RVWebCommonProduct {
  badges {
    ...BadgesFragment
    __typename
  }
  cityID
  currencyCode
  description
  detailedDescription
  discountPrimary
  displayName
  estimatedTripTime
  etaStringShort
  fares {
    capacity
    discountPrimary
    fare
    fareAmountE5
    hasPromo
    hasRidePass
    meta
    preAdjustmentValue
    __typename
  }
  hasPromo
  hasRidePass
  hasBenefitsOnFare
  hourly {
    tiers {
      ...HourlyTierFragment
      __typename
    }
    overageRates {
      ...HourlyOverageRatesFragment
      __typename
    }
    __typename
  }
  iconType
  id
  is3p
  isAvailable
  legalConsent {
    ...ProductLegalConsentFragment
    __typename
  }
  parentProductUuid
  preAdjustmentValue
  productImageUrl
  productUuid
  reserveEnabled
  __typename
}

fragment ProductLegalConsentFragment on RVWebCommonProductLegalConsent {
  header
  image {
    url
    width
    __typename
  }
  description
  enabled
  ctaUrl
  ctaDisplayString
  buttonLabel
  showOnce
  shouldBlockRequest
  __typename
}

fragment HourlyOverageRatesFragment on RVWebCommonHourlyOverageRates {
  perDistanceUnit
  perTemporalUnit
  __typename
}
"""
    
    def __init__(self, cookies: Dict[str, str], city_id: str = "342"):
        """
        Initialize the Uber GraphQL client.
        
        Args:
            cookies: Dictionary of cookie name-value pairs from an authenticated session
            city_id: Uber city ID (default: 342 for Pune)
        """
        self.cookies = cookies
        self.city_id = city_id
        
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
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'content-type': 'application/json',
            'x-uber-rv-session-type': 'desktop_session',
            'x-uber-rv-initial-load-city-id': self.city_id,
            'x-csrf-token': 'x',
            'Origin': 'https://m.uber.com',
        }
        
        variables = {
            "includeRecommended": False,
            "destinations": [
                {
                    "latitude": dropoff_lat,
                    "longitude": dropoff_lng
                }
            ],
            "payment": {},
            "pickup": {
                "latitude": pickup_lat,
                "longitude": pickup_lng
            }
        }
        
        payload = {
            "operationName": "Products",
            "variables": variables,
            "query": self.PRODUCTS_QUERY
        }
        
        response = requests.post(
            self.BASE_URL,
            headers=headers,
            cookies=self.cookies,
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def parse_ride_options(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse the GraphQL response into simplified ride options.
        
        Args:
            response_data: Raw response from get_ride_prices()
            
        Returns:
            List of ride options with name, price, ETA, etc.
        """
        rides = []
        
        try:
            products_data = response_data.get('data', {}).get('products', {})
            tiers = products_data.get('tiers', [])
            
            for tier in tiers:
                tier_title = tier.get('title', '')
                products = tier.get('products', [])
                
                for product in products:
                    if not product.get('isAvailable', False):
                        continue
                    
                    fares = product.get('fares', [])
                    if not fares:
                        continue
                    
                    fare_info = fares[0]  # First fare option
                    
                    # Get service name and add Uber prefix if not present
                    display_name = product.get('displayName', 'Unknown')
                    name = display_name if display_name.startswith('Uber') else f'Uber {display_name}'
                    
                    ride = {
                        'name': name,
                        'description': product.get('detailedDescription', product.get('description', '')),
                        'price': fare_info.get('fare', 'N/A'),
                        'currency': product.get('currencyCode', 'INR'),
                        'eta': product.get('etaStringShort', 'N/A'),
                        'estimated_trip_time_seconds': product.get('estimatedTripTime', 0),
                        'capacity': fare_info.get('capacity', 0),
                        'tier': tier_title,
                        'has_promo': fare_info.get('hasPromo', False),
                        'discount': product.get('discountPrimary', ''),
                        'pre_discount_price': fare_info.get('preAdjustmentValue', ''),
                    }
                    
                    rides.append(ride)
        except (KeyError, TypeError, IndexError) as e:
            print(f"Error parsing ride options: {e}")
            
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
    """Example usage of the Uber GraphQL client."""
    # Example cookie string - replace with your actual cookies
    cookie_string = """
    marketing_vistor_id=d5b554a7-81a6-4850-baf1-3f67dc040f1b; 
    sid=QA.CAESEGczVWP2r0U8j_mJbtTtqXoYjq7jyQYiATEqJDVkYTVmNzMxLTA1ZmMtNGY0MS04OTEzLWY5YjhhNzQ3Yjg3MjI8ULL_Domb5sJAHrtrMrEiaoJKTEMl01d3Ptui0sl3pIG1HgG1uRuFDWCaZRw-dSJWRIb9NmlfJGueWUh7OgExQgh1YmVyLmNvbQ.kOz2HTA0GX6vVqnm7dyRw0MZLkBpFgGSJKf9J7qolvg;
    csid=1.1765333891607.M/I5c/LAsR0hAw0C2nUgPKzS5bb/7VVuAcIn9Z9xUnI=;
    jwt-session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7InNsYXRlLWV4cGlyZXMtYXQiOjE3NjI3NDM2OTIxMTQsIlVzZXItQWdlbnQiOiIiLCJ4LXViZXItY2xpZW50LWlkIjoiIiwieC11YmVyLWRldmljZSI6IiIsIngtdWJlci1jbGllbnQtdXNlci1zZXNzaW9uLWlkIjoiIiwidGVuYW5jeSI6InViZXIvcHJvZHVjdGlvbiJ9LCJpYXQiOjE3NjI2NjkyOTMsImV4cCI6MTc2Mjc1NTY5M30.VWZDdjXB-fJBDQfRhsqaxVYzPJ9drdY6FDS2YXJbPG8
    """
    
    # Parse cookies
    cookies = UberGraphQLClient.cookies_from_string(cookie_string)
    
    # Create client
    client = UberGraphQLClient(cookies=cookies, city_id="342")
    
    # Example: Get prices from Loni Kalbhor to Pune Railway Station
    pickup_lat = 18.488900
    pickup_lng = 74.025588
    dropoff_lat = 18.502726
    dropoff_lng = 73.950883

    
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
        print(f"Uber Ride Options from ({pickup_lat}, {pickup_lng}) to ({dropoff_lat}, {dropoff_lng})")
        print(f"{'='*60}\n")
        
        for ride in rides:
            print(f"{ride['name']:15} | {ride['price']:10} | ETA: {ride['eta']:8} | {ride['description']}")
            if ride['discount']:
                print(f"                  💰 {ride['discount']} off (was {ride['pre_discount_price']})")
            print()
            
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print("Make sure your cookies are valid and not expired.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
