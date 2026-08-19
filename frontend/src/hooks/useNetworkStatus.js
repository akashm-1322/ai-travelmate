import { useEffect } from "react";
import { useTravelMate } from "../context/TravelMateContext";

export default function useNetworkStatus() {
  const { setOfflineMode } = useTravelMate();

  useEffect(() => {
    const handleOnline = () => {
      setOfflineMode(false);
    };

    const handleOffline = () => {
      setOfflineMode(true);
    };

    window.addEventListener(
      "online",
      handleOnline
    );

    window.addEventListener(
      "offline",
      handleOffline
    );

    setOfflineMode(!navigator.onLine);

    return () => {
      window.removeEventListener(
        "online",
        handleOnline
      );

      window.removeEventListener(
        "offline",
        handleOffline
      );
    };
  }, [setOfflineMode]);
}