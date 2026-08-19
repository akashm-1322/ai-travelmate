import {
    Bell,
    CircleUserRound,
    Wifi,
    WifiOff,
  } from "lucide-react";
  
  import { useTravelMate } from "../../context/TravelMateContext";
  
  export default function TopBar() {
    const {
      offlineMode,
      weatherAlert,
    } = useTravelMate();
  
    return (
      <header className="sticky top-0 z-40 flex h-16 items-center justify-between border-b border-white/10 bg-slate-950/90 px-6 backdrop-blur">
        <div>
          <div className="text-sm font-semibold">
            AI TravelMate
          </div>
  
          <div className="text-xs text-slate-500">
            Intelligent travel companion
          </div>
        </div>
  
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs">
            {offlineMode ? (
              <>
                <WifiOff size={15} />
                Offline
              </>
            ) : (
              <>
                <Wifi size={15} />
                Online
              </>
            )}
          </div>
  
          <button className="relative rounded-full p-2 hover:bg-white/10">
            <Bell size={19} />
  
            {weatherAlert && (
              <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-red-500" />
            )}
          </button>
  
          <CircleUserRound size={22} />
        </div>
      </header>
    );
  }