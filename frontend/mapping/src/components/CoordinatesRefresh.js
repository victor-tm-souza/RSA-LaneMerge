import { useEffect, useState } from 'react';
import { Marker } from 'react-leaflet'
import L from 'leaflet';

function iconCar1() {
    return L.icon({
        iconUrl: require('../img/car.png'),
        iconSize: new L.Point(40, 40),
    })
}

const CoordinatesRefresh = ({ myId }) => {

    const [newCoordinates, setNewCoordinates] = useState(() => {
        console.log(myId);
        if (myId === 1) {
            return [40.6443603103219, -8.657333046197893];
        } else if (myId === 2) {
            return [40.64436605970026, -8.657389003783466];
        } else {
            return [40.64439663817633, -8.657339215278627];
        }
    });

    useEffect(() => {
        let socket = new WebSocket('ws://localhost:7555');
        let message;
        // WebSocket event: socket open
        socket.onopen = () => {
            //console.log('WebSocket connection opened.');
        }

        // Function to handle incoming messages
        socket.onmessage = event => {
            message = event.data;
            const id = parseInt(message.split(' ')[0])
            if (myId === id) {
                const lat = parseFloat(message.split(' ')[1]);
                const lon = parseFloat(message.split(' ')[2]);
                setNewCoordinates([lat, lon]);
                console.log(newCoordinates);
            }
        };


        // WebSocket event: connection closed
        socket.onclose = () => {
            //console.log('WebSocket connection closed.');
        };

        return () => {
            socket.close();
        };
    }, [newCoordinates]);

    return (
        <>
            <Marker icon={iconCar1()} position={newCoordinates} />
        </>
    );

};

export default CoordinatesRefresh;