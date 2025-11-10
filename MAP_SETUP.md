# Map Integration Setup Guide

This guide explains how to set up the interactive map feature for location selection in CabSync.

## Overview

CabSync now uses **Mapbox GL JS** for interactive map-based location selection. Users can:
- Search for locations using text search with autocomplete
- Click on the map to select any location
- Drag markers to adjust pickup/drop-off points
- Use their current location
- View location suggestions for anywhere in India

## Quick Start (Works Without API Key)

The application works out of the box in **MOCK mode** without any API key configuration. Mock data includes major locations across India.

## Setup with Mapbox (Recommended for Production)

### Step 1: Get a Free Mapbox API Key

1. Go to [Mapbox](https://account.mapbox.com/)
2. Sign up for a free account (no credit card required)
3. Navigate to **Access Tokens** in your account dashboard
4. Create a new token or copy the default public token
5. The free tier includes:
   - 50,000 free geocoding requests per month
   - 50,000 free map loads per month
   - More than enough for development and small-scale production

### Step 2: Configure Your Environment

1. Open the `.env` file in the project root
2. Replace `your_mapbox_token_here` with your actual token:
   ```env
   VITE_MAPBOX_TOKEN=pk.eyJ1IjoieW91ci11c2VybmFtZSIsImEiOiJ5b3VyLXRva2VuIn0.xxxx
   ```
3. Change the mode to LIVE:
   ```env
   VITE_MODE=LIVE
   ```

### Step 3: Restart the Development Server

```bash
npm run dev
```

## Features

### Interactive Map Picker
- Click the map icon (🗺️) next to pickup/drop-off fields
- Opens a full-screen interactive map
- Click anywhere on the map to select a location
- Drag the marker to fine-tune the position
- Addresses are automatically retrieved via reverse geocoding

### Text Search with Autocomplete
- Type in the pickup/drop-off fields
- Get real-time suggestions for Indian locations
- Results are proximity-based (closer locations shown first)

### Current Location
- Click "Use current location" in the map picker
- Browser will request permission to access your location
- Map will automatically center on your position

### Map Controls
- **Zoom**: Use mouse wheel, +/- buttons, or pinch gestures
- **Pan**: Click and drag the map
- **Navigation**: Full 360° rotation support
- **Geolocate**: Built-in control to center on your location

## API Usage & Limits

### Mapbox Free Tier
- **50,000** geocoding requests/month
- **50,000** map loads/month
- **100,000** directions requests/month (if needed later)

For a typical user journey:
- 1 map load = opening the map picker
- 1 geocoding request = searching for a location
- 1 reverse geocoding request = clicking on the map

**Example**: 1,000 users, each making 2 trips per month with map usage = ~6,000 requests (well within limits)

## Troubleshooting

### Map Not Loading
1. Check if `VITE_MAPBOX_TOKEN` is set correctly in `.env`
2. Verify the token is valid on [Mapbox Dashboard](https://account.mapbox.com/access-tokens/)
3. Check browser console for error messages
4. Ensure `.env` file is in the project root (same level as `package.json`)

### "Invalid Token" Error
- Token might be expired or revoked
- Create a new token on Mapbox dashboard
- Ensure token has "Public scopes" enabled

### Mock Mode Not Working
- Set `VITE_MODE=MOCK` in `.env`
- Restart the development server
- Mock mode doesn't require an API key

### Location Permissions Denied
- Browser blocks geolocation by default on non-HTTPS
- Allow location permissions in browser settings
- Use `http://localhost` which is whitelisted by browsers

## Architecture

### Components
- **`MapPicker.tsx`**: Interactive map modal component
- **`SearchCard.tsx`**: Search form with map integration
- **`useLocationSearch.ts`**: Hook for location search and autocomplete

### Services
- **`geocoding.ts`**: Geocoding and reverse geocoding utilities
  - `searchLocations()`: Search for locations by text
  - `reverseGeocode()`: Convert coordinates to addresses
  - `getCurrentLocation()`: Get user's current location
  - `calculateDistance()`: Calculate distance between two points

### Mock Data
When running in MOCK mode, the app uses pre-defined locations including:
- Delhi NCR (Connaught Place, Noida, Gurugram)
- Major cities (Mumbai, Bangalore, Chennai, Kolkata, Hyderabad, Pune, Ahmedabad)

## Best Practices

1. **Development**: Use MOCK mode to avoid consuming API limits
2. **Staging**: Use LIVE mode with a development token
3. **Production**: Use LIVE mode with a production token (consider paid tier for high traffic)
4. **Rate Limiting**: Implement request debouncing (already included - 300ms delay)
5. **Caching**: Consider caching frequent location searches

## Alternative: Using Google Maps

If you prefer Google Maps, you can modify the implementation:

1. Replace Mapbox with Google Maps JavaScript API
2. Update `MapPicker.tsx` to use Google Maps components
3. Update `geocoding.ts` to use Google Geocoding API
4. Add `VITE_GOOGLE_MAPS_API_KEY` to `.env`

Note: Google Maps Geocoding API has similar free tier limits (~$200 credit/month).

## Next Steps

- Add route visualization between pickup and drop-off
- Display estimated distance and duration on the map
- Add traffic layer for real-time conditions
- Implement favorite locations with local storage
- Add map style selection (street, satellite, dark mode)

## Support

For issues or questions:
1. Check the [Mapbox Documentation](https://docs.mapbox.com/)
2. Review the code comments in the map-related files
3. Open an issue in the project repository
