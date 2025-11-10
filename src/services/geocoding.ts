import { Location } from '../types';

const NOMINATIM_BASE_URL = 'https://nominatim.openstreetmap.org';
const PHOTON_BASE_URL = 'https://photon.komoot.io/api';
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

  const limit = options.limit || 5;
  const cacheKey = JSON.stringify({
    query: trimmedQuery,
    country: options.country || 'in',
    proximity: options.proximity || null,
    limit,
  });

  const cached = searchCache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.results;
  }

  try {
    const [photonResults, nominatimResults] = await Promise.all([
      fetchPhotonSuggestions(trimmedQuery, options).catch(() => []),
      fetchNominatimSuggestions(trimmedQuery, options).catch(() => []),
    ]);

    const mergedResults = mergeAndRankResults([
      ...photonResults,
      ...nominatimResults,
    ], trimmedQuery, limit);

    const finalResults = mergedResults.length > 0
      ? mergedResults
      : generateMockSuggestions(trimmedQuery);

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

async function fetchPhotonSuggestions(
  query: string,
  options: { proximity?: [number, number]; limit?: number; country?: string }
): Promise<any[]> {
  const params = new URLSearchParams({
    q: query,
    lang: 'en',
    limit: String((options.limit || 5) * 2),
  });

  if (options.proximity) {
    params.append('lat', String(options.proximity[1]));
    params.append('lon', String(options.proximity[0]));
  }

  const response = await fetch(`${PHOTON_BASE_URL}?${params}`);
  if (!response.ok) {
    throw new Error(`Photon API error: ${response.statusText}`);
  }

  const data = await response.json();
  const features = data?.features || [];

  return features
    .map((feature: any) => {
      const properties = feature.properties || {};
      const geometry = feature.geometry || {};
      const coordinates = geometry.coordinates || [];
      const [lng, lat] = coordinates;

      if (typeof lat !== 'number' || typeof lng !== 'number') {
        return null;
      }

      if (options.country && properties.countrycode && properties.countrycode.toLowerCase() !== options.country.toLowerCase()) {
        return null;
      }

      const parts = [
        properties.name,
        properties.street,
        properties.suburb,
        properties.city,
        properties.state,
        properties.postcode,
        properties.country,
      ]
        .filter(Boolean)
        .map((part: string) => part.trim());

      const uniqueParts = Array.from(new Set(parts));
      const address = uniqueParts.join(', ');

      if (!address) {
        return null;
      }

      return {
        lat,
        lng,
        address,
        placeId: properties.osm_id ? `${properties.osm_type || 'osm'}-${properties.osm_id}` : undefined,
        _raw: {
          source: 'photon',
          properties,
          importance: properties?.extent ? 0.6 : 0.3,
        },
      };
    })
    .filter(Boolean);
}

async function fetchNominatimSuggestions(
  query: string,
  options: { proximity?: [number, number]; country?: string; limit?: number }
): Promise<any[]> {
  const params = new URLSearchParams({
    format: 'jsonv2',
    q: query,
    addressdetails: '1',
    namedetails: '1',
    extratags: '1',
    dedupe: '1',
    limit: String((options.limit || 5) * 2),
  });

  if (options.country) {
    params.append('countrycodes', options.country);
  }

  if (options.proximity) {
    params.append('viewbox', `${options.proximity[0] - 1},${options.proximity[1] - 1},${options.proximity[0] + 1},${options.proximity[1] + 1}`);
    params.append('bounded', '0');
  }

  const response = await fetch(
    `${NOMINATIM_BASE_URL}/search?${params}`,
    {
      headers: {
        'User-Agent': USER_AGENT,
      },
    },
  );

  if (!response.ok) {
    throw new Error(`Nominatim API error: ${response.statusText}`);
  }

  const data = await response.json();

  return data.map((item: any) => ({
    lat: parseFloat(item.lat),
    lng: parseFloat(item.lon),
    address: item.display_name,
    placeId: item.place_id?.toString(),
    _raw: {
      source: 'nominatim',
      ...item,
    },
  }));
}

function mergeAndRankResults(locations: any[], query: string, limit: number): Location[] {
  const scored = scoreAndFilterResults(locations, query);
  const unique: any[] = [];
  const seen = new Set<string>();

  for (const location of scored) {
    const key = normalizeLocationKey(location.address, location.lat, location.lng);
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    unique.push(location);
    if (unique.length >= limit) {
      break;
    }
  }

  return unique.map(({ lat, lng, address, placeId }) => ({
    lat,
    lng,
    address,
    placeId,
  }));
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
      const raw = location._raw || {};
      const source = raw.source || 'unknown';
      
      // Source weighting (Photon tends to have better ranking for POIs)
      if (source === 'photon') {
        score += 20;
      } else if (source === 'nominatim') {
        score += 10;
      }

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
      const type = raw.type || raw.properties?.type || '';
      const placeType = raw.class || raw.properties?.osm_type || '';
      if (['city', 'town', 'village', 'locality'].includes(type)) {
        score += 30;
      }
      if (['amenity', 'tourism', 'shop'].includes(placeType)) {
        score += 15;
      }
      
      // Prefer places with higher importance
      const importance = parseFloat(raw.importance || raw.properties?.importance || 0);
      score += importance * 50;
      
      // Penalize very long addresses (usually less relevant)
      if (address.length > 150) {
        score -= 10;
      }
      
      // Prefer places with names over generic addresses
      const rawName = raw.name || raw.namedetails?.name || raw.properties?.name;
      if (rawName && rawName.toLowerCase().includes(lowerQuery)) {
        score += 25;
      }

      // Boost proximity matches if available
      if (raw.properties?.distance) {
        score += Math.max(0, 10 - raw.properties.distance);
      }
      
      return { ...location, _score: score };
    })
    .filter(location => location._score > 10) // Filter out low-scoring results
    .sort((a, b) => b._score - a._score); // Sort by score descending
}

function normalizeLocationKey(address: string, lat: number, lng: number): string {
  const roundedLat = lat.toFixed(4);
  const roundedLng = lng.toFixed(4);
  return `${address.toLowerCase().trim()}-${roundedLat}-${roundedLng}`;
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
