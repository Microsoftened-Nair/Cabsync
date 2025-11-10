"""Test script for Ola API integration."""
from platforms.ola import OlaProvider
from models.ride import RideRequest, Location

# Create test locations
pickup = Location(
    lat=18.52862,
    lng=73.87467,
    address="Pune Railway Station, Maharashtra"
)

dropoff = Location(
    lat=18.4866,
    lng=74.0251,
    address="Loni Kalbhor, Maharashtra"
)

# Create ride request
request = RideRequest(pickup=pickup, dropoff=dropoff)

# Initialize provider and fetch quotes
provider = OlaProvider()
quotes = provider.fetch_quotes(request)

# Display results
print(f"\n{'='*70}")
print(f"Ola Quotes: {pickup.address} -> {dropoff.address}")
print(f"{'='*70}\n")

if not quotes:
    print("❌ No quotes returned!")
    print("\nPossible reasons:")
    print("1. Cookies not configured (check backend/ola_cookies.txt)")
    print("2. Cookies expired (get fresh cookies from browser)")
    print("3. Service not available in this area")
    print("4. Network error or API unavailable")
    print("\nTo configure cookies:")
    print("- Go to book.olacabs.com")
    print("- Search for a ride")
    print("- F12 -> Network -> Find 'category-fare' request")
    print("- Copy as cURL and extract Cookie header")
else:
    print(f"✅ Found {len(quotes)} ride options:\n")
    for quote in quotes:
        surge_text = f" (SURGE {quote.surge}x)" if quote.surge else ""
        print(f"  {quote.service_type:15} | {quote.price.currency}{quote.price.value:7.2f}{surge_text}")
        print(f"                    ETA: {quote.eta.text}")
        if quote.meta and quote.meta.vehicle_capacity:
            print(f"                    Capacity: {quote.meta.vehicle_capacity} passengers")
        print()
