import { useState } from "react";
import {
  sendChatMessage,
  checkBackendHealth,
} from "../services/api";
import { useTravelMate } from "../context/TravelMateContext";

export default function TravelChat() {
  const {
    conversationId,
    messages,
    setMessages,
  } = useTravelMate();

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] =
    useState("unknown");
  const [error, setError] = useState("");

  async function testBackend() {
    try {
      setError("");

      const data = await checkBackendHealth();

      if (data?.status === "healthy") {
        setBackendStatus("connected");
      } else {
        setBackendStatus("unknown");
      }
    } catch (err) {
      console.error(err);

      setBackendStatus("offline");
      setError(
        "Unable to connect to AI TravelMate backend."
      );
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const trimmedMessage = input.trim();

    if (!trimmedMessage || loading) {
      return;
    }

    setLoading(true);
    setError("");

    const userMessage = {
      role: "user",
      content: trimmedMessage,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setInput("");

    try {
      const data = await sendChatMessage({
        message: trimmedMessage,
        conversationId,
      });

      const assistantContent =
        data?.response ||
        data?.message ||
        "I received your request, but no response was returned.";

      const assistantMessage = {
        role: "assistant",
        content: assistantContent,
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);

      setBackendStatus("connected");
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
        "Something went wrong while contacting the backend."
      );

      setBackendStatus("offline");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        maxWidth: "900px",
        margin: "40px auto",
        padding: "24px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "24px",
        }}
      >
        <div>
          <h1 style={{ marginBottom: "6px" }}>
            AI TravelMate
          </h1>

          <p
            style={{
              margin: 0,
              color: "#666",
            }}
          >
            Your AI travel copilot
          </p>
        </div>

        <button
          type="button"
          onClick={testBackend}
          style={{
            padding: "10px 16px",
            cursor: "pointer",
          }}
        >
          Test Backend
        </button>
      </div>

      <div
        style={{
          padding: "12px 16px",
          marginBottom: "20px",
          border: "1px solid #ddd",
          borderRadius: "8px",
          background:
            backendStatus === "connected"
              ? "#eefbf0"
              : "#f8f8f8",
        }}
      >
        Backend:{" "}
        <strong>
          {backendStatus === "connected"
            ? "Connected"
            : backendStatus === "offline"
              ? "Offline"
              : "Not tested"}
        </strong>
      </div>

      <div
        style={{
          minHeight: "400px",
          maxHeight: "600px",
          overflowY: "auto",
          border: "1px solid #ddd",
          borderRadius: "12px",
          padding: "20px",
          marginBottom: "20px",
          background: "#fafafa",
        }}
      >
        {messages.length === 0 ? (
          <div
            style={{
              textAlign: "center",
              color: "#777",
              padding: "100px 20px",
            }}
          >
            <h2>Where would you like to go?</h2>

            <p>
              Ask me to plan a trip, find attractions,
              recommend food, or organize your itinerary.
            </p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              style={{
                display: "flex",
                justifyContent:
                  message.role === "user"
                    ? "flex-end"
                    : "flex-start",
                marginBottom: "16px",
              }}
            >
              <div
                style={{
                  maxWidth: "75%",
                  padding: "14px 18px",
                  borderRadius: "14px",
                  background:
                    message.role === "user"
                      ? "#2563eb"
                      : "#ffffff",
                  color:
                    message.role === "user"
                      ? "#ffffff"
                      : "#222",
                  border:
                    message.role === "assistant"
                      ? "1px solid #ddd"
                      : "none",
                  whiteSpace: "pre-wrap",
                  lineHeight: "1.5",
                }}
              >
                <div
                  style={{
                    fontSize: "12px",
                    fontWeight: "bold",
                    marginBottom: "6px",
                    opacity: 0.7,
                  }}
                >
                  {message.role === "user"
                    ? "YOU"
                    : "AI TRAVELMATE"}
                </div>

                {message.content}
              </div>
            </div>
          ))
        )}

        {loading && (
          <div
            style={{
              color: "#777",
              padding: "10px",
            }}
          >
            AI TravelMate is thinking...
          </div>
        )}
      </div>

      {error && (
        <div
          style={{
            padding: "12px",
            marginBottom: "16px",
            borderRadius: "8px",
            background: "#fff0f0",
            color: "#b00020",
          }}
        >
          {error}
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        style={{
          display: "flex",
          gap: "10px",
        }}
      >
        <input
          value={input}
          onChange={(event) =>
            setInput(event.target.value)
          }
          placeholder="Ask AI TravelMate anything..."
          disabled={loading}
          style={{
            flex: 1,
            padding: "14px 16px",
            border: "1px solid #ccc",
            borderRadius: "10px",
            fontSize: "16px",
          }}
        />

        <button
          type="submit"
          disabled={loading || !input.trim()}
          style={{
            padding: "14px 22px",
            border: "none",
            borderRadius: "10px",
            cursor:
              loading || !input.trim()
                ? "not-allowed"
                : "pointer",
          }}
        >
          {loading ? "Sending..." : "Send"}
        </button>
      </form>

      <div
        style={{
          marginTop: "16px",
          fontSize: "12px",
          color: "#888",
        }}
      >
        Conversation ID: {conversationId}
      </div>
    </div>
  );
}
