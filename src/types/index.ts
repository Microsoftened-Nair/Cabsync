export interface Location {
  lat: number;
  lng: number;
  address: string;
  placeId?: string;
}

export interface RideRequest {
  pickup: Location;
  dropoff: Location;
  when?: Date;
  vehicleType?: VehicleType;
  seaterCapacity?: number;
}

export type RideProvider = 'uber' | 'ola' | 'rapido' | 'indrive';

export interface RideResult {
  provider: RideProvider;
  serviceType: string;
  price: {
    value: number;
    currency: string;
    confidence: number; // 0-1, higher for official APIs
  };
  eta: {
    seconds: number;
    text: string;
  };
  distance: number; // in meters
  surge?: number;
  deepLink: string;
  meta?: {
    vehicleCapacity?: number;
    rating?: number;
    co2Estimate?: number; // grams per trip
  };
}

export interface CompareResponse {
  results: RideResult[];
  meta: {
    queriedAt: string;
    cacheKey: string;
    totalProviders: number;
    failedProviders: string[];
  };
}

export type VehicleType = 'auto' | 'bike' | 'car' | 'car-4' | 'car-6' | 'suv';

export type SortOption = 'cheapest' | 'fastest' | 'recommended';

export interface FilterOptions {
  sortBy: SortOption;
  vehicleTypes: VehicleType[];
  showCO2: boolean;
  maxPrice?: number;
  maxETA?: number;
}

export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  preferences: {
    defaultVehicleType: VehicleType;
    favoriteLocations: Location[];
    theme: 'dark' | 'light' | 'system';
  };
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

// Mapbox types
export interface MapboxFeature {
  id: string;
  place_name: string;
  center: [number, number];
  geometry: {
    coordinates: [number, number];
    type: 'Point';
  };
  properties: {
    address?: string;
    category?: string;
  };
}

// Theme types
export type Theme = 'dark' | 'light';

export interface ThemeConfig {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}
