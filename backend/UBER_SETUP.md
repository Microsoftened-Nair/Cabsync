# Uber GraphQL API Setup

This guide explains how to configure real-time Uber price fetching using session cookies.

## Overview

The Uber integration uses the mobile GraphQL API (`m.uber.com/go/graphql`) to fetch real-time ride prices. Since Uber doesn't provide a public API for price estimates, we authenticate using session cookies from a logged-in browser session.

## Setup Instructions

### Option 1: Using Cookie File (Recommended)

1. **Open Uber in your browser**
   - Navigate to https://m.uber.com
   - Log in to your Uber account

2. **Capture the cookies**
   - Open Developer Tools (F12)
   - Go to the **Network** tab
   - Search for a ride (enter pickup and dropoff locations)
   - Find a request to `graphql` endpoint
   - Right-click → **Copy** → **Copy as cURL**

3. **Extract the Cookie header**
   - Look for the `-H 'Cookie: ...'` line in the cURL command
   - Copy everything between the quotes after `Cookie:`
   - Example: `sid=QA.CAESEGc...; csid=1.1765...; jwt-session=eyJhbGc...`

4. **Save to file**
   - Open `backend/uber_cookies.txt`
   - Replace the placeholder text with your actual cookies
   - Save the file

### Option 2: Using Environment Variable

Set the `UBER_COOKIES` environment variable:

```bash
export UBER_COOKIES="sid=QA.CAESEGc...; csid=1.1765...; jwt-session=eyJhbGc..."
```

Or add to your `.env` file:

```env
UBER_COOKIES="sid=QA.CAESEGc...; csid=1.1765...; jwt-session=eyJhbGc..."
UBER_CITY_ID=342  # Optional: Uber city ID (default: 342 for Pune)
```

## Important Cookies

The following cookies are required:
- `sid` - Session ID (required)
- `csid` - Client Session ID (required)  
- `jwt-session` - JWT session token (required)
- `marketing_vistor_id` - Optional but recommended

## Cookie Expiration

Session cookies typically expire after:
- **Inactivity**: 24-48 hours of no activity
- **Logout**: Immediately when you log out
- **Token expiry**: JWT tokens have an expiration time

When cookies expire, you'll see empty results. Simply repeat the setup steps to get fresh cookies.

## Testing

Test your Uber integration:

```bash
cd backend
python platforms/uber_graphql.py
```

You should see real Uber prices for the example route.

## API Endpoint

- **URL**: `https://m.uber.com/go/graphql`
- **Method**: POST
- **Auth**: Cookie-based
- **CSRF Token**: `x` (static value)

## Architecture

```
┌─────────────────┐
│   Your App      │
│  (uber.py)      │
└────────┬────────┘
         │
         │ Uses
         ▼
┌─────────────────┐
│ UberGraphQL     │
│   Client        │
│ (uber_graphql)  │
└────────┬────────┘
         │
         │ HTTP POST
         ▼
┌─────────────────┐
│  Uber GraphQL   │
│      API        │
│ m.uber.com/go   │
└─────────────────┘
```

## Troubleshooting

### No results returned
- Check if cookies are set correctly
- Verify cookies haven't expired
- Ensure you're logged into Uber in your browser

### HTTP 401/403 errors
- Cookies are invalid or expired
- Get fresh cookies from browser

### HTTP 302 redirect
- Missing required cookies (sid, csid, jwt-session)
- CSRF token not set correctly

## Alternative: Official Uber API

For production use, consider applying for the official Uber API:
- Website: https://developer.uber.com/
- Provides stable authentication via OAuth
- No cookie management required
- Rate limits and pricing apply

## Alternative: Beckn Protocol (India Only)

For India-specific implementation:
- Use Namma Yatri (Beckn-compliant)
- See `BECKN_INTEGRATION.md` for details
- Open protocol, no proprietary API keys needed
