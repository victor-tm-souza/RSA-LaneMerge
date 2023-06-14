import React, { useEffect } from 'react';
import "./App.css"
import "leaflet/dist/leaflet.css"
import { MapContainer, TileLayer, useMapEvents, Marker, Polyline } from 'react-leaflet'
import L from 'leaflet';
import CoordinatesRefresh from './components/CoordinatesRefresh';
import MCMmessages from './components/MCMmessages'

delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png')
});

function iconCircle() {
  return L.icon({
    iconUrl: require('./img/circle.png'),
    iconSize: new L.Point(8, 8),
  })
}

function LocationMarker() {
  const map = useMapEvents({
    click(e) {
      var popup = L.popup();
      popup
        .setLatLng(e.latlng)
        .setContent("This point has coordinates: (" + e.latlng.lat + ", " + e.latlng.lng + ")")
        .openOn(map);
    }
  })
}

function FirstLine() {
  return (
    <div>
      <Marker icon={iconCircle()} position={[40.644327187923224, -8.657387495040895]}></Marker>
      <Polyline color='blue' positions={[[40.64474541472825, -8.656694144010546], [40.64498149293546, -8.656294494867327]]} />
      <Marker icon={iconCircle()} position={[40.644516458772785, -8.657076358795168]}></Marker>
      <Polyline color='blue' positions={[[40.644327187923224, -8.657387495040895], [40.644516458772785, -8.657076358795168]]} />
      <Marker icon={iconCircle()} position={[40.64474541472825, -8.656694144010546]}></Marker>
      <Polyline color='blue' positions={[[40.644516458772785, -8.657076358795168], [40.64474541472825, -8.656694144010546]]} />
      <Marker icon={iconCircle()} position={[40.64498149293546, -8.656294494867327]}></Marker>
      <Polyline color='blue' positions={[[40.64498149293546, -8.656294494867327], [40.645211464868865, -8.655894845724108]]} />
      <Marker icon={iconCircle()} position={[40.645211464868865, -8.655894845724108]}></Marker>
    </div>
  );
}

function SecondLine() {
  return (
    <div>
      <Marker icon={iconCircle()} position={[40.64434932042932, -8.657415993511679]}></Marker>
      <Polyline color='green' positions={[[40.64434932042932, -8.657415993511679], [40.64454062638292, -8.657107539474966]]} />
      <Marker icon={iconCircle()} position={[40.64454062638292, -8.657107539474966]}></Marker>
      <Polyline color='green' positions={[[40.64454062638292, -8.657107539474966], [40.644768310280604, -8.656727671623232]]} />
      <Marker icon={iconCircle()} position={[40.644768310280604, -8.656727671623232]}></Marker>
      <Polyline color='green' positions={[[40.644768310280604, -8.656727671623232], [40.645006423559465, -8.65632198750973]]} />
      <Marker icon={iconCircle()} position={[40.645006423559465, -8.65632198750973]}></Marker>
      <Polyline color='green' positions={[[40.645006423559465, -8.65632198750973], [40.64523410586812, -8.655930384993555]]} />
      <Marker icon={iconCircle()} position={[40.64523410586812, -8.655930384993555]}></Marker>
    </div>
  );
}


function App() {
  return (
    <>
      <div className='wrapper'>
        <MapContainer id="map" center={[40.64477594212965, -8.656680732965471]} zoom={20}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url='http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
            subdomains={['mt0', 'mt1', 'mt2', 'mt3']}

            maxZoom={50}
            maxNativeZoom={45}
          />
          {/*<LocationMarker />*/}
          <FirstLine />
          <SecondLine />
          <CoordinatesRefresh myId={1} />
          <CoordinatesRefresh myId={2} />
          <CoordinatesRefresh myId={3} />
        </MapContainer>
        <div className='messages'>
          <MCMmessages />
        </div>
      </div>
    </>
  );
}

export default App;
