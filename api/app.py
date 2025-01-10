from flask import Flask, jsonify, request, render_template

import json

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return '', 204 


@app.route('/conversations', methods=['GET'])
def get_conversations():
    try:
        with open('conversation_history.json', 'r') as file:
            data = json.load(file)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": "Failed to load conversations"}), 500
    
# Endpoint to add a new conversation (POST request)
@app.route('/add_conversation', methods=['POST'])
def add_conversation():
    try:
        data = request.get_json()

        if 'question' not in data or 'answer' not in data:
            return jsonify({"error": "Missing 'question' or 'answer' in the request data"}), 400

        # Check if the file exists, and create it if it doesn't
        if not os.path.exists('conversation_history.json'):
            with open('conversation_history.json', 'w') as file:
                json.dump([], file)

        try:
            with open('conversation_history.json', 'r') as file:
                conversations = json.load(file)
        except json.JSONDecodeError:
            return jsonify({"error": "Error decoding JSON from the conversation file."}), 500

        new_conversation = {
            "question": data['question'],
            "answer": data['answer'],
            "timestamp": data.get('timestamp', 'unknown')
        }
        conversations.append(new_conversation)

        with open('conversation_history.json', 'w') as file:
            json.dump(conversations, file, indent=4)

        return jsonify({"message": "Conversation added successfully!"}), 201

    except Exception as e:
        return jsonify({"error": f"Error adding conversation: {e}"}), 500

@app.route('/')
def home():
    try:
        with open('conversation_history.json', 'r') as file:
            data = json.load(file)
        return render_template('index.html', conversations=data)
    except FileNotFoundError:
        return jsonify({"error": "No conversation history found."}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding the conversation history file."}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
