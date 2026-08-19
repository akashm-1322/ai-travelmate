
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { TravelMateProvider } from "./context/TravelMateContext";
import "./index.css";

ReactDOM.createRoot(
  document.getElementById("root")
).render(
  <React.StrictMode>
    <TravelMateProvider>
      <App />
    </TravelMateProvider>
  </React.StrictMode>
);

