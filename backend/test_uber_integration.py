"""Test script for Uber GraphQL integration."""
from platforms.uber import UberProvider
from models.ride import RideRequest, Location

# Create test locations
pickup = Location(
    lat=18.488900,
    lng=74.025588,
    address="Loni Kalbhor, Maharashtra"
)

dropoff = Location(
    lat=18.502726,
    lng=73.950883,
    address="Pune Railway Station"
)

# Create ride request
request = RideRequest(pickup=pickup, dropoff=dropoff)

# Initialize provider and fetch quotes
provider = UberProvider()
quotes = provider.fetch_quotes(request)

# Display results
print(f"\n{'='*70}")
print(f"Uber Quotes: {pickup.address} -> {dropoff.address}")
print(f"{'='*70}\n")

if not quotes:
    print("❌ No quotes returned!")
    print("\nPossible reasons:")
    print("1. Cookies not configured (check backend/uber_cookies.txt)")
    print("2. Cookies expired (get fresh cookies from browser)")
    print("3. Network error or API unavailable")
    print("\nSee UBER_SETUP.md for configuration instructions.")
else:
    print(f"✅ Found {len(quotes)} ride options:\n")
    for quote in quotes:
        print(f"  {quote.service_type:15} | {quote.price.currency}{quote.price.value:7.2f} | ETA: {quote.eta.text}")
        if quote.meta and quote.meta.vehicle_capacity:
            print(f"                    Capacity: {quote.meta.vehicle_capacity} passengers")
        print()
