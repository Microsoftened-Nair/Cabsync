import { useState, useRef, useEffect } from 'react';
import { debounce } from '../utils';
import { searchLocations } from '../services/geocoding';
import { Location } from '../types';

interface UseLocationSearchProps {
  onLocationSelect?: (location: Location) => void;
  delay?: number;
}

export function useLocationSearch({ onLocationSelect, delay = 600 }: UseLocationSearchProps = {}) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<Location[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const lastQueryRef = useRef<string>('');

  const performSearch = async (searchQuery: string) => {
    const trimmedQuery = searchQuery.trim();
    
    // Don't search if query is too short or hasn't changed
    if (trimmedQuery.length < 3) {
      setSuggestions([]);
      setIsLoading(false);
      return;
    }

    // Skip if query hasn't changed
    if (trimmedQuery === lastQueryRef.current) {
      return;
    }

    lastQueryRef.current = trimmedQuery;

    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    setIsLoading(true);

    try {
      const locations = await searchLocations(trimmedQuery, {
        proximity: [77.2090, 28.6139], // Default to Delhi
        country: 'in',
        limit: 5,
      });
      
      // Only update if this is still the current query
      if (trimmedQuery === lastQueryRef.current) {
        setSuggestions(locations);
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        console.error('Location search error:', error);
        setSuggestions([]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const debouncedSearch = debounce(performSearch, delay);

  useEffect(() => {
    debouncedSearch(query);
  }, [query]);

  const handleLocationSelect = (location: Location) => {
    setQuery(location.address);
    setIsOpen(false);
    setSuggestions([]);
    lastQueryRef.current = location.address;
    onLocationSelect?.(location);
  };

  const clearSearch = () => {
    setQuery('');
    setSuggestions([]);
    setIsOpen(false);
    lastQueryRef.current = '';
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
