import React, { useState } from 'react';
import './App.css';

function App() {
    const [messages, setMessages] = useState([]); // Store messages
    const [input, setInput] = useState('');       // Store user input

    // Function to send a message
    const sendMessage = async () => {
        if (!input.trim()) return; // Prevent sending empty messages

        // Add user message to chat
        setMessages((prevMessages) => [
            ...prevMessages,
            { role: 'user', content: input },
        ]);

        // Send message to backend
        try {
            const response = await fetch('https://dominant-lab-multiply.ngrok-free.app/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',  
                body: JSON.stringify({ message: input }),
            });

            const data = await response.json();

            if (response.ok) {
                // Add bot response to chat
                setMessages((prevMessages) => [
                    ...prevMessages,
                    { role: 'bot', content: data.response },
                ]);
            } else {
                // Handle error in case the response isn't OK
                setMessages((prevMessages) => [
                    ...prevMessages,
                    { role: 'bot', content: 'Error: Failed to fetch response' },
                ]);
            }
        } catch (error) {
            // Handle network error
            setMessages((prevMessages) => [
                ...prevMessages,
                { role: 'bot', content: 'Error: Could not reach the server.' },
            ]);
        }

        setInput(''); // Clear the input field after sending the message
    };

    return (
        <div className="App">
            <div className="chat-container">
                <div className="chat-window">
                    {messages.map((msg, index) => (
                        <div key={index} className={`message ${msg.role}`}>
                            <span>{msg.content}</span>
                        </div>
                    ))}
                </div>
                <div className="input-container">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your message..."
                        onKeyDown={(e) => e.key === 'Enter' && sendMessage()} // Send message on 'Enter'
                    />
                    <button onClick={sendMessage}>Send</button>
                </div>
            </div>
        </div>
    );
}

export default App;
