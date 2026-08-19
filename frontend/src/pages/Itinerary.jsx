import {
    useState,
  } from "react";
  
  import {
    LoaderCircle,
    MapPinned,
    Sparkles,
  } from "lucide-react";
  
  import DayTimeline from "../components/itinerary/DayTimeline";
  
  import {
    generateItinerary,
  } from "../services/itineraryApi";
  
  
  export default function Itinerary() {
    const [city, setCity] =
      useState("Chennai");
  
    const [days, setDays] =
      useState(3);
  
    const [interests, setInterests] =
      useState(
        "temples, food, beaches"
      );
  
    const [budget, setBudget] =
      useState("moderate");
  
    const [
      itinerary,
      setItinerary,
    ] = useState(null);
  
    const [
      loading,
      setLoading,
    ] = useState(false);
  
    const [
      error,
      setError,
    ] = useState("");
  
  
    async function handleGenerate(
      event
    ) {
      event.preventDefault();
  
      setLoading(true);
      setError("");
  
      try {
        const result =
          await generateItinerary({
            city,
            days: Number(days),
            interests,
            budget,
          });
  
        setItinerary(result);
      } catch (err) {
        console.error(err);
  
        setError(
          err.message ||
          "Unable to generate itinerary."
        );
      } finally {
        setLoading(false);
      }
    }
  
  
    return (
      <div className="mx-auto max-w-7xl space-y-8 p-5 md:p-8">
  
        {/* ================================================== */}
        {/* HEADER */}
        {/* ================================================== */}
  
        <section>
  
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1 text-xs font-semibold text-blue-300">
            <Sparkles size={14} />
            Structured AI itinerary
          </div>
  
          <h1 className="mt-4 text-3xl font-bold md:text-4xl">
            Build your trip
          </h1>
  
          <p className="mt-2 max-w-2xl text-slate-400">
            AI TravelMate will generate,
            resolve, optimize and schedule
            your itinerary using the backend
            travel intelligence pipeline.
          </p>
  
        </section>
  
  
        {/* ================================================== */}
        {/* FORM */}
        {/* ================================================== */}
  
        <form
  onSubmit={handleGenerate}
  className="
    grid
    gap-5
    rounded-3xl
    border
    border-slate-700/70
    bg-gradient-to-br
    from-slate-900
    to-slate-950
    p-6
    shadow-2xl
    shadow-black/20
    lg:grid-cols-5
  "
>
  
          <InputGroup label="Destination">
            <input
              value={city}
              onChange={(event) =>
                setCity(
                  event.target.value
                )
              }
              className="field"
              placeholder="Chennai"
              required
            />
          </InputGroup>
  
  
          <InputGroup label="Days">
            <input
              type="number"
              min="1"
              max="14"
              value={days}
              onChange={(event) =>
                setDays(
                  event.target.value
                )
              }
              className="field"
              required
            />
          </InputGroup>
  
  
          <InputGroup label="Interests">
            <input
              value={interests}
              onChange={(event) =>
                setInterests(
                  event.target.value
                )
              }
              className="field"
              placeholder="temples, food, beaches"
            />
          </InputGroup>
  
  
          <InputGroup label="Budget">
            <select
              value={budget}
              onChange={(event) =>
                setBudget(
                  event.target.value
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
          </InputGroup>
  
  
          <div className="flex items-end">
  
          <button
  type="submit"
  disabled={loading}
  className="
    flex
    h-[46px]
    w-full
    items-center
    justify-center
    gap-2
    rounded-xl
    bg-gradient-to-r
    from-blue-600
    to-indigo-600
    px-4
    font-bold
    text-white
    shadow-lg
    shadow-blue-950/30
    transition-all
    duration-200
    hover:-translate-y-0.5
    hover:from-blue-500
    hover:to-indigo-500
    hover:shadow-xl
    disabled:cursor-not-allowed
    disabled:opacity-50
  "
>
  {loading ? "Building..." : "Build Trip"}
</button>
  
          </div>
  
        </form>
  
  
        {/* ================================================== */}
        {/* ERROR */}
        {/* ================================================== */}
  
        {error && (
          <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
            {error}
          </div>
        )}
  
  
        {/* ================================================== */}
        {/* EMPTY STATE */}
        {/* ================================================== */}
  
        {!loading &&
          !itinerary &&
          !error && (
            <div className="rounded-3xl border border-dashed border-white/10 py-20 text-center">
  
              <MapPinned
                size={36}
                className="mx-auto text-slate-600"
              />
  
              <h2 className="mt-4 text-xl font-semibold">
                Your itinerary will appear here
              </h2>
  
              <p className="mt-2 text-sm text-slate-500">
                Enter your destination,
                interests and budget above.
              </p>
  
            </div>
          )}
  
  
        {/* ================================================== */}
        {/* RESULTS */}
        {/* ================================================== */}
  
        {itinerary && (
          <div className="space-y-8">
  
            <div className="rounded-3xl border border-blue-500/20 bg-blue-500/5 p-6">
  
              <div className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-400">
                AI TravelMate Trip
              </div>
  
              <div className="mt-2 flex flex-col justify-between gap-3 md:flex-row md:items-end">
  
                <div>
  
                  <h2 className="text-3xl font-bold">
                    {itinerary.city}
                  </h2>
  
                  <div className="mt-1 text-sm text-slate-400">
                    {itinerary.days?.length || 0} day itinerary
                  </div>
  
                </div>
  
                <div
                  className={
                    itinerary.time_validation?.valid
                      ? "text-sm font-semibold text-green-400"
                      : "text-sm font-semibold text-red-400"
                  }
                >
                  {itinerary.time_validation?.valid
                    ? "✓ Schedule valid"
                    : "⚠ Schedule needs attention"}
                </div>
  
              </div>
  
            </div>
  
  
            {itinerary.days?.map(
              (day) => (
                <DayTimeline
                  key={day.day}
                  day={day}
                />
              )
            )}
  
          </div>
        )}
  
      </div>
    );
  }
  
  
  function InputGroup({
    label,
    children,
  }) {
    return (
      <label className="block">
  
        <div
          className="
            mb-2
            text-xs
            font-bold
            uppercase
            tracking-wider
            text-slate-300
          "
        >
          {label}
        </div>
  
        {children}
  
      </label>
    );
  }