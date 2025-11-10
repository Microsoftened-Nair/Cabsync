# cabsync

A modern ride aggregator that compares fares and ETAs across Uber, Ola, Rapido, and inDrive with a beautiful dark-mode interface.

## Features

- 🌙 Beautiful dark mode with light mode toggle
- 🚗 Compare rides from Uber, Ola, Rapido, and inDrive using a unified data model
- ⚡ Real-time price and ETA comparison
- 📱 Fully responsive design
- ♿ Accessible (WCAG AA compliant)
- 🎨 Smooth animations with Framer Motion
- 🗺️ **Interactive map-based location picker using OpenStreetMap (100% FREE!)**
- 🔍 Location search with autocomplete for anywhere in India
- 📍 Click-to-select on map, drag markers, or use current location
- 🆓 **No API keys required** - works completely free with Leaflet & OpenStreetMap
- 🌏 Unlimited geocoding with Nominatim (OpenStreetMap's geocoding service)

## Tech Stack

### Frontend
````markdown
# cabsync

A modern ride aggregator that compares fares and ETAs across Uber, Ola, Rapido, and inDrive with a beautiful dark-mode interface.

## What this update adds
- A very detailed, step-by-step installation and run guide so even a beginner (or a pre-teen!) can get the app running locally.

## Quick Overview (what you will do)
1. Install Node.js and npm (for the frontend)
2. Install Python and create a virtual environment (for the backend)
3. Install frontend and backend dependencies
4. Run frontend and backend locally and visit the app in your browser

---

## Very Detailed Installation Guide (Linux / bash)

This guide assumes you are on Linux and using the `bash` shell. Copy and paste the commands one-by-one into a terminal. If a step fails, the guide tells you how to check and what to do next.

### 1) Open a terminal
- On Linux press Ctrl+Alt+T or open your terminal application.

### 2) Clone the repository (if you haven't already)
Replace `your-username` with your GitHub username if you forked it, otherwise use the repo URL.

```bash
# Clone the project into a folder named cabsync
git clone https://github.com/Microsoftened-Nair/Cabsync.git cabsync
cd cabsync
pwd  # Confirm you're in the project folder
```

If `git` is not installed, install it first (example for Debian/Ubuntu):
```bash
sudo apt update
sudo apt install -y git
```

### 3) Install Node.js (required for the frontend)
We recommend Node.js 18 or newer. If you already have `node -v` >= 18, skip this step.

Option A — install via NodeSource (recommended):
```bash
# Download and run NodeSource install script for Node 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify versions
node -v
npm -v
```

Option B — use your package manager or nvm if you prefer. If you use Windows, follow Node installers on nodejs.org.

### 4) Install Python 3 and pip (required for the backend)
We recommend Python 3.8 or newer. Check your version:
```bash
python3 --version
```

If Python is missing on Debian/Ubuntu:
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

### 5) Create a Python virtual environment for the backend
We keep backend dependencies isolated using a virtual environment.

```bash
cd backend
# Create a virtual environment named 'virt' (you can name it venv if you like)
python3 -m venv virt

# Activate the virtual environment (this changes your prompt)
source virt/bin/activate

# You should now see (virt) in your terminal prompt.
```

If `source virt/bin/activate` fails, check that `virt/bin/activate` exists and that Python created the environment.

### 6) Install backend Python dependencies
With the virtual environment activated:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If you see permission errors, make sure the virtualenv is activated (the prompt shows `(virt)`).

### 7) Install frontend dependencies
Open a new terminal tab or window, or stop the virtualenv activation (you can have both frontend and backend terminals). From the project root (not the `backend` folder):

```bash
cd ..  # back to project root if you were in backend
npm install
```

This installs everything the frontend needs (React, TailwindCSS, Vite, etc.).

### 8) Environment files (optional but recommended)
There may be example environment files in the repo. Copy them if you need to set environment variables.

```bash
# From project root
cp .env.example .env 2>/dev/null || true
cp backend/.env.example backend/.env 2>/dev/null || true

# Edit the files if you need (use nano, vim, or a GUI editor):
nano .env
nano backend/.env
```

Notes:
- `VITE_API_BASE_URL` should be `http://localhost:8000` during local development.
- By default the project supports `MOCK` mode so a Mapbox token is not strictly required.

### 9) Run the backend server
Make sure you're in the `backend` directory and the virtualenv is activated.

```bash
cd backend
source virt/bin/activate  # activate if not already active
# Start backend (FastAPI via Uvicorn)
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

If the server starts successfully you'll see output that Uvicorn is running and listening on port 8000.

You can quickly test the backend health endpoint in another terminal:
```bash
curl http://localhost:8000/api/health
```

### 10) Run the frontend dev server
Open another terminal (frontend runs separately) and start the Vite dev server:

```bash
cd <path-to-cabsync-root>  # change back to the project root
npm run dev
```

The frontend usually runs on http://localhost:5173. Open that URL in your browser.

### 11) Run both frontend and backend together (shortcut)
From the project root you can run both with one command (uses `concurrently`):

```bash
npm run dev:full
```

This opens two processes: the frontend dev server and the backend server.

### 12) Build for production (optional)
To generate a production-ready frontend bundle:

```bash
npm run build
```

To run a production-preview of the frontend:

```bash
npm run preview
```

### 13) Run tests
The project includes frontend tests (Vitest). Run:

```bash
npm run test
```

### 14) Common troubleshooting
- If `npm install` fails: make sure `node` and `npm` are installed and you have a working internet connection.
- If backend `pip install -r requirements.txt` fails: activate virtualenv and use `pip --version` to check which pip is active.
- If ports are already in use: check which process is using it (`sudo lsof -i :8000`) and stop that process or change the port.
- If the frontend shows a blank page: open the browser console (F12) and check for error messages; ensure the backend is running at `VITE_API_BASE_URL`.

### 15) Notes for Windows users
- Use PowerShell for running commands. Activate virtualenv on Windows with `virt\Scripts\Activate.ps1` or `virt\Scripts\activate` depending on shell.
- For Node installation on Windows use the installer from nodejs.org.

---

## Short Reference of Useful Commands

```bash
# Clone the repo
git clone https://github.com/Microsoftened-Nair/Cabsync.git

# Frontend (project root)
npm install
npm run dev         # start frontend dev server
npm run build       # build frontend for production

# Backend (backend folder)
python3 -m venv virt
source virt/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run both together
npm run dev:full

# Run tests
npm run test
```

---

If anything in these steps is unclear or you hit an error, tell me the exact command you ran and the full terminal output — I will help debug it step-by-step.

Made with ❤️ to help you get started quickly.

````
