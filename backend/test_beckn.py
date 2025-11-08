#!/usr/bin/env python
"""Test script for Beckn protocol integration."""

import asyncio
import json
from datetime import datetime

from app import create_app
from fastapi.testclient import TestClient
from models.ride import transaction_store, TransactionState, RideRequest, Location


def test_beckn_callback_flow():
    """Test the complete Beckn callback flow."""
    
    print("=" * 60)
    print("Beckn Protocol Integration Test")
    print("=" * 60)
    
    # Create FastAPI test client
    app = create_app()
    client = TestClient(app)
    
    # Test 1: Callback with unknown transaction (should NACK)
    print("\n1. Testing unknown transaction (should NACK)...")
    response = client.post(
        "/api/beckn/on_search",
        json={
            "context": {"transaction_id": "unknown-123"},
            "message": {}
        }
    )
    assert response.status_code == 200
    assert response.json()["message"]["ack"]["status"] == "NACK"
    print("   ✅ Unknown transaction correctly returned NACK")
    
    # Test 2: Create a transaction and simulate callback
    print("\n2. Creating test transaction...")
    test_request = RideRequest(
        pickup=Location(lat=12.9716, lng=77.5946, address="MG Road, Bangalore"),
        dropoff=Location(lat=12.9352, lng=77.6245, address="Koramangala, Bangalore"),
        vehicle_type="auto"
    )
    
    transaction_id = "test-beckn-txn-" + datetime.now().strftime("%Y%m%d%H%M%S")
    transaction_store[transaction_id] = TransactionState(
        transaction_id=transaction_id,
        request=test_request
    )
    print(f"   ✅ Created transaction: {transaction_id}")
    
    # Test 3: Send callback with Beckn catalog response
    print("\n3. Sending Beckn on_search callback...")
    beckn_response = {
        "context": {
            "transaction_id": transaction_id,
            "action": "on_search"
        },
        "message": {
            "catalog": {
                "providers": [
                    {
                        "id": "namma-yatri-driver-1",
                        "items": [
                            {
                                "id": "auto-ride-1",
                                "descriptor": {"name": "Auto Rickshaw"},
                                "price": {"value": "145", "currency": "INR"},
                                "fulfillment": {
                                    "state": {
                                        "descriptor": {"name": "ETA 4 mins"}
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "id": "namma-yatri-driver-2",
                        "items": [
                            {
                                "id": "auto-ride-2",
                                "descriptor": {"name": "Auto Rickshaw"},
                                "price": {"value": "160", "currency": "INR"},
                                "fulfillment": {
                                    "state": {
                                        "descriptor": {"name": "ETA 7 mins"}
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        }
    }
    
    response = client.post("/api/beckn/on_search", json=beckn_response)
    assert response.status_code == 200
    assert response.json()["message"]["ack"]["status"] == "ACK"
    print("   ✅ Callback returned ACK")
    
    # Test 4: Verify transaction state updated
    print("\n4. Verifying transaction state...")
    state = transaction_store[transaction_id]
    assert state.status.value == "completed"
    assert len(state.results) == 2
    print(f"   ✅ Transaction status: {state.status.value}")
    print(f"   ✅ Results count: {len(state.results)}")
    
    # Test 5: Verify parsed results
    print("\n5. Verifying parsed results...")
    for i, result in enumerate(state.results, 1):
        print(f"   Result {i}:")
        print(f"     - Provider: {result.provider}")
        print(f"     - Service: {result.service_type}")
        print(f"     - Price: {result.price.currency}{result.price.value}")
        print(f"     - ETA: {result.eta.text}")
        print(f"     - Deep Link: {result.deep_link}")
        
        assert result.provider == "namma_yatri"
        assert result.service_type == "Auto Rickshaw"
        assert result.price.currency == "₹"
        assert result.price.value > 0
    
    print("\n" + "=" * 60)
    print("✅ All Beckn integration tests passed!")
    print("=" * 60)
    
    # Test 6: Error handling
    print("\n6. Testing error handling...")
    error_txn = "test-error-" + datetime.now().strftime("%Y%m%d%H%M%S")
    transaction_store[error_txn] = TransactionState(
        transaction_id=error_txn,
        request=test_request
    )
    
    error_response = {
        "context": {"transaction_id": error_txn},
        "message": {},
        "error": {"message": "Provider unavailable"}
    }
    
    response = client.post("/api/beckn/on_search", json=error_response)
    assert response.status_code == 200
    error_state = transaction_store[error_txn]
    assert error_state.status.value == "failed"
    assert error_state.error == "Provider unavailable"
    print("   ✅ Error handling works correctly")
    
    print("\n✅ Beckn protocol integration is fully functional!")
    print("\nNext steps:")
    print("1. Set up ngrok for public callback URL: ngrok http 8000")
    print("2. Update BAP_URI in .env to ngrok URL")
    print("3. Set NAMMA_YATRI_ENABLED=true")
    print("4. Test with real Beckn gateway")


if __name__ == "__main__":
    test_beckn_callback_flow()
