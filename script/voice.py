import openai
import speech_recognition as sr
import pyttsx3
import os
import time
import smbus
import RPi.GPIO as GPIO
import psutil
import datetime
import requests
import threading
import webbrowser

# Grove LCD constants
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e

# Initialize SMBus for I2C
rev = GPIO.RPI_REVISION
bus = smbus.SMBus(1 if rev in [2, 3] else 0)

# Touch Sensor Setup
TOUCH_PIN = 16  

# Initialize GPIO for the touch sensor
GPIO.setmode(GPIO.BCM)
GPIO.setup(TOUCH_PIN, GPIO.IN)

# Variables to control the assistant state
is_paused = False  # Keeps track of the assistant state (paused or running)

# LCD Grove Functions
def setRGB(r, g, b):
    bus.write_byte_data(DISPLAY_RGB_ADDR, 0, 0)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 1, 0)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 0x08, 0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 4, r)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 3, g)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 2, b)

def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x80, cmd)

def setText(text):
    textCommand(0x01)  # Clear screen
    time.sleep(0.05)
    textCommand(0x08 | 0x04)  # Display on, no cursor
    textCommand(0x28)  # 2 lines
    time.sleep(0.05)
    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
        if c == '\n':
            continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x40, ord(c))

def scrollText(text):
    """Scroll text on the first line of the LCD, leaving the second line empty."""
    if len(text) <= 16:
        setText(text + "\n")
        return

    display_text = text.ljust(len(text) + 16)  # Add padding for smooth scrolling
    textCommand(0x01)
    for i in range(len(display_text) - 15):  # Scroll in 16-character chunks
        line_to_show = display_text[i:i + 16]
        textCommand(0x02)  # Return cursor to beginning
        for char in line_to_show:
            bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x40, ord(char))
        time.sleep(0.1)  # Adjust scroll speed

# OpenAI API key
openai.api_key = "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"

def get_microphone_index():
    """Identify and return the correct microphone device index."""
    mic_list = sr.Microphone.list_microphone_names()
    print("Available microphones:")
    for idx, name in enumerate(mic_list):
        print(f"{idx}: {name}")
    return 2 if len(mic_list) > 2 else 0

def voice_to_text():
    recognizer = sr.Recognizer()
    microphone_index = get_microphone_index()
    mic = sr.Microphone(device_index=microphone_index, sample_rate=16000)
    with mic as source:
        print("Listening... Make sure the microphone is connected.")
        try:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)
            print("Processing audio...")
            text = recognizer.recognize_google(audio, language="en-US")
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand.")
            return ""
        except sr.RequestError as e:
            print(f"Error accessing the speech recognition service: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected error in voice-to-text conversion: {e}")
            return ""

def ask_chatgpt(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question},
            ],
            max_tokens=150,
            temperature=0.7,
        )
        response = response.choices[0].message['content']
        return response.strip()
    except Exception as e:
        print(f"Error querying OpenAI: {e}")
        return "Sorry, I encountered an issue retrieving the response."

def text_to_speech(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    # Select an English-compatible voice for Raspberry Pi
    for voice in voices:
        if "en" in voice.id or "english" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    # Set speech rate and volume
    engine.setProperty('rate', 150)  # Words per minute
    engine.setProperty('volume', 0.9)  # Volume level

    try:
        engine.say(text)
        engine.runAndWait()
    except RuntimeError as e:
        print(f"Error in TTS engine: {e}")
    except Exception as e:
        print(f"Unexpected error in text-to-speech: {e}")

# Function to send conversation to the Flask server
def send_conversation_to_api(question, answer):
    url = 'http://127.0.0.1:5000/add_conversation'
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = {
        'question': question,
        'answer': answer,
        'timestamp': timestamp
    }

    print("Sending data:", data)  # Add this line to see the data being sent

    try:
        response = requests.post(url, json=data)
        if response.status_code == 201:
            print("Conversation successfully added to the server.")
        else:
            print(f"Error adding conversation: {response.status_code}")
            print("Response content:", response.text)  # Log the response content for more details
    except requests.exceptions.RequestException as e:
        print(f"Failed to send conversation to API: {e}")

# Function to handle touch sensor events
def touch_sensor_handler():
    global is_paused
    while True:
        if GPIO.input(TOUCH_PIN) == GPIO.HIGH:  # Check if the touch sensor is pressed
            if is_paused:
                print("Resuming the assistant...")
                setText("Assistant Resumed")
                is_paused = False  # Change state to "running"
            else:
                print("Pausing the assistant...")
                setText("Assistant Paused")
                is_paused = True  # Change state to "paused"
                webbrowser.open("http://127.0.0.1:5000/")  # Navigate to the API "/" page
            time.sleep(0.5)  # Short wait to avoid multiple triggers

# Function to get CPU temperature
def get_cpu_temperature():
    try:
        temperature = psutil.sensors_temperatures()
        if "cpu_thermal" in temperature:
            return temperature["cpu_thermal"][0].current
        else:
            print("Could not get temperature.")
            return None
    except Exception as e:
        print(f"Error fetching CPU temperature: {e}")
        return None

# Function to display CPU temperature on LCD
def display_cpu_temperature():
    temperature = get_cpu_temperature()
    if temperature:
        temperature_text = f"CPU Temp: {temperature}°C"
        setText(temperature_text)
    else:
        setText("Error getting temp")

if __name__ == "__main__":
    print("Starting voice assistant. Press Ctrl+C to exit.")
    setRGB(0, 128, 255)  # Set initial LCD color to blue
    setText("Voice Assistant\nReady!")

    # Start the touch sensor handler in a separate thread
    touch_thread = threading.Thread(target=touch_sensor_handler)
    touch_thread.daemon = True  
    touch_thread.start()

    while True:
        try:
            if is_paused:
                time.sleep(1)  # Wait if the assistant is paused
                continue  # Skip the rest of the logic if paused

            print("Ask your question:")
            user_input = voice_to_text()

            if user_input:
                print(f"You asked: {user_input}")
                response = ask_chatgpt(user_input)
            else:
                response = "Sorry, I couldn't understand."

            print(f"Response: {response}")
            text_to_speech(response)

            # Send the conversation to the Flask server
            send_conversation_to_api(user_input, response)

            # Display the response on the LCD screen
            setRGB(0, 255, 0)  # Change color to green for response
            scrollText(response)

            # Display CPU temperature on the LCD
            display_cpu_temperature()

        except KeyboardInterrupt:
            print("Exiting the assistant. Goodbye!")
            setText("Goodbye!")
            GPIO.cleanup()
            setRGB(255, 0, 0)  # Set color to red before exit
            break
        except Exception as e:
            print(f"Unexpected error in main loop: {e}")
