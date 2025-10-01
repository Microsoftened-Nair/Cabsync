import { useState, useRef, useEffect } from 'react';
import { debounce } from '../utils';
import { Location, MapboxFeature } from '../types';

interface UseLocationSearchProps {
  onLocationSelect?: (location: Location) => void;
  delay?: number;
}

export function useLocationSearch({ onLocationSelect, delay = 300 }: UseLocationSearchProps = {}) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<Location[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const searchLocations = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setSuggestions([]);
      setIsLoading(false);
      return;
    }

    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    setIsLoading(true);

    try {
      const mapboxToken = import.meta.env.VITE_MAPBOX_TOKEN;
      
      if (!mapboxToken || import.meta.env.VITE_MODE === 'MOCK') {
        // Use mock data in development
        const mockResults = generateMockSuggestions(searchQuery);
        setSuggestions(mockResults);
        setIsLoading(false);
        return;
      }

      const response = await fetch(
        `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(searchQuery)}.json?` +
        new URLSearchParams({
          access_token: mapboxToken,
          country: 'IN',
          types: 'place,postcode,address,poi',
          limit: '5',
          proximity: '77.2090,28.6139', // Delhi coordinates as default
        }),
        { signal: abortControllerRef.current.signal }
      );

      if (!response.ok) throw new Error('Search failed');

      const data = await response.json();
      const locations: Location[] = data.features.map((feature: MapboxFeature) => ({
        lat: feature.center[1],
        lng: feature.center[0],
        address: feature.place_name,
        placeId: feature.id,
      }));

      setSuggestions(locations);
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        console.error('Location search error:', error);
        setSuggestions([]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const debouncedSearch = debounce(searchLocations, delay);

  useEffect(() => {
    debouncedSearch(query);
  }, [query]);

  const handleLocationSelect = (location: Location) => {
    setQuery(location.address);
    setIsOpen(false);
    setSuggestions([]);
    onLocationSelect?.(location);
  };

  const clearSearch = () => {
    setQuery('');
    setSuggestions([]);
    setIsOpen(false);
  };

  return {
    query,
    setQuery,
    suggestions,
    isLoading,
    isOpen,
    setIsOpen,
    handleLocationSelect,
    clearSearch,
  };
}

function generateMockSuggestions(query: string): Location[] {
  const mockLocations = [
    { lat: 28.6139, lng: 77.2090, address: 'Connaught Place, New Delhi' },
    { lat: 28.5355, lng: 77.3910, address: 'Noida City Centre, Noida' },
    { lat: 28.4595, lng: 77.0266, address: 'Cyber Hub, Gurugram' },
    { lat: 28.6692, lng: 77.4538, address: 'Akshardham Temple, Delhi' },
    { lat: 28.5274, lng: 77.2065, address: 'Hauz Khas Village, Delhi' },
    { lat: 28.6508, lng: 77.2311, address: 'Karol Bagh, Delhi' },
    { lat: 28.6304, lng: 77.2177, address: 'India Gate, New Delhi' },
    { lat: 28.6562, lng: 77.2410, address: 'Red Fort, Delhi' },
  ];

  return mockLocations
    .filter(location => 
      location.address.toLowerCase().includes(query.toLowerCase())
    )
    .slice(0, 5);
}
