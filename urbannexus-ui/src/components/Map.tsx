'use client';

import { MapContainer, TileLayer, Polygon, Popup, Tooltip, useMap } from 'react-leaflet';
// import 'leaflet/dist/leaflet.css'; // Moved to layout.tsx
import { Zone } from '@/types';
import L from 'leaflet';
import { useEffect } from 'react';

// Fix for default Leaflet markers in Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface MapProps {
  zones: Zone[];
  selectedZone: Zone | null;
  onSelectZone: (zone: Zone) => void;
}

// Component to handle auto-fitting bounds
function MapController({ selectedZone }: { selectedZone: Zone | null }) {
  const map = useMap();

  useEffect(() => {
    if (selectedZone && selectedZone.coordinates && selectedZone.coordinates.length > 0) {
      // Create bounds from coordinates
      const bounds = L.latLngBounds(selectedZone.coordinates);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [selectedZone, map]);

  return null;
}

export default function Map({ zones, selectedZone, onSelectZone }: MapProps) {
  // Default center: FAU / Boca Raton
  const defaultCenter: [number, number] = [26.373, -80.101];

  return (
    <MapContainer center={defaultCenter} zoom={16} className="h-full w-full z-10">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      <MapController selectedZone={selectedZone} />

      {zones.map((zone) => (
        <Polygon
          key={zone.zone_id}
          positions={zone.coordinates}
          pathOptions={{
            color: selectedZone?.zone_id === zone.zone_id ? '#ea580c' : '#2563eb', // Orange if selected, Blue if not
            fillColor: selectedZone?.zone_id === zone.zone_id ? '#f97316' : '#3b82f6',
            fillOpacity: selectedZone?.zone_id === zone.zone_id ? 0.6 : 0.4, // Increased opacity
            weight: selectedZone?.zone_id === zone.zone_id ? 3 : 2
          }}
          eventHandlers={{
            click: () => onSelectZone(zone),
            mouseover: (e) => {
              const layer = e.target;
              layer.setStyle({
                fillOpacity: 0.7,
                weight: 4,
                color: '#f97316' // Highlight color (Orange)
              });
            },
            mouseout: (e) => {
              const layer = e.target;
              // Reset to default style based on selection state
              const isSelected = selectedZone?.zone_id === zone.zone_id;
              layer.setStyle({
                fillOpacity: isSelected ? 0.6 : 0.4,
                weight: isSelected ? 3 : 2,
                color: isSelected ? '#ea580c' : '#2563eb'
              });
            }
          }}
        >
          <Tooltip direction="center" offset={[0, 0]} opacity={1} permanent>
            <span className="font-bold text-xs">{zone.name}</span>
          </Tooltip>
          <Popup>
            <div className="font-sans">
              <h3 className="font-bold text-sm">{zone.name}</h3>
              <p className="text-xs text-slate-600">{zone.description}</p>
            </div>
          </Popup>
        </Polygon>
      ))}
    </MapContainer>
  );
}
