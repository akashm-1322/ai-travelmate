import React from "react";


export default function ItineraryPanel({
  itinerary,
}) {
  if (!itinerary) {
    return (
      <div className="rounded-2xl bg-white p-6 shadow-xl">

        <h2 className="text-xl font-bold text-slate-900">
          Your Itinerary
        </h2>

        <p className="mt-2 text-sm text-slate-500">
          Generate a trip above and your optimized itinerary will appear here.
        </p>

      </div>
    );
  }


  return (
    <div className="rounded-2xl bg-white p-6 shadow-xl">

      <div className="flex items-center justify-between">

        <div>

          <h2 className="text-xl font-bold text-slate-900">
            {itinerary.city} Itinerary
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            AI-generated, route-optimized and scheduled
          </p>

        </div>

        <span
          className={
            itinerary
              ?.time_validation
              ?.valid
              ? "rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700"
              : "rounded-full bg-red-50 px-3 py-1 text-xs font-bold text-red-700"
          }
        >
          {
            itinerary
              ?.time_validation
              ?.valid
              ? "✓ VALID"
              : "⚠ REVIEW"
          }
        </span>

      </div>


      <div className="mt-6 space-y-6">

        {itinerary.days?.map(
          (day) => (

            <div
              key={day.day}
              className="rounded-2xl border border-slate-200 bg-slate-50 p-5"
            >

              <div className="flex flex-wrap items-center justify-between gap-3">

                <h3 className="text-lg font-extrabold text-slate-900">
                  Day {day.day}
                </h3>

                <div className="flex gap-2">

                  <Badge>
                    📏{" "}
                    {Number(
                      day.total_distance_km || 0
                    ).toFixed(2)}
                    {" "}km
                  </Badge>

                  <Badge>
                    🕐{" "}
                    {day.start_time || "—"}
                    {" → "}
                    {day.end_time || "—"}
                  </Badge>

                </div>

              </div>


              <div className="mt-5 space-y-3">

                {day.places?.map(
                  (
                    place,
                    index
                  ) => (

                    <div
                      key={
                        `${day.day}-${index}-${place.name}`
                      }
                      className="flex gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
                    >

                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-100 font-bold text-blue-700">
                        {index + 1}
                      </div>


                      <div className="min-w-0 flex-1">

                        <div className="flex flex-wrap items-start justify-between gap-2">

                          <div>

                            <p className="font-bold text-slate-900">
                              {place.name}
                            </p>

                            <p className="mt-1 text-xs capitalize text-slate-500">
                              {
                                place.category
                                  ?.replaceAll(
                                    "_",
                                    " "
                                  ) ||
                                "place"
                              }
                            </p>

                          </div>


                          <div className="text-right text-xs text-slate-500">

                            <div className="font-bold text-slate-800">
                              {
                                place.arrival_time ||
                                "—"
                              }
                              {" → "}
                              {
                                place.departure_time ||
                                "—"
                              }
                            </div>

                          </div>

                        </div>


                        <div className="mt-3 flex flex-wrap gap-2 text-xs">

                          <Badge>
                            🚗{" "}
                            {
                              place.travel_time_minutes ||
                              0
                            }
                            {" "}min
                          </Badge>

                          <Badge>
                            📏{" "}
                            {Number(
                              place.distance_from_previous_km ||
                              0
                            ).toFixed(2)}
                            {" "}km
                          </Badge>

                          <Badge>
                            ⏱{" "}
                            {
                              place.visit_duration_minutes ||
                              0
                            }
                            {" "}min visit
                          </Badge>

                        </div>


                        {place.map_url && (
                          <a
                            href={
                              place.map_url
                            }
                            target="_blank"
                            rel="noreferrer"
                            className="mt-3 inline-block text-xs font-bold text-blue-600 hover:text-blue-800"
                          >
                            View map →
                          </a>
                        )}

                      </div>

                    </div>

                  )
                )}

              </div>

            </div>

          )
        )}

      </div>

    </div>
  );
}


function Badge({
  children,
}) {
  return (
    <span className="rounded-full bg-slate-100 px-2.5 py-1 font-medium text-slate-600">
      {children}
    </span>
  );
}