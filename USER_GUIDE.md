# Quick User Guide: How to Select Pickup & Drop-off Locations

## Two Ways to Select Locations

### Method 1: Text Search (Works in all modes)

1. Type your location in the "From" or "To" field
2. See autocomplete suggestions appear below
3. Click on a suggestion to select it

**Example:**
```
Type: "connaught place"
→ See: "Connaught Place, New Delhi, Delhi, India"
→ Click to select
```

### Method 2: Interactive Map (Requires Mapbox API key or works with limited mock data)

1. Look for the 🗺️ **map icon** next to the input field
2. Click the map icon
3. A full-screen map will open
4. Select your location in one of these ways:
   - **Click anywhere** on the map
   - **Search** using the search bar at the top
   - **Drag the marker** to adjust position
   - Click **"Use current location"** to auto-detect

5. Review the selected address at the bottom
6. Click **"Confirm Location"** to save

## Step-by-Step Example

### Scenario: Book a ride from Connaught Place to India Gate

#### Step 1: Select Pickup Location
1. Go to the "Rides" page
2. In the "From" field:
   - **Option A:** Type "connaught place" and select from dropdown
   - **Option B:** Click 🗺️ icon → Search for "Connaught Place" → Click on map → Confirm

#### Step 2: Select Drop-off Location  
1. In the "To" field:
   - **Option A:** Type "india gate" and select from dropdown
   - **Option B:** Click 🗺️ icon → Search for "India Gate" → Click on map → Confirm

#### Step 3: Choose Vehicle Type
1. Select from: Auto, Bike, or Car
2. If Car is selected, optionally choose 4-seater or 6-seater

#### Step 4: Compare Rides
1. Click "Compare Rides" button
2. See prices and ETAs from different providers
3. Choose the best option for you!

## Tips & Tricks

### 🎯 For Accurate Locations
- Use the map to click on your exact building or landmark
- Drag the marker to fine-tune the position
- The address will update automatically as you move the marker

### 📍 Using Current Location
- Click "Use current location" in the map picker
- Allow browser permissions when prompted
- The map will center on your current position

### 🔍 Better Search Results
- Be specific: "MG Road Bangalore" instead of just "MG Road"
- Include landmarks: "Near Saket Metro Station"
- Add city names for locations outside Delhi

### ⚡ Quick Selection
- Recent searches appear first (coming soon)
- Favorite locations for quick access (coming soon)

## Keyboard Shortcuts (Map Picker)

- **Esc** - Close map picker
- **+/-** - Zoom in/out
- **Arrow keys** - Pan the map
- **Enter** - Confirm location (when in search bar)

## Troubleshooting

### "Map not loading"
- You're in MOCK mode, which is fine! Use text search instead
- Or add a Mapbox API key to enable full map features (see MAP_SETUP.md)

### "Location not found"
- Check spelling
- Try being more specific with city/area name
- Use the map to click directly on your location

### "Can't access current location"
- Enable location permissions in your browser
- Ensure you're on HTTPS (or localhost)
- Check if location services are enabled on your device

### "Map icon not working"
- If no Mapbox API key is configured, you'll see an error
- Use text search instead, or configure API key (see MAP_SETUP.md)

## What Locations Are Available?

### In MOCK Mode (without API key)
Pre-loaded major cities:
- Delhi NCR: Connaught Place, Noida, Gurugram, Karol Bagh, Hauz Khas
- Mumbai, Bangalore, Chennai
- Kolkata, Hyderabad, Pune, Ahmedabad

### In LIVE Mode (with Mapbox API key)
- **Any location in India** 🇮🇳
- Cities, towns, villages
- Streets, landmarks, buildings
- GPS coordinates

## Example Locations to Try

```
Delhi:
- Connaught Place
- India Gate
- Red Fort
- Qutub Minar
- Lotus Temple

Bangalore:
- MG Road
- Electronic City
- Koramangala
- Indiranagar

Mumbai:
- Gateway of India
- Bandra Kurla Complex
- Andheri Station
- Colaba

Chennai:
- Marina Beach
- T Nagar
- Adyar
```

## Mobile Usage

### Touch Gestures
- **Tap** - Select location on map
- **Pinch** - Zoom in/out
- **Drag** - Move the map
- **Long press** - Place/move marker

### Mobile Tips
- Hold phone in landscape for better map view
- Use the search bar for easier text input
- "Use current location" works great on mobile!

## Privacy & Permissions

### What We Access
- Your location (only if you click "Use current location")
- Search history (stored locally, not sent to servers)

### What We Don't Do
- Track your location continuously
- Share your location with third parties
- Store location history on servers

### Browser Permissions
- Location access is requested only when needed
- You can deny and still use text search
- Permissions can be revoked anytime in browser settings

## Need Help?

- Check the [MAP_SETUP.md](./MAP_SETUP.md) for technical setup
- Read the [README.md](./README.md) for general information
- Open an issue on GitHub for bugs or feature requests

---

**Happy riding! 🚗**
