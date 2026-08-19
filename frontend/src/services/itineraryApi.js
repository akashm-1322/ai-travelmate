import { API_BASE_URL } from "./api";


export async function generateItinerary({
  city,
  days,
  interests,
  budget,
  origin = null,
  destination = null,
  customLocations = [],
}) {
  const url =
    `${API_BASE_URL}/itinerary/`;

  console.log(
    "AI TravelMate itinerary request:",
    url
  );

  let response;

  try {
    response = await fetch(
      url,
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
  } catch (error) {
    console.error(
      "Backend connection failed:",
      error
    );

    throw new Error(
      `Could not connect to AI TravelMate backend at ${API_BASE_URL}. ` +
      `Make sure FastAPI is running on port 8000.`
    );
  }


  let data = null;

  try {
    data = await response.json();
  } catch {
    // Response may not contain JSON.
  }


  if (!response.ok) {
    console.error(
      "Itinerary API error:",
      response.status,
      data
    );

    throw new Error(
      data?.detail ||
      data?.message ||
      `Itinerary request failed with HTTP ${response.status}.`
    );
  }


  return data;
}