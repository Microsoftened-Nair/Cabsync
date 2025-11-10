import { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Location } from '../types';
import { Button } from './ui/Button';

// Fix for default marker icon in Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

interface MapPickerProps {
  initialLocation?: Location;
  onLocationSelect: (location: Location) => void;
  onClose: () => void;
  title?: string;
}

// Component to handle map clicks
function MapClickHandler({ onLocationClick }: { onLocationClick: (lat: number, lng: number) => void }) {
  useMapEvents({
    click: (e) => {
      onLocationClick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

// Component to fly to location
function FlyToLocation({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, zoom, { duration: 1.5 });
  }, [center, zoom, map]);
  return null;
}

export function MapPicker({ 
  initialLocation, 
  onLocationSelect, 
  onClose,
  title = 'Select Location'
}: MapPickerProps) {
  const [markerPosition, setMarkerPosition] = useState<[number, number]>(
    initialLocation ? [initialLocation.lat, initialLocation.lng] : [28.6139, 77.2090]
  );
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(initialLocation || null);
  const [isGeocoding, setIsGeocoding] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Location[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [flyToCenter, setFlyToCenter] = useState<[number, number]>(markerPosition);

  useEffect(() => {
    if (initialLocation) {
      reverseGeocode(initialLocation.lng, initialLocation.lat);
    }
  }, []);

  const reverseGeocode = async (lng: number, lat: number) => {
    setIsGeocoding(true);
    try {
      // Using Nominatim (OpenStreetMap) for reverse geocoding - completely free!
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&countrycodes=in&addressdetails=1`,
        {
          headers: {
            'User-Agent': 'CabSync-App/1.0'
          }
        }
      );

      if (!response.ok) throw new Error('Geocoding failed');

      const data = await response.json();
      const location: Location = {
        lat,
        lng,
        address: data.display_name || `${lat.toFixed(6)}, ${lng.toFixed(6)}`,
        placeId: data.place_id?.toString(),
      };
      setSelectedLocation(location);
    } catch (error) {
      console.error('Reverse geocoding error:', error);
      setSelectedLocation({
        lat,
        lng,
        address: `${lat.toFixed(6)}, ${lng.toFixed(6)}`,
      });
    } finally {
      setIsGeocoding(false);
    }
  };

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      // Using Nominatim (OpenStreetMap) for geocoding - completely free!
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&countrycodes=in&limit=5&addressdetails=1`,
        {
          headers: {
            'User-Agent': 'CabSync-App/1.0'
          }
        }
      );

      if (!response.ok) throw new Error('Search failed');

      const data = await response.json();
      const locations: Location[] = data.map((item: any) => ({
        lat: parseFloat(item.lat),
        lng: parseFloat(item.lon),
        address: item.display_name,
        placeId: item.place_id?.toString(),
      }));

      setSearchResults(locations);
    } catch (error) {
      console.error('Location search error:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSearchSelect = (location: Location) => {
    setMarkerPosition([location.lat, location.lng]);
    setFlyToCenter([location.lat, location.lng]);
    setSelectedLocation(location);
    setSearchResults([]);
    setSearchQuery('');
  };

  const handleMapClick = async (lat: number, lng: number) => {
    setMarkerPosition([lat, lng]);
    await reverseGeocode(lng, lat);
  };

  const handleMarkerDrag = (e: L.DragEndEvent) => {
    const marker = e.target as L.Marker;
    const position = marker.getLatLng();
    setMarkerPosition([position.lat, position.lng]);
    reverseGeocode(position.lng, position.lat);
  };

  const handleConfirm = () => {
    if (selectedLocation) {
      onLocationSelect(selectedLocation);
      onClose();
    }
  };

  const handleUseCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setMarkerPosition([latitude, longitude]);
          setFlyToCenter([latitude, longitude]);
          reverseGeocode(longitude, latitude);
        },
        (error) => {
          console.error('Error getting location:', error);
          alert('Could not get your location. Please enable location services.');
        }
      );
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-surface rounded-xl shadow-2xl max-w-4xl w-full h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="text-xl font-semibold text-text-primary">{title}</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-muted/10 rounded-lg transition-colors"
          >
            <XIcon className="h-5 w-5 text-text-secondary" />
          </button>
        </div>

        {/* Search Bar */}
        <div className="p-4 border-b border-border">
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                handleSearch(e.target.value);
              }}
              placeholder="Search for a location..."
              className="w-full px-4 py-2 pl-10 bg-background border border-border rounded-lg text-text-primary placeholder:text-text-secondary focus:outline-none focus:ring-2 focus:ring-accent"
            />
            <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-text-secondary" />
            {isSearching && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <LoadingIcon className="h-5 w-5 animate-spin text-accent" />
              </div>
            )}
          </div>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="absolute z-10 mt-1 w-[calc(100%-2rem)] bg-surface border border-border rounded-lg shadow-lg max-h-60 overflow-y-auto">
              {searchResults.map((location, index) => (
                <button
                  key={index}
                  onClick={() => handleSearchSelect(location)}
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

        {/* Quick Actions */}
        <div className="px-4 py-2 border-b border-border">
          <button
            onClick={handleUseCurrentLocation}
            className="flex items-center space-x-2 text-sm text-accent hover:text-accent/80 transition-colors"
          >
            <LocationIcon className="h-4 w-4" />
            <span>Use current location</span>
          </button>
        </div>

        {/* Map Container */}
        <div className="flex-1 relative">
          <MapContainer
            center={markerPosition}
            zoom={initialLocation ? 14 : 11}
            style={{ width: '100%', height: '100%' }}
            zoomControl={true}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <Marker 
              position={markerPosition} 
              draggable={true}
              eventHandlers={{
                dragend: handleMarkerDrag,
              }}
            />
            <MapClickHandler onLocationClick={handleMapClick} />
            <FlyToLocation center={flyToCenter} zoom={14} />
          </MapContainer>
          
          {/* Location Info Overlay */}
          {selectedLocation && (
            <div className="absolute bottom-4 left-4 right-4 bg-surface/95 backdrop-blur-sm border border-border rounded-lg p-4 shadow-lg">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-sm font-medium text-text-primary mb-1">
                    Selected Location
                  </h3>
                  <p className="text-sm text-text-secondary">
                    {isGeocoding ? 'Loading address...' : selectedLocation.address}
                  </p>
                  <p className="text-xs text-text-secondary mt-1">
                    {selectedLocation.lat.toFixed(6)}, {selectedLocation.lng.toFixed(6)}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-border flex items-center justify-between">
          <p className="text-sm text-text-secondary">
            Click on the map or drag the marker to select a location
          </p>
          <div className="flex space-x-3">
            <Button
              variant="outline"
              onClick={onClose}
            >
              Cancel
            </Button>
            <Button
              onClick={handleConfirm}
              disabled={!selectedLocation || isGeocoding}
            >
              Confirm Location
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Icon Components
function XIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

function SearchIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  );
}

function LocationIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  );
}

function LoadingIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
    </svg>
  );
}
