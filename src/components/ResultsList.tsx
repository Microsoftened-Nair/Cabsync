import React from 'react';
import { RideResult } from '../types';
import { Card } from './ui/Card';
import { Button } from './ui/Button';
import { LoadingSkeleton } from './ui/Loading';

const providerLabels: Record<string, string> = {
  uber: 'Uber',
  ola: 'Ola',
  rapido: 'Rapido',
  indrive: 'inDrive',
};

interface ResultsListProps {
  results: RideResult[];
  isLoading?: boolean;
  className?: string;
}

export function ResultsList({ results, isLoading = false, className = '' }: ResultsListProps) {
  if (isLoading) {
    return (
      <div className={`space-y-4 ${className}`}>
        <h2 className="text-xl font-semibold text-text-primary mb-4">Comparing rides...</h2>
        {[...Array(4)].map((_, index) => (
          <Card key={index} className="animate-pulse">
            <LoadingSkeleton lines={3} avatar />
          </Card>
        ))}
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className={`text-center py-12 ${className}`}>
        <div className="text-6xl mb-4">🚗</div>
        <h3 className="text-lg font-medium text-text-primary mb-2">No rides found</h3>
        <p className="text-text-secondary">Try adjusting your pickup or dropoff location.</p>
      </div>
    );
  }

  return (
    <div className={className}>
      <h2 className="text-xl font-semibold text-text-primary mb-4">
        Available rides ({results.length})
      </h2>
      
      <div className="space-y-3">
        {results.map((result, index) => (
          <ResultCard key={index} result={result} />
        ))}
      </div>
    </div>
  );
}

interface ResultCardProps {
  result: RideResult;
}

function ResultCard({ result }: ResultCardProps) {
  const handleBookRide = () => {
    if (result.deepLink) {
      window.open(result.deepLink, '_blank');
    }
  };

  return (
    <Card hover className="transition-all duration-200 hover:scale-[1.01]">
      <div className="flex items-center justify-between">
        {/* Left Section: Provider & Service */}
        <div className="flex items-center space-x-4">
          <div className="flex-shrink-0">
            <ProviderLogo provider={result.provider} />
          </div>
          
          <div className="min-w-0 flex-1">
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-semibold text-text-primary truncate">
                {result.serviceType}
              </h3>
              {result.surge && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-danger/10 text-danger">
                  {result.surge.toFixed(1)}x surge
                </span>
              )}
            </div>
            
            <div className="flex items-center space-x-3 text-sm text-text-secondary mt-1">
              <span className="flex items-center space-x-1">
                <ClockIcon className="h-4 w-4" />
                <span>{result.eta.text}</span>
              </span>
              <span className="flex items-center space-x-1">
                <RouteIcon className="h-4 w-4" />
                <span>{formatDistance(result.distance)}</span>
              </span>
              {result.meta?.rating && (
                <span className="flex items-center space-x-1">
                  <StarIcon className="h-4 w-4 text-yellow-500" />
                  <span>{result.meta.rating.toFixed(1)}</span>
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Right Section: Price & Action */}
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-2xl font-bold text-text-primary">
              {formatPrice(result.price.value, result.price.currency)}
            </div>
            {result.price.confidence < 0.9 && (
              <div className="text-xs text-text-secondary">
                ~{Math.round(result.price.confidence * 100)}% accurate
              </div>
            )}
          </div>
          
          <Button onClick={handleBookRide} size="lg">
            Book Now
          </Button>
        </div>
      </div>

      {/* Additional Details */}
      {result.meta && (
        <div className="mt-4 pt-4 border-t border-border flex items-center justify-between text-sm text-text-secondary">
          <div className="flex items-center space-x-4">
            {result.meta.vehicleCapacity && (
              <span className="flex items-center space-x-1">
                <UsersIcon className="h-4 w-4" />
                <span>{result.meta.vehicleCapacity} seats</span>
              </span>
            )}
            {result.meta.co2Estimate && (
              <span className="flex items-center space-x-1">
                <LeafIcon className="h-4 w-4 text-green-500" />
                <span>{formatCO2(result.meta.co2Estimate)}</span>
              </span>
            )}
          </div>
          
          <div className="text-xs">
            {providerLabels[result.provider] || result.provider}
          </div>
        </div>
      )}
    </Card>
  );
}

function ProviderLogo({ provider }: { provider: string }) {
  const logos = {
    uber: '🚗',
    ola: '🚕',
    rapido: '🏍️',
    indrive: '🚘',
  };

  const label = providerLabels[provider] || provider.charAt(0).toUpperCase() + provider.slice(1);
  const symbol = logos[provider as keyof typeof logos];

  return (
    <div
      className="w-12 h-12 rounded-xl bg-surface border border-border flex items-center justify-center text-2xl"
      title={label}
    >
      {symbol || label[0]}
    </div>
  );
}

// Utility functions
function formatPrice(value: number, currency: string = '₹'): string {
  return `${currency}${Math.round(value)}`;
}

function formatDistance(meters: number): string {
  if (meters < 1000) {
    return `${Math.round(meters)}m`;
  }
  return `${(meters / 1000).toFixed(1)}km`;
}

function formatCO2(grams: number): string {
  if (grams < 1000) {
    return `${Math.round(grams)}g CO₂`;
  }
  return `${(grams / 1000).toFixed(1)}kg CO₂`;
}

// Icon components
function ClockIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function RouteIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
    </svg>
  );
}

function StarIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
    </svg>
  );
}

function UsersIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  );
}

function LeafIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
    </svg>
  );
}
