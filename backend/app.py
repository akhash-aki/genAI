from flask import Flask, request, jsonify, render_template, session
from openai import OpenAI
import html  # To escape HTML characters
from filelock import FileLock
import os
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Set a secret key for session management
app.secret_key = 'your_secret_key'  # Change this to a random secret key for security

LOG_DIR = 'user_logs'
os.makedirs(LOG_DIR, exist_ok=True)  # Create directory if it doesn't exist

# Initialize OpenAI client
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Debug output
        print(f"Received message: {user_message}")

        # Initialize user session if not already done
        if 'user_id' not in session:
            session['user_id'] = 'user_id_example'  # Set a user ID or any identifier

        # Add a system prompt to introduce the AI as "Jarvis"
        system_prompt = {
            "role": "system", 
            "content": "You are an AI named Jarvis developed by Akhash. You are helpful, friendly, and should always introduce yourself as Jarvis when asked."
        }

        # Create the completion request with the system prompt
        completion = client.chat.completions.create(
            model="model-identifier",  # Replace with your actual model identifier
            messages=[system_prompt, {"role": "user", "content": user_message}],
            temperature=0.7,
        )

        # Access the message content
        response_message = completion.choices[0].message.content

        # Escape any HTML characters if the message contains code blocks (```code```)
        if "```" in response_message:
            response_message = html.escape(response_message)

        # Log chat
        log_chat(user_message, response_message)

        return jsonify({"response": response_message}), 200  # Ensure 200 OK response

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

def log_chat(user_message, response_message):
    # Generate a unique log file name based on current date and time
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = os.path.join(LOG_DIR, f"log_{timestamp}.txt")

    # Append the user message and AI response to the log file with file locking
    with FileLock(f"{log_filename}.lock"):  # Create a lock file
        with open(log_filename, 'a') as log_file:
            log_file.write(f"User: {user_message}\n")
            log_file.write(f"Jarvis: {response_message}\n")
            log_file.write("-" * 40 + "\n")  # Separator line for readability

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Run on all interfaces, change port if needed
