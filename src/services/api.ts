import { RideRequest, CompareResponse, Location } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  
  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.message || `HTTP ${response.status}`,
        response.status,
        errorData.code
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    
    // Network or other errors
    throw new ApiError(
      error instanceof Error ? error.message : 'Network error'
    );
  }
}

export const rideService = {
  async compareRides(request: RideRequest): Promise<CompareResponse> {
    const mode = (import.meta.env.VITE_MODE ?? 'LIVE') as string;
    const preferLocalMock = mode === 'CLIENT_MOCK';

    if (preferLocalMock) {
      return generateMockCompareResponse(request);
    }

    try {
      return await apiRequest<CompareResponse>('/api/compare', {
        method: 'POST',
        body: JSON.stringify(request),
      });
    } catch (error) {
  if (mode === 'MOCK') {
        console.warn('[rideService] Falling back to mock data after API error', error);
        return generateMockCompareResponse(request);
      }
      throw error;
    }
  },

  async healthCheck(): Promise<{ status: string }> {
    return apiRequest<{ status: string }>('/api/health');
  },
};

export const authService = {
  async initiateUberAuth(): Promise<{ authUrl: string }> {
    return apiRequest<{ authUrl: string }>('/api/auth/uber');
  },
};

function generateMockCompareResponse(request: RideRequest): Promise<CompareResponse> {
  const toRadians = (value: number) => (value * Math.PI) / 180;

  const computeDistanceKm = (a: Location | undefined, b: Location | undefined) => {
    if (!a || !b) return 6 + Math.random() * 6;
    const earthRadiusKm = 6371;
    const dLat = toRadians(b.lat - a.lat);
    const dLng = toRadians(b.lng - a.lng);
    const lat1 = toRadians(a.lat);
    const lat2 = toRadians(b.lat);

    const haversine =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.sin(dLng / 2) * Math.sin(dLng / 2) * Math.cos(lat1) * Math.cos(lat2);
    const arc = 2 * Math.atan2(Math.sqrt(haversine), Math.sqrt(1 - haversine));
    return Math.max(0.75, earthRadiusKm * arc);
  };

  const when = request.when instanceof Date ? request.when : new Date();
  const distanceKm = computeDistanceKm(request.pickup, request.dropoff);
  const trafficMultiplier = (() => {
    const hour = when.getHours();
    let multiplier = 1;
    if ((hour >= 7 && hour < 10) || (hour >= 17 && hour < 21)) multiplier += 0.3;
    else if (hour >= 22 || hour < 5) multiplier -= 0.15;
    if ([0, 6].includes(when.getDay())) multiplier += 0.05;
    return Math.max(0.8, Math.min(multiplier, 1.5));
  })();

  const serviceCatalog = [
    {
      provider: 'uber' as const,
      serviceType: 'Uber Auto',
      vehicleType: 'auto',
      baseFare: 38,
      perKm: 9.2,
      perMin: 1.15,
      minFare: 85,
      avgSpeed: 25,
      etaRange: [4, 10] as const,
      confidence: 0.93,
      vehicleCapacity: 3,
      rating: 4.65,
      co2PerKm: 95,
      surgeChance: 0.25,
    },
    {
      provider: 'uber' as const,
      serviceType: 'Uber Go',
      vehicleType: 'car',
      baseFare: 55,
      perKm: 11.8,
      perMin: 1.6,
      minFare: 120,
      avgSpeed: 30,
      etaRange: [5, 12] as const,
      confidence: 0.95,
      vehicleCapacity: 4,
      rating: 4.82,
      co2PerKm: 165,
      surgeChance: 0.3,
    },
    {
      provider: 'ola' as const,
      serviceType: 'Ola Auto',
      vehicleType: 'auto',
      baseFare: 34,
      perKm: 9,
      perMin: 1.05,
      minFare: 80,
      avgSpeed: 24,
      etaRange: [4, 11] as const,
      confidence: 0.91,
      vehicleCapacity: 3,
      rating: 4.52,
      co2PerKm: 90,
      surgeChance: 0.28,
    },
    {
      provider: 'ola' as const,
      serviceType: 'Ola Bike',
      vehicleType: 'bike',
      baseFare: 28,
      perKm: 7.1,
      perMin: 0.85,
      minFare: 65,
      avgSpeed: 32,
      etaRange: [3, 9] as const,
      confidence: 0.88,
      vehicleCapacity: 1,
      rating: 4.48,
      co2PerKm: 55,
      surgeChance: 0.18,
    },
    {
      provider: 'rapido' as const,
      serviceType: 'Rapido Bike',
      vehicleType: 'bike',
      baseFare: 25,
      perKm: 6.4,
      perMin: 0.76,
      minFare: 60,
      avgSpeed: 34,
      etaRange: [3, 8] as const,
      confidence: 0.78,
      vehicleCapacity: 1,
      rating: 4.35,
      co2PerKm: 50,
      surgeChance: 0.16,
    },
    {
      provider: 'rapido' as const,
      serviceType: 'Rapido Auto',
      vehicleType: 'auto',
      baseFare: 30,
      perKm: 8.4,
      perMin: 1,
      minFare: 70,
      avgSpeed: 24,
      etaRange: [4, 10] as const,
      confidence: 0.8,
      vehicleCapacity: 3,
      rating: 4.28,
      co2PerKm: 88,
      surgeChance: 0.22,
    },
    {
      provider: 'indrive' as const,
      serviceType: 'inDrive Saver',
      vehicleType: 'car',
      baseFare: 60,
      perKm: 12.2,
      perMin: 1.8,
      minFare: 150,
      avgSpeed: 29,
      etaRange: [6, 13] as const,
      confidence: 0.86,
      vehicleCapacity: 4,
      rating: 4.6,
      co2PerKm: 160,
      surgeChance: 0.27,
    },
    {
      provider: 'indrive' as const,
      serviceType: 'inDrive Plus',
      vehicleType: 'car',
      baseFare: 82,
      perKm: 15.8,
      perMin: 2.35,
      minFare: 200,
      avgSpeed: 31,
      etaRange: [7, 14] as const,
      confidence: 0.9,
      vehicleCapacity: 4,
      rating: 4.74,
      co2PerKm: 175,
      surgeChance: 0.3,
    },
  ];

  const preferredType = request.vehicleType?.toLowerCase();
  const matches = serviceCatalog.filter((service) =>
    preferredType ? service.vehicleType === preferredType : true,
  );
  const relaxedMatches = (() => {
    if (!preferredType) return serviceCatalog;
    if (preferredType === 'auto') return serviceCatalog.filter((service) => ['auto', 'car'].includes(service.vehicleType));
    if (preferredType === 'car') return serviceCatalog.filter((service) => ['car', 'suv'].includes(service.vehicleType));
    return serviceCatalog.filter((service) => service.vehicleType === preferredType);
  })();
  const chosenServices = matches.length > 0 ? matches : relaxedMatches;

  const deepLinks: Record<string, string> = {
    uber: 'https://m.uber.com/ul/?action=setPickup',
    ola: 'https://book.olacabs.com/',
    rapido: 'https://rapido.bike/book/ride',
    indrive: 'https://indrive.com/ride',
  };

  // Simulate network delay similar to backend
  return new Promise<CompareResponse>((resolve) => {
    setTimeout(() => {
      const results = chosenServices.map((service) => {
        const speed = Math.max(service.avgSpeed, 20);
        const tripMinutes = Math.max((distanceKm / speed) * 60, 6) * trafficMultiplier * (0.95 + Math.random() * 0.15);
        let price = service.baseFare + distanceKm * service.perKm * (0.6 + trafficMultiplier * 0.5) + tripMinutes * service.perMin * (0.4 + trafficMultiplier * 0.3);
        price = Math.max(service.minFare, price) * (0.96 + Math.random() * 0.08);

        let surge: number | undefined;
        if (trafficMultiplier > 1.1 && Math.random() < service.surgeChance * trafficMultiplier) {
          surge = parseFloat((1.1 + Math.random() * 0.4).toFixed(2));
          price *= surge;
        }

        const etaMinutes = Math.max(
          0.5,
          (service.etaRange[0] + Math.random() * (service.etaRange[1] - service.etaRange[0])) * (0.85 + (trafficMultiplier - 1) * 0.5),
        );
        const etaSeconds = Math.max(30, Math.round(etaMinutes * 60));
        const etaText = etaMinutes <= 1 ? 'Now' : `${Math.round(etaMinutes)} mins`;

        return {
          provider: service.provider,
          serviceType: service.serviceType,
          price: {
            value: Math.round(Math.max(service.minFare, price) / 5) * 5,
            currency: '₹',
            confidence: service.confidence,
          },
          eta: {
            seconds: etaSeconds,
            text: etaText,
          },
          distance: Math.round(distanceKm * 1000),
          surge,
          deepLink: deepLinks[service.provider],
          meta: {
            vehicleCapacity: service.vehicleCapacity,
            rating: service.rating,
            co2Estimate: Math.round(distanceKm * service.co2PerKm),
          },
        };
      });

      results.sort((a, b) => a.price.value - b.price.value);

      resolve({
        results,
        meta: {
          queriedAt: new Date().toISOString(),
          cacheKey: `mock_${Date.now()}`,
          totalProviders: 4,
          failedProviders: [],
        },
      });
    }, 400 + Math.random() * 400);
  });
}

export { ApiError };
