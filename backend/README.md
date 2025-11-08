# Cabsync Backend

Modular FastAPI backend for aggregating ride quotes from multiple providers.

## Features

- 🚗 **Multi-Provider Aggregation**: Uber, Ola, Rapido, Namma Yatri
- 🔌 **Modular Architecture**: Each provider in separate file
- 🌐 **Real-Time Integration**: Namma Yatri via Beckn Protocol
- 🎯 **Advanced Filtering**: Vehicle type + seater capacity
- 📊 **Metadata**: Ratings, CO2 estimates, deep links

## Quick Start

### Prerequisites

- Python 3.12+
- Virtual environment created in `../virt/`

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Start server
python main.py
```

Server runs on `http://localhost:8000`

## API Endpoints

### Health Check
```bash
GET /api/health
```

### Compare Rides
```bash
POST /api/compare
Content-Type: application/json

{
  "pickup": {
    "lat": 12.9716,
    "lng": 77.5946,
    "address": "MG Road, Bangalore"
  },
  "dropoff": {
    "lat": 12.9352,
    "lng": 77.6245,
    "address": "Koramangala, Bangalore"
  },
  "vehicleType": "auto",
  "seaterCapacity": 4
}
```

### Beckn Callback (Namma Yatri)
```bash
POST /api/beckn/on_search
Content-Type: application/json

# Called by Beckn Gateway - see BECKN_INTEGRATION.md
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   └── factory.py           # FastAPI app factory
├── models/
│   └── ride.py             # Pydantic models + Beckn state
├── platforms/
│   ├── base.py             # Mock data provider
│   ├── uber.py             # Uber integration (mock)
│   ├── ola.py              # Ola integration (mock)
│   ├── rapido.py           # Rapido integration (mock)
│   └── namma_yatri.py      # Namma Yatri (Beckn protocol)
├── services/
│   ├── aggregator.py       # Quote aggregation logic
│   └── registry.py         # Provider registry
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── .env.example           # Config template
└── test_beckn.py          # Beckn integration tests
```

## Configuration

### Environment Variables

```bash
# API
CABSYNC_API_VERSION=2.0.0
FRONTEND_URL=http://localhost:5173

# Namma Yatri / Beckn Protocol
NAMMA_YATRI_ENABLED=false
BECKN_GATEWAY_URL=https://gateway.beckn.nsdl.co.in
BAP_ID=cabsync.app
BAP_URI=http://localhost:8000/api/beckn
```

**Important:** Namma Yatri integration requires a publicly accessible `BAP_URI`. See [QUICKSTART_NAMMA_YATRI.md](./QUICKSTART_NAMMA_YATRI.md) for setup.

## Providers

### Mock Providers (Uber, Ola, Rapido)
- Return realistic mock data
- Support vehicle type filtering
- Include seater capacity (4/6 seater cars)
- Ratings, CO2 estimates, deep links

### Namma Yatri (Beckn Protocol)
- Real-time integration when enabled
- Async callback architecture
- Transaction state management
- 5-second timeout for responses
- Disabled by default (requires public callback URL)

## Testing

### Run Test Suite
```bash
python test_beckn.py
```

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test compare (all providers)
curl -X POST http://localhost:8000/api/compare \
  -H "Content-Type: application/json" \
  -d @test_request.json

# Test Beckn callback
curl -X POST http://localhost:8000/api/beckn/on_search \
  -H "Content-Type: application/json" \
  -d @test_callback.json
```

## Namma Yatri Integration

The Namma Yatri provider uses the **Beckn Protocol** for real-time ride quotes.

### Architecture
- Async request/callback pattern
- Transaction state tracking
- Public webhook endpoint required

### Quick Enable (with ngrok)
```bash
# Terminal 1: Start backend
python main.py

# Terminal 2: Expose via ngrok
ngrok http 8000

# Terminal 3: Update config
echo "BAP_URI=https://your-url.ngrok.io/api/beckn" >> .env
echo "NAMMA_YATRI_ENABLED=true" >> .env

# Restart backend
```

### Documentation
- [BECKN_INTEGRATION.md](./BECKN_INTEGRATION.md) - Technical details
- [QUICKSTART_NAMMA_YATRI.md](./QUICKSTART_NAMMA_YATRI.md) - Setup guide
- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - Implementation overview

## Development

### Adding a New Provider

1. Create `platforms/new_provider.py`:
```python
from models.ride import RideRequest, RideResult

class NewProvider:
    provider_id = "new_provider"
    provider_name = "New Provider"
    
    def fetch_quotes(self, request: RideRequest) -> list[RideResult]:
        # Implementation
        return []
```

2. Register in `services/registry.py`:
```python
from platforms.new_provider import NewProvider

def build_platform_registry():
    return {
        # ... existing providers
        "new_provider": NewProvider(),
    }
```

### Running in Development

```bash
# With auto-reload
uvicorn main:app --reload --port 8000

# With logs
python main.py 2>&1 | tee logs/backend_$(date +%Y%m%d).log
```

## Troubleshooting

### Import Errors
```bash
# Run from backend/ directory
cd backend
python main.py
```

### Port Already in Use
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --port 8001
```

### Namma Yatri Returns 501
This is expected when `NAMMA_YATRI_ENABLED=false` (default). See [QUICKSTART_NAMMA_YATRI.md](./QUICKSTART_NAMMA_YATRI.md) to enable.

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

MIT

## Support

For issues or questions:
1. Check logs: `tail -f /tmp/cabsync_backend.log`
2. Run tests: `python test_beckn.py`
3. Review documentation in `/backend/*.md`
