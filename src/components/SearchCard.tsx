import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';
import { Input } from './ui/Input';
import { Button } from './ui/Button';
import { MapPicker } from './MapPicker';
import { useLocationSearch } from '../hooks/useLocationSearch';
import { Location, VehicleType } from '../types';

interface SearchCardProps {
  onSearch: (pickup: Location, dropoff: Location, vehicleType?: VehicleType, seaterCapacity?: number) => void;
  isLoading?: boolean;
  className?: string;
}

export function SearchCard({ onSearch, isLoading = false, className = '' }: SearchCardProps) {
  const [pickup, setPickup] = useState<Location | null>(null);
  const [dropoff, setDropoff] = useState<Location | null>(null);
  const [vehicleType, setVehicleType] = useState<VehicleType>('auto');
  const [seaterCapacity, setSeaterCapacity] = useState<number | undefined>(undefined);
  const [showPickupMap, setShowPickupMap] = useState(false);
  const [showDropoffMap, setShowDropoffMap] = useState(false);

  const pickupSearch = useLocationSearch({
    onLocationSelect: setPickup,
  });

  const dropoffSearch = useLocationSearch({
    onLocationSelect: setDropoff,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (pickup && dropoff) {
      onSearch(pickup, dropoff, vehicleType, seaterCapacity);
    }
  };

  const handlePickupFromMap = (location: Location) => {
    setPickup(location);
    pickupSearch.setQuery(location.address);
  };

  const handleDropoffFromMap = (location: Location) => {
    setDropoff(location);
    dropoffSearch.setQuery(location.address);
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
                <div className="flex items-center space-x-1">
                  {pickupSearch.query && (
                    <button
                      type="button"
                      onClick={pickupSearch.clearSearch}
                      className="hover:text-text-primary transition-colors"
                    >
                      <XIcon className="h-4 w-4" />
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={() => setShowPickupMap(true)}
                    className="p-1 hover:bg-accent/10 rounded transition-colors"
                    title="Select on map"
                  >
                    <MapIcon className="h-4 w-4 text-accent" />
                  </button>
                </div>
              }
            />
            
            {/* Pickup Suggestions */}
            {pickupSearch.isOpen && (pickupSearch.suggestions.length > 0 || pickupSearch.isLoading || (pickupSearch.query && pickupSearch.query.length < 3)) && (
              <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-surface border border-border rounded-lg shadow-lg max-h-64 overflow-y-auto">
                {pickupSearch.isLoading && (
                  <div className="p-3 text-text-secondary text-sm flex items-center space-x-2">
                    <LoadingIcon className="h-4 w-4 animate-spin" />
                    <span>Searching...</span>
                  </div>
                )}
                {!pickupSearch.isLoading && pickupSearch.query && pickupSearch.query.length < 3 && (
                  <div className="p-3 text-text-secondary text-sm">
                    Type at least 3 characters to search...
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
                <div className="flex items-center space-x-1">
                  {dropoffSearch.query && (
                    <button
                      type="button"
                      onClick={dropoffSearch.clearSearch}
                      className="hover:text-text-primary transition-colors"
                    >
                      <XIcon className="h-4 w-4" />
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={() => setShowDropoffMap(true)}
                    className="p-1 hover:bg-accent/10 rounded transition-colors"
                    title="Select on map"
                  >
                    <MapIcon className="h-4 w-4 text-accent" />
                  </button>
                </div>
              }
            />
            
            {/* Dropoff Suggestions */}
            {dropoffSearch.isOpen && (dropoffSearch.suggestions.length > 0 || dropoffSearch.isLoading || (dropoffSearch.query && dropoffSearch.query.length < 3)) && (
              <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-surface border border-border rounded-lg shadow-lg max-h-64 overflow-y-auto">
                {dropoffSearch.isLoading && (
                  <div className="p-3 text-text-secondary text-sm flex items-center space-x-2">
                    <LoadingIcon className="h-4 w-4 animate-spin" />
                    <span>Searching...</span>
                  </div>
                )}
                {!dropoffSearch.isLoading && dropoffSearch.query && dropoffSearch.query.length < 3 && (
                  <div className="p-3 text-text-secondary text-sm">
                    Type at least 3 characters to search...
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
                  onClick={() => {
                    setVehicleType(type);
                    // Reset seater capacity when changing vehicle type
                    if (type !== 'car') {
                      setSeaterCapacity(undefined);
                    }
                  }}
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

          {/* Seater Capacity (only for cars) */}
          {vehicleType === 'car' && (
            <div className="space-y-2">
              <label className="block text-sm font-medium text-text-primary">
                Seater Capacity (Optional)
              </label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => setSeaterCapacity(undefined)}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    seaterCapacity === undefined
                      ? 'border-accent bg-accent/10 text-accent'
                      : 'border-border hover:border-accent/50 text-text-secondary'
                  }`}
                >
                  <div className="text-center">
                    <div className="text-sm font-medium">All</div>
                  </div>
                </button>
                <button
                  type="button"
                  onClick={() => setSeaterCapacity(4)}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    seaterCapacity === 4
                      ? 'border-accent bg-accent/10 text-accent'
                      : 'border-border hover:border-accent/50 text-text-secondary'
                  }`}
                >
                  <div className="text-center">
                    <div className="text-sm font-medium">4 Seater</div>
                  </div>
                </button>
                <button
                  type="button"
                  onClick={() => setSeaterCapacity(6)}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    seaterCapacity === 6
                      ? 'border-accent bg-accent/10 text-accent'
                      : 'border-border hover:border-accent/50 text-text-secondary'
                  }`}
                >
                  <div className="text-center">
                    <div className="text-sm font-medium">6 Seater</div>
                  </div>
                </button>
              </div>
            </div>
          )}

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

        {/* Quick ETA Display removed per UI request */}
      </CardContent>

      {/* Map Modals */}
      {showPickupMap && (
        <MapPicker
          initialLocation={pickup || undefined}
          onLocationSelect={handlePickupFromMap}
          onClose={() => setShowPickupMap(false)}
          title="Select Pickup Location"
        />
      )}

      {showDropoffMap && (
        <MapPicker
          initialLocation={dropoff || undefined}
          onLocationSelect={handleDropoffFromMap}
          onClose={() => setShowDropoffMap(false)}
          title="Select Drop-off Location"
        />
      )}
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

function MapIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
      />
    </svg>
  );
}
