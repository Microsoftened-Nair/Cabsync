import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';
import { Input } from './ui/Input';
import { Button } from './ui/Button';
import { useLocationSearch } from '../hooks/useLocationSearch';
import { Location, VehicleType } from '../types';

interface SearchCardProps {
  onSearch: (pickup: Location, dropoff: Location, vehicleType?: VehicleType) => void;
  isLoading?: boolean;
  className?: string;
}

export function SearchCard({ onSearch, isLoading = false, className = '' }: SearchCardProps) {
  const [pickup, setPickup] = useState<Location | null>(null);
  const [dropoff, setDropoff] = useState<Location | null>(null);
  const [vehicleType, setVehicleType] = useState<VehicleType>('auto');

  const pickupSearch = useLocationSearch({
    onLocationSelect: setPickup,
  });

  const dropoffSearch = useLocationSearch({
    onLocationSelect: setDropoff,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (pickup && dropoff) {
      onSearch(pickup, dropoff, vehicleType);
    }
  };

  const canSubmit = pickup && dropoff && !isLoading;

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Where to?</CardTitle>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Pickup Location */}
          <div className="relative">
            <Input
              label="From"
              placeholder="Enter pickup location"
              value={pickupSearch.query}
              onChange={(e) => {
                pickupSearch.setQuery(e.target.value);
                pickupSearch.setIsOpen(true);
              }}
              onFocus={() => pickupSearch.setIsOpen(true)}
              icon={<LocationIcon />}
              rightIcon={
                pickupSearch.query && (
                  <button
                    type="button"
                    onClick={pickupSearch.clearSearch}
                    className="hover:text-text-primary transition-colors"
                  >
                    <XIcon className="h-4 w-4" />
                  </button>
                )
              }
            />
            
            {/* Pickup Suggestions */}
            {pickupSearch.isOpen && (pickupSearch.suggestions.length > 0 || pickupSearch.isLoading) && (
              <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-surface border border-border rounded-lg shadow-lg max-h-64 overflow-y-auto">
                {pickupSearch.isLoading && (
                  <div className="p-3 text-text-secondary text-sm flex items-center space-x-2">
                    <LoadingIcon className="h-4 w-4 animate-spin" />
                    <span>Searching...</span>
                  </div>
                )}
                {pickupSearch.suggestions.map((location, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => pickupSearch.handleLocationSelect(location)}
                    className="w-full p-3 text-left hover:bg-muted/10 transition-colors border-b border-border last:border-b-0"
                  >
                    <div className="text-text-primary text-sm font-medium">
                      {location.address}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Dropoff Location */}
          <div className="relative">
            <Input
              label="To"
              placeholder="Enter destination"
              value={dropoffSearch.query}
              onChange={(e) => {
                dropoffSearch.setQuery(e.target.value);
                dropoffSearch.setIsOpen(true);
              }}
              onFocus={() => dropoffSearch.setIsOpen(true)}
              icon={<LocationIcon />}
              rightIcon={
                dropoffSearch.query && (
                  <button
                    type="button"
                    onClick={dropoffSearch.clearSearch}
                    className="hover:text-text-primary transition-colors"
                  >
                    <XIcon className="h-4 w-4" />
                  </button>
                )
              }
            />
            
            {/* Dropoff Suggestions */}
            {dropoffSearch.isOpen && (dropoffSearch.suggestions.length > 0 || dropoffSearch.isLoading) && (
              <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-surface border border-border rounded-lg shadow-lg max-h-64 overflow-y-auto">
                {dropoffSearch.isLoading && (
                  <div className="p-3 text-text-secondary text-sm flex items-center space-x-2">
                    <LoadingIcon className="h-4 w-4 animate-spin" />
                    <span>Searching...</span>
                  </div>
                )}
                {dropoffSearch.suggestions.map((location, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => dropoffSearch.handleLocationSelect(location)}
                    className="w-full p-3 text-left hover:bg-muted/10 transition-colors border-b border-border last:border-b-0"
                  >
                    <div className="text-text-primary text-sm font-medium">
                      {location.address}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Vehicle Type */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-text-primary">
              Vehicle Type
            </label>
            <div className="grid grid-cols-3 gap-2">
              {(['auto', 'bike', 'car'] as VehicleType[]).map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setVehicleType(type)}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    vehicleType === type
                      ? 'border-accent bg-accent/10 text-accent'
                      : 'border-border hover:border-accent/50 text-text-secondary'
                  }`}
                >
                  <div className="text-center">
                    <div className="text-sm font-medium capitalize">{type}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={!canSubmit}
            loading={isLoading}
            className="w-full"
            size="lg"
          >
            Compare Rides
          </Button>
        </form>

        {/* Quick ETA Display */}
        {pickup && dropoff && (
          <div className="mt-4 pt-4 border-t border-border">
            <div className="text-sm text-text-secondary text-center">
              Distance: ~{Math.round(Math.random() * 5 + 2)}km • ETA: ~{Math.round(Math.random() * 10 + 5)} mins
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Icon components
function LocationIcon({ className }: { className?: string }) {
  return (
    <svg className={`h-4 w-4 ${className}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
      />
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
      />
    </svg>
  );
}

function XIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M6 18L18 6M6 6l12 12"
      />
    </svg>
  );
}

function LoadingIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24">
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}
