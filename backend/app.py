from flask import Flask, request, jsonify, render_template, session, make_response
from flask_session import Session
from openai import OpenAI
import html
from filelock import FileLock
import os
from datetime import datetime
from uuid import uuid4
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3000", "https://alert-raven-wealthy.ngrok-free.app","https://gen-ai-mu.vercel.app/","https://gen-ai-akhashs-projects-944c749a.vercel.app/"],
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     expose_headers=['Content-Type', 'Authorization'])

# Configure server-side sessions
app.config['SESSION_TYPE'] = 'filesystem'  # or another backend like 'redis'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_default_secret_key')
app.config['SESSION_COOKIE_NAME'] = 'my_session'  # Name for the session cookie
app.config['SESSION_PERMANENT'] = True  # Set to True if you want the session to persist after closing the browser
app.config['SESSION_USE_SIGNER'] = True  # Use a secure cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # This allows cookies to be sent cross-origin
app.config['SESSION_COOKIE_SECURE'] = True  # Make sure you're using HTTPS in production
Session(app)  # Initialize the session

LOG_DIR = 'user_logs'
os.makedirs(LOG_DIR, exist_ok=True)

# Initialize OpenAI client
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = 'https://alert-raven-wealthy.ngrok-free.app'  # Replace with your frontend origin
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    # Handle POST request
    try:
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Debug output
        print(f"Received message: {user_message}")

        # Initialize user session if not already done
        if 'user_id' not in session:
            session['user_id'] = str(uuid4())  # Generate a unique user ID
            print("New user session created with ID:", session['user_id'])

        # Initialize chat history in session if not already done
        if 'chat_history' not in session:
            session['chat_history'] = []  # Initialize an empty chat history

        # Add the user message to the chat history
        session['chat_history'].append({"role": "user", "content": user_message})

        # Create the completion request with the chat history
        completion = client.chat.completions.create(
            model="model-identifier",  # Replace with your actual model identifier
            messages=session['chat_history'],  # Send the full chat history
            temperature=0.7,
        )

        # Access the assistant's message
        response_message = completion.choices[0].message.content

        # Escape HTML characters
        response_message = html.escape(response_message)

        # Add the assistant's response to the chat history
        session['chat_history'].append({"role": "assistant", "content": response_message})

        # Log chat
        log_chat(user_message, response_message)

        # Add CORS headers for POST request
        response = jsonify({"response": response_message})
        response.headers['Access-Control-Allow-Origin'] = 'https://alert-raven-wealthy.ngrok-free.app'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    except Exception as e:
        with open('error_log.txt', 'a') as f:
            f.write(f"{datetime.now()}: {str(e)}\n")
        return jsonify({"error": "Internal Server Error"}), 500

def log_chat(user_message, response_message):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = os.path.join(LOG_DIR, f"log_{timestamp}.txt")

    # Use a single lock for the log directory
    with FileLock(f"{LOG_DIR}/log.lock"):
        with open(log_filename, 'a') as log_file:
            log_file.write(f"User: {user_message}\n")
            log_file.write(f"Jarvis: {response_message}\n")
            log_file.write("-" * 40 + "\n")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
