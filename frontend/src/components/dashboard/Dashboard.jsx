import React, {
  useState,
} from "react";

import TripPlanner from "./TripPlanner";
import ItineraryPanel from "./ItineraryPanel";
import TravelChat from "./TravelChat";
import LiveContext from "./LiveContext";
import VoiceAssistant from "./VoiceAssistant";
import SightseeingLens from "./SightseeingLens";
import BookingPanel from "./BookingPanel";
import GroupTravel from "./GroupTravel";
import OfflineIndicator from "./OfflineIndicator";
import DynamicCopilot from "./DynamicCopilot";



export default function Dashboard() {

  const [
    itinerary,
    setItinerary,
  ] = useState(null);

  const [
    destination,
    setDestination,
  ] = useState("Chennai");

  const [
    tripStartDate,
    setTripStartDate,
  ] = useState(
    new Date()
      .toISOString()
      .slice(
        0,
        10
      )
  );


  return (
    <div className="min-h-screen bg-slate-950">

      <OfflineIndicator />


      {/* ====================================================== */}
      {/* HEADER */}
      {/* ====================================================== */}

      <header className="border-b border-slate-800 bg-slate-950">

        <div
          className="
            mx-auto
            flex
            w-full
            max-w-7xl
            flex-col
            items-start
            gap-3
            px-4
            py-4
            sm:flex-row
            sm:items-center
            sm:justify-between
            sm:px-6
            sm:py-5
          "
        >

          <div>

            <h1
              className="
                text-xl
                font-extrabold
                tracking-tight
                text-white
                sm:text-2xl
              "
            >
              AI TravelMate
            </h1>

            <p className="mt-1 text-sm text-slate-400">
              Your intelligent travel copilot
            </p>

          </div>


          <div className="flex flex-wrap gap-2">

            <span
              className="
                rounded-full
                bg-emerald-500/10
                px-3
                py-1
                text-xs
                font-bold
                text-emerald-400
              "
            >
              ● AI ONLINE
            </span>

            <span
              className="
                rounded-full
                bg-blue-500/10
                px-3
                py-1
                text-xs
                font-bold
                text-blue-400
              "
            >
              LIVE
            </span>

          </div>

        </div>

      </header>


      {/* ====================================================== */}
      {/* MAIN CONTENT */}
      {/* ====================================================== */}

      <main
        className="
          mx-auto
          w-full
          max-w-7xl
          px-3
          py-4
          sm:px-4
          sm:py-6
          md:px-6
          md:py-8
          lg:px-8
        "
      >


        {/* ==================================================== */}
        {/* TRIP PLANNER */}
        {/* ==================================================== */}

        <TripPlanner

          onItineraryGenerated={
            setItinerary
          }

          onDestinationChange={
            setDestination
          }

        />


        {/* ==================================================== */}
        {/* DASHBOARD GRID */}
        {/* ==================================================== */}

        <section
          className="
            mt-5
            grid
            grid-cols-1
            gap-4
            md:mt-6
            md:gap-5
            lg:mt-8
            lg:grid-cols-3
            lg:gap-6
          "
        >


          {/* ================================================== */}
          {/* LEFT / MAIN COLUMN */}
          {/* ================================================== */}

          <div
            className="
              min-w-0
              space-y-4
              md:space-y-6
              lg:col-span-2
            "
          >

            <TravelChat />


            <ItineraryPanel
              itinerary={
                itinerary
              }
            />


            <BookingPanel />

          </div>


          {/* ================================================== */}
          {/* RIGHT / ASSISTANT COLUMN */}
          {/* ================================================== */}

          <div
            className="
              min-w-0
              space-y-4
              md:space-y-6
            "
          >

        <LiveContext
        city={
          destination
        }
        />


<DynamicCopilot

  city={
    destination
  }

  itinerary={
    itinerary
  }

  startDate={
    tripStartDate
  }

  onStartDateChange={
    setTripStartDate
  }

  onItineraryUpdated={
    setItinerary
  }

/>



        <VoiceAssistant />


        <SightseeingLens />


        <GroupTravel />

          </div>

        </section>

      </main>

    </div>
  );
}