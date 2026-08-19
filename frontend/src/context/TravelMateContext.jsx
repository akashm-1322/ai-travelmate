
import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

const TravelMateContext = createContext(null);

export function TravelMateProvider({ children }) {
  // ============================================================
  // CONVERSATION
  // ============================================================

  const [conversationId] = useState(() => {
    const storedId = localStorage.getItem(
      "travelmate_conversation_id"
    );

    if (storedId) {
      return storedId;
    }

    const newId = `travelmate-${crypto.randomUUID()}`;

    localStorage.setItem(
      "travelmate_conversation_id",
      newId
    );

    return newId;
  });

  const [messages, setMessages] = useState([]);

  // ============================================================
  // CURRENT TRIP
  // ============================================================

  const [currentTrip, setCurrentTrip] = useState({
    destination: "",
    startDate: "",
    endDate: "",
    travelers: 1,
    preferences: [],
  });

  // ============================================================
  // VOICE
  // ============================================================

  const [voiceMode, setVoiceMode] = useState(false);

  const [ambientMode, setAmbientMode] = useState(false);

  // ============================================================
  // NETWORK / OFFLINE
  // ============================================================

  const [offlineMode, setOfflineMode] = useState(
    !navigator.onLine
  );

  // ============================================================
  // WEATHER / TRAVEL ALERTS
  // ============================================================

  const [weatherAlert, setWeatherAlert] = useState(null);

  // ============================================================
  // ACTIVE FRONTEND FEATURE
  // ============================================================

  const [activeFeature, setActiveFeature] =
    useState("dashboard");

  // ============================================================
  // PERSIST CONVERSATION ID
  // ============================================================

  useEffect(() => {
    localStorage.setItem(
      "travelmate_conversation_id",
      conversationId
    );
  }, [conversationId]);

  // ============================================================
  // ONLINE / OFFLINE DETECTION
  // ============================================================

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

    // Set initial state
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
  }, []);

  // ============================================================
  // CONTEXT VALUE
  // ============================================================

  const value = useMemo(
    () => ({
      // Conversation
      conversationId,
      messages,
      setMessages,

      // Trip
      currentTrip,
      setCurrentTrip,

      // Voice
      voiceMode,
      setVoiceMode,

      ambientMode,
      setAmbientMode,

      // Network
      offlineMode,
      setOfflineMode,

      // Alerts
      weatherAlert,
      setWeatherAlert,

      // Navigation
      activeFeature,
      setActiveFeature,
    }),
    [
      conversationId,
      messages,
      currentTrip,
      voiceMode,
      ambientMode,
      offlineMode,
      weatherAlert,
      activeFeature,
    ]
  );

  // ============================================================
  // PROVIDER
  // ============================================================

  return (
    <TravelMateContext.Provider value={value}>
      {children}
    </TravelMateContext.Provider>
  );
}

// ============================================================
// CUSTOM HOOK
// ============================================================

export function useTravelMate() {
  const context = useContext(TravelMateContext);

  if (!context) {
    throw new Error(
      "useTravelMate must be used inside TravelMateProvider"
    );
  }

  return context;
}
