import {
    Camera,
    Map,
    Mic,
    Plane,
    Sparkles,
    CloudSun,
    Users,
  } from "lucide-react";
  
  import { Link } from "react-router-dom";
  
  const features = [
    {
      title: "AI Trip Planner",
      description:
        "Build intelligent itineraries using your preferences.",
      icon: Sparkles,
      path: "/planner",
    },
    {
      title: "Sightseeing Lens",
      description:
        "Point your camera at a landmark or menu and ask TravelMate.",
      icon: Camera,
      path: "/lens",
    },
    {
      title: "Voice TravelMate",
      description:
        "Talk naturally with your AI travel companion.",
      icon: Mic,
      path: "/voice",
    },
    {
      title: "Live Itinerary",
      description:
        "See your trip, routes and activities on an interactive map.",
      icon: Map,
      path: "/itinerary",
    },
    {
      title: "Live Travel",
      description:
        "Flights, hotels and activities will become bookable here.",
      icon: Plane,
      path: "/flights",
    },
    {
      title: "Travel Groups",
      description:
        "Synchronize trips and expenses with your friends.",
      icon: Users,
      path: "/groups",
    },
  ];
  
  export default function Dashboard() {
    return (
      <div className="mx-auto max-w-7xl space-y-8 p-6 lg:p-8">
        <section className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-blue-600/20 via-slate-900 to-purple-600/10 p-8">
          <div className="max-w-3xl">
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-blue-400/20 bg-blue-500/10 px-3 py-1 text-xs text-blue-300">
              <Sparkles size={14} />
              AI-powered travel intelligence
            </div>
  
            <h1 className="text-4xl font-bold tracking-tight lg:text-5xl">
              Travel smarter.
              <br />
              Experience more.
            </h1>
  
            <p className="mt-4 max-w-2xl text-slate-400">
              Plan your journey, talk to your AI companion,
              understand the world through your camera and
              adapt your itinerary as your trip changes.
            </p>
  
            <div className="mt-6 flex flex-wrap gap-3">
              <Link
                to="/planner"
                className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold hover:bg-blue-500"
              >
                Plan a trip
              </Link>
  
              <Link
                to="/voice"
                className="rounded-xl border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold hover:bg-white/10"
              >
                Talk to TravelMate
              </Link>
            </div>
          </div>
        </section>
  
        <section>
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold">
                TravelMate capabilities
              </h2>
  
              <p className="text-sm text-slate-500">
                Your intelligent travel toolkit
              </p>
            </div>
          </div>
  
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {features.map((feature) => {
              const Icon = feature.icon;
  
              return (
                <Link
                  key={feature.path}
                  to={feature.path}
                  className="group rounded-2xl border border-white/10 bg-white/[0.03] p-5 transition hover:-translate-y-1 hover:bg-white/[0.06]"
                >
                  <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400">
                    <Icon size={21} />
                  </div>
  
                  <h3 className="font-semibold">
                    {feature.title}
                  </h3>
  
                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    {feature.description}
                  </p>
  
                  <div className="mt-4 text-xs font-semibold text-blue-400">
                    Open →
                  </div>
                </Link>
              );
            })}
          </div>
        </section>
  
        <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
          <div className="flex items-center gap-3">
            <CloudSun className="text-yellow-400" />
  
            <div>
              <div className="font-semibold">
                Live travel intelligence
              </div>
  
              <div className="text-sm text-slate-500">
                Weather, traffic and disruption-aware itinerary
                updates will appear here.
              </div>
            </div>
          </div>
        </section>
      </div>
    );
  }