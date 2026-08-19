import {
    Clock3,
    ExternalLink,
    MapPin,
    Route,
  } from "lucide-react";
  
  import {
    formatCategory,
    getCategoryIcon,
  } from "../../utils/placeUtils";
  
  
  export default function PlaceCard({
    place,
    index,
  }) {
    const icon = getCategoryIcon(
      place.category
    );
  
    const mapUrl =
      place.map_url ||
      (
        place.latitude &&
        place.longitude
          ? `https://www.openstreetmap.org/?mlat=${place.latitude}&mlon=${place.longitude}`
          : null
      );
  
    return (
      <div className="relative">
  
        {/* Timeline line */}
        <div className="absolute left-[21px] top-11 bottom-[-22px] w-px bg-slate-700 last:hidden" />
  
        <div className="flex gap-4">
  
          {/* Timeline marker */}
          <div className="relative z-10 flex h-11 w-11 shrink-0 items-center justify-center rounded-full border border-white/10 bg-slate-900 text-xl">
            {icon}
          </div>
  
          {/* Place card */}
          <div className="mb-6 flex-1 rounded-2xl border border-white/10 bg-white/[0.04] p-5">
  
            <div className="flex flex-col justify-between gap-4 md:flex-row">
  
              <div>
  
                <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-blue-400">
                  Stop {index + 1}
                  {" • "}
                  {formatCategory(
                    place.category
                  )}
                </div>
  
                <h3 className="text-lg font-bold text-white">
                  {place.name}
                </h3>
  
                {place.address && (
                  <div className="mt-2 flex items-start gap-2 text-sm text-slate-400">
                    <MapPin
                      size={15}
                      className="mt-0.5 shrink-0"
                    />
  
                    {place.address}
                  </div>
                )}
  
              </div>
  
              {/* Time */}
              <div className="flex gap-5 text-sm">
  
                <div>
                  <div className="text-xs text-slate-500">
                    Arrival
                  </div>
  
                  <div className="font-semibold">
                    {place.arrival_time || "—"}
                  </div>
                </div>
  
                <div>
                  <div className="text-xs text-slate-500">
                    Departure
                  </div>
  
                  <div className="font-semibold">
                    {place.departure_time || "—"}
                  </div>
                </div>
  
              </div>
  
            </div>
  
            {/* Metrics */}
            <div className="mt-5 grid gap-3 sm:grid-cols-3">
  
              <Metric
                icon={<Route size={15} />}
                label="Distance"
                value={`${Number(
                  place.distance_from_previous_km || 0
                ).toFixed(2)} km`}
              />
  
              <Metric
                icon={<Clock3 size={15} />}
                label="Travel"
                value={`${place.travel_time_minutes || 0} min`}
              />
  
              <Metric
                icon={<Clock3 size={15} />}
                label="Visit"
                value={`${place.visit_duration_minutes || 0} min`}
              />
  
            </div>
  
            {/* Opening hours */}
            {place.opening_hours && (
              <div className="mt-4 text-xs text-slate-500">
                Opening hours:{" "}
                <span className="text-slate-300">
                  {place.opening_hours}
                </span>
              </div>
            )}
  
            {/* Map */}
            {mapUrl && (
              <a
                href={mapUrl}
                target="_blank"
                rel="noreferrer"
                className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-blue-400 hover:text-blue-300"
              >
                View on map
                <ExternalLink size={14} />
              </a>
            )}
  
          </div>
  
        </div>
  
      </div>
    );
  }
  
  
  function Metric({
    icon,
    label,
    value,
  }) {
    return (
      <div className="rounded-xl bg-slate-950/60 p-3">
  
        <div className="flex items-center gap-2 text-xs text-slate-500">
          {icon}
          {label}
        </div>
  
        <div className="mt-1 font-semibold">
          {value}
        </div>
  
      </div>
    );
  }