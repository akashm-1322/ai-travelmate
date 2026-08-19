import React from "react";

export default function BookingPanel() {

  return (
    <div className="rounded-2xl bg-white p-6 shadow-xl">

      <div className="flex items-center justify-between">

        <div>
          <h2 className="text-xl font-bold text-slate-900">
            Travel Bookings
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Flights, hotels and experiences
          </p>
        </div>

        <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-600">
          BOOKING HUB
        </span>

      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-3">

        <button className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-left transition hover:-translate-y-1 hover:shadow-md">
          <div className="text-2xl">✈️</div>
          <p className="mt-2 font-bold text-slate-900">
            Flights
          </p>
          <p className="text-xs text-slate-500">
            Search & book
          </p>
        </button>

        <button className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-left transition hover:-translate-y-1 hover:shadow-md">
          <div className="text-2xl">🏨</div>
          <p className="mt-2 font-bold text-slate-900">
            Hotels
          </p>
          <p className="text-xs text-slate-500">
            Find stays
          </p>
        </button>

        <button className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-left transition hover:-translate-y-1 hover:shadow-md">
          <div className="text-2xl">🎟️</div>
          <p className="mt-2 font-bold text-slate-900">
            Experiences
          </p>
          <p className="text-xs text-slate-500">
            Discover activities
          </p>
        </button>

      </div>

    </div>
  );
}