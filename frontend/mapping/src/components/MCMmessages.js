import React, { useEffect, useState } from 'react';

const WebSocketComponent = () => {
    const [messages, setMessages] = useState([]);

    useEffect(() => {
        // Create a new WebSocket connection
        const socket = new WebSocket('ws://localhost:7556');

        // Listen for WebSocket messages
        socket.onmessage = (event) => {
            const message = event.data;
            const id = parseInt(message.split(' ')[0])

            // Add the new message to the existing messages array
            setMessages((prevMessages) => [...prevMessages, message]);
        };

        // Clean up the WebSocket connection on component unmount
        return () => {
            socket.close();
        };
    }, []);

    return (
        <div>
            <h1>Sent MCM Messages:</h1>
            <br></br>
            {
                messages.map((message, index) => (
                    <div key={index}>
                        <h2>OBU {message.split('*')[0]} - {message.split('*')[1]}</h2>
                        <p>{message.split('*')[2]}</p>
                    </div>
                ))
            }
        </div >
    );
};

export default WebSocketComponent;
