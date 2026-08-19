export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

export const API_ENDPOINTS = {
  health: "/health",

  chat: "/chat/",
  voice: "/voice/",

  history: (conversationId) =>
    `/chat/history/${conversationId}`,

  vision: "/vision/",

  weather: "/weather/",
  itinerary: "/itinerary/",

  flights: "/flights/",
  hotels: "/hotels/",
  activities: "/activities/",

  groups: "/groups/",
  expenses: "/expenses/",
};

export default API_BASE_URL;