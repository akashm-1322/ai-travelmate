import { useEffect, useState } from "react";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

import L from "leaflet";

import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";


const DefaultIcon = L.icon({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,

  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});


L.Marker.prototype.options.icon = DefaultIcon;


function App() {

  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(true);


  useEffect(() => {

    fetch("http://127.0.0.1:8000/places/Chennai")

      .then((response) => response.json())

      .then((data) => {

        setPlaces(data.places);

        setLoading(false);

      })

      .catch((error) => {

        console.error(error);

        setLoading(false);

      });

  }, []);


  if (loading) {
    return <h2>Loading Chennai itinerary...</h2>;
  }


  const route = places.map((place) => [
    place.latitude,
    place.longitude
  ]);


  return (

    <div style={{ padding: "20px" }}>

      <h1>AI TravelMate</h1>

      <h2>Chennai Interactive Trip</h2>


      <div
        style={{
          height: "600px",
          width: "100%"
        }}
      >

        <MapContainer

          center={[13.0478, 80.2785]}

          zoom={12}

          style={{
            height: "100%",
            width: "100%"
          }}

        >

          <TileLayer

            attribution="&copy; OpenStreetMap contributors"

            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"

          />


          {places.map((place) => (

            <Marker

              key={place.name}

              position={[
                place.latitude,
                place.longitude
              ]}

            >

              <Popup>

                <h3>
                  {place.name}
                </h3>

                <p>
                  {place.description}
                </p>

                <strong>
                  Category:
                </strong>{" "}
                {place.category}

              </Popup>

            </Marker>

          ))}


          {route.length > 1 && (

            <Polyline
              positions={route}
            />

          )}

        </MapContainer>

      </div>


      <h2>Trip Stops</h2>

      <div>

        {places.map((place, index) => (

          <div
            key={place.name}
            style={{
              marginBottom: "15px",
              padding: "15px",
              border: "1px solid #ddd",
              borderRadius: "10px"
            }}
          >

            <strong>
              {index + 1}. {place.name}
            </strong>

            <p>
              {place.description}
            </p>

            <small>
              {place.latitude}, {place.longitude}
            </small>

          </div>

        ))}

      </div>

    </div>

  );
}


export default App;