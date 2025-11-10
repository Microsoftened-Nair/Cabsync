import { Location } from '../types';

const NOMINATIM_BASE_URL = 'https://nominatim.openstreetmap.org';
const USER_AGENT = 'CabSync-App/1.0';

// Cache for search results
const searchCache = new Map<string, { results: Location[]; timestamp: number }>();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

/**
 * Get location suggestions based on a search query using Nominatim (OpenStreetMap)
 * @param query Search query string
 * @param options Search options
 * @returns Array of location suggestions
 */
export async function searchLocations(
  query: string,
  options: {
    proximity?: [number, number]; // [lng, lat]
    country?: string;
    types?: string;
    limit?: number;
  } = {}
): Promise<Location[]> {
  const trimmedQuery = query.trim();
  
  // Minimum 3 characters for stable results
  if (trimmedQuery.length < 3) {
    return [];
  }

  // Check cache first
  const cacheKey = `${trimmedQuery}-${options.country || 'in'}`;
  const cached = searchCache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.results;
  }

  try {
    const params = new URLSearchParams({
      format: 'json',
      q: trimmedQuery,
      countrycodes: options.country || 'in',
      limit: String(options.limit || 10), // Get more for better filtering
      addressdetails: '1',
    });

    // Add proximity for better results
    if (options.proximity) {
      params.append('viewbox', `${options.proximity[0] - 1},${options.proximity[1] - 1},${options.proximity[0] + 1},${options.proximity[1] + 1}`);
      params.append('bounded', '0');
    }

    const response = await fetch(
      `${NOMINATIM_BASE_URL}/search?${params}`,
      {
        headers: {
          'User-Agent': USER_AGENT,
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Geocoding API error: ${response.statusText}`);
    }

    const data = await response.json();
    
    // Map and score results
    let locations = data.map((item: any) => ({
      lat: parseFloat(item.lat),
      lng: parseFloat(item.lon),
      address: item.display_name,
      placeId: item.place_id?.toString(),
      _raw: item, // Keep raw data for scoring
    }));

    // Score and filter results for relevance
    locations = scoreAndFilterResults(locations, trimmedQuery);

    // Remove raw data and limit results
    const finalResults = locations
      .map(({ _raw, ...location }: any) => location)
      .slice(0, options.limit || 5);

    // Cache results
    searchCache.set(cacheKey, {
      results: finalResults,
      timestamp: Date.now(),
    });

    return finalResults;
  } catch (error) {
    console.error('Location search error:', error);
    return generateMockSuggestions(trimmedQuery);
  }
}

/**
 * Score and filter search results for relevance
 */
function scoreAndFilterResults(locations: any[], query: string): any[] {
  const lowerQuery = query.toLowerCase();
  
  return locations
    .map(location => {
      let score = 0;
      const address = location.address.toLowerCase();
      const raw = location._raw;
      
      // Exact match gets highest score
      if (address.startsWith(lowerQuery)) {
        score += 100;
      }
      
      // Word match at beginning
      const words = lowerQuery.split(/\s+/);
      words.forEach(word => {
        if (address.includes(word)) {
          score += 20;
        }
      });
      
      // Prefer cities, localities, and landmarks
      const type = raw.type || '';
      const placeType = raw.class || '';
      if (['city', 'town', 'village', 'locality'].includes(type)) {
        score += 30;
      }
      if (['amenity', 'tourism', 'shop'].includes(placeType)) {
        score += 15;
      }
      
      // Prefer places with higher importance
      const importance = parseFloat(raw.importance) || 0;
      score += importance * 50;
      
      // Penalize very long addresses (usually less relevant)
      if (address.length > 150) {
        score -= 10;
      }
      
      // Prefer places with names over generic addresses
      if (raw.name && raw.name.toLowerCase().includes(lowerQuery)) {
        score += 25;
      }
      
      return { ...location, _score: score };
    })
    .filter(location => location._score > 10) // Filter out low-scoring results
    .sort((a, b) => b._score - a._score); // Sort by score descending
}

/**
 * Convert coordinates to a human-readable address (reverse geocoding) using Nominatim
 * @param lng Longitude
 * @param lat Latitude
 * @returns Location object with address
 */
export async function reverseGeocode(lng: number, lat: number): Promise<Location> {
  try {
    const response = await fetch(
      `${NOMINATIM_BASE_URL}/reverse?format=json&lat=${lat}&lon=${lng}&countrycodes=in&addressdetails=1`,
      {
        headers: {
          'User-Agent': USER_AGENT,
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Reverse geocoding API error: ${response.statusText}`);
    }

    const data = await response.json();
    
    if (data && data.display_name) {
      return {
        lat,
        lng,
        address: data.display_name,
        placeId: data.place_id?.toString(),
      };
    }

    // Fallback if no results
    return {
      lat,
      lng,
      address: `${lat.toFixed(6)}, ${lng.toFixed(6)}`,
    };
  } catch (error) {
    console.error('Reverse geocoding error:', error);
    return {
      lat,
      lng,
      address: `${lat.toFixed(6)}, ${lng.toFixed(6)}`,
    };
  }
}

/**
 * Get the user's current location using the browser's geolocation API
 * @returns Promise that resolves to the user's current location
 */
export async function getCurrentLocation(): Promise<Location> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation is not supported by your browser'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        try {
          const location = await reverseGeocode(longitude, latitude);
          resolve(location);
        } catch (error) {
          // If reverse geocoding fails, return coordinates
          resolve({
            lat: latitude,
            lng: longitude,
            address: `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`,
          });
        }
      },
      (error) => {
        reject(new Error(`Geolocation error: ${error.message}`));
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  });
}

/**
 * Calculate distance between two locations using Haversine formula
 * @param loc1 First location
 * @param loc2 Second location
 * @returns Distance in kilometers
 */
export function calculateDistance(loc1: Location, loc2: Location): number {
  const R = 6371; // Earth's radius in kilometers
  const dLat = toRadians(loc2.lat - loc1.lat);
  const dLng = toRadians(loc2.lng - loc1.lng);
  
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(loc1.lat)) *
    Math.cos(toRadians(loc2.lat)) *
    Math.sin(dLng / 2) *
    Math.sin(dLng / 2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function toRadians(degrees: number): number {
  return degrees * (Math.PI / 180);
}

/**
 * Generate mock location suggestions for testing without API key
 */
function generateMockSuggestions(query: string): Location[] {
  const mockLocations: Location[] = [
    { lat: 28.6139, lng: 77.2090, address: 'Connaught Place, New Delhi, Delhi, India' },
    { lat: 28.5355, lng: 77.3910, address: 'Noida City Centre, Noida, Uttar Pradesh, India' },
    { lat: 28.4595, lng: 77.0266, address: 'Cyber Hub, Gurugram, Haryana, India' },
    { lat: 28.6692, lng: 77.4538, address: 'Akshardham Temple, Delhi, India' },
    { lat: 28.5274, lng: 77.2065, address: 'Hauz Khas Village, Delhi, India' },
    { lat: 28.6508, lng: 77.2311, address: 'Karol Bagh, Delhi, India' },
    { lat: 28.6304, lng: 77.2177, address: 'India Gate, New Delhi, Delhi, India' },
    { lat: 28.6562, lng: 77.2410, address: 'Red Fort, Delhi, India' },
    { lat: 12.9716, lng: 77.5946, address: 'MG Road, Bangalore, Karnataka, India' },
    { lat: 19.0760, lng: 72.8777, address: 'Mumbai, Maharashtra, India' },
    { lat: 13.0827, lng: 80.2707, address: 'Chennai, Tamil Nadu, India' },
    { lat: 22.5726, lng: 88.3639, address: 'Kolkata, West Bengal, India' },
    { lat: 17.3850, lng: 78.4867, address: 'Hyderabad, Telangana, India' },
    { lat: 23.0225, lng: 72.5714, address: 'Ahmedabad, Gujarat, India' },
    { lat: 18.5204, lng: 73.8567, address: 'Pune, Maharashtra, India' },
  ];

  const lowerQuery = query.toLowerCase();
  return mockLocations
    .filter(location => location.address.toLowerCase().includes(lowerQuery))
    .slice(0, 5);
}
