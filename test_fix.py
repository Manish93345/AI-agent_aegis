#!/usr/bin/env python3
"""
Test if Lisa captures commands after wake word
"""

import speech_recognition as sr
import pyttsx3
import time
import sys
import io
import os

# Fix Windows console
if sys.platform == "win32":
    if sys.stdout and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    os.system('chcp 65001 > nul')

print("="*60)
print("TEST: Can Lisa capture commands after 'Hey Lisa'?")
print("="*60)

# Initialize
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if "zira" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

recognizer = sr.Recognizer()

print("\nStep 1: Testing wake word detection...")
print("Say 'Hey Lisa'")

with sr.Microphone() as source:
    recognizer.adjust_for_ambient_noise(source, duration=1)
    
    try:
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
        text = recognizer.recognize_google(audio)
        print(f"Heard: '{text}'")
        
        if "lisa" in text.lower():
            print("✅ Wake word detected!")
            engine.say("Yes, I'm listening. Now say a command.")
            engine.runAndWait()
            
            print("\nStep 2: Testing command capture...")
            print("Say a command like 'What time is it?'")
            
            audio2 = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            text2 = recognizer.recognize_google(audio2)
            print(f"Heard: '{text2}'")
            
            print(f"\n✅ SUCCESS! Command captured: '{text2}'")
            
            if "time" in text2.lower():
                from datetime import datetime
                current_time = datetime.now().strftime("%I:%M %p")
                response = f"The time is {current_time}"
                print(f"LISA would say: {response}")
                engine.say(response)
                engine.runAndWait()
            
        else:
            print("❌ No wake word detected")
            
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
    except sr.RequestError as e:
        print(f"❌ API error: {e}")
    except sr.WaitTimeoutError:
        print("❌ No speech detected (timeout)")