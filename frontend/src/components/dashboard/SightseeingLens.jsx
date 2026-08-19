import React, {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  analyzeSightseeingImage,
  generateSightseeingAudio,
} from "../../services/travelApi";


export default function SightseeingLens() {

  // ============================================================
  // REFS
  // ============================================================

  const videoRef = useRef(null);

  const canvasRef = useRef(null);

  const streamRef = useRef(null);


  // ============================================================
  // CAMERA STATE
  // ============================================================

  const [
    cameraOpen,
    setCameraOpen,
  ] = useState(false);

  const [
    cameraStarting,
    setCameraStarting,
  ] = useState(false);

  const [
    cameraReady,
    setCameraReady,
  ] = useState(false);


  // ============================================================
  // PHOTO / ALBUM STATE
  // ============================================================

  const [
    photos,
    setPhotos,
  ] = useState([]);

  const [
    selectedPhoto,
    setSelectedPhoto,
  ] = useState(null);


  // ============================================================
  // AI STATE
  // ============================================================

  const [
    analyzingPhotoId,
    setAnalyzingPhotoId,
  ] = useState(null);

  const [
    analysisError,
    setAnalysisError,
  ] = useState("");


  // ============================================================
  // GENERAL ERROR
  // ============================================================

  const [
    error,
    setError,
  ] = useState("");

  const audioRef =
  useRef(null);

const [
  audioPhotoId,
  setAudioPhotoId,
] = useState(null);

const [
  audioPlaying,
  setAudioPlaying,
] = useState(false);

const [
  audioError,
  setAudioError,
] = useState("");

  // ============================================================
  // CLEAN CAMERA ON COMPONENT UNMOUNT
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

    };

  }, []);


  // ============================================================
  // DETECT MOBILE
  // ============================================================

  function isMobileDevice() {

    return (
      /Android|iPhone|iPad|iPod/i
        .test(
          navigator.userAgent
        )
    );

  }


  // ============================================================
  // START CAMERA
  // ============================================================

  async function startCamera() {

    setError("");

    setAnalysisError("");

    setCameraStarting(true);

    setCameraReady(false);


    try {

      if (
        !navigator.mediaDevices ||
        !navigator.mediaDevices.getUserMedia
      ) {

        throw new Error(
          "Camera access is not supported in this browser."
        );

      }


      // --------------------------------------------------------
      // Stop previous stream if one exists
      // --------------------------------------------------------

      if (streamRef.current) {

        streamRef.current
          .getTracks()
          .forEach(
            (track) =>
              track.stop()
          );

        streamRef.current = null;

      }


      // --------------------------------------------------------
      // FAST CAMERA CONFIGURATION
      //
      // Laptop:
      // Let browser choose fastest webcam settings.
      //
      // Mobile:
      // Prefer rear camera.
      // --------------------------------------------------------

      const mobile =
        isMobileDevice();


      let stream;


      if (mobile) {

        try {

          stream =
            await navigator.mediaDevices.getUserMedia({

              video: {

                facingMode: {
                  ideal: "environment",
                },

              },

              audio: false,

            });

        } catch {

          // Fallback if rear-camera constraint fails.

          stream =
            await navigator.mediaDevices.getUserMedia({

              video: true,

              audio: false,

            });

        }

      } else {

        // Fastest option for laptops / desktops.

        stream =
          await navigator.mediaDevices.getUserMedia({

            video: true,

            audio: false,

          });

      }


      streamRef.current =
        stream;


      setCameraOpen(true);


      // React renders <video> after cameraOpen = true.
      // We wait one frame so the ref exists.

      requestAnimationFrame(
        async () => {

          const video =
            videoRef.current;


          if (!video) {

            setError(
              "Camera preview could not be initialized."
            );

            return;

          }


          video.srcObject =
            stream;


          try {

            await video.play();

          } catch (playError) {

            console.error(
              "Camera playback error:",
              playError
            );

          }

        }
      );


    } catch (err) {

      console.error(
        "Camera error:",
        err
      );


      if (
        err.name === "NotAllowedError"
      ) {

        setError(
          "Camera permission was denied. Please allow camera access for AI TravelMate."
        );

      } else if (
        err.name === "NotFoundError"
      ) {

        setError(
          "No camera was detected on this device."
        );

      } else if (
        err.name === "NotReadableError"
      ) {

        setError(
          "Your camera is currently being used by another application."
        );

      } else {

        setError(
          err.message ||
          "Unable to start the camera."
        );

      }

    } finally {

      setCameraStarting(false);

    }

  }


  // ============================================================
  // STOP CAMERA
  // ============================================================

  function stopCamera() {

    if (streamRef.current) {

      streamRef.current
        .getTracks()
        .forEach(
          (track) =>
            track.stop()
        );


      streamRef.current =
        null;

    }


    if (videoRef.current) {

      videoRef.current.srcObject =
        null;

    }


    setCameraReady(false);

    setCameraOpen(false);

  }


  // ============================================================
  // CAPTURE PHOTO
  // ============================================================

  function capturePhoto() {

    const video =
      videoRef.current;

    const canvas =
      canvasRef.current;


    if (
      !video ||
      !canvas ||
      !cameraReady ||
      video.videoWidth === 0 ||
      video.videoHeight === 0
    ) {

      setError(
        "Camera is still starting."
      );

      return;

    }


    const context =
      canvas.getContext(
        "2d"
      );


    if (!context) {

      setError(
        "Unable to capture camera image."
      );

      return;

    }


    // --------------------------------------------------------
    // Limit huge camera frames.
    //
    // This keeps AI requests and browser memory reasonable.
    // --------------------------------------------------------

    const MAX_WIDTH = 1600;

    const scale =
      Math.min(
        1,
        MAX_WIDTH /
        video.videoWidth
      );


    canvas.width =
      Math.round(
        video.videoWidth *
        scale
      );

    canvas.height =
      Math.round(
        video.videoHeight *
        scale
      );


    context.drawImage(

      video,

      0,
      0,

      canvas.width,
      canvas.height

    );


    const dataUrl =
      canvas.toDataURL(
        "image/jpeg",
        0.88
      );


    const newPhoto = {

      id:
        crypto.randomUUID(),

      dataUrl,

      capturedAt:
        new Date()
          .toISOString(),

      placeName:
        "",

      description:
        "",

      history:
        "",

      interestingFacts:
        [],

      detectedText:
        "",

      translation:
        "",

      vegetarianItems:
        [],

      travelTip:
        "",

      analysisType:
        "",

      confidence:
        0,

      cityOrRegion:
        "",

      country:
        "",

      aiAnalyzed:
        false,

    };


    setPhotos(
      (previous) => [
        ...previous,
        newPhoto,
      ]
    );


    setSelectedPhoto(
      newPhoto
    );


    setError("");

  }


  // ============================================================
  // DATA URL -> BLOB
  // ============================================================

  async function dataUrlToBlob(
    dataUrl
  ) {

    const response =
      await fetch(
        dataUrl
      );


    return await response.blob();

  }


  // ============================================================
  // AI ANALYSIS
  // ============================================================

  async function analyzePhoto(
    photo
  ) {

    if (!photo) {
      return;
    }


    setAnalysisError("");

    setAnalyzingPhotoId(
      photo.id
    );


    try {

      const imageBlob =
        await dataUrlToBlob(
          photo.dataUrl
        );


      const result =
        await analyzeSightseeingImage(
          imageBlob
        );


      if (
        !result ||
        !result.analysis
      ) {

        throw new Error(
          "TravelMate returned an invalid vision response."
        );

      }


      const analysis =
        result.analysis;


      const updatedPhoto = {

        ...photo,

        placeName:
          analysis.place_name ||
          photo.placeName ||
          "Travel Memory",

        description:
          analysis.summary ||
          "",

        history:
          analysis.history ||
          "",

        interestingFacts:
          analysis.interesting_facts ||
          [],

        detectedText:
          analysis.detected_text ||
          "",

        translation:
          analysis.translation ||
          "",

        vegetarianItems:
          analysis.vegetarian_items ||
          [],

        travelTip:
          analysis.travel_tip ||
          "",

        analysisType:
          analysis.analysis_type ||
          "unknown",

        confidence:
          analysis.confidence ??
          0,

        cityOrRegion:
          analysis.city_or_region ||
          "",

        country:
          analysis.country ||
          "",

        aiAnalyzed:
          true,

      };


      setPhotos(
        (previous) =>
          previous.map(
            (existingPhoto) =>
              existingPhoto.id ===
              photo.id
                ? updatedPhoto
                : existingPhoto
          )
      );


      setSelectedPhoto(
        updatedPhoto
      );


    } catch (err) {

      console.error(
        "Sightseeing AI error:",
        err
      );


      setAnalysisError(
        err.message ||
        "Unable to analyze this photo."
      );


    } finally {

      setAnalyzingPhotoId(
        null
      );

    }

  }

  async function listenToPhoto(
    photo
  ) {
  
    if (!photo?.aiAnalyzed) {
  
      setAudioError(
        "Analyze the photo with AI first."
      );
  
      return;
    }
  
  
    setAudioError("");
  
    setAudioPhotoId(
      photo.id
    );
  
  
    try {
  
      // Stop previous audio.
  
      if (audioRef.current) {
  
        audioRef.current.pause();
  
        audioRef.current.currentTime =
          0;
  
      }
  
  
      const audioBlob =
        await generateSightseeingAudio({
  
          placeName:
            photo.placeName,
  
          summary:
            photo.description,
  
          history:
            photo.history,
  
          travelTip:
            photo.travelTip,
  
        });
  
  
      const audioUrl =
        URL.createObjectURL(
          audioBlob
        );
  
  
      const audio =
        new Audio(
          audioUrl
        );
  
  
      audioRef.current =
        audio;
  
  
      audio.onplay =
        () => {
  
          setAudioPlaying(
            true
          );
  
        };
  
  
      audio.onended =
        () => {
  
          setAudioPlaying(
            false
          );
  
          setAudioPhotoId(
            null
          );
  
          URL.revokeObjectURL(
            audioUrl
          );
  
        };
  
  
      audio.onerror =
        () => {
  
          setAudioPlaying(
            false
          );
  
          setAudioPhotoId(
            null
          );
  
          setAudioError(
            "Unable to play the audio guide."
          );
  
          URL.revokeObjectURL(
            audioUrl
          );
  
        };
  
  
      await audio.play();
  
  
    } catch (err) {
  
      console.error(
        "Sightseeing audio error:",
        err
      );
  
  
      setAudioPlaying(
        false
      );
  
      setAudioPhotoId(
        null
      );
  
  
      setAudioError(
        err.message ||
        "Unable to generate audio guide."
      );
  
    }
  
  }

  function stopAudioGuide() {

    if (audioRef.current) {
  
      audioRef.current.pause();
  
      audioRef.current.currentTime =
        0;
  
    }
  
  
    setAudioPlaying(
      false
    );
  
    setAudioPhotoId(
      null
    );
  
  }
  // ============================================================
  // REMOVE PHOTO
  // ============================================================

  function removePhoto(
    photoId
  ) {

    setPhotos(
      (previous) =>
        previous.filter(
          (photo) =>
            photo.id !==
            photoId
        )
    );


    if (
      selectedPhoto?.id ===
      photoId
    ) {

      setSelectedPhoto(
        null
      );

    }

  }


  // ============================================================
  // CLEAR ALBUM
  // ============================================================

  function clearAlbum() {

    setPhotos([]);

    setSelectedPhoto(null);

    setAnalysisError("");

  }


  // ============================================================
  // DOWNLOAD ONE PHOTO
  // ============================================================

  function downloadPhoto(
    photo,
    index
  ) {

    const link =
      document.createElement(
        "a"
      );


    link.href =
      photo.dataUrl;


    const safeName =
      photo.placeName
        ?.trim()
        ?.replace(
          /[^a-zA-Z0-9-_]+/g,
          "-"
        )
        ||
      `photo-${index + 1}`;


    link.download =
      `travelmate-${safeName}.jpg`;


    document.body.appendChild(
      link
    );


    link.click();

    link.remove();

  }
  // ============================================================
// DOWNLOAD COMPLETE AI TRAVEL ALBUM
// ============================================================

function downloadCompleteAlbum() {

  if (photos.length === 0) {

    setError(
      "Capture at least one photo before downloading the album."
    );

    return;
  }


  // ----------------------------------------------------------
  // ESCAPE HTML
  // ----------------------------------------------------------

  function escapeHtml(
    value
  ) {

    return String(
      value ?? ""
    )
      .replaceAll(
        "&",
        "&amp;"
      )
      .replaceAll(
        "<",
        "&lt;"
      )
      .replaceAll(
        ">",
        "&gt;"
      )
      .replaceAll(
        '"',
        "&quot;"
      )
      .replaceAll(
        "'",
        "&#039;"
      );

  }


  // ----------------------------------------------------------
  // BUILD PHOTO CARDS
  // ----------------------------------------------------------

  const albumCards =
    photos
      .map(
        (
          photo,
          index
        ) => {

          const capturedAt =
            new Date(
              photo.capturedAt
            ).toLocaleString();


          const location =
            [
              photo.cityOrRegion,
              photo.country,
            ]
              .filter(Boolean)
              .join(", ");


          const facts =
            (
              photo.interestingFacts ||
              []
            )
              .map(
                (fact) => (
                  `<li>${escapeHtml(fact)}</li>`
                )
              )
              .join("");


          const vegetarianItems =
            (
              photo.vegetarianItems ||
              []
            )
              .map(
                (item) => (
                  `<li>${escapeHtml(item)}</li>`
                )
              )
              .join("");


          return `
            <article class="memory">

              <div class="image-wrapper">

                <img
                  src="${photo.dataUrl}"
                  alt="${escapeHtml(
                    photo.placeName ||
                    `Travel Memory ${index + 1}`
                  )}"
                />

                <div class="photo-number">
                  MEMORY ${index + 1}
                </div>

                ${
                  photo.aiAnalyzed
                    ? `
                      <div class="ai-badge">
                        AI ENRICHED
                      </div>
                    `
                    : ""
                }

              </div>


              <div class="content">

                <div class="eyebrow">
                  ${
                    escapeHtml(
                      photo.analysisType ||
                      "travel memory"
                    )
                  }
                </div>


                <h2>
                  ${
                    escapeHtml(
                      photo.placeName ||
                      `Travel Memory ${index + 1}`
                    )
                  }
                </h2>


                ${
                  location
                    ? `
                      <div class="location">
                        📍 ${escapeHtml(location)}
                      </div>
                    `
                    : ""
                }


                <div class="timestamp">
                  Captured ${escapeHtml(capturedAt)}
                </div>


                ${
                  photo.description
                    ? `
                      <section>
                        <h3>What you're looking at</h3>

                        <p>
                          ${escapeHtml(photo.description)}
                        </p>
                      </section>
                    `
                    : ""
                }


                ${
                  photo.history
                    ? `
                      <section>
                        <h3>History</h3>

                        <p>
                          ${escapeHtml(photo.history)}
                        </p>
                      </section>
                    `
                    : ""
                }


                ${
                  facts
                    ? `
                      <section>
                        <h3>Interesting facts</h3>

                        <ul>
                          ${facts}
                        </ul>
                      </section>
                    `
                    : ""
                }


                ${
                  photo.detectedText
                    ? `
                      <section>
                        <h3>Detected text</h3>

                        <p>
                          ${escapeHtml(photo.detectedText)}
                        </p>
                      </section>
                    `
                    : ""
                }


                ${
                  photo.translation
                    ? `
                      <section>
                        <h3>Translation</h3>

                        <p>
                          ${escapeHtml(photo.translation)}
                        </p>
                      </section>
                    `
                    : ""
                }


                ${
                  vegetarianItems
                    ? `
                      <section>
                        <h3>Likely vegetarian options</h3>

                        <ul>
                          ${vegetarianItems}
                        </ul>
                      </section>
                    `
                    : ""
                }


                ${
                  photo.travelTip
                    ? `
                      <div class="tip">
                        <strong>
                          TravelMate Tip
                        </strong>

                        <p>
                          ${escapeHtml(photo.travelTip)}
                        </p>
                      </div>
                    `
                    : ""
                }


                ${
                  photo.aiAnalyzed
                    ? `
                      <div class="confidence">

                        <span>
                          AI confidence
                        </span>

                        <strong>
                          ${
                            Math.round(
                              (
                                photo.confidence ||
                                0
                              ) * 100
                            )
                          }%
                        </strong>

                      </div>
                    `
                    : ""
                }

              </div>

            </article>
          `;

        }
      )
      .join("");


  // ----------------------------------------------------------
  // COMPLETE SELF-CONTAINED HTML
  // ----------------------------------------------------------

  const html = `
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8" />

<meta
  name="viewport"
  content="width=device-width, initial-scale=1.0"
/>

<title>
  AI TravelMate Travel Journal
</title>


<style>

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;

  font-family:
    Inter,
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;

  background:
    linear-gradient(
      180deg,
      #020617,
      #0f172a
    );

  color:
    #e2e8f0;
}


.hero {
  padding:
    64px 24px
    48px;

  text-align:
    center;
}


.logo {
  font-size:
    13px;

  font-weight:
    800;

  letter-spacing:
    0.16em;

  text-transform:
    uppercase;

  color:
    #a78bfa;
}


.hero h1 {
  margin:
    12px 0
    8px;

  font-size:
    clamp(
      32px,
      6vw,
      54px
    );

  color:
    #ffffff;
}


.hero p {
  margin:
    auto;

  max-width:
    600px;

  color:
    #94a3b8;

  line-height:
    1.7;
}


.stats {
  display:
    flex;

  flex-wrap:
    wrap;

  justify-content:
    center;

  gap:
    12px;

  margin-top:
    24px;
}


.stat {
  padding:
    8px 14px;

  border:
    1px solid
    #334155;

  border-radius:
    999px;

  background:
    rgba(
      15,
      23,
      42,
      0.7
    );

  color:
    #cbd5e1;

  font-size:
    13px;
}


.album {
  width:
    min(
      1000px,
      calc(
        100% - 28px
      )
    );

  margin:
    0 auto
    60px;

  display:
    grid;

  gap:
    32px;
}


.memory {
  overflow:
    hidden;

  border:
    1px solid
    #1e293b;

  border-radius:
    26px;

  background:
    #0f172a;

  box-shadow:
    0 24px 60px
    rgba(
      0,
      0,
      0,
      0.35
    );
}


.image-wrapper {
  position:
    relative;

  background:
    #020617;
}


.image-wrapper img {
  display:
    block;

  width:
    100%;

  max-height:
    650px;

  object-fit:
    cover;
}


.photo-number {
  position:
    absolute;

  left:
    16px;

  top:
    16px;

  padding:
    7px 10px;

  border-radius:
    999px;

  background:
    rgba(
      2,
      6,
      23,
      0.76
    );

  color:
    #ffffff;

  font-size:
    10px;

  font-weight:
    800;

  letter-spacing:
    0.13em;
}


.ai-badge {
  position:
    absolute;

  right:
    16px;

  top:
    16px;

  padding:
    7px 10px;

  border-radius:
    999px;

  background:
    #7c3aed;

  color:
    white;

  font-size:
    10px;

  font-weight:
    800;
}


.content {
  padding:
    26px;
}


.eyebrow {
  color:
    #a78bfa;

  font-size:
    11px;

  font-weight:
    800;

  letter-spacing:
    0.15em;

  text-transform:
    uppercase;
}


h2 {
  margin:
    7px 0
    4px;

  font-size:
    28px;

  color:
    #ffffff;
}


.location {
  margin-top:
    8px;

  color:
    #cbd5e1;

  font-size:
    14px;
}


.timestamp {
  margin-top:
    5px;

  color:
    #64748b;

  font-size:
    12px;
}


section {
  margin-top:
    24px;
}


section h3 {
  margin:
    0 0
    7px;

  font-size:
    12px;

  letter-spacing:
    0.08em;

  text-transform:
    uppercase;

  color:
    #94a3b8;
}


section p,
section li {
  color:
    #cbd5e1;

  line-height:
    1.75;
}


section ul {
  padding-left:
    22px;
}


.tip {
  margin-top:
    24px;

  padding:
    16px;

  border:
    1px solid
    rgba(
      59,
      130,
      246,
      0.25
    );

  border-radius:
    16px;

  background:
    rgba(
      30,
      64,
      175,
      0.15
    );
}


.tip strong {
  color:
    #60a5fa;
}


.tip p {
  margin:
    6px 0
    0;

  color:
    #bfdbfe;

  line-height:
    1.6;
}


.confidence {
  display:
    flex;

  justify-content:
    space-between;

  margin-top:
    24px;

  padding-top:
    14px;

  border-top:
    1px solid
    #1e293b;

  color:
    #64748b;

  font-size:
    12px;
}


.confidence strong {
  color:
    #cbd5e1;
}


footer {
  padding:
    0 24px
    50px;

  text-align:
    center;

  color:
    #64748b;

  font-size:
    12px;

  line-height:
    1.7;
}


@media (
  max-width: 600px
) {

  .hero {
    padding:
      44px 16px
      32px;
  }

  .content {
    padding:
      20px;
  }

  h2 {
    font-size:
      23px;
  }

}

</style>

</head>


<body>


<header class="hero">

  <div class="logo">
    AI TravelMate
  </div>

  <h1>
    My Travel Journal
  </h1>

  <p>
    A private collection of travel memories
    captured and optionally enriched with
    AI Sightseeing Lens.
  </p>


  <div class="stats">

    <div class="stat">
      📷 ${photos.length} memories
    </div>

    <div class="stat">
      ✨ ${
        photos.filter(
          (photo) =>
            photo.aiAnalyzed
        ).length
      } AI enriched
    </div>

    <div class="stat">
      📅 ${
        new Date()
          .toLocaleDateString()
      }
    </div>

  </div>

</header>


<main class="album">

${albumCards}

</main>


<footer>

  Created with AI TravelMate Sightseeing Lens.

  <br />

  This album was generated from the
  current browser session.

  <br />

  Photos were not permanently stored
  in the TravelMate database.

</footer>


</body>

</html>
`;


  // ----------------------------------------------------------
  // DOWNLOAD
  // ----------------------------------------------------------

  const blob =
    new Blob(
      [html],
      {
        type:
          "text/html;charset=utf-8",
      }
    );


  const url =
    URL.createObjectURL(
      blob
    );


  const link =
    document.createElement(
      "a"
    );


  const date =
    new Date()
      .toISOString()
      .slice(
        0,
        10
      );


  link.href =
    url;


  link.download =
    `travelmate-journal-${date}.html`;


  document.body.appendChild(
    link
  );


  link.click();


  link.remove();


  setTimeout(
    () => {

      URL.revokeObjectURL(
        url
      );

    },
    1000
  );

}

  // ============================================================
  // UI
  // ============================================================

  return (

    <div
      className="
        rounded-2xl
        bg-white
        p-4
        shadow-xl
        sm:p-6
      "
    >

      {/* ====================================================== */}
      {/* HEADER */}
      {/* ====================================================== */}

      <div
        className="
          flex
          flex-wrap
          items-center
          justify-between
          gap-3
        "
      >

        <div
          className="
            flex
            items-center
            gap-3
          "
        >

          <div
            className="
              flex
              h-11
              w-11
              items-center
              justify-center
              rounded-xl
              bg-purple-100
              text-xl
              sm:h-12
              sm:w-12
              sm:text-2xl
            "
          >
            📷
          </div>


          <div>

            <h2
              className="
                font-bold
                text-slate-900
              "
            >
              Sightseeing Lens
            </h2>


            <p
              className="
                text-xs
                text-slate-500
              "
            >
              Capture • Understand • Remember
            </p>

          </div>

        </div>


        <span
          className="
            rounded-full
            bg-purple-50
            px-3
            py-1
            text-xs
            font-bold
            text-purple-700
          "
        >

          {photos.length}

          {" "}

          {
            photos.length === 1
              ? "photo"
              : "photos"
          }

        </span>

      </div>


      {/* ====================================================== */}
      {/* CAMERA AREA */}
      {/* ====================================================== */}

      <div className="mt-5">

        {!cameraOpen && (

          <div
            className="
              rounded-2xl
              border-2
              border-dashed
              border-purple-200
              bg-purple-50
              px-4
              py-8
              text-center
              sm:px-5
              sm:py-10
            "
          >

            <div className="text-5xl">
              📸
            </div>


            <h3
              className="
                mt-4
                font-bold
                text-slate-900
              "
            >
              Start Sightseeing Camera
            </h3>


            <p
              className="
                mx-auto
                mt-2
                max-w-sm
                text-xs
                leading-5
                text-slate-500
              "
            >
              Capture landmarks, monuments,
              menus and travel memories using
              your phone camera or webcam.
            </p>


            <button
              type="button"

              onClick={
                startCamera
              }

              disabled={
                cameraStarting
              }

              className="
                mt-5
                min-h-[46px]
                rounded-xl
                bg-purple-600
                px-6
                py-3
                font-bold
                text-white
                shadow
                transition
                hover:bg-purple-500
                disabled:cursor-not-allowed
                disabled:opacity-50
              "
            >

              {
                cameraStarting
                  ? "Opening Camera..."
                  : "📷 Open Camera"
              }

            </button>

          </div>

        )}


        {/* ==================================================== */}
        {/* LIVE CAMERA */}
        {/* ==================================================== */}

        {cameraOpen && (

          <div>

            <div
              className="
                relative
                w-full
                overflow-hidden
                rounded-xl
                bg-black
                shadow-lg
                sm:rounded-2xl
              "
            >

              <video

                ref={
                  videoRef
                }

                autoPlay

                playsInline

                muted

                onCanPlay={() => {
                  setCameraReady(true);
                }}

                onLoadedMetadata={() => {
                  setCameraReady(true);
                }}

                className="
                  aspect-[3/4]
                  w-full
                  object-cover
                  sm:aspect-video
                "

              />


              {/* LIVE BADGE */}

              <div
                className="
                  absolute
                  left-3
                  top-3
                  flex
                  items-center
                  gap-2
                  rounded-full
                  bg-black/60
                  px-3
                  py-1
                  text-xs
                  font-bold
                  text-white
                  backdrop-blur
                "
              >

                <span
                  className="
                    h-2
                    w-2
                    rounded-full
                    bg-red-500
                  "
                />

                LIVE

              </div>


              {/* PHOTO COUNT */}

              <div
                className="
                  absolute
                  right-3
                  top-3
                  rounded-full
                  bg-black/60
                  px-3
                  py-1
                  text-xs
                  font-bold
                  text-white
                  backdrop-blur
                "
              >
                📷 {photos.length}
              </div>

            </div>


            {/* CAMERA CONTROLS */}

            <div
              className="
                mt-3
                grid
                grid-cols-1
                gap-2
                sm:mt-4
                sm:grid-cols-[1fr_2fr_1fr]
                sm:items-center
                sm:gap-3
              "
            >

              <button
                type="button"

                onClick={
                  stopCamera
                }

                className="
                  min-h-[44px]
                  rounded-xl
                  border
                  border-slate-300
                  bg-white
                  px-3
                  py-3
                  text-sm
                  font-semibold
                  text-slate-700
                  transition
                  hover:bg-slate-50
                "
              >
                Close Camera
              </button>


              <button
                type="button"

                onClick={
                  capturePhoto
                }

                disabled={
                  !cameraReady
                }

                className="
                  flex
                  min-h-[50px]
                  items-center
                  justify-center
                  gap-2
                  rounded-xl
                  bg-gradient-to-r
                  from-purple-600
                  to-indigo-600
                  px-4
                  py-4
                  font-bold
                  text-white
                  shadow-lg
                  transition
                  hover:-translate-y-0.5
                  hover:from-purple-500
                  hover:to-indigo-500
                  disabled:cursor-not-allowed
                  disabled:opacity-40
                "
              >

                {
                  cameraReady
                    ? "📸 Capture Photo"
                    : "Starting Camera..."
                }

              </button>


              <div
                className="
                  rounded-xl
                  bg-slate-50
                  px-3
                  py-3
                  text-center
                  text-xs
                  font-semibold
                  text-slate-500
                "
              >

                {photos.length}
                {" "}
                saved

              </div>

            </div>

          </div>

        )}


        {/* Hidden capture canvas */}

        <canvas
          ref={
            canvasRef
          }

          className="hidden"
        />

      </div>


      {/* ====================================================== */}
      {/* GENERAL CAMERA ERROR */}
      {/* ====================================================== */}

      {error && (

        <div
          className="
            mt-4
            rounded-xl
            bg-red-50
            p-3
            text-sm
            font-semibold
            text-red-700
          "
        >
          {error}
        </div>

      )}


      {/* ====================================================== */}
      {/* ALBUM */}
      {/* ====================================================== */}

      {photos.length > 0 && (

        <section className="mt-7">

          <div
            className="
              mb-4
              flex
              flex-wrap
              items-center
              justify-between
              gap-3
            "
          >

            <div>

              <h3
                className="
                  font-bold
                  text-slate-900
                "
              >
                Trip Album
              </h3>


              <p
                className="
                  text-xs
                  text-slate-500
                "
              >
                Captured during this browser session
              </p>

            </div>


            <button
              type="button"

              onClick={
                clearAlbum
              }

              className="
                text-xs
                font-bold
                text-red-500
                hover:text-red-700
              "
            >
              Clear Album
            </button>

          </div>


          <div
            className="
              grid
              grid-cols-2
              gap-2
              sm:gap-3
              md:grid-cols-3
              xl:grid-cols-4
            "
          >

            {photos.map(
              (
                photo,
                index
              ) => (

                <button

                  type="button"

                  key={
                    photo.id
                  }

                  onClick={() =>
                    setSelectedPhoto(
                      photo
                    )
                  }

                  className="
                    group
                    relative
                    overflow-hidden
                    rounded-xl
                    border
                    border-slate-200
                    bg-slate-50
                    text-left
                    shadow-sm
                    transition
                    hover:-translate-y-0.5
                    hover:shadow-md
                  "
                >

                  <img
                    src={
                      photo.dataUrl
                    }

                    alt={
                      photo.placeName ||
                      `Travel capture ${index + 1}`
                    }

                    className="
                      aspect-square
                      w-full
                      object-cover
                    "
                  />


                  {photo.aiAnalyzed && (

                    <div
                      className="
                        absolute
                        right-2
                        top-2
                        rounded-full
                        bg-purple-600
                        px-2
                        py-1
                        text-[9px]
                        font-bold
                        text-white
                        shadow
                      "
                    >
                      ✨ AI
                    </div>

                  )}


                  <div
                    className="
                      absolute
                      inset-x-0
                      bottom-0
                      bg-gradient-to-t
                      from-black/90
                      via-black/60
                      to-transparent
                      p-3
                      text-white
                    "
                  >

                    <p
                      className="
                        truncate
                        text-xs
                        font-bold
                      "
                    >

                      {
                        photo.placeName ||
                        `Photo ${index + 1}`
                      }

                    </p>


                    <p
                      className="
                        mt-0.5
                        text-[10px]
                        text-white/70
                      "
                    >

                      {
                        new Date(
                          photo.capturedAt
                        ).toLocaleTimeString()
                      }

                    </p>

                  </div>

                  

                </button>

              )
            )}

          </div>
          {/* COMPLETE ALBUM DOWNLOAD */}

<button
  type="button"

  onClick={
    downloadCompleteAlbum
  }

  className="
    mt-5
    flex
    min-h-[48px]
    w-full
    items-center
    justify-center
    gap-2
    rounded-xl
    bg-gradient-to-r
    from-purple-600
    to-indigo-600
    px-4
    py-3
    font-bold
    text-white
    shadow-lg
    transition
    hover:-translate-y-0.5
    hover:from-purple-500
    hover:to-indigo-500
  "
>
  📖 Download AI Travel Journal
</button>

        </section>

      )}


      {/* ====================================================== */}
      {/* SELECTED PHOTO */}
      {/* ====================================================== */}

      {selectedPhoto && (

        <section
          className="
            mt-6
            rounded-2xl
            border
            border-purple-100
            bg-purple-50
            p-4
          "
        >

          <div
            className="
              flex
              flex-col
              gap-4
              sm:flex-row
            "
          >

            <img
              src={
                selectedPhoto.dataUrl
              }

              alt="Selected travel memory"

              className="
                h-48
                w-full
                rounded-xl
                object-cover
                sm:h-28
                sm:w-28
                sm:shrink-0
              "
            />


            <div
              className="
                min-w-0
                flex-1
              "
            >

              <div
                className="
                  text-xs
                  font-bold
                  uppercase
                  tracking-wide
                  text-purple-600
                "
              >
                Selected Memory
              </div>


              <h4
                className="
                  mt-1
                  font-bold
                  text-slate-900
                "
              >

                {
                  selectedPhoto.placeName ||
                  "Sightseeing Photo"
                }

              </h4>


              <p
                className="
                  mt-1
                  text-xs
                  text-slate-500
                "
              >

                {
                  new Date(
                    selectedPhoto.capturedAt
                  ).toLocaleString()
                }

              </p>


              <div
                className="
                  mt-3
                  flex
                  flex-wrap
                  gap-2
                "
              >

                <button

                  type="button"

                  onClick={() => {

                    const index =
                      photos.findIndex(
                        (photo) =>
                          photo.id ===
                          selectedPhoto.id
                      );


                    downloadPhoto(
                      selectedPhoto,
                      index
                    );

                  }}

                  className="
                    rounded-lg
                    bg-white
                    px-3
                    py-2
                    text-xs
                    font-bold
                    text-purple-700
                    shadow-sm
                  "
                >
                  ⬇ Download
                </button>


                <button

                  type="button"

                  onClick={() =>
                    removePhoto(
                      selectedPhoto.id
                    )
                  }

                  className="
                    rounded-lg
                    bg-red-50
                    px-3
                    py-2
                    text-xs
                    font-bold
                    text-red-600
                  "
                >
                  Remove
                </button>


                <button

                  type="button"

                  onClick={() =>
                    analyzePhoto(
                      selectedPhoto
                    )
                  }

                  disabled={
                    analyzingPhotoId ===
                    selectedPhoto.id
                  }

                  className="
                    rounded-lg
                    bg-purple-600
                    px-3
                    py-2
                    text-xs
                    font-bold
                    text-white
                    transition
                    hover:bg-purple-500
                    disabled:cursor-not-allowed
                    disabled:opacity-50
                  "
                >

                  {
                    analyzingPhotoId ===
                    selectedPhoto.id
                      ? "✨ Analyzing..."
                      : selectedPhoto.aiAnalyzed
                        ? "✨ Analyze Again"
                        : "✨ Analyze with AI"
                  }

                </button>

              </div>

            </div>

          </div>


          {/* ================================================== */}
          {/* AI ERROR */}
          {/* ================================================== */}

          {analysisError && (

            <div
              className="
                mt-4
                rounded-xl
                bg-red-50
                p-3
                text-sm
                font-semibold
                text-red-700
              "
            >
              {analysisError}
            </div>

          )}


          {/* ================================================== */}
          {/* AI RESULT */}
          {/* ================================================== */}

          {selectedPhoto.aiAnalyzed && (

            <div
              className="
                mt-5
                space-y-4
                rounded-xl
                bg-white
                p-4
                shadow-sm
              "
            >

              {/* IDENTIFICATION */}

              <div>

                <div
                  className="
                    text-[10px]
                    font-bold
                    uppercase
                    tracking-wider
                    text-purple-600
                  "
                >
                  AI Identification
                </div>


                <h3
                  className="
                    mt-1
                    text-lg
                    font-extrabold
                    text-slate-900
                  "
                >

                  {
                    selectedPhoto.placeName ||
                    "Travel Scene"
                  }

                </h3>


                {(
                  selectedPhoto.cityOrRegion ||
                  selectedPhoto.country
                ) && (

                  <p
                    className="
                      mt-1
                      text-xs
                      text-slate-500
                    "
                  >
                    📍{" "}

                    {
                      [
                        selectedPhoto.cityOrRegion,
                        selectedPhoto.country,
                      ]
                        .filter(Boolean)
                        .join(", ")
                    }

                  </p>

                )}

              </div>
              {/* AUDIO GUIDE CONTROLS */}

<div
  className="
    flex
    flex-wrap
    gap-2
  "
>

  <button
    type="button"

    onClick={() =>
      listenToPhoto(
        selectedPhoto
      )
    }

    disabled={
      audioPhotoId ===
      selectedPhoto.id &&
      audioPlaying
    }

    className="
      rounded-xl
      bg-gradient-to-r
      from-blue-600
      to-indigo-600
      px-4
      py-2.5
      text-xs
      font-bold
      text-white
      shadow
      transition
      hover:from-blue-500
      hover:to-indigo-500
      disabled:opacity-50
    "
  >

    {
      audioPhotoId ===
        selectedPhoto.id &&
      audioPlaying
        ? "🔊 Speaking..."
        : "🔊 Listen to Guide"
    }

  </button>


  {audioPlaying && (

    <button
      type="button"

      onClick={
        stopAudioGuide
      }

      className="
        rounded-xl
        border
        border-slate-300
        bg-white
        px-4
        py-2.5
        text-xs
        font-bold
        text-slate-700
      "
    >
      ⏹ Stop
    </button>

  )}

</div>

{/* AUDIO GUIDE ERROR */}

{audioError && (

<div
  className="
    rounded-xl
    bg-red-50
    p-3
    text-xs
    font-semibold
    text-red-700
  "
>
  {audioError}
</div>

)}

              {/* SUMMARY */}

              {selectedPhoto.description && (

                <InfoBlock
                  title="What you're looking at"
                >
                  {selectedPhoto.description}
                </InfoBlock>

              )}


              {/* HISTORY */}

              {selectedPhoto.history && (

                <InfoBlock
                  title="History"
                >
                  {selectedPhoto.history}
                </InfoBlock>

              )}


              {/* FACTS */}

              {selectedPhoto
                .interestingFacts
                ?.length > 0 && (

                <InfoBlock
                  title="Interesting facts"
                >

                  <ul
                    className="
                      list-disc
                      space-y-1
                      pl-4
                    "
                  >

                    {
                      selectedPhoto
                        .interestingFacts
                        .map(
                          (
                            fact,
                            index
                          ) => (

                            <li
                              key={index}
                            >
                              {fact}
                            </li>

                          )
                        )
                    }

                  </ul>

                </InfoBlock>

              )}


              {/* DETECTED TEXT */}

              {selectedPhoto.detectedText && (

                <InfoBlock
                  title="Text detected"
                >
                  {selectedPhoto.detectedText}
                </InfoBlock>

              )}


              {/* TRANSLATION */}

              {selectedPhoto.translation && (

                <InfoBlock
                  title="Translation"
                >
                  {selectedPhoto.translation}
                </InfoBlock>

              )}


              {/* VEGETARIAN ITEMS */}

              {selectedPhoto
                .vegetarianItems
                ?.length > 0 && (

                <InfoBlock
                  title="Likely vegetarian options"
                >

                  <ul
                    className="
                      list-disc
                      space-y-1
                      pl-4
                    "
                  >

                    {
                      selectedPhoto
                        .vegetarianItems
                        .map(
                          (
                            item,
                            index
                          ) => (

                            <li
                              key={index}
                            >
                              {item}
                            </li>

                          )
                        )
                    }

                  </ul>

                </InfoBlock>

              )}


              {/* TRAVEL TIP */}

              {selectedPhoto.travelTip && (

                <div
                  className="
                    rounded-xl
                    bg-blue-50
                    p-3
                  "
                >

                  <div
                    className="
                      text-xs
                      font-bold
                      text-blue-700
                    "
                  >
                    💡 TravelMate Tip
                  </div>


                  <p
                    className="
                      mt-1
                      text-xs
                      leading-5
                      text-blue-800
                    "
                  >
                    {selectedPhoto.travelTip}
                  </p>

                </div>

              )}


              {/* CONFIDENCE */}

              <div
                className="
                  flex
                  items-center
                  justify-between
                  border-t
                  border-slate-100
                  pt-3
                "
              >

                <span
                  className="
                    text-xs
                    text-slate-500
                  "
                >
                  AI confidence
                </span>


                <span
                  className="
                    text-xs
                    font-bold
                    text-slate-700
                  "
                >

                  {
                    Math.round(
                      (
                        selectedPhoto
                          .confidence ||
                        0
                      ) * 100
                    )
                  }
                  %

                </span>

              </div>

            </div>

          )}

        </section>

      )}


      {/* ====================================================== */}
      {/* PRIVACY */}
      {/* ====================================================== */}

      <div
        className="
          mt-6
          rounded-xl
          border
          border-emerald-100
          bg-emerald-50
          p-3
        "
      >

        <p
          className="
            text-xs
            font-bold
            text-emerald-800
          "
        >
          🔒 Session-only album
        </p>


        <p
          className="
            mt-1
            text-[11px]
            leading-5
            text-emerald-700
          "
        >
          Captured photos remain in browser memory.
          A selected image is sent temporarily for
          AI analysis, but TravelMate does not save
          these photographs in its database.
        </p>

      </div>

    </div>

  );

}


// ============================================================
// REUSABLE AI INFORMATION BLOCK
// ============================================================

function InfoBlock({
  title,
  children,
}) {

  return (

    <div>

      <h4
        className="
          text-xs
          font-bold
          uppercase
          tracking-wide
          text-slate-500
        "
      >
        {title}
      </h4>


      <div
        className="
          mt-1
          text-sm
          leading-6
          text-slate-700
        "
      >
        {children}
      </div>

    </div>

  );

}