import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
import speech_recognition as sr
from gtts import gTTS
from tempfile import NamedTemporaryFile
import webbrowser

# load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# streamlit page setup
st.set_page_config(page_title="Beyond GPS Navigator!", page_icon=":brain:", layout="centered")
st.title(" Gemini - ChatBot")

# configure gemini Pro model api
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')

# translate roles for chat history display
def translate_role_for_streamlit(user_role):
    return "assistant" if user_role == "model" else user_role

# speech recognition
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info(" Listening...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        st.warning("Sorry, I could not understand your audio.")
        return ""
    except sr.RequestError as e:
        st.error(f"Google Speech Recognition error: {e}")
        return ""

# text-to-speech
def speak(text):
    tts = gTTS(text=text, lang='en')
    with NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.write_to_fp(f)
        filename = f.name
    st.audio(filename, format='audio/mp3')

# get location and destination
current_location = st.text_input("📍 Your current location:")
destination = st.text_input("🚩 Destination:")

# initialize chat session
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# display previous chat history
for message in st.session_state.chat_session.history:
    with st.chat_message(translate_role_for_streamlit(message.role)):
        st.markdown(message.parts[0].text)

# input handling
user_prompt = ""
if st.checkbox(" Voice Input"):
    if st.button(" Speak Now"):
        with st.spinner("Listening..."):
            user_prompt = recognize_speech()
            if user_prompt:
                st.success(f"You said: {user_prompt}")
else:
    user_prompt = st.text_input("Ask Gemini-Pro...")

# send to gemini and respond
if user_prompt:
    st.chat_message("user").markdown(user_prompt)
    gemini_response = st.session_state.chat_session.send_message(user_prompt)

    with st.chat_message("assistant"):
        st.markdown(gemini_response.text)
        speak(gemini_response.text)

    if "directions" in gemini_response.text and current_location and destination:
        maps_url = f"https://www.google.com/maps/dir/?api=1&origin={current_location}&destination={destination}"
        webbrowser.open(maps_url)

