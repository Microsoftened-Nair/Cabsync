import React, { useState } from 'react';
import { Header } from '../components/Header';
import { SearchCard } from '../components/SearchCard';
import { ResultsList } from '../components/ResultsList';
import { rideService } from '../services/api';
import { Location, VehicleType, RideResult } from '../types';

export default function RidesPage() {
  const [results, setResults] = useState<RideResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (pickup: Location, dropoff: Location, vehicleType?: VehicleType) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await rideService.compareRides({ pickup, dropoff, vehicleType, when: new Date() });
      setResults(response.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch ride data');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Header />
  <main id="main" className="flex-1 container mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          <div className="lg:w-[440px] space-y-6">
            <SearchCard onSearch={handleSearch} isLoading={isLoading} />
            {results.length > 0 && (
              <div className="bg-surface rounded-xl p-4 border border-border">
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div>
                    <div className="text-lg font-semibold text-text-primary">
                      ₹{Math.min(...results.map((r) => r.price.value))}
                    </div>
                    <div className="text-sm text-text-secondary">Cheapest</div>
                  </div>
                  <div>
                    <div className="text-lg font-semibold text-text-primary">
                      {Math.min(...results.map((r) => Math.round(r.eta.seconds / 60)))}m
                    </div>
                    <div className="text-sm text-text-secondary">Fastest</div>
                  </div>
                </div>
              </div>
            )}
          </div>
          <div className="flex-1">
            {error && (
              <div className="bg-danger/10 border border-danger/20 rounded-lg p-4 mb-6">
                <div className="flex items-center space-x-2">
                  <div className="text-danger">⚠️</div>
                  <div className="text-danger font-medium">Error</div>
                </div>
                <div className="text-danger/80 text-sm mt-1">{error}</div>
              </div>
            )}
            <ResultsList results={results} isLoading={isLoading} />
          </div>
        </div>
      </main>
      <footer className="border-t border-border bg-surface/50 py-8">
        <div className="container mx-auto px-4 text-center">
          <p className="text-text-secondary text-sm">Made with ❤️ to help you find the best ride options</p>
          <p className="text-text-secondary text-xs mt-2">RideMeta • Compare rides across multiple platforms</p>
        </div>
      </footer>
    </div>
  );
}
