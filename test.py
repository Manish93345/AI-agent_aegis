# test_voice.py
import speech_recognition as sr
import pyttsx3

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

r = sr.Recognizer()
speak("Hello, I am Aegis. Say something.")

with sr.Microphone() as source:
    print("Listening...")
    audio = r.listen(source)
    
    try:
        text = r.recognize_google(audio)
        print(f"You said: {text}")
        speak(f"I heard you say: {text}")
    except sr.UnknownValueError:
        print("Could not understand audio")
        speak("I didn't catch that")
    except sr.RequestError:
        print("API error")
        speak("There was an error")