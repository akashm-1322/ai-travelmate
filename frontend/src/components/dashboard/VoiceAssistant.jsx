import React, {
    useEffect,
    useRef,
    useState,
  } from "react";
  import {
    getChatHistory,
  } from "../../services/travelApi";
  
  import { useTravelMate } from "../../context/TravelMateContext";
  
  const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000";
  
  
  export default function VoiceAssistant() {
  
    const {
        conversationId,
        setMessages,
      } = useTravelMate();

    const recordingStartRef =
        useRef(null);
  
    const mediaRecorderRef =
      useRef(null);
  
    const streamRef =
      useRef(null);
  
    const chunksRef =
      useRef([]);
  
    const audioRef =
      useRef(null);
  
    const [
      recording,
      setRecording,
    ] = useState(false);
  
    const [
      processing,
      setProcessing,
    ] = useState(false);
  
    const [
      playing,
      setPlaying,
    ] = useState(false);
  
    const [
      error,
      setError,
    ] = useState("");
  
    const [
      responseAudioUrl,
      setResponseAudioUrl,
    ] = useState(null);
  
  
    // ============================================================
    // CLEANUP
    // ============================================================
  
    useEffect(() => {
  
      return () => {
  
        if (streamRef.current) {
  
          streamRef.current
            .getTracks()
            .forEach(
              (track) =>
                track.stop()
            );
        }
  
        if (responseAudioUrl) {
          URL.revokeObjectURL(
            responseAudioUrl
          );
        }
  
      };
  
    }, [responseAudioUrl]);
  
  
    // ============================================================
    // START RECORDING
    // ============================================================
  
    async function startRecording() {
  
      setError("");
  
      try {
  
        if (
          !navigator.mediaDevices ||
          !navigator.mediaDevices.getUserMedia
        ) {
          throw new Error(
            "Microphone recording is not supported in this browser."
          );
        }
  
  
        const stream =
  await navigator.mediaDevices.getUserMedia({
    audio: {
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
      channelCount: 1,
    },
  });
  
  
        streamRef.current =
          stream;
  
        chunksRef.current =
          [];
  
  
        const supportedTypes = [
          "audio/webm;codecs=opus",
          "audio/webm",
          "audio/ogg;codecs=opus",
        ];
  
  
        const mimeType =
          supportedTypes.find(
            (type) =>
              MediaRecorder.isTypeSupported(
                type
              )
          );
  
  
        const recorder =
          mimeType
            ? new MediaRecorder(
                stream,
                {
                  mimeType,
                }
              )
            : new MediaRecorder(
                stream
              );
  
  
        mediaRecorderRef.current =
          recorder;
  
  
        recorder.ondataavailable =
          (event) => {
  
            if (
              event.data &&
              event.data.size > 0
            ) {
  
              chunksRef.current.push(
                event.data
              );
  
            }
  
          };
  
  
        recorder.onstop =
          async () => {
  
            const blob =
              new Blob(
                chunksRef.current,
                {
                  type:
                    recorder.mimeType ||
                    "audio/webm",
                }
              );
  
  
            stream
              .getTracks()
              .forEach(
                (track) =>
                  track.stop()
              );
  
  
            streamRef.current =
              null;
  
  
            await sendVoiceMessage(
              blob
            );
  
          };
  
        recordingStartRef.current =
        Date.now();

        recorder.start(250);

        recordingStartRef.current =
        Date.now();

        setRecording(true);

        setTimeout(() => {
            console.log(
              "TravelMate microphone ready"
            );
          }, 300);
  
      } catch (err) {
  
        console.error(err);
  
        setError(
          err.message ||
          "Unable to access microphone."
        );
  
      }
  
    }
  
  
    // ============================================================
    // STOP RECORDING
    // ============================================================
  
    function stopRecording() {
        const recordingDuration =
        recordingStartRef.current
          ? Date.now() -
            recordingStartRef.current
          : 0;
      
      if (recordingDuration < 1200) {
        setError(
          "Please speak for at least a second before sending."
        );
      
        return;
      }
  
      if (
        !mediaRecorderRef.current
      ) {
        return;
      }
  
  
      if (
        mediaRecorderRef.current
          .state === "recording"
      ) {
  
        mediaRecorderRef.current.stop();
  
      }
  
  
      setRecording(false);
  
    }
  
  
    // ============================================================
    // SEND AUDIO TO BACKEND
    // ============================================================
  
    async function sendVoiceMessage(
      audioBlob
    ) {
  
      setProcessing(true);
      setError("");
  
  
      try {
  
        const formData =
          new FormData();
  
  
        formData.append(
          "audio",
          audioBlob,
          "travelmate_voice.webm"
        );
  
  
        formData.append(
          "conversation_id",
          conversationId
        );
  
  
        const response =
          await fetch(
            `${API_BASE_URL}/voice/`,
            {
              method: "POST",
              body: formData,
            }
          );
  
  
        if (!response.ok) {
  
          let message =
            `Voice request failed with HTTP ${response.status}`;
  
  
          try {
  
            const data =
              await response.json();
  
            message =
              data?.detail ||
              data?.error ||
              message;
  
          } catch {
            // Response may not be JSON.
          }
  
  
          throw new Error(
            message
          );
  
        }
  
  
        const contentType =
          response.headers.get(
            "content-type"
          ) || "";
  
  
        if (
          !contentType.includes(
            "audio/"
          )
        ) {
  
          throw new Error(
            "Backend did not return an audio response."
          );
  
        }
  
  
        const responseBlob =
          await response.blob();
  
        // ============================================================
// REFRESH SHARED CONVERSATION HISTORY
// ============================================================

try {

    const history =
      await getChatHistory(
        conversationId
      );
  
  
    const updatedMessages =
      (
        history?.messages ||
        []
      ).map(
        (
          message,
          index,
          array
        ) => {
  
          // Voice endpoint adds:
          //
          // user
          // assistant
          //
          // The final pair therefore belongs
          // to this voice interaction.
  
          if (
            index ===
            array.length - 2 &&
            message.role === "user"
          ) {
  
            return {
              ...message,
              input_mode: "voice",
            };
  
          }
  
          return message;
  
        }
      );
  
  
    setMessages(
      updatedMessages
    );
  
  } catch (historyError) {
  
    console.error(
      "Unable to refresh voice conversation:",
      historyError
    );
  
  }

        if (
          responseBlob.size === 0
        ) {
  
          throw new Error(
            "TravelMate returned an empty audio response."
          );
  
        }
  
  
        if (responseAudioUrl) {
  
          URL.revokeObjectURL(
            responseAudioUrl
          );
  
        }
  
  
        const url =
          URL.createObjectURL(
            responseBlob
          );
  
  
        setResponseAudioUrl(
          url
        );
  
  
        // Wait for React state update only for UI.
        // Play directly using the new URL.
  
        const audio =
          new Audio(url);
  
  
        audioRef.current =
          audio;
  
  
        audio.onplay =
          () => {
            setPlaying(true);
          };
  
  
        audio.onended =
          () => {
            setPlaying(false);
          };
  
  
        audio.onerror =
          () => {
  
            setPlaying(false);
  
            setError(
              "Unable to play TravelMate's voice response."
            );
  
          };
  
  
        await audio.play();
  
      } catch (err) {
  
        console.error(
          "Voice error:",
          err
        );
  
  
        setError(
          err.message ||
          "Voice request failed."
        );
  
      } finally {
  
        setProcessing(false);
  
      }
  
    }
  
  
    // ============================================================
    // REPLAY RESPONSE
    // ============================================================
  
    async function replayResponse() {
  
      if (!responseAudioUrl) {
        return;
      }
  
  
      try {
  
        const audio =
          new Audio(
            responseAudioUrl
          );
  
  
        audioRef.current =
          audio;
  
  
        audio.onplay =
          () =>
            setPlaying(true);
  
  
        audio.onended =
          () =>
            setPlaying(false);
  
  
        await audio.play();
  
      } catch (err) {
  
        console.error(err);
  
        setError(
          "Unable to replay audio."
        );
  
      }
  
    }
  
  
    // ============================================================
    // STOP AI SPEECH
    // ============================================================
  
    function stopPlayback() {
  
      if (audioRef.current) {
  
        audioRef.current.pause();
  
        audioRef.current.currentTime =
          0;
  
        setPlaying(false);
  
      }
  
    }
  
  
    // ============================================================
    // UI
    // ============================================================
  
    return (
      <div className="
        rounded-2xl
        bg-gradient-to-br
        from-indigo-600
        via-blue-700
        to-slate-900
        p-6
        shadow-xl
      ">
  
        <div className="flex items-center gap-3">
  
          <div className="
            flex
            h-12
            w-12
            items-center
            justify-center
            rounded-full
            bg-white/15
            text-2xl
            shadow-inner
          ">
            🎙️
          </div>
  
  
          <div>
  
            <h2 className="font-bold text-white">
              Voice TravelMate
            </h2>
  
            <p className="text-sm text-blue-100">
              Speak naturally with your AI travel companion
            </p>
  
          </div>
  
        </div>
  
  
        {/* STATUS */}
  
        <div className="
          mt-5
          rounded-xl
          border
          border-white/10
          bg-black/15
          p-4
        ">
  
          <div className="flex items-center justify-between">
  
            <span className="text-sm font-semibold text-white">
              Status
            </span>
  
  
            {recording && (
              <span className="text-xs font-bold text-red-300">
                ● RECORDING
              </span>
            )}
  
  
            {processing && (
              <span className="text-xs font-bold text-yellow-300">
                ● THINKING
              </span>
            )}
  
  
            {playing && (
              <span className="text-xs font-bold text-emerald-300">
                ● SPEAKING
              </span>
            )}
  
  
            {!recording &&
              !processing &&
              !playing && (
                <span className="text-xs font-bold text-blue-200">
                  READY
                </span>
              )}
  
          </div>
  
  
          <p className="mt-2 text-xs text-blue-100/80">
  
            {recording &&
              "Speak now. TravelMate is listening."}
  
            {processing &&
              "Understanding your voice and preparing a response..."}
  
            {playing &&
              "TravelMate is speaking."}
  
            {!recording &&
              !processing &&
              !playing &&
              "Tap the microphone and ask anything about your trip."}
  
          </p>
  
        </div>
  
  
        {/* MIC BUTTON */}
  
        {!recording ? (
  
          <button
            onClick={
              startRecording
            }
            disabled={
              processing
            }
            className="
              mt-5
              flex
              w-full
              items-center
              justify-center
              gap-2
              rounded-xl
              bg-white
              py-3
              font-bold
              text-blue-700
              shadow-lg
              transition
              hover:-translate-y-0.5
              hover:bg-blue-50
              disabled:cursor-not-allowed
              disabled:opacity-50
            "
          >
            🎤 Start Talking
          </button>
  
        ) : (
  
          <button
            onClick={
              stopRecording
            }
            className="
              mt-5
              flex
              w-full
              items-center
              justify-center
              gap-2
              rounded-xl
              bg-red-500
              py-3
              font-bold
              text-white
              shadow-lg
              transition
              hover:bg-red-400
            "
          >
            ⏹ Stop & Send
          </button>
  
        )}
  
  
        {/* PLAYBACK CONTROLS */}
  
        {responseAudioUrl && (
  
          <div className="
            mt-3
            grid
            grid-cols-2
            gap-2
          ">
  
            <button
              onClick={
                replayResponse
              }
              disabled={
                playing
              }
              className="
                rounded-xl
                border
                border-white/15
                bg-white/10
                py-2.5
                text-sm
                font-semibold
                text-white
                transition
                hover:bg-white/20
                disabled:opacity-40
              "
            >
              🔊 Replay
            </button>
  
  
            <button
              onClick={
                stopPlayback
              }
              disabled={
                !playing
              }
              className="
                rounded-xl
                border
                border-white/15
                bg-white/10
                py-2.5
                text-sm
                font-semibold
                text-white
                transition
                hover:bg-white/20
                disabled:opacity-40
              "
            >
              ⏹ Stop Audio
            </button>
  
          </div>
  
        )}
  
  
        {/* ERROR */}
  
        {error && (
  
          <div className="
            mt-4
            rounded-xl
            border
            border-red-300/30
            bg-red-950/30
            p-3
            text-sm
            font-medium
            text-red-100
          ">
            {error}
          </div>
  
        )}
  
  
        <p className="
          mt-4
          break-all
          text-center
          text-[10px]
          text-blue-200/60
        ">
          Conversation: {conversationId}
        </p>
  
      </div>
    );
  }