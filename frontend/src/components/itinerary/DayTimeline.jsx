import {
    Clock,
    Route,
  } from "lucide-react";
  
  import PlaceCard from "./PlaceCard";
  
  
  export default function DayTimeline({
    day,
  }) {
    const places =
      day.places || [];
  
    return (
      <section className="rounded-3xl border border-white/10 bg-slate-900/60 p-5 md:p-7">
  
        {/* Header */}
        <div className="mb-7 flex flex-col justify-between gap-4 border-b border-white/10 pb-5 md:flex-row md:items-center">
  
          <div>
  
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-400">
              Travel Plan
            </div>
  
            <h2 className="mt-1 text-2xl font-bold">
              Day {day.day}
            </h2>
  
          </div>
  
          <div className="flex flex-wrap gap-3">
  
            <SummaryItem
              icon={<Route size={16} />}
              value={`${Number(
                day.total_distance_km || 0
              ).toFixed(2)} km`}
            />
  
            <SummaryItem
              icon={<Clock size={16} />}
              value={
                `${day.start_time || "—"} → ${
                  day.end_time || "—"
                }`
              }
            />
  
          </div>
  
        </div>
  
        {/* Places */}
        {places.length === 0 ? (
          <div className="py-12 text-center text-slate-500">
            No places scheduled for this day.
          </div>
        ) : (
          places.map(
            (place, index) => (
              <PlaceCard
                key={
                  `${day.day}-${index}-${place.name}`
                }
                place={place}
                index={index}
              />
            )
          )
        )}
  
        {/* Day warnings */}
        {day.time_validation?.warnings?.length > 0 && (
          <div className="mt-4 rounded-xl border border-yellow-500/20 bg-yellow-500/5 p-4">
  
            <div className="mb-2 font-semibold text-yellow-400">
              TravelMate notices
            </div>
  
            {day.time_validation.warnings.map(
              (warning, index) => (
                <div
                  key={index}
                  className="text-sm text-yellow-200/80"
                >
                  • {warning}
                </div>
              )
            )}
  
          </div>
        )}
  
      </section>
    );
  }
  
  
  function SummaryItem({
    icon,
    value,
  }) {
    return (
      <div className="flex items-center gap-2 rounded-xl bg-white/5 px-3 py-2 text-sm text-slate-300">
        {icon}
        {value}
      </div>
    );
  }