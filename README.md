# RideMeta

A modern ride aggregator that compares fares and ETAs across Uber, Ola, Rapido, and inDrive with a beautiful dark-mode interface.

## Features

- 🌙 Beautiful dark mode with light mode toggle
- 🚗 Compare rides from Uber, Ola, Rapido, and inDrive using a unified data model
- ⚡ Real-time price and ETA comparison
- 📱 Fully responsive design
- ♿ Accessible (WCAG AA compliant)
- 🎨 Smooth animations with Framer Motion
- 🗺️ Interactive map with route preview (Mapbox)
- 🔍 Location search with autocomplete

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **TailwindCSS** for styling
- **Framer Motion** for animations
- **React Query** for server state management
- **React Hook Form** for form handling
- **Lucide React** for icons
- **Mapbox GL** for maps

### Backend
- **FastAPI** (Python) serving curated ride samples
- **Deterministic price/ETA synthesis** based on provider rate cards
- **OAuth2** placeholders for future Uber integration
- **CORS** and response normalization helpers

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.8+
- npm or yarn

### Installation

1. **Clone and install frontend dependencies:**
```bash
npm install
```

2. **Set up Python backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Environment setup:**
```bash
# Copy environment templates
cp .env.example .env
cp backend/.env.example backend/.env
```

4. **Configure environment variables:**

**.env** (Frontend):
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_MAPBOX_TOKEN=your_mapbox_token_here
VITE_MODE=MOCK
```

**backend/.env** (Backend):
```env
# Uber API
UBER_CLIENT_ID=your_uber_client_id
UBER_CLIENT_SECRET=your_uber_client_secret
UBER_REDIRECT_URI=http://localhost:8000/auth/uber/callback

# Mapbox (for geocoding)
MAPBOX_ACCESS_TOKEN=your_mapbox_token

# App settings
MODE=MOCK  # Set to LIVE for production
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379
```

### Development

**Option 1: Run both frontend and backend together:**
```bash
npm run dev:full
```

**Option 2: Run separately:**
```bash
# Terminal 1 - Backend
npm run backend

# Terminal 2 - Frontend  
npm run dev
```

Visit http://localhost:5173 to see the app.

## API Endpoints

- `GET /api/health` — basic readiness probe with provider count.
- `POST /api/compare` — returns normalized ride options across Uber, Ola, Rapido, and inDrive.
- `GET /api/providers` — exposes the sample provider catalogue used for mock comparisons.

## API Modes

### MOCK Mode (Default)
- Backend serves deterministic sample data sourced from curated Uber/Ola/Rapido/inDrive rate cards
- No API keys required
- Perfect for UI development and testing; frontend falls back to the same dataset if the API is offline

### LIVE Mode
- Placeholder for real provider integrations (Uber OAuth scaffolding is in place)
- Requires proper OAuth setup before enabling in production environments
- Extend `generate_sample_results` with real API calls when credentials are available

---

Made with ❤️ to help you find the best ride options.
