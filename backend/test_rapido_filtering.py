"""Test script for Rapido filtering logic."""
import sys
from models.ride import RideRequest, Location
from platforms.rapido import RapidoProvider


def test_no_filter():
    """Test without any filters - should return all rides."""
    print("=" * 70)
    print("Test 1: No Filters (should return all 5 ride types)")
    print("=" * 70)
    
    pickup = Location(lat=18.4878505, lng=74.0234138, address="Loni Kalbhor")
    dropoff = Location(lat=18.5288974, lng=73.8665321, address="Pune Railway Station")
    request = RideRequest(pickup=pickup, dropoff=dropoff)
    
    provider = RapidoProvider()
    results = provider.fetch_quotes(request)
    
    print(f"✅ Returned {len(results)} results")
    for r in results:
        print(f"  - {r.service_type} ({r.meta.vehicle_capacity} seats)")
    print()
    return len(results) == 5


def test_filter_bike():
    """Test filtering for bikes only."""
    print("=" * 70)
    print("Test 2: Filter vehicle_type='bike' (should return 1 result)")
    print("=" * 70)
    
    pickup = Location(lat=18.4878505, lng=74.0234138, address="Loni Kalbhor")
    dropoff = Location(lat=18.5288974, lng=73.8665321, address="Pune Railway Station")
    request = RideRequest(pickup=pickup, dropoff=dropoff, vehicle_type="bike")
    
    provider = RapidoProvider()
    results = provider.fetch_quotes(request)
    
    print(f"✅ Returned {len(results)} results")
    for r in results:
        print(f"  - {r.service_type} ({r.meta.vehicle_capacity} seats)")
    
    # Verify all are bikes
    all_bikes = all('bike' in r.service_type.lower() for r in results)
    print(f"All results are bikes: {all_bikes}")
    print()
    return len(results) == 1 and all_bikes


def test_filter_auto():
    """Test filtering for autos only."""
    print("=" * 70)
    print("Test 3: Filter vehicle_type='auto' (should return 1 result)")
    print("=" * 70)
    
    pickup = Location(lat=18.4878505, lng=74.0234138, address="Loni Kalbhor")
    dropoff = Location(lat=18.5288974, lng=73.8665321, address="Pune Railway Station")
    request = RideRequest(pickup=pickup, dropoff=dropoff, vehicle_type="auto")
    
    provider = RapidoProvider()
    results = provider.fetch_quotes(request)
    
    print(f"✅ Returned {len(results)} results")
    for r in results:
        print(f"  - {r.service_type} ({r.meta.vehicle_capacity} seats)")
    
    # Verify all are autos
    all_autos = all('auto' in r.service_type.lower() for r in results)
    print(f"All results are autos: {all_autos}")
    print()
    return len(results) == 1 and all_autos


def test_filter_car():
    """Test filtering for cars only."""
    print("=" * 70)
    print("Test 4: Filter vehicle_type='car' (should return 3 results)")
    print("=" * 70)
    
    pickup = Location(lat=18.4878505, lng=74.0234138, address="Loni Kalbhor")
    dropoff = Location(lat=18.5288974, lng=73.8665321, address="Pune Railway Station")
    request = RideRequest(pickup=pickup, dropoff=dropoff, vehicle_type="car")
    
    provider = RapidoProvider()
    results = provider.fetch_quotes(request)
    
    print(f"✅ Returned {len(results)} results")
    for r in results:
        print(f"  - {r.service_type} ({r.meta.vehicle_capacity} seats)")
    
    # Verify all are cars (Cab, Cab Economy, or Premium)
    all_cars = all(r.meta.vehicle_capacity == 4 for r in results)
    print(f"All results have 4 seats (cars): {all_cars}")
    print()
    return len(results) == 3 and all_cars


def test_filter_capacity_1():
    """Test filtering for 1 seater (bike)."""
    print("=" * 70)
    print("Test 5: Filter seater_capacity=1 (should return 1 result)")
    print("=" * 70)
    
    pickup = Location(lat=18.4878505, lng=74.0234138, address="Loni Kalbhor")
    dropoff = Location(lat=18.5288974, lng=73.8665321, address="Pune Railway Station")
    request = RideRequest(pickup=pickup, dropoff=dropoff, seater_capacity=1)
    
    provider = RapidoProvider()
    results = provider.fetch_quotes(request)
    
    print(f"✅ Returned {len(results)} results")
    for r in results:
        print(f"  - {r.service_type} ({r.meta.vehicle_capacity} seats)")
    
    # Verify all have 1 seat
    all_correct = all(r.meta.vehicle_capacity == 1 for r in results)
    print(f"All results have 1 seat: {all_correct}")
    print()
    return len(results) == 1 and all_correct


def test_filter_capacity_3():
    """Test filtering for 3 seater (auto)."""
    print("=" * 70)
    print("Test 6: Filter seater_capacity=3 (should return 1 result)")
    print("=" * 70)
    
    pickup = Location(lat=18.4878505, lng=74.0234138, address="Loni Kalbhor")
    dropoff = Location(lat=18.5288974, lng=73.8665321, address="Pune Railway Station")
    request = RideRequest(pickup=pickup, dropoff=dropoff, seater_capacity=3)
    
    provider = RapidoProvider()
    results = provider.fetch_quotes(request)
    
    print(f"✅ Returned {len(results)} results")
    for r in results:
        print(f"  - {r.service_type} ({r.meta.vehicle_capacity} seats)")
    
    # Verify all have 3 seats
    all_correct = all(r.meta.vehicle_capacity == 3 for r in results)
    print(f"All results have 3 seats: {all_correct}")
    print()
    return len(results) == 1 and all_correct


def test_filter_capacity_4():
    """Test filtering for 4 seater (cars)."""
    print("=" * 70)
    print("Test 7: Filter seater_capacity=4 (should return 3 results)")
    print("=" * 70)
    
    pickup = Location(lat=18.4878505, lng=74.0234138, address="Loni Kalbhor")
    dropoff = Location(lat=18.5288974, lng=73.8665321, address="Pune Railway Station")
    request = RideRequest(pickup=pickup, dropoff=dropoff, seater_capacity=4)
    
    provider = RapidoProvider()
    results = provider.fetch_quotes(request)
    
    print(f"✅ Returned {len(results)} results")
    for r in results:
        print(f"  - {r.service_type} ({r.meta.vehicle_capacity} seats)")
    
    # Verify all have 4 seats
    all_correct = all(r.meta.vehicle_capacity == 4 for r in results)
    print(f"All results have 4 seats: {all_correct}")
    print()
    return len(results) == 3 and all_correct


def main():
    """Run all filtering tests."""
    print("\n" + "=" * 70)
    print("Rapido Filtering Logic Tests")
    print("=" * 70 + "\n")
    
    tests = [
        ("No Filter", test_no_filter),
        ("Filter Bike", test_filter_bike),
        ("Filter Auto", test_filter_auto),
        ("Filter Car", test_filter_car),
        ("Filter Capacity 1", test_filter_capacity_1),
        ("Filter Capacity 3", test_filter_capacity_3),
        ("Filter Capacity 4", test_filter_capacity_4),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"❌ {name} failed with error: {e}\n")
            results.append((name, False))
    
    # Summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(passed for _, passed in results)
    print("=" * 70)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
