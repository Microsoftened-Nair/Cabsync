"""Test script for Rapido real-time API integration."""
import sys
from models.ride import RideRequest, Location
from platforms.rapido import RapidoProvider


def test_rapido_integration():
    """Test Rapido provider with real-time API."""
    print("=" * 70)
    print("Rapido Real-Time API Integration Test")
    print("=" * 70)
    
    # Create a sample ride request
    pickup = Location(
        lat=18.4878505,
        lng=74.0234138,
        address="Loni Kalbhor, Maharashtra, India"
    )
    
    dropoff = Location(
        lat=18.5288974,
        lng=73.8665321,
        address="PUNE RAILWAY STATION, Pune, Maharashtra, India"
    )
    
    request = RideRequest(
        pickup=pickup,
        dropoff=dropoff,
    )
    
    print(f"\nTest Request:")
    print(f"  From: {pickup.address} ({pickup.lat}, {pickup.lng})")
    print(f"  To: {dropoff.address} ({dropoff.lat}, {dropoff.lng})")
    
    # Create provider and fetch quotes
    provider = RapidoProvider()
    
    print(f"\nUsing Real-Time API: {provider.use_real_api}")
    
    try:
        results = provider.fetch_quotes(request)
        
        print(f"\n✅ Successfully fetched {len(results)} ride options from Rapido")
        print("\n" + "-" * 70)
        print(f"{'Service Type':<25} {'Price':<15} {'ETA':<10} {'Confidence'}")
        print("-" * 70)
        
        for result in results:
            price_str = f"{result.price.currency}{result.price.value:.0f}"
            print(f"{result.service_type:<25} {price_str:<15} {result.eta.text:<10} {result.price.confidence:.2f}")
        
        print("-" * 70)
        
        # Show detailed info for first result
        if results:
            first = results[0]
            print(f"\n📋 Detailed Info for {first.service_type}:")
            print(f"  Provider: {first.provider}")
            print(f"  Price: {first.price.currency}{first.price.value:.2f}")
            print(f"  Confidence: {first.price.confidence:.2%}")
            print(f"  ETA: {first.eta.text} ({first.eta.seconds}s)")
            print(f"  Distance: {first.distance}m ({first.distance/1000:.1f} km)")
            if first.meta:
                print(f"  Vehicle Capacity: {first.meta.vehicle_capacity} passengers")
                print(f"  Rating: {first.meta.rating}/5.0")
                if first.meta.co2_estimate:
                    print(f"  CO2 Estimate: {first.meta.co2_estimate:.0f}g")
            print(f"  Deep Link: {first.deep_link}")
        
        print("\n" + "=" * 70)
        print("✅ Rapido integration test completed successfully!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing Rapido integration: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_rapido_integration()
    sys.exit(0 if success else 1)
