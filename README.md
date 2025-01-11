# Voice Assistant Project

This project is a voice assistant built using Python and the Raspberry Pi. It interacts with the user via speech recognition and text-to-speech functionality, powered by OpenAI's GPT-3. It also uses a small LCD display (Grove LCD) and communicates with an external Flask API for saving conversations.

## Features:
- **Speech recognition**: Converts speech to text using the `SpeechRecognition` library.
- **Text-to-speech**: Converts responses to speech using `pyttsx3` and eSpeak.
- **OpenAI GPT-3 Integration**: Queries OpenAI's GPT-3 for intelligent responses.
- **LCD Display**: Shows the responses and system information like CPU temperature.
- **Flask API**: Stores conversations with a Flask server and retrieves them.
- **Touch sensor**: Pauses or resumes the assistant and opens the `/` page in the browser when touched.

## Prerequisites

Before running this project, you need to have the following installed on your Raspberry Pi:

- **Python 3**: Ensure you have Python 3 installed. If not, install it by running:
    
    sudo apt-get update  
    sudo apt-get install python3 python3-pip

- **eSpeak**: For text-to-speech functionality:
    
    sudo apt-get install espeak

- **Raspberry Pi libraries**: For GPIO control and I2C communication:
    
    sudo apt-get install python3-rpi.gpio python-smbus

### Install Python dependencies
First, create a virtual environment (recommended) and activate it:

    python3 -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate

Then, install all dependencies from the `requirements.txt` file:

    pip install -r requirements.txt

The `requirements.txt` should contain:

    openai
    SpeechRecognition
    pyttsx3
    smbus2
    RPi.GPIO
    psutil
    requests
    flask

---

## Setup Instructions

1. **Clone the repository**:

       git clone https://github.com/yourusername/voice-assistant.git
       cd voice-assistant

2. **Create a Flask server to save conversations**  
   You need to set up a Flask API. Create a Flask app (`app.py`) that listens to POST requests for saving conversations. The API should have a route like:
   
       @app.route('/add_conversation', methods=['POST'])
       def add_conversation():
           # Code to save conversations

3. **Run the Flask server**:  
   Run the Flask app on your Raspberry Pi:

       python3 app.py

   This will start the Flask server, and you can interact with it via your Python script.

---

## Running the Voice Assistant

- **Run the assistant script**:  
      
      python3 voice.py

- **Test the functionality**:
  - The assistant will listen for questions, and you can speak to it.
  - It will query OpenAI's GPT-3 and provide a response both as speech and text.
  - The conversation will be sent to the Flask API for storage.

- **Touch sensor**:  
  If you press the touch sensor connected to GPIO pin 16, it will pause or resume the assistant. If paused, it will open the `/` route of your Flask API in the browser.

---

## Troubleshooting

- **"Could not open lock file" error**:  
  This error occurs when there are permission issues with installing packages. Try running the command with `sudo`:
    
      sudo pip3 install -r requirements.txt

- **"Error decoding JSON from the conversation file"**:  
  Ensure that your `conversation_history.json` is correctly formatted. You can validate your JSON using [jsonlint.com](https://jsonlint.com).

- **Microphone issues**:  
  If the microphone is not recognized, make sure it's connected properly and check the device index using:
    
      python3 -m speech_recognition

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
