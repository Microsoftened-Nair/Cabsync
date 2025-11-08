# Namma Yatri Integration - Quick Start Guide

## Overview

The Beckn protocol integration is now **fully implemented and tested**! The callback infrastructure is working correctly.

## Current Status

✅ **Working Components:**
- Transaction state management
- Beckn search request payload formatting  
- `/api/beckn/on_search` callback endpoint
- Result parsing from Beckn catalog to RideResult
- Error handling and timeout management
- Comprehensive test suite

## Quick Start

### 1. Local Testing (Disabled by Default)

The integration is **disabled by default** to avoid errors without a public callback URL:

```bash
# Backend returns 501 for Namma Yatri when disabled
curl -X POST http://localhost:8000/api/compare \
  -H "Content-Type: application/json" \
  -d '{"pickup": {"lat": 12.9716, "lng": 77.5946, "address": "MG Road"}, ...}'

# Response: Other providers (Uber, Ola, Rapido) work, Namma Yatri in failedProviders
```

### 2. Enable with Public Callback URL

To enable real-time Namma Yatri integration, you need a **publicly accessible callback URL**:

#### Option A: Using ngrok (Recommended for Testing)

```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start ngrok tunnel
ngrok http 8000

# Output will show: Forwarding https://abc123.ngrok.io -> http://localhost:8000

# Terminal 3: Update environment and restart
cd backend
echo "BAP_URI=https://abc123.ngrok.io/api/beckn" >> .env
echo "NAMMA_YATRI_ENABLED=true" >> .env

# Restart backend (Ctrl+C in Terminal 1, then):
python main.py
```

#### Option B: Production Deployment

```bash
# In production with HTTPS domain:
BAP_URI=https://your-domain.com/api/beckn
NAMMA_YATRI_ENABLED=true
```

### 3. Test the Integration

```bash
# Run comprehensive test suite
cd backend
python test_beckn.py

# Test via API
curl -X POST http://localhost:8000/api/compare \
  -H "Content-Type: application/json" \
  -d '{
    "pickup": {"lat": 12.9716, "lng": 77.5946, "address": "MG Road, Bangalore"},
    "dropoff": {"lat": 12.9352, "lng": 77.6245, "address": "Koramangala, Bangalore"},
    "vehicleType": "auto"
  }'
```

## Architecture

### Async Flow

```
1. Client → /api/compare
2. Backend → Beckn Gateway (search request)
3. Beckn Gateway → ACK (immediate response)
4. Backend waits up to 5 seconds...
5. Beckn Gateway → /api/beckn/on_search (async callback)
6. Backend parses results, updates transaction store
7. Backend → Client (with Namma Yatri results)
```

### Transaction Store

In-memory transaction tracking:

```python
transaction_store = {
    "uuid-1234": TransactionState(
        transaction_id="uuid-1234",
        request=RideRequest(...),
        status=TransactionStatus.COMPLETED,
        results=[RideResult(...), RideResult(...)]
    )
}
```

## Configuration

### Environment Variables

```bash
# backend/.env
NAMMA_YATRI_ENABLED=false              # Set to true to enable
BECKN_GATEWAY_URL=https://gateway.beckn.nsdl.co.in
BAP_ID=cabsync.app
BAP_URI=http://localhost:8000/api/beckn  # Must be publicly accessible!
```

### Testing Without Gateway

You can test the callback endpoint directly:

```bash
# Simulate a Beckn callback
curl -X POST http://localhost:8000/api/beckn/on_search \
  -H "Content-Type: application/json" \
  -d '{
    "context": {"transaction_id": "test-123"},
    "message": {
      "catalog": {
        "providers": [{
          "items": [{
            "descriptor": {"name": "Auto Rickshaw"},
            "price": {"value": "150"},
            "fulfillment": {"state": {"descriptor": {"name": "ETA 5 mins"}}}
          }]
        }]
      }
    }
  }'
```

## Troubleshooting

### Issue: "Namma Yatri integration is disabled"

**Solution:** Set `NAMMA_YATRI_ENABLED=true` in `backend/.env`

### Issue: "Failed to connect to Namma Yatri"

**Causes:**
- Beckn gateway URL is incorrect
- No internet connection
- Gateway is down

**Solution:** Check `BECKN_GATEWAY_URL` and test connectivity

### Issue: Timeout - no results from Namma Yatri

**Causes:**
- BAP_URI is not publicly accessible
- Beckn gateway cannot reach callback endpoint
- No drivers available for route

**Solution:**
1. Verify BAP_URI is a public URL (use ngrok for testing)
2. Check ngrok is running and forwarding to port 8000
3. Monitor backend logs for callback activity

### Issue: Results appear but are empty

**Cause:** Beckn gateway returned empty catalog

**Solution:** This is expected if no drivers are available for the requested route

## Next Steps

### For Production Deployment

1. **Replace in-memory store with Redis**
   ```python
   # Use Redis for distributed transaction storage
   import redis
   transaction_store = redis.Redis(host='localhost', port=6379, db=0)
   ```

2. **Implement additional callbacks**
   - `/api/beckn/on_select` - Ride selection
   - `/api/beckn/on_confirm` - Booking confirmation
   - `/api/beckn/on_track` - Live tracking

3. **Add request signing**
   - Sign outgoing requests with Ed25519
   - Verify incoming callback signatures

4. **Register as BAP**
   - Register in Beckn registry
   - Obtain official BAP credentials
   - Configure production gateway

5. **Add monitoring**
   - Transaction success/failure rates
   - Callback latency metrics
   - Gateway availability

## Resources

- [BECKN_INTEGRATION.md](./BECKN_INTEGRATION.md) - Full technical documentation
- [test_beckn.py](./test_beckn.py) - Comprehensive test suite
- [Beckn Protocol Specs](https://github.com/beckn/protocol-specifications)
- [Namma Yatri GitHub](https://github.com/nammayatri/nammayatri)

## Support

Check logs for detailed error messages:

```bash
cd backend
python main.py 2>&1 | tee logs/beckn_$(date +%Y%m%d).log
```
