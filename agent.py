import streamlit as st
import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import requests
import wikipedia
import time

# ============ CONFIG ============
OPENWEATHER_API_KEY = "YIUR API KEY"

# ============ SESSION STATE ============
if 'response' not in st.session_state:
    st.session_state.response = ""
if 'last_spoken' not in st.session_state:
    st.session_state.last_spoken = ""
if 'command_history' not in st.session_state:
    st.session_state.command_history = []

# ============ CORE FUNCTIONS ============
def speak(text):
    """Convert text to speech with fresh engine every time."""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if "female" in voice.name.lower() or "zira" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.say(text)
        engine.runAndWait()
        time.sleep(0.3)
        engine.stop()
    except Exception as e:
        print("Error speaking:", e)

def listen():
    """Listen to voice input and return as text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio, language="en-in")
            st.session_state.command_history.append(("user", command))
            return command.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""

def get_weather(city):
    """Fetch live weather for a given city."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()
    if response.get("cod") != 200:
        return f"❌ Could not find weather data for {city}."
    temp = response['main']['temp']
    desc = response['weather'][0]['description']
    return f"The temperature in {city} is {temp}°C with {desc}."

def get_wikipedia_summary(query):
    """Fetch a quick summary from Wikipedia."""
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found, try being more specific: {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        return "❌ No information found on Wikipedia."

def process_command(command):
    """Process the given voice/text command."""
    if not command:
        return "I didn't catch that. Please try again."
    
    if "weather" in command:
        if "weather in" in command:
            city = command.split("weather in")[-1].strip()
        else:
            city = command.replace("weather", "").strip()
        if city:
            return get_weather(city)
        else:
            return "Please specify a city. Example: 'weather in Lucknow'."
    
    elif "temperature" in command:
        if "temperature in" in command:
            city = command.split("temperature in")[-1].strip()
        else:
            city = command.replace("temperature", "").strip()
        if city:
            return get_weather(city)
        else:
            return "Please specify a city for temperature."
    
    elif "open" in command:
        # Open any website
        website = command.replace("open", "").strip().replace(" ", "")
        if not website.startswith("http"):
            website = "https://www." + website + ".com"
        try:
            webbrowser.open(website)
            return f"Opening {website}"
        except:
            return f"Cannot open {website}"
    
    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        return f"The current time is {current_time}."
    
    elif "wikipedia" in command or "who is" in command or "what is" in command:
        search_term = command.replace("wikipedia", "").replace("who is", "").replace("what is", "").strip()
        if search_term:
            return get_wikipedia_summary(search_term)
        else:
            return "Please specify what you want to search on Wikipedia."
    
    elif "exit" in command or "quit" in command:
        return "Goodbye!"
    
    else:
        return "Sorry, I didn't understand that. Try asking about weather, time, Wikipedia, or opening a website."

# ============ STREAMLIT UI ============
st.set_page_config(page_title="MyEAIAgent", page_icon="🤖", layout="wide")
st.markdown("<h1 style='text-align: center; color: #6A0DAD;'>🤖 MyEAIAgent</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #8A2BE2;'>Your Personal AI Voice Assistant</h4>", unsafe_allow_html=True)
st.markdown("---")

# Input Section
col1, col2 = st.columns([1,3])

with col1:
    if st.button("🎙️ Speak Command"):
        voice_command = listen()
        if voice_command:
            response = process_command(voice_command)
            st.session_state.response = response
            st.session_state.command_history.append(("assistant", response))
            speak(response)

with col2:
    user_input = st.text_input("Or type your command here:", placeholder="e.g., 'What's the weather in London?'")
    if st.button("▶️ Run Text Command"):
        if user_input:
            st.session_state.command_history.append(("user", user_input))
            response = process_command(user_input.lower())
            st.session_state.response = response
            st.session_state.command_history.append(("assistant", response))
            speak(response)

# Display Response
st.markdown("### 💬 Response:")
if st.session_state.response:
    st.markdown(f"<div style='background-color:#E6F0FF;padding:15px;border-radius:10px'>{st.session_state.response}</div>", unsafe_allow_html=True)
else:
    st.info("Your response will appear here after you give a command.")

# Command History
st.markdown("### 📜 Command History")
for sender, msg in st.session_state.command_history[-10:]:
    if sender == "user":
        st.markdown(f"👤 You: {msg}")
    else:
        st.markdown(f"🤖 Assistant: {msg}")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Built with ❤️ by Divyanshi Singh</div>", unsafe_allow_html=True)
