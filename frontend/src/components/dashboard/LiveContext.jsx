import React, {
    useEffect,
    useState,
  } from "react";
  
  import {
    getWeather,
  } from "../../services/travelApi";
  
  
  export default function LiveContext({
    city,
  }) {
    const [weather, setWeather] =
      useState(null);
  
    const [loading, setLoading] =
      useState(false);
  
    const [error, setError] =
      useState("");
  
  
    useEffect(() => {
  
      if (!city?.trim()) {
        return;
      }
  
      loadWeather();
  
    }, [city]);
  
  
    async function loadWeather() {
  
      setLoading(true);
      setError("");
  
      try {
  
        const result =
          await getWeather(city);
  
        setWeather(result);
  
      } catch (err) {
  
        console.error(err);
  
        setError(
          "Weather unavailable"
        );
  
      } finally {
  
        setLoading(false);
  
      }
  
    }
  
  
    return (
      <div className="rounded-2xl bg-white p-6 shadow-xl">
  
        <div className="flex items-center justify-between">
  
          <div>
  
            <h2 className="text-lg font-bold text-slate-900">
              Live Travel Context
            </h2>
  
            <p className="mt-1 text-xs text-slate-500">
              Real-time destination intelligence
            </p>
  
          </div>
  
          <span
            className={
              weather
                ? "h-3 w-3 rounded-full bg-emerald-500"
                : "h-3 w-3 rounded-full bg-slate-300"
            }
          />
  
        </div>
  
  
        <div className="mt-5 rounded-xl bg-blue-50 p-4">
  
          <p className="text-xs font-bold uppercase tracking-wide text-blue-600">
            🌤 Weather
          </p>
  
  
          {loading && (
            <p className="mt-2 font-bold text-slate-800">
              Loading live weather...
            </p>
          )}
  
  
          {!loading &&
            error && (
              <p className="mt-2 text-sm font-semibold text-red-600">
                {error}
              </p>
            )}
  
  
          {!loading &&
            weather && (
              <>
  
                <p className="mt-2 text-3xl font-extrabold text-slate-900">
  
                  {
                    weather.temperature ??
                    weather.current_temperature ??
                    "—"
                  }
  
                  °C
  
                </p>
  
  
                <div className="mt-3 space-y-1 text-sm text-slate-600">
  
                  {
                    weather.feels_like != null &&
                    (
                      <p>
                        Feels like:{" "}
                        <strong>
                          {weather.feels_like}
                          °C
                        </strong>
                      </p>
                    )
                  }
  
  
                  {
                    weather.humidity != null &&
                    (
                      <p>
                        Humidity:{" "}
                        <strong>
                          {weather.humidity}%
                        </strong>
                      </p>
                    )
                  }
  
  
                  {
                    weather.wind != null &&
                    (
                      <p>
                        Wind:{" "}
                        <strong>
                          {weather.wind}
                        </strong>
                      </p>
                    )
                  }
  
                </div>
  
              </>
            )}
  
        </div>
  
  
        <div className="mt-3 rounded-xl bg-amber-50 p-4">
  
          <p className="text-xs font-bold uppercase tracking-wide text-amber-600">
            🚦 Traffic
          </p>
  
          <p className="mt-1 font-bold text-slate-900">
            Integration coming next
          </p>
  
        </div>
  
  
        <div className="mt-3 rounded-xl bg-purple-50 p-4">
  
          <p className="text-xs font-bold uppercase tracking-wide text-purple-600">
            🎭 Events
          </p>
  
          <p className="mt-1 font-bold text-slate-900">
            Dynamic event feed coming next
          </p>
  
        </div>
  
      </div>
    );
  }