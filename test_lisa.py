#!/usr/bin/env python3
"""
Test Lisa voice assistant
"""

import speech_recognition as sr
import pyttsx3
import sys
import io
import os

# Fix Windows console
if sys.platform == "win32":
    if sys.stdout and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    os.system('chcp 65001 > nul')

def test_lisa():
    """Test Lisa voice recognition"""
    print("="*60)
    print("LISA VOICE ASSISTANT - TEST")
    print("="*60)
    
    # Initialize TTS with female voice
    print("\nInitializing female voice...")
    engine = pyttsx3.init()
    
    # List voices
    voices = engine.getProperty('voices')
    print(f"\nFound {len(voices)} voices:")
    
    female_voice = None
    for i, voice in enumerate(voices):
        if "female" in voice.name.lower() or "zira" in voice.name.lower():
            female_voice = voice.id
            print(f"  [{i}] ✅ {voice.name} (Female)")
        else:
            print(f"  [{i}] {voice.name}")
    
    # Set to female voice if found
    if female_voice:
        engine.setProperty('voice', female_voice)
        print("\n✓ Female voice selected")
    else:
        print("\n⚠️ No specific female voice found, using default")
    
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    
    # Initialize speech recognition
    print("\nInitializing speech recognition...")
    recognizer = sr.Recognizer()
    
    # List microphones
    print("\nAvailable microphones:")
    mics = sr.Microphone.list_microphone_names()
    for i, mic in enumerate(mics[:3]):  # Show first 3
        print(f"  [{i}] {mic}")
    
    print("\n" + "="*60)
    print("TESTING 'HEY LISA' RECOGNITION")
    print("="*60)
    print("\nSpeak 'Hey Lisa' clearly")
    print("Press Ctrl+C to stop\n")
    
    try:
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Lisa introduces herself
            engine.say("Hello, I am Lisa, your personal assistant. Say Hey Lisa to wake me up.")
            engine.runAndWait()
            
            while True:
                try:
                    print("\n[Listening for 'Hey Lisa'...]", end="", flush=True)
                    audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                    
                    try:
                        text = recognizer.recognize_google(audio)
                        text_lower = text.lower()
                        print(f"\rHeard: '{text}'")
                        
                        # Check for "Hey Lisa" or variations
                        if any(wake in text_lower for wake in ["hey lisa", "hello lisa", "lisa", "hey leesa"]):
                            print(f"\n✅ SUCCESS! 'Hey Lisa' detected!")
                            print(f"   Full text: '{text}'")
                            
                            # Lisa responds
                            response = "Yes, I'm listening. How can I help you?"
                            print(f"\nLISA: {response}")
                            engine.say(response)
                            engine.runAndWait()
                            
                            # Listen for command
                            print("\n[Listening for command...]", end="", flush=True)
                            audio2 = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                            
                            try:
                                command = recognizer.recognize_google(audio2)
                                print(f"\rCommand: '{command}'")
                                
                                response = f"I heard you say: {command}"
                                print(f"\nLISA: {response}")
                                engine.say(response)
                                engine.runAndWait()
                                
                            except sr.UnknownValueError:
                                print("\rNo command understood")
                                engine.say("I didn't catch that")
                                engine.runAndWait()
                                
                        else:
                            print(f"\nℹ️ Heard '{text}' but no wake word")
                            
                    except sr.UnknownValueError:
                        print("\rNo speech detected", end="", flush=True)
                    except sr.RequestError as e:
                        print(f"\rAPI error: {e}")
                        
                except sr.WaitTimeoutError:
                    print("\rNo audio...", end="", flush=True)
                    
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        engine.say("Goodbye")
        engine.runAndWait()
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    test_lisa()