import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import { MapPin, Navigation, AlertCircle } from 'lucide-react';
import L from 'leaflet';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

function LocationMarker({ position, onPositionChange }) {
  useMapEvents({
    click(e) {
      onPositionChange(e.latlng.lat, e.latlng.lng);
    },
  });

  return position ? (
    <Marker 
      position={position}
      draggable={true}
      eventHandlers={{
        dragend: (e) => {
          const marker = e.target;
          const pos = marker.getLatLng();
          onPositionChange(pos.lat, pos.lng);
        },
      }}
    />
  ) : null;
}

export default function MapPicker({ initialCoords, onLocationSelect }) {
  const [coords, setCoords] = useState(initialCoords || { lat: 23.2332, lng: 77.4350 });
  const [accuracy, setAccuracy] = useState(null);
  const [isLocating, setIsLocating] = useState(false);
  const [gpsError, setGpsError] = useState(null);

  const locateUser = () => {
    setIsLocating(true);
    setGpsError(null);
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const newPos = {
            lat: pos.coords.latitude,
            lng: pos.coords.longitude,
          };
          setCoords(newPos);
          setAccuracy(Math.round(pos.coords.accuracy));
          setIsLocating(false);
          onLocationSelect({
            lat: newPos.lat,
            lng: newPos.lng,
            accuracy: Math.round(pos.coords.accuracy),
          });
        },
        (err) => {
          setIsLocating(false);
          setGpsError("GPS signal weak or permission denied. You can tap or drag the pin on the map.");
        },
        { enableHighAccuracy: true, timeout: 8000 }
      );
    } else {
      setIsLocating(false);
      setGpsError("Geolocation is not supported by your browser.");
    }
  };

  const handlePositionChange = (lat, lng) => {
    const updated = { lat, lng };
    setCoords(updated);
    onLocationSelect({
      lat,
      lng,
      accuracy: accuracy || 10,
    });
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 text-xs text-slate-600 font-medium">
          <MapPin className="w-4 h-4 text-saffron-600" />
          <span>Pin-Drop on Map (Tap or drag pin to adjust)</span>
        </div>
        <button
          type="button"
          onClick={locateUser}
          disabled={isLocating}
          className="px-3 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-bold rounded-lg border border-emerald-200 flex items-center gap-1.5 transition-colors"
        >
          <Navigation className={`w-3.5 h-3.5 ${isLocating ? 'animate-spin' : ''}`} />
          <span>{isLocating ? 'Locating GPS...' : 'Auto-Detect GPS'}</span>
        </button>
      </div>

      <div className="h-56 sm:h-64 rounded-xl overflow-hidden border border-slate-300 relative shadow-inner">
        <MapContainer
          center={[coords.lat, coords.lng]}
          zoom={14}
          scrollWheelZoom={false}
          className="h-full w-full"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <LocationMarker
            position={[coords.lat, coords.lng]}
            onPositionChange={handlePositionChange}
          />
        </MapContainer>
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-500 px-1">
        <span>GPS Coordinates: {coords.lat.toFixed(5)}, {coords.lng.toFixed(5)}</span>
        {accuracy && (
          <span className="text-emerald-700 font-medium">
            GPS Accuracy: ±{accuracy}m
          </span>
        )}
      </div>

      {gpsError && (
        <p className="text-[11px] text-amber-700 bg-amber-50 p-2 rounded flex items-center gap-1">
          <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
          {gpsError}
        </p>
      )}
    </div>
  );
}
