# Uber Real-Time Integration Summary

## What Changed

✅ **Uber now uses real API data instead of mock data**

### Files Modified
1. **`platforms/uber.py`** - Completely rewritten to use GraphQL API
2. **`platforms/uber_graphql.py`** - New GraphQL client (already created)

### Files Created
1. **`backend/uber_cookies.txt`** - Cookie storage file (needs your cookies)
2. **`backend/UBER_SETUP.md`** - Detailed setup instructions
3. **`backend/test_uber_integration.py`** - Test script

## Quick Start

### Step 1: Get Your Cookies

1. Open Firefox and go to https://m.uber.com
2. Log in to your account
3. Search for any ride (enter pickup and dropoff)
4. Open Developer Tools (F12) → **Network** tab
5. Find the request to `graphql`
6. Right-click → **Copy** → **Copy as cURL**

You'll get something like:
```bash
curl 'https://m.uber.com/go/graphql' \
  -H 'Cookie: sid=QA.CAESEGc...; csid=1.1765...; jwt-session=eyJhbGc...' \
  --data-raw '...'
```

### Step 2: Extract Cookies

Copy everything after `Cookie:` (between the quotes). Example:
```
sid=QA.CAESEGc...; csid=1.1765...; jwt-session=eyJhbGc...
```

### Step 3: Update Cookie File

Open `backend/uber_cookies.txt` and replace the placeholder with your cookies:
```bash
cd /home/megh/cabsync/backend
nano uber_cookies.txt
```

Paste your cookies (all on one line), save and exit.

### Step 4: Test It

```bash
python test_uber_integration.py
```

You should see real Uber prices! 🎉

## How It Works

```
┌─────────────────────────────────────────────────────┐
│  Your CabSync App                                   │
│                                                     │
│  GET /api/compare?pickup=...&dropoff=...           │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  RideAggregator (aggregator.py)                     │
│  Calls all providers in parallel                    │
└─────────────────┬───────────────────────────────────┘
                  │
        ┌─────────┼─────────┬─────────┐
        ▼         ▼         ▼         ▼
    ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
    │ Uber │ │ Ola  │ │Rapido│ │Namma │
    │      │ │      │ │      │ │Yatri │
    └───┬──┘ └──┬───┘ └──┬───┘ └──┬───┘
        │       │        │        │
        ▼       ▼        ▼        ▼
      REAL    MOCK     MOCK     REAL
      API     DATA     DATA     API
```

**Before**: Uber used mock/calculated prices
**Now**: Uber calls real GraphQL API with your cookies

## Example Response

```python
# Old (mock data)
UberProvider.fetch_quotes() → [
    RideResult(service_type="Uber Go", price=55+12*distance, ...)
]

# New (real API data)
UberProvider.fetch_quotes() → [
    RideResult(service_type="Auto", price=301.06, ...),
    RideResult(service_type="Uber Go", price=311.75, ...),
    RideResult(service_type="Go Sedan", price=326.43, ...),
    RideResult(service_type="UberXL", price=478.92, ...),
    RideResult(service_type="Premier", price=374.10, ...)
]
```

## Cookie Expiration

⚠️ **Important**: Session cookies expire after 24-48 hours of inactivity.

When expired:
- `UberProvider.fetch_quotes()` returns empty list `[]`
- Other providers (Ola, Rapido) continue working normally
- Simply update `uber_cookies.txt` with fresh cookies

## Environment Variables (Optional)

Instead of the file, you can use environment variables:

```bash
export UBER_COOKIES="sid=...; csid=...; jwt-session=..."
export UBER_CITY_ID="342"  # Pune (default)
```

## Testing the Full API

```bash
# Start the backend
cd /home/megh/cabsync/backend
python main.py

# In another terminal, test the API
curl "http://localhost:5000/api/compare?pickup=18.488900,74.025588,Loni&dropoff=18.502726,73.950883,Pune"
```

You should see Uber prices alongside Ola, Rapido, and Namma Yatri results!

## Troubleshooting

### No Uber results returned
```bash
# Check if cookies are configured
cat backend/uber_cookies.txt

# Should NOT see "REPLACE_ME"
```

### "All providers failed" error
- All providers (including Uber) are failing
- Check network connectivity
- Check if Flask app is running correctly

### Only other providers work (no Uber)
- Uber cookies are missing or expired
- Update `uber_cookies.txt` with fresh cookies
- Run `python test_uber_integration.py` to verify

## Production Considerations

### Option 1: Keep Cookie-Based (Current Implementation)
- **Pros**: Free, no API registration needed
- **Cons**: Cookies expire, requires manual updates
- **Best for**: Personal projects, demos, prototypes

### Option 2: Official Uber API
- Apply at https://developer.uber.com/
- **Pros**: Stable OAuth, no expiration issues
- **Cons**: Requires approval, may have costs
- **Best for**: Production applications

### Option 3: Beckn Protocol (India Only)
- Use Namma Yatri (already integrated!)
- **Pros**: Open protocol, no API keys
- **Cons**: Only works in India
- **Best for**: India-specific deployments

## Next Steps

1. ✅ Update `uber_cookies.txt` with your cookies
2. ✅ Run `python test_uber_integration.py` to verify
3. ✅ Start your backend: `python main.py`
4. ✅ Test the full API endpoint
5. 📝 Set a reminder to refresh cookies every 1-2 days
6. 🎯 Consider applying for official Uber API for production

## Questions?

See `UBER_SETUP.md` for detailed documentation.
