const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";


async function handleResponse(response) {
  let data = null;

  try {
    data = await response.json();
  } catch {
    // Response may not contain JSON.
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
      data?.message ||
      `Request failed with HTTP ${response.status}`
    );
  }

  return data;
}


// ============================================================
// HEALTH
// ============================================================

export async function getHealth() {
  const response = await fetch(
    `${API_BASE_URL}/health`
  );

  return handleResponse(response);
}


// ============================================================
// WEATHER
// ============================================================

export async function getWeather(city) {
  const response = await fetch(
    `${API_BASE_URL}/weather/${encodeURIComponent(city)}`
  );

  return handleResponse(response);
}


// ============================================================
// PLACES
// ============================================================

export async function getPlaces(city) {
  const response = await fetch(
    `${API_BASE_URL}/places/${encodeURIComponent(city)}`
  );

  return handleResponse(response);
}


// ============================================================
// CHAT
// ============================================================

export async function sendChat({
  message,
  conversationId,
}) {
  const response = await fetch(
    `${API_BASE_URL}/chat/`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    }
  );

  return handleResponse(response);
}


// ============================================================
// CHAT HISTORY
// ============================================================

export async function getChatHistory(
  conversationId
) {
  const response = await fetch(
    `${API_BASE_URL}/chat/history/${conversationId}`
  );

  return handleResponse(response);
}


// ============================================================
// ITINERARY
// ============================================================

export async function createItinerary({
  city,
  days,
  interests,
  budget,
  origin = null,
  destination = null,
  customLocations = [],
}) {
  const response = await fetch(
    `${API_BASE_URL}/itinerary/`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        city,
        days,
        interests,
        budget,
        origin,
        destination,
        custom_locations: customLocations,
      }),
    }
  );

  return handleResponse(response);
}


export { API_BASE_URL };

// ============================================================
// SIGHTSEEING VISION
// ============================================================

export async function analyzeSightseeingImage(
  imageBlob
) {

  const formData =
    new FormData();


  formData.append(
    "image",
    imageBlob,
    "sightseeing-capture.jpg"
  );


  const response =
    await fetch(
      `${API_BASE_URL}/vision/analyze`,
      {
        method: "POST",
        body: formData,
      }
    );


  return handleResponse(
    response
  );
}

// ============================================================
// SIGHTSEEING AUDIO GUIDE
// ============================================================

export async function generateSightseeingAudio({
  placeName,
  summary,
  history,
  travelTip,
}) {

  const response =
    await fetch(
      `${API_BASE_URL}/sightseeing-audio/`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json",
        },

        body: JSON.stringify({

          place_name:
            placeName || "",

          summary:
            summary || "",

          history:
            history || "",

          travel_tip:
            travelTip || "",

        }),

      }
    );


  if (!response.ok) {

    let message =
      `Audio guide failed with HTTP ${response.status}`;


    try {

      const data =
        await response.json();

      message =
        data?.detail ||
        message;

    } catch {
      // Response may not contain JSON.
    }


    throw new Error(
      message
    );

  }


  return await response.blob();
}

// ============================================================
// DYNAMIC ITINERARY DISRUPTION ANALYSIS
// ============================================================

export async function analyzeTripDisruptions({
  city,
  itinerary,
}) {

  const response =
    await fetch(
      `${API_BASE_URL}/disruptions/analyze`,
      {

        method: "POST",

        headers: {
          "Content-Type":
            "application/json",
        },

        body: JSON.stringify({

          city,

          itinerary,

        }),

      }
    );


  return handleResponse(
    response
  );

}

// ============================================================
// APPLY DYNAMIC ITINERARY CHANGE
// ============================================================

export async function applyTripDisruption({
  itinerary,
  day,
  fromIndex,
  toIndex,
}) {

  const response =
    await fetch(
      `${API_BASE_URL}/disruptions/apply`,
      {

        method: "POST",

        headers: {
          "Content-Type":
            "application/json",
        },

        body: JSON.stringify({

          itinerary,

          day,

          from_index:
            fromIndex,

          to_index:
            toIndex,

        }),

      }
    );


  return handleResponse(
    response
  );

}

// ============================================================
// FORECAST-AWARE ITINERARY ANALYSIS
// ============================================================

export async function analyzeForecastTiming({
  city,
  startDate,
  itinerary,
}) {

  const response =
    await fetch(
      `${API_BASE_URL}/disruptions/forecast-analyze`,
      {

        method: "POST",

        headers: {
          "Content-Type":
            "application/json",
        },

        body: JSON.stringify({

          city,

          start_date:
            startDate,

          itinerary,

        }),

      }
    );


  return handleResponse(
    response
  );

}