import React, {
    useState,
  } from "react";
  
  import {
    createItinerary,
  } from "../../services/travelApi";
  
  
  export default function TripPlanner({
    onItineraryGenerated,
    onDestinationChange,
  }) {
    const [destination, setDestination] =
      useState("Chennai");
  
    const [days, setDays] =
      useState(3);
  
    const [travelers, setTravelers] =
      useState(1);
  
    const [interests, setInterests] =
      useState(
        "temples, food, beaches"
      );
  
    const [budget, setBudget] =
      useState("moderate");
  
    const [loading, setLoading] =
      useState(false);
  
    const [error, setError] =
      useState("");
  
  
    const handlePlanTrip =
      async () => {
  
        if (!destination.trim()) {
          setError(
            "Please enter a destination."
          );
  
          return;
        }
  
        setLoading(true);
        setError("");
  
        try {
  
          const result =
            await createItinerary({
              city: destination,
              days: Number(days),
              interests,
              budget,
            });
  
          if (
            onItineraryGenerated
          ) {
            onItineraryGenerated(
              result
            );
          }
  
          if (
            onDestinationChange
          ) {
            onDestinationChange(
              destination
            );
          }
  
        } catch (err) {
  
          console.error(err);
  
          setError(
            err.message ||
            "Unable to generate trip."
          );
  
        } finally {
  
          setLoading(false);
  
        }
      };
  
  
    return (
      <div className="rounded-2xl bg-white p-6 shadow-xl">
  
        <div className="mb-6">
  
          <h2 className="text-xl font-bold text-slate-900">
            Plan Your Trip
          </h2>
  
          <p className="mt-1 text-sm text-slate-500">
            Build a real optimized itinerary using AI TravelMate.
          </p>
  
        </div>
  
  
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
  
          <Field label="Destination">
  
            <input
              value={destination}
              onChange={(e) => {
                setDestination(
                  e.target.value
                );
  
                if (
                  onDestinationChange
                ) {
                  onDestinationChange(
                    e.target.value
                  );
                }
              }}
              className="field"
            />
  
          </Field>
  
  
          <Field label="Days">
  
            <input
              type="number"
              min="1"
              max="14"
              value={days}
              onChange={(e) =>
                setDays(
                  e.target.value
                )
              }
              className="field"
            />
  
          </Field>
  
  
          <Field label="Travelers">
  
            <input
              type="number"
              min="1"
              max="20"
              value={travelers}
              onChange={(e) =>
                setTravelers(
                  e.target.value
                )
              }
              className="field"
            />
  
          </Field>
  
  
          <Field label="Interests">
  
            <input
              value={interests}
              onChange={(e) =>
                setInterests(
                  e.target.value
                )
              }
              className="field"
            />
  
          </Field>
  
  
          <Field label="Budget">
  
            <select
              value={budget}
              onChange={(e) =>
                setBudget(
                  e.target.value
                )
              }
              className="field"
            >
  
              <option value="budget">
                Budget
              </option>
  
              <option value="moderate">
                Moderate
              </option>
  
              <option value="luxury">
                Luxury
              </option>
  
            </select>
  
          </Field>
  
        </div>
  
  
        {error && (
          <div className="mt-4 rounded-xl bg-red-50 p-3 text-sm font-medium text-red-700">
            {error}
          </div>
        )}
  
  
        <button
          onClick={handlePlanTrip}
          disabled={loading}
          className="
            mt-5
            flex
            h-[46px]
            w-full
            items-center
            justify-center
            rounded-xl
            bg-gradient-to-r
            from-blue-600
            to-indigo-600
            px-4
            font-bold
            text-white
            shadow-lg
            transition
            hover:from-blue-500
            hover:to-indigo-500
            disabled:opacity-50
          "
        >
  
          {loading
            ? "✨ AI TravelMate is planning..."
            : "✨ Generate AI Travel Plan"
          }
  
        </button>
  
      </div>
    );
  }
  
  
  function Field({
    label,
    children,
  }) {
    return (
      <label>
  
        <div className="field-label">
          {label}
        </div>
  
        {children}
  
      </label>
    );
  }