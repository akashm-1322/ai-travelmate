import React from "react";

export default function GroupTravel() {

  return (
    <div className="rounded-2xl bg-white p-6 shadow-xl">

      <div className="flex items-center gap-3">

        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100">
          👥
        </div>

        <div>
          <h2 className="font-bold text-slate-900">
            Group Travel
          </h2>

          <p className="text-xs text-slate-500">
            Shared trip & expenses
          </p>
        </div>

      </div>

      <div className="mt-5 rounded-xl bg-slate-50 p-4">

        <div className="flex justify-between">
          <span className="text-sm text-slate-500">
            Group members
          </span>

          <span className="font-bold text-slate-900">
            1
          </span>
        </div>

        <div className="mt-3 flex justify-between">
          <span className="text-sm text-slate-500">
            Shared expenses
          </span>

          <span className="font-bold text-slate-900">
            ₹0
          </span>
        </div>

      </div>

      <button className="mt-4 w-full rounded-xl border border-emerald-600 py-2.5 font-semibold text-emerald-700 transition hover:bg-emerald-50">
        + Create Group Trip
      </button>

    </div>
  );
}