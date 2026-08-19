import React, { useEffect, useState } from "react";

export default function OfflineIndicator() {

  const [online, setOnline] = useState(navigator.onLine);

  useEffect(() => {

    const handleOnline = () => setOnline(true);
    const handleOffline = () => setOnline(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };

  }, []);

  if (online) {
    return null;
  }

  return (
    <div className="fixed left-0 right-0 top-0 z-50 bg-red-600 px-4 py-2 text-center text-sm font-bold text-white">
      ⚠️ You are offline. Saved travel information remains available.
    </div>
  );
}