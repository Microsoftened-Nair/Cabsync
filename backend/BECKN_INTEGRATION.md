# Beckn Protocol Integration for Namma Yatri

## Overview

Namma Yatri uses the **Beckn Protocol** - an open mobility specification that enables decentralized, interoperable ride-hailing services.

## Architecture

### Beckn Protocol Entities

1. **BAP (Beckn Application Platform)** - Consumer-facing app (Cabsync)
2. **BPP (Beckn Provider Platform)** - Service provider (Namma Yatri drivers)
3. **BG (Beckn Gateway)** - Discovery and routing gateway
4. **Registry** - Platform discovery service

### Communication Flow

```
Cabsync (BAP) → Beckn Gateway → Namma Yatri (BPP)
                    ↓
               on_search callback
                    ↓
Cabsync (BAP) ← Beckn Gateway ← Namma Yatri (BPP)
```

## API Specification

### 1. Search (Discovery)

**Request:**
```json
{
  "context": {
    "domain": "mobility",
    "action": "search",
    "version": "1.1.0",
    "bap_id": "cabsync.app",
    "bap_uri": "https://cabsync.app/beckn",
    "transaction_id": "uuid",
    "message_id": "uuid",
    "timestamp": "2025-11-08T08:00:00.000Z"
  },
  "message": {
    "intent": {
      "fulfillment": {
        "start": {
          "location": {
            "gps": "12.9716,77.5946"
          }
        },
        "end": {
          "location": {
            "gps": "12.9352,77.6245"
          }
        }
      }
    }
  }
}
```

**Response (ACK):**
```json
{
  "message": {
    "ack": {
      "status": "ACK"
    }
  }
}
```

**Callback (on_search):**
```json
{
  "context": { /* same as request */ },
  "message": {
    "catalog": {
      "providers": [{
        "id": "namma-yatri-driver-123",
        "items": [{
          "id": "auto-ride",
          "descriptor": {
            "name": "Auto Rickshaw"
          },
          "price": {
            "value": "150",
            "currency": "INR"
          },
          "fulfillment": {
            "state": {
              "descriptor": {
                "name": "ETA 5 mins"
              }
            }
          }
        }]
      }]
    }
  }
}
```

## Implementation Status

### ✅ Completed
- Beckn protocol context structure
- Search request payload formatting
- HTTP client with async support
- Provider scaffolding
- Transaction state management with in-memory store
- Callback endpoint `/api/beckn/on_search` for receiving async responses
- Result parsing from Beckn catalog format to RideResult models
- Timeout handling for callback responses (5 second wait)
- Error handling and NACK responses

### 🚧 Pending
1. **Public Callback URL**
   - Deploy with ngrok or similar tunnel for local testing
   - Configure production webhook with HTTPS
   - Update BAP_URI environment variable

2. **BAP Registration**
   - Register with Beckn registry
   - Obtain BAP credentials
   - Configure gateway endpoints

3. **Additional Callbacks**
   - `/beckn/on_select` for ride selection
   - `/beckn/on_confirm` for booking confirmation
   - `/beckn/on_track` for live tracking

4. **Production Enhancements**
   - Redis for distributed transaction store
   - Request signing with Ed25519
   - Signature verification for callbacks
   - TLS/HTTPS enforcement
   - Rate limiting and DDoS protection

## Configuration

### Environment Variables

```bash
# Enable Namma Yatri integration
NAMMA_YATRI_ENABLED=true

# Beckn Gateway URL
BECKN_GATEWAY_URL=https://gateway.beckn.nsdl.co.in

# BAP Identification
BAP_ID=cabsync.app
BAP_URI=https://cabsync.app/beckn

# Callback endpoint (must be publicly accessible)
BECKN_CALLBACK_URL=https://cabsync.app/api/beckn/callback
```

## Testing

### Local Testing with Callback Endpoint

The implementation includes a working callback endpoint that can be tested:

```bash
# 1. Start the backend server
cd backend
source ../virt/bin/activate
python main.py

# 2. Test the callback endpoint directly
curl -X POST http://localhost:8000/api/beckn/on_search \
  -H "Content-Type: application/json" \
  -d '{
    "context": {
      "transaction_id": "test-123",
      "action": "on_search"
    },
    "message": {
      "catalog": {
        "providers": [{
          "id": "driver-1",
          "items": [{
            "id": "auto-1",
            "descriptor": {"name": "Auto Rickshaw"},
            "price": {"value": "150", "currency": "INR"},
            "fulfillment": {
              "state": {
                "descriptor": {"name": "ETA 5 mins"}
              }
            }
          }]
        }]
      }
    }
  }'
```

### Using ngrok for Real Gateway Testing

To test with a real Beckn gateway, you need a public callback URL:

```bash
# 1. Install ngrok
# Visit https://ngrok.com/ and follow installation instructions

# 2. Start ngrok tunnel
ngrok http 8000

# 3. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)

# 4. Update backend/.env
BAP_URI=https://abc123.ngrok.io/api/beckn
NAMMA_YATRI_ENABLED=true

# 5. Restart backend and test
```

### Testing with Frontend

```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend
cd ..
npm run dev

# Open browser to http://localhost:5173
# Enter pickup/dropoff locations
# Select vehicle type
# Click "Compare Prices"
# Namma Yatri results will appear if NAMMA_YATRI_ENABLED=true
```

### Using Mock Gateway

For development, you can use a mock Beckn gateway:

```bash
# Install beckn-sandbox
npm install -g beckn-sandbox

# Start mock gateway
beckn-sandbox start --port 5555

# Update environment
BECKN_GATEWAY_URL=http://localhost:5555
```

### Manual Testing

```bash
# Test search request
curl -X POST https://gateway.beckn.nsdl.co.in/search \
  -H "Content-Type: application/json" \
  -d @test_search_request.json
```

## Resources

- [Beckn Protocol Specifications](https://github.com/beckn/protocol-specifications)
- [Namma Yatri GitHub](https://github.com/nammayatri/nammayatri)
- [Beckn Mobility API Docs](https://developers.beckn.org/docs/mobility/)
- [ONDC Network Registry](https://registry.ondc.org/)

## Next Steps

1. Set up public callback endpoint (use ngrok for testing)
2. Implement webhook handlers for on_search, on_select, on_confirm
3. Register as BAP in Beckn registry
4. Test with Beckn sandbox environment
5. Deploy to production with proper security
