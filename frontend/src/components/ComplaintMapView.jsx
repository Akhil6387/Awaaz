import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Users } from 'lucide-react';
import L from 'leaflet';

export default function ComplaintMapView({ complaints, onSelectComplaint }) {
  const defaultCenter = [23.2000, 77.3500];

  const getMarkerIcon = (status) => {
    let color = '#f97316';
    if (status === 'RESOLVED') color = '#22c55e';
    else if (status === 'IN_PROGRESS') color = '#3b82f6';
    else if (status === 'UNDER_REVIEW') color = '#ef4444';

    return L.divIcon({
      className: 'custom-map-pin',
      html: `<div style="background-color: ${color}; width: 26px; height: 26px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 11px;">!</div>`,
      iconSize: [26, 26],
      iconAnchor: [13, 13],
      popupAnchor: [0, -14],
    });
  };

  return (
    <div className="h-[600px] w-full rounded-2xl overflow-hidden border border-slate-200 shadow-md relative">
      <MapContainer
        center={complaints.length > 0 ? [complaints[0].latitude, complaints[0].longitude] : defaultCenter}
        zoom={12}
        scrollWheelZoom={true}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {complaints.map((c) => (
          <Marker
            key={c.id}
            position={[c.latitude, c.longitude]}
            icon={getMarkerIcon(c.status)}
          >
            <Popup>
              <div className="p-1 space-y-2 max-w-xs">
                <div className="flex items-center justify-between gap-2 border-b pb-1 text-[11px]">
                  <span className="font-bold text-slate-700">{c.public_id}</span>
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800">
                    {c.status_display || c.status}
                  </span>
                </div>
                
                <h4 className="font-bold text-xs text-slate-900 line-clamp-2">
                  {c.title}
                </h4>

                <p className="text-[11px] text-slate-500">
                  📍 {c.sub_location}
                </p>

                <div className="flex items-center justify-between pt-1">
                  <span className="text-[11px] font-semibold text-saffron-700 flex items-center gap-1">
                    <Users className="w-3.5 h-3.5" />
                    {c.co_sign_count} Co-signed
                  </span>
                  <button
                    onClick={() => onSelectComplaint(c.id)}
                    className="px-2.5 py-1 bg-slate-900 text-white rounded text-xs font-semibold hover:bg-saffron-600 transition-colors"
                  >
                    View Docket
                  </button>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
