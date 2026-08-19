import React, {
    useState,
  } from "react";
  
  import {
    analyzeTripDisruptions,
    applyTripDisruption,
    analyzeForecastTiming,
  } from "../../services/travelApi";
  
  
  export default function DynamicCopilot({
    city,
    itinerary,
    startDate,
    onStartDateChange,
    onItineraryUpdated,
  }) {
  
    // ============================================================
    // STATE
    // ============================================================
  
    const [
      result,
      setResult,
    ] = useState(null);
  
    const [
      loading,
      setLoading,
    ] = useState(false);
  
    const [
      forecastResult,
      setForecastResult,
    ] = useState(null);
  
    const [
      forecastLoading,
      setForecastLoading,
    ] = useState(false);
  
    const [
      applyingIndex,
      setApplyingIndex,
    ] = useState(null);
  
    const [
      applyingTimingIndex,
      setApplyingTimingIndex,
    ] = useState(null);
  
    const [
      successMessage,
      setSuccessMessage,
    ] = useState("");
  
    const [
      error,
      setError,
    ] = useState("");
  
  
    // ============================================================
    // CURRENT-WEATHER CHECK
    // ============================================================
  
    async function checkTrip() {
  
      if (!itinerary) {
  
        setError(
          "Generate an itinerary first."
        );
  
        return;
      }
  
  
      setError("");
  
      setSuccessMessage("");
  
      setLoading(true);
  
  
      try {
  
        const response =
          await analyzeTripDisruptions({
            city,
            itinerary,
          });
  
  
        setResult(
          response
        );
  
  
      } catch (err) {
  
        console.error(
          "Dynamic copilot error:",
          err
        );
  
  
        setError(
          err.message ||
          "Unable to check trip conditions."
        );
  
  
      } finally {
  
        setLoading(
          false
        );
  
      }
  
    }
  
  
    // ============================================================
    // APPLY CURRENT-WEATHER SUGGESTION
    // ============================================================
  
    async function applySuggestion(
      disruption,
      disruptionIndex
    ) {
  
      const alternative =
        disruption
          .suggested_alternative;
  
  
      if (
        !alternative ||
        alternative.place_index ===
          undefined ||
        alternative.place_index ===
          null
      ) {
  
        setError(
          "This adjustment cannot be applied automatically."
        );
  
        return;
      }
  
  
      setError("");
  
      setSuccessMessage("");
  
      setApplyingIndex(
        disruptionIndex
      );
  
  
      try {
  
        const response =
          await applyTripDisruption({
  
            itinerary,
  
            day:
              disruption.day,
  
            fromIndex:
              disruption.place_index,
  
            toIndex:
              alternative.place_index,
  
          });
  
  
        const updatedItinerary =
          response.itinerary;
  
  
        if (!updatedItinerary) {
  
          throw new Error(
            "Backend did not return an updated itinerary."
          );
  
        }
  
  
        if (onItineraryUpdated) {
  
          onItineraryUpdated(
            updatedItinerary
          );
  
        }
  
  
        setSuccessMessage(
          `Updated Day ${disruption.day}: ${alternative.name} has been prioritized.`
        );
  
  
        // Old analysis is no longer valid
        // because itinerary order has changed.
  
        setResult(null);
  
        setForecastResult(null);
  
  
      } catch (err) {
  
        console.error(
          "Apply disruption error:",
          err
        );
  
  
        setError(
          err.message ||
          "Unable to update itinerary."
        );
  
  
      } finally {
  
        setApplyingIndex(
          null
        );
  
      }
  
    }
  
  
    // ============================================================
    // HOURLY FORECAST CHECK
    // ============================================================
  
    async function checkForecastTiming() {
  
      if (!itinerary) {
  
        setError(
          "Generate an itinerary first."
        );
  
        return;
      }
  
  
      if (!startDate) {
  
        setError(
          "Choose a trip start date."
        );
  
        return;
      }
  
  
      setError("");
  
      setSuccessMessage("");
  
      setForecastLoading(
        true
      );
  
  
      try {
  
        const response =
          await analyzeForecastTiming({
  
            city,
  
            startDate,
  
            itinerary,
  
          });
  
  
        setForecastResult(
          response
        );
  
  
      } catch (err) {
  
        console.error(
          "Forecast timing error:",
          err
        );
  
  
        setError(
          err.message ||
          "Unable to analyze forecast timing."
        );
  
  
      } finally {
  
        setForecastLoading(
          false
        );
  
      }
  
    }
  
  
    // ============================================================
    // APPLY SMART TIMING
    // ============================================================
  
    async function applySmartTiming(
      alert,
      alertIndex
    ) {
  
      const smartTiming =
        alert.smart_timing;
  
  
      if (
        !smartTiming ||
        smartTiming.target_place_index ===
          undefined ||
        smartTiming.target_place_index ===
          null
      ) {
  
        setError(
          "No safe automatic timing adjustment is available."
        );
  
        return;
      }
  
  
      setError("");
  
      setSuccessMessage("");
  
      setApplyingTimingIndex(
        alertIndex
      );
  
  
      try {
  
        const response =
          await applyTripDisruption({
  
            itinerary,
  
            day:
              alert.day,
  
            fromIndex:
              alert.place_index,
  
            toIndex:
              smartTiming
                .target_place_index,
  
          });
  
  
        const updatedItinerary =
          response.itinerary;
  
  
        if (!updatedItinerary) {
  
          throw new Error(
            "Backend did not return the updated itinerary."
          );
  
        }
  
  
        if (onItineraryUpdated) {
  
          onItineraryUpdated(
            updatedItinerary
          );
  
        }
  
  
        setSuccessMessage(
  
          `${alert.place_name} was moved toward `
          +
          `${smartTiming.recommended_time}, `
          +
          `reducing forecast risk from `
          +
          `${alert.risk_score} to `
          +
          `${smartTiming.recommended_risk_score}.`
  
        );
  
  
        // Clear stale analyses because
        // itinerary timings have changed.
  
        setForecastResult(null);
  
        setResult(null);
  
  
      } catch (err) {
  
        console.error(
          "Smart timing update error:",
          err
        );
  
  
        setError(
          err.message ||
          "Unable to apply the timing adjustment."
        );
  
  
      } finally {
  
        setApplyingTimingIndex(
          null
        );
  
      }
  
    }
  
  
    // ============================================================
    // UI
    // ============================================================
  
    return (
  
      <div
        className="
          rounded-2xl
          bg-white
          p-4
          shadow-xl
          sm:p-6
        "
      >
  
        {/* ====================================================== */}
        {/* HEADER */}
        {/* ====================================================== */}
  
        <div
          className="
            flex
            flex-wrap
            items-center
            justify-between
            gap-3
          "
        >
  
          <div>
  
            <h2
              className="
                font-bold
                text-slate-900
              "
            >
              Dynamic Travel Copilot
            </h2>
  
  
            <p
              className="
                mt-1
                text-xs
                text-slate-500
              "
            >
              Live weather and forecast-aware
              itinerary optimization
            </p>
  
          </div>
  
  
          <div
            className="
              rounded-full
              bg-blue-50
              px-3
              py-1
              text-xs
              font-bold
              text-blue-700
            "
          >
            LIVE
          </div>
  
        </div>
  
  
        {/* ====================================================== */}
        {/* TRIP START DATE */}
        {/* ====================================================== */}
  
        <div
          className="
            mt-5
            rounded-xl
            bg-slate-50
            p-3
          "
        >
  
          <label
            className="
              text-xs
              font-bold
              text-slate-600
            "
          >
            Trip start date
          </label>
  
  
          <input
  
            type="date"
  
            value={
              startDate || ""
            }
  
            onChange={
              (event) =>
                onStartDateChange?.(
                  event.target.value
                )
            }
  
            className="
              mt-2
              h-11
              w-full
              rounded-lg
              border
              border-slate-300
              bg-white
              px-3
              text-sm
              text-slate-900
              outline-none
              focus:border-blue-500
            "
  
          />
  
        </div>
  
  
        {/* ====================================================== */}
        {/* ACTION BUTTONS */}
        {/* ====================================================== */}
  
        <button
  
          type="button"
  
          onClick={
            checkTrip
          }
  
          disabled={
            loading ||
            !itinerary
          }
  
          className="
            mt-4
            min-h-[46px]
            w-full
            rounded-xl
            bg-gradient-to-r
            from-blue-600
            to-indigo-600
            px-4
            py-3
            font-bold
            text-white
            shadow
            transition
            hover:from-blue-500
            hover:to-indigo-500
            disabled:cursor-not-allowed
            disabled:opacity-40
          "
        >
  
          {
            loading
              ? "Checking live conditions..."
              : "🌦 Check My Itinerary"
          }
  
        </button>
  
  
        <button
  
          type="button"
  
          onClick={
            checkForecastTiming
          }
  
          disabled={
            forecastLoading ||
            !itinerary
          }
  
          className="
            mt-2
            min-h-[46px]
            w-full
            rounded-xl
            border
            border-indigo-200
            bg-indigo-50
            px-4
            py-3
            font-bold
            text-indigo-700
            shadow-sm
            transition
            hover:bg-indigo-100
            disabled:cursor-not-allowed
            disabled:opacity-40
          "
        >
  
          {
            forecastLoading
              ? "Checking hourly forecast..."
              : "⏱ Check Best Times"
          }
  
        </button>
  
  
        {/* ====================================================== */}
        {/* SUCCESS */}
        {/* ====================================================== */}
  
        {successMessage && (
  
          <div
            className="
              mt-4
              rounded-xl
              border
              border-emerald-200
              bg-emerald-50
              p-3
              text-sm
              font-semibold
              text-emerald-700
            "
          >
            ✓ {successMessage}
          </div>
  
        )}
  
  
        {/* ====================================================== */}
        {/* ERROR */}
        {/* ====================================================== */}
  
        {error && (
  
          <div
            className="
              mt-4
              rounded-xl
              bg-red-50
              p-3
              text-sm
              font-semibold
              text-red-700
            "
          >
            {error}
          </div>
  
        )}
  
  
        {/* ====================================================== */}
        {/* CURRENT-WEATHER RESULT */}
        {/* ====================================================== */}
  
        {result && (
  
          <div
            className="
              mt-5
              space-y-4
            "
          >
  
            {/* -------------------------------------------------- */}
            {/* CURRENT CONDITIONS */}
            {/* -------------------------------------------------- */}
  
            <div
              className="
                rounded-xl
                bg-slate-50
                p-4
              "
            >
  
              <div
                className="
                  text-xs
                  font-bold
                  uppercase
                  tracking-wide
                  text-slate-500
                "
              >
                Current conditions
              </div>
  
  
              <div
                className="
                  mt-2
                  grid
                  grid-cols-2
                  gap-2
                  text-sm
                  sm:grid-cols-3
                "
              >
  
                <Metric
  
                  label="Temperature"
  
                  value={
                    `${
                      result.weather
                        ?.temperature_c ??
                      "-"
                    }°C`
                  }
  
                />
  
  
                <Metric
  
                  label="Feels like"
  
                  value={
                    `${
                      result.weather
                        ?.feels_like_c ??
                      "-"
                    }°C`
                  }
  
                />
  
  
                <Metric
  
                  label="Rain"
  
                  value={
                    `${
                      result.weather
                        ?.precipitation_mm ??
                      0
                    } mm`
                  }
  
                />
  
              </div>
  
            </div>
  
  
            {/* -------------------------------------------------- */}
            {/* NO CURRENT-WEATHER PROBLEMS */}
            {/* -------------------------------------------------- */}
  
            {!result.has_disruptions && (
  
              <div
                className="
                  rounded-xl
                  border
                  border-emerald-200
                  bg-emerald-50
                  p-4
                "
              >
  
                <p
                  className="
                    font-bold
                    text-emerald-800
                  "
                >
                  ✓ Your itinerary looks good
                </p>
  
  
                <p
                  className="
                    mt-1
                    text-sm
                    text-emerald-700
                  "
                >
                  No major current-weather conflicts
                  were detected for the plan.
                </p>
  
              </div>
  
            )}
  
  
            {/* -------------------------------------------------- */}
            {/* CURRENT-WEATHER DISRUPTIONS */}
            {/* -------------------------------------------------- */}
  
            {result.has_disruptions && (
  
              <div>
  
                <div
                  className="
                    mb-3
                    flex
                    flex-wrap
                    items-center
                    justify-between
                    gap-2
                  "
                >
  
                  <h3
                    className="
                      font-bold
                      text-slate-900
                    "
                  >
                    Suggested adjustments
                  </h3>
  
  
                  <span
                    className="
                      rounded-full
                      bg-amber-50
                      px-3
                      py-1
                      text-xs
                      font-bold
                      text-amber-700
                    "
                  >
                    {
                      result.disruption_count
                    }{" "}
                    alerts
                  </span>
  
                </div>
  
  
                <div
                  className="
                    space-y-3
                  "
                >
  
                  {
                    result.disruptions
                      ?.map(
                        (
                          disruption,
                          index
                        ) => (
  
                          <div
                            key={
                              `${disruption.day}-${disruption.place_index}-${index}`
                            }
  
                            className="
                              rounded-xl
                              border
                              border-amber-200
                              bg-amber-50
                              p-4
                            "
                          >
  
                            {/* HEADER */}
  
                            <div
                              className="
                                flex
                                flex-wrap
                                items-start
                                justify-between
                                gap-2
                              "
                            >
  
                              <div>
  
                                <div
                                  className="
                                    text-xs
                                    font-bold
                                    text-amber-700
                                  "
                                >
                                  Day {
                                    disruption.day
                                  }
                                </div>
  
  
                                <h4
                                  className="
                                    mt-1
                                    font-bold
                                    text-slate-900
                                  "
                                >
                                  {
                                    disruption.place_name
                                  }
                                </h4>
  
                              </div>
  
  
                              <span
                                className="
                                  rounded-full
                                  bg-white
                                  px-2
                                  py-1
                                  text-[10px]
                                  font-bold
                                  uppercase
                                  text-amber-700
                                "
                              >
                                {
                                  disruption.severity
                                }
                              </span>
  
                            </div>
  
  
                            {/* REASONS */}
  
                            <div
                              className="
                                mt-3
                                space-y-1
                              "
                            >
  
                              {
                                disruption.reasons
                                  ?.map(
                                    (
                                      reason,
                                      reasonIndex
                                    ) => (
  
                                      <p
                                        key={
                                          reasonIndex
                                        }
  
                                        className="
                                          text-xs
                                          leading-5
                                          text-slate-600
                                        "
                                      >
                                        • {reason}
                                      </p>
  
                                    )
                                  )
                              }
  
                            </div>
  
  
                            {/* SUGGESTED ALTERNATIVE */}
  
                            {
                              disruption
                                .suggested_alternative && (
  
                                <div
                                  className="
                                    mt-3
                                    rounded-lg
                                    bg-white
                                    p-3
                                  "
                                >
  
                                  <div
                                    className="
                                      text-[10px]
                                      font-bold
                                      uppercase
                                      tracking-wide
                                      text-blue-600
                                    "
                                  >
                                    Suggested swap
                                  </div>
  
  
                                  <p
                                    className="
                                      mt-1
                                      text-sm
                                      font-bold
                                      text-slate-900
                                    "
                                  >
                                    {
                                      disruption
                                        .suggested_alternative
                                        .name
                                    }
                                  </p>
  
  
                                  <p
                                    className="
                                      mt-1
                                      text-xs
                                      text-slate-500
                                    "
                                  >
                                    {
                                      disruption
                                        .suggested_alternative
                                        .category
                                    }
                                  </p>
  
  
                                  <button
  
                                    type="button"
  
                                    onClick={() =>
                                      applySuggestion(
                                        disruption,
                                        index
                                      )
                                    }
  
                                    disabled={
                                      applyingIndex ===
                                      index
                                    }
  
                                    className="
                                      mt-3
                                      min-h-[42px]
                                      w-full
                                      rounded-lg
                                      bg-blue-600
                                      px-3
                                      py-2
                                      text-xs
                                      font-bold
                                      text-white
                                      transition
                                      hover:bg-blue-500
                                      disabled:cursor-not-allowed
                                      disabled:opacity-50
                                    "
                                  >
  
                                    {
                                      applyingIndex ===
                                      index
                                        ? "Applying change..."
                                        : "✓ Apply Suggested Swap"
                                    }
  
                                  </button>
  
                                </div>
  
                              )
                            }
  
                          </div>
  
                        )
                      )
                  }
  
                </div>
  
              </div>
  
            )}
  
          </div>
  
        )}
  
  
        {/* ====================================================== */}
        {/* HOURLY FORECAST RESULT */}
        {/* IMPORTANT: THIS IS OUTSIDE result */}
        {/* ====================================================== */}
  
        {forecastResult && (
  
          <div
            className="
              mt-5
              rounded-xl
              border
              border-indigo-100
              bg-indigo-50
              p-4
            "
          >
  
            {/* -------------------------------------------------- */}
            {/* FORECAST HEADER */}
            {/* -------------------------------------------------- */}
  
            <div
              className="
                flex
                flex-wrap
                items-center
                justify-between
                gap-2
              "
            >
  
              <div>
  
                <div
                  className="
                    text-xs
                    font-bold
                    uppercase
                    tracking-wide
                    text-indigo-600
                  "
                >
                  Hourly Forecast Copilot
                </div>
  
  
                <p
                  className="
                    mt-1
                    text-xs
                    text-slate-600
                  "
                >
                  {
                    forecastResult
                      .forecast_location ||
                    city
                  }
                </p>
  
              </div>
  
  
              <span
                className="
                  rounded-full
                  bg-white
                  px-3
                  py-1
                  text-xs
                  font-bold
                  text-indigo-700
                "
              >
                {
                  forecastResult
                    .alert_count ??
                  0
                }{" "}
                timing alerts
              </span>
  
            </div>
  
  
            {/* -------------------------------------------------- */}
            {/* FORECAST IS SAFE */}
            {/* -------------------------------------------------- */}
  
            {!forecastResult
              .has_timing_risks && (
  
              <div
                className="
                  mt-4
                  rounded-lg
                  border
                  border-emerald-200
                  bg-emerald-50
                  p-3
                "
              >
  
                <p
                  className="
                    text-sm
                    font-bold
                    text-emerald-700
                  "
                >
                  ✓ Current timings look weather-friendly
                </p>
  
  
                <p
                  className="
                    mt-1
                    text-xs
                    leading-5
                    text-emerald-700
                  "
                >
                  TravelMate did not find any significant
                  forecast-related timing conflicts for
                  your outdoor stops.
                </p>
  
              </div>
  
            )}
  
  
            {/* -------------------------------------------------- */}
            {/* FORECAST RISKS */}
            {/* -------------------------------------------------- */}
  
            {forecastResult
              .has_timing_risks && (
  
              <div
                className="
                  mt-4
                  space-y-3
                "
              >
  
                {
                  forecastResult
                    .alerts
                    ?.map(
                      (
                        alert,
                        index
                      ) => (
  
                        <div
                          key={
                            `${alert.day}-${alert.place_index}-${index}`
                          }
  
                          className="
                            rounded-xl
                            bg-white
                            p-3
                            shadow-sm
                          "
                        >
  
                          {/* ALERT HEADING */}
  
                          <div
                            className="
                              text-xs
                              font-bold
                              text-indigo-600
                            "
                          >
                            Day {alert.day}
                            {" • "}
                            {alert.arrival_time}
                          </div>
  
  
                          <div
                            className="
                              mt-1
                              font-bold
                              text-slate-900
                            "
                          >
                            {alert.place_name}
                          </div>
  
  
                          {/* CURRENT FORECAST */}
  
                          <div
                            className="
                              mt-3
                              grid
                              grid-cols-2
                              gap-2
                            "
                          >
  
                            <ForecastMetric
  
                              label="Rain chance"
  
                              value={
                                `${
                                  alert.forecast
                                    ?.precipitation_probability ??
                                  0
                                }%`
                              }
  
                            />
  
  
                            <ForecastMetric
  
                              label="Rain"
  
                              value={
                                `${
                                  alert.forecast
                                    ?.precipitation ??
                                  0
                                } mm`
                              }
  
                            />
  
  
                            <ForecastMetric
  
                              label="Feels like"
  
                              value={
                                `${
                                  alert.forecast
                                    ?.apparent_temperature ??
                                  "-"
                                }°C`
                              }
  
                            />
  
  
                            <ForecastMetric
  
                              label="Risk score"
  
                              value={
                                alert.risk_score
                              }
  
                            />
  
                          </div>
  
  
                          <p
                            className="
                              mt-3
                              text-xs
                              leading-5
                              text-slate-600
                            "
                          >
                            TravelMate recommends moving
                            this outdoor stop toward a
                            lower-risk weather window.
                          </p>
  
  
                          {/* ==================================== */}
                          {/* SMART TIMING */}
                          {/* ==================================== */}
  
                          {alert.smart_timing && (
  
                            <div
                              className="
                                mt-3
                                rounded-xl
                                border
                                border-emerald-200
                                bg-emerald-50
                                p-3
                              "
                            >
  
                              <div
                                className="
                                  text-[10px]
                                  font-bold
                                  uppercase
                                  tracking-wide
                                  text-emerald-700
                                "
                              >
                                Smart Timing Recommendation
                              </div>
  
  
                              <div
                                className="
                                  mt-2
                                  flex
                                  flex-wrap
                                  items-end
                                  justify-between
                                  gap-3
                                "
                              >
  
                                <div>
  
                                  <p
                                    className="
                                      text-sm
                                      font-bold
                                      text-slate-900
                                    "
                                  >
                                    Move toward{" "}
                                    {
                                      alert
                                        .smart_timing
                                        .recommended_time
                                    }
                                  </p>
  
  
                                  <p
                                    className="
                                      mt-1
                                      text-xs
                                      leading-5
                                      text-slate-600
                                    "
                                  >
                                    Swap with{" "}
                                    <strong>
                                      {
                                        alert
                                          .smart_timing
                                          .target_place_name
                                      }
                                    </strong>
                                    {" "}to reduce weather risk.
                                  </p>
  
                                </div>
  
  
                                <div
                                  className="
                                    rounded-lg
                                    bg-white
                                    px-3
                                    py-2
                                    text-center
                                  "
                                >
  
                                  <div
                                    className="
                                      text-[9px]
                                      font-bold
                                      uppercase
                                      tracking-wide
                                      text-slate-400
                                    "
                                  >
                                    Risk
                                  </div>
  
  
                                  <div
                                    className="
                                      mt-1
                                      font-extrabold
                                      text-emerald-700
                                    "
                                  >
                                    {
                                      alert.risk_score
                                    }
  
                                    {" → "}
  
                                    {
                                      alert
                                        .smart_timing
                                        .recommended_risk_score
                                    }
                                  </div>
  
                                </div>
  
                              </div>
  
  
                              {/* BEST WEATHER WINDOW */}
  
                              <div
                                className="
                                  mt-3
                                  grid
                                  grid-cols-2
                                  gap-2
                                  sm:grid-cols-3
                                "
                              >
  
                                <ForecastMetric
  
                                  label="Best time"
  
                                  value={
                                    alert
                                      .smart_timing
                                      .recommended_time
                                  }
  
                                />
  
  
                                <ForecastMetric
  
                                  label="Rain chance"
  
                                  value={
                                    `${
                                      alert
                                        .smart_timing
                                        .forecast
                                        ?.precipitation_probability
                                      ??
                                      0
                                    }%`
                                  }
  
                                />
  
  
                                <ForecastMetric
  
                                  label="Feels like"
  
                                  value={
                                    `${
                                      alert
                                        .smart_timing
                                        .forecast
                                        ?.apparent_temperature
                                      ??
                                      "-"
                                    }°C`
                                  }
  
                                />
  
                              </div>
  
  
                              {/* APPLY SMART TIMING */}
  
                              <button
  
                                type="button"
  
                                onClick={() =>
                                  applySmartTiming(
                                    alert,
                                    index
                                  )
                                }
  
                                disabled={
                                  applyingTimingIndex ===
                                  index
                                }
  
                                className="
                                  mt-3
                                  min-h-[44px]
                                  w-full
                                  rounded-lg
                                  bg-emerald-600
                                  px-4
                                  py-2.5
                                  text-xs
                                  font-bold
                                  text-white
                                  shadow
                                  transition
                                  hover:bg-emerald-500
                                  disabled:cursor-not-allowed
                                  disabled:opacity-50
                                "
                              >
  
                                {
                                  applyingTimingIndex ===
                                  index
                                    ? "Applying smart timing..."
                                    : "✓ Apply Smart Timing"
                                }
  
                              </button>
  
                            </div>
  
                          )}
  
  
                          {/* NO BETTER TIME */}
  
                          {!alert.smart_timing && (
  
                            <div
                              className="
                                mt-3
                                rounded-lg
                                border
                                border-amber-200
                                bg-amber-50
                                p-3
                              "
                            >
  
                              <p
                                className="
                                  text-xs
                                  font-semibold
                                  leading-5
                                  text-amber-700
                                "
                              >
                                No sufficiently safer automatic
                                time slot was found within the
                                current day's itinerary.
                              </p>
  
                            </div>
  
                          )}
  
                        </div>
  
                      )
                    )
                }
  
              </div>
  
            )}
  
          </div>
  
        )}
  
      </div>
  
    );
  
  }
  
  
  // ============================================================
  // CURRENT WEATHER METRIC
  // ============================================================
  
  function Metric({
    label,
    value,
  }) {
  
    return (
  
      <div
        className="
          rounded-lg
          bg-white
          p-3
        "
      >
  
        <div
          className="
            text-[10px]
            font-bold
            uppercase
            tracking-wide
            text-slate-400
          "
        >
          {label}
        </div>
  
  
        <div
          className="
            mt-1
            font-bold
            text-slate-900
          "
        >
          {value}
        </div>
  
      </div>
  
    );
  
  }
  
  
  // ============================================================
  // FORECAST METRIC
  // ============================================================
  
  function ForecastMetric({
    label,
    value,
  }) {
  
    return (
  
      <div
        className="
          rounded-lg
          bg-slate-50
          p-2
        "
      >
  
        <div
          className="
            text-[9px]
            font-bold
            uppercase
            tracking-wide
            text-slate-400
          "
        >
          {label}
        </div>
  
  
        <div
          className="
            mt-1
            font-bold
            text-slate-800
          "
        >
          {value}
        </div>
  
      </div>
  
    );
  
  }