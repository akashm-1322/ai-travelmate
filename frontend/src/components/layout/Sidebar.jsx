import {
    Compass,
    Map,
    MessageCircle,
    Camera,
    Mic,
    Plane,
    Hotel,
    Users,
    Wallet,
    Settings,
  } from "lucide-react";
  
  import { NavLink } from "react-router-dom";
  
  const navigation = [
    {
      label: "Dashboard",
      path: "/",
      icon: Compass,
    },
    {
      label: "AI Planner",
      path: "/planner",
      icon: MessageCircle,
    },
    {
      label: "Sightseeing Lens",
      path: "/lens",
      icon: Camera,
    },
    {
      label: "Voice TravelMate",
      path: "/voice",
      icon: Mic,
    },
    {
      label: "Itinerary",
      path: "/itinerary",
      icon: Map,
    },
    {
      label: "Flights",
      path: "/flights",
      icon: Plane,
    },
    {
      label: "Hotels",
      path: "/hotels",
      icon: Hotel,
    },
    {
      label: "Group Trip",
      path: "/groups",
      icon: Users,
    },
    {
      label: "Expenses",
      path: "/expenses",
      icon: Wallet,
    },
  ];
  
  export default function Sidebar() {
    return (
      <aside className="hidden w-64 border-r border-white/10 bg-slate-900/80 p-4 lg:block">
        <div className="mb-8 px-3">
          <div className="text-xl font-bold">
            AI TravelMate
          </div>
  
          <div className="mt-1 text-xs text-slate-400">
            Your intelligent travel co-pilot
          </div>
        </div>
  
        <nav className="space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
  
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  [
                    "flex items-center gap-3 rounded-xl px-3 py-3",
                    "text-sm transition",
                    isActive
                      ? "bg-blue-600 text-white"
                      : "text-slate-400 hover:bg-white/5 hover:text-white",
                  ].join(" ")
                }
              >
                <Icon size={18} />
  
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
  
        <div className="mt-8 border-t border-white/10 pt-4">
          <NavLink
            to="/settings"
            className="flex items-center gap-3 rounded-xl px-3 py-3 text-sm text-slate-400 hover:bg-white/5 hover:text-white"
          >
            <Settings size={18} />
            Settings
          </NavLink>
        </div>
      </aside>
    );
  }