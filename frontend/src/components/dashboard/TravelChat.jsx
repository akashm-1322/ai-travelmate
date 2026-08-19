import React, {
    useEffect,
    useRef,
    useState,
  } from "react";
  
  import {
    sendChat,
    getChatHistory,
  } from "../../services/travelApi";
  
  import {
    useTravelMate,
  } from "../../context/TravelMateContext";
  
  
  export default function TravelChat() {
  
    const {
      conversationId,
      messages,
      setMessages,
    } = useTravelMate();
  
    const [message, setMessage] =
      useState("");
  
    const [loading, setLoading] =
      useState(false);
  
    const [error, setError] =
      useState("");
  
    const bottomRef =
      useRef(null);
  
  
    // ============================================================
    // LOAD EXISTING CONVERSATION
    // ============================================================
  
    useEffect(() => {
  
      async function loadHistory() {
  
        try {
  
          const data =
            await getChatHistory(
              conversationId
            );
  
          setMessages(
            data?.messages || []
          );
  
        } catch (err) {
  
          console.error(
            "Conversation history error:",
            err
          );
  
        }
  
      }
  
      loadHistory();
  
    }, [
      conversationId,
      setMessages,
    ]);
  
  
    // ============================================================
    // AUTO SCROLL
    // ============================================================
  
    useEffect(() => {
  
      bottomRef.current?.scrollIntoView({
        behavior: "smooth",
      });
  
    }, [
      messages,
      loading,
    ]);
  
  
    // ============================================================
    // SEND TEXT MESSAGE
    // ============================================================
  
    async function sendMessage() {
  
      const text =
        message.trim();
  
      if (
        !text ||
        loading
      ) {
        return;
      }
  
      setLoading(true);
      setError("");
      setMessage("");
  
  
      // Show immediately in UI.
      setMessages(
        (previous) => [
          ...previous,
          {
            role: "user",
            content: text,
            input_mode: "text",
          },
        ]
      );
  
  
      try {
  
        await sendChat({
          message: text,
          conversationId,
        });
  
  
        // Reload authoritative backend history.
        const history =
          await getChatHistory(
            conversationId
          );
  
  
        setMessages(
          history?.messages || []
        );
  
      } catch (err) {
  
        console.error(err);
  
        setError(
          err.message ||
          "Unable to contact TravelMate."
        );
  
      } finally {
  
        setLoading(false);
  
      }
  
    }
  
  
    // ============================================================
    // ENTER TO SEND
    // ============================================================
  
    function handleKeyDown(event) {
  
      if (
        event.key === "Enter" &&
        !event.shiftKey
      ) {
  
        event.preventDefault();
  
        sendMessage();
  
      }
  
    }
  
  
    // ============================================================
    // UI
    // ============================================================
  
    return (
      <div className="rounded-2xl bg-white p-6 shadow-xl">
  
        {/* HEADER */}
  
        <div className="mb-5 flex items-center justify-between">
  
          <div>
  
            <h2 className="text-xl font-extrabold text-slate-900">
              AI Travel Assistant
            </h2>
  
            <p className="mt-1 text-sm text-slate-500">
              Text and voice share the same conversation
            </p>
  
          </div>
  
  
          <span className="
            rounded-full
            bg-emerald-50
            px-3
            py-1
            text-xs
            font-bold
            text-emerald-700
          ">
            ● LIVE
          </span>
  
        </div>
  
  
        {/* CHAT WINDOW */}
  
        <div className="
          h-[430px]
          overflow-y-auto
          rounded-2xl
          border
          border-slate-200
          bg-slate-50
          p-4
        ">
  
          {messages.length === 0 && (
  
            <div className="
              flex
              h-full
              flex-col
              items-center
              justify-center
              text-center
            ">
  
              <div className="text-4xl">
                ✈️
              </div>
  
              <p className="mt-4 font-bold text-slate-800">
                Start your journey
              </p>
  
              <p className="mt-1 max-w-sm text-sm text-slate-500">
                Type here or use Voice TravelMate.
                Both modes share the same AI memory.
              </p>
  
            </div>
  
          )}
  
  
          {messages.map(
            (
              item,
              index
            ) => {
  
              const isUser =
                item.role === "user";
  
              return (
                <div
                  key={index}
                  className={
                    isUser
                      ? "mb-4 flex justify-end"
                      : "mb-4 flex justify-start"
                  }
                >
  
                  <div
                    className={
                      isUser
                        ? `
                          max-w-[85%]
                          rounded-2xl
                          rounded-br-md
                          bg-blue-600
                          px-4
                          py-3
                          text-white
                          shadow
                        `
                        : `
                          max-w-[85%]
                          rounded-2xl
                          rounded-bl-md
                          border
                          border-slate-200
                          bg-white
                          px-4
                          py-3
                          text-slate-800
                          shadow-sm
                        `
                    }
                  >
  
                    <div
                      className={
                        isUser
                          ? "mb-1 text-[10px] font-bold uppercase tracking-wide text-blue-100"
                          : "mb-1 text-[10px] font-bold uppercase tracking-wide text-blue-600"
                      }
                    >
  
                      {isUser
                        ? (
                          item.input_mode === "voice"
                            ? "🎤 You · Voice"
                            : "You"
                        )
                        : "✨ AI TravelMate"
                      }
  
                    </div>
  
  
                    <div className="
                      whitespace-pre-wrap
                      text-sm
                      leading-6
                    ">
                      {item.content}
                    </div>
  
                  </div>
  
                </div>
              );
  
            }
          )}
  
  
          {loading && (
  
            <div className="mb-4 flex justify-start">
  
              <div className="
                rounded-2xl
                border
                border-slate-200
                bg-white
                px-4
                py-3
                shadow-sm
              ">
  
                <div className="text-xs font-bold text-blue-600">
                  ✨ AI TravelMate
                </div>
  
                <div className="mt-2 flex gap-1">
  
                  <Dot />
                  <Dot delay="150ms" />
                  <Dot delay="300ms" />
  
                </div>
  
              </div>
  
            </div>
  
          )}
  
  
          <div ref={bottomRef} />
  
        </div>
  
  
        {/* ERROR */}
  
        {error && (
  
          <div className="
            mt-3
            rounded-xl
            bg-red-50
            p-3
            text-sm
            font-semibold
            text-red-700
          ">
            {error}
          </div>
  
        )}
  
  
        {/* INPUT */}
  
        <div className="mt-4 flex gap-3">
  
          <input
            value={message}
            onChange={(event) =>
              setMessage(
                event.target.value
              )
            }
            onKeyDown={
              handleKeyDown
            }
            placeholder="Ask TravelMate anything..."
            className="field"
          />
  
  
          <button
            onClick={
              sendMessage
            }
            disabled={
              loading ||
              !message.trim()
            }
            className="
              shrink-0
              rounded-xl
              bg-blue-600
              px-6
              font-bold
              text-white
              shadow
              transition
              hover:bg-blue-500
              disabled:cursor-not-allowed
              disabled:opacity-40
            "
          >
            Send
          </button>
  
        </div>
  
  
        <p className="
          mt-3
          text-center
          text-[10px]
          text-slate-400
        ">
          Conversation ID: {conversationId}
        </p>
  
      </div>
    );
  }
  
  
  function Dot({
    delay = "0ms",
  }) {
  
    return (
      <span
        className="
          h-2
          w-2
          animate-bounce
          rounded-full
          bg-blue-500
        "
        style={{
          animationDelay: delay,
        }}
      />
    );
  }