const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

async function parseResponse(response) {
  const contentType =
    response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    return await response.json();
  }

  return await response.text();
}

export async function checkBackendHealth() {
  const response = await fetch(
    `${API_BASE_URL}/health`
  );

  const data = await parseResponse(response);

  if (!response.ok) {
    throw new Error(
      data?.detail ||
      "Backend health check failed"
    );
  }

  return data;
}

export async function sendChatMessage({
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

  const data = await parseResponse(response);

  if (!response.ok) {
    const errorMessage =
      data?.detail ||
      data?.message ||
      "Chat request failed";

    throw new Error(errorMessage);
  }

  return data;
}

export async function getConversationHistory(
  conversationId
) {
  const response = await fetch(
    `${API_BASE_URL}/chat/history/${conversationId}`
  );

  const data = await parseResponse(response);

  if (!response.ok) {
    throw new Error(
      data?.detail ||
      "Unable to load conversation history"
    );
  }

  return data;
}

export { API_BASE_URL };
