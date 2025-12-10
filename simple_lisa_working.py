#!/usr/bin/env python3
"""
Simple Lisa that definitely works
"""

import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
import sys
import io
import os

# Fix Windows console
if sys.platform == "win32":
    if sys.stdout and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    os.system('chcp 65001 > nul')

class SimpleLisa:
    def __init__(self):
        self.is_running = True
        self.command_queue = queue.Queue()
        self.engine = None
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_waiting_for_command = False
        
    def init_speech(self):
        """Initialize speech engine with female voice"""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)
            
            # Set to female voice
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if "zira" in voice.name.lower():  # Windows female voice
                    self.engine.setProperty('voice', voice.id)
                    print(f"✓ Using female voice: {voice.name}")
                    break
            
            print("✓ Speech engine ready")
            return True
        except Exception as e:
            print(f"✗ Speech engine error: {e}")
            return False
    
    def speak(self, text):
        """Speak text"""
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
    
    def listen_loop(self):
        """Main listening loop in separate thread"""
        print("Starting listening thread...")
        
        try:
            self.microphone = sr.Microphone()
            
            with self.microphone as source:
                print("Adjusting for noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("✓ Ready! Say 'Hey Lisa'\n")
                
                while self.is_running:
                    try:
                        if not self.is_waiting_for_command:
                            print("[Sleeping - waiting for 'Hey Lisa']", end="\r", flush=True)
                        else:
                            print("[Awake - waiting for command]    ", end="\r", flush=True)
                        
                        # Listen with short timeout
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                        
                        try:
                            text = self.recognizer.recognize_google(audio)
                            text_lower = text.lower()
                            print(f"\nHeard: '{text}'")
                            
                            # Check for wake word
                            if not self.is_waiting_for_command and any(wake in text_lower for wake in ["hey lisa", "hello lisa", "lisa"]):
                                print(f"\n🎯 WAKE WORD DETECTED!")
                                self.is_waiting_for_command = True
                                self.command_queue.put({
                                    "type": "wake",
                                    "text": text,
                                    "time": time.time()
                                })
                                
                            # If waiting for command, process it
                            elif self.is_waiting_for_command:
                                print(f"\n🎯 COMMAND DETECTED!")
                                self.is_waiting_for_command = False  # Reset after command
                                self.command_queue.put({
                                    "type": "command",
                                    "text": text,
                                    "time": time.time()
                                })
                                
                        except sr.UnknownValueError:
                            if self.is_waiting_for_command:
                                # If waiting for command and nothing heard for 3 seconds, reset
                                print("\rNo command heard, going back to sleep", end="", flush=True)
                                self.is_waiting_for_command = False
                        except sr.RequestError as e:
                            print(f"\nAPI error: {e}")
                            
                    except sr.WaitTimeoutError:
                        # No audio, check if we should reset command waiting
                        if self.is_waiting_for_command:
                            # If waiting too long for command, reset
                            pass
                        continue
                        
        except Exception as e:
            print(f"\nListening error: {e}")
    
    def process_command(self, command_text):
        """Process a command"""
        command_text = command_text.lower()
        
        if any(word in command_text for word in ["hello", "hi"]):
            return "Hello! How can I help you?"
        
        elif any(word in command_text for word in ["time", "what time"]):
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}"
        
        elif any(word in command_text for word in ["your name", "who are you"]):
            return "My name is Lisa, your personal assistant!"
        
        elif any(word in command_text for word in ["thank", "thanks"]):
            return "You're welcome!"
        
        elif any(word in command_text for word in ["exit", "quit", "goodbye", "stop"]):
            self.is_running = False
            return "Goodbye! Shutting down."
        
        else:
            return f"I heard: {command_text}. How can I help with that?"
    
    def run(self):
        """Main loop"""
        print("="*60)
        print("LISA - Learning Intelligent System Assistant")
        print("="*60)
        
        if not self.init_speech():
            print("Failed to initialize speech")
            return
        
        # Start listening thread
        listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
        listen_thread.start()
        
        # Say hello
        self.speak("Hello! I am Lisa. Say Hey Lisa to begin.")
        
        try:
            while self.is_running:
                # Process commands from queue
                try:
                    item = self.command_queue.get(timeout=0.1)
                    
                    if item["type"] == "wake":
                        print(f"\n" + "="*40)
                        print(f"✓ Wake: '{item['text']}'")
                        response = "Yes, I'm listening. What would you like?"
                        print(f"LISA: {response}")
                        self.speak(response)
                        print("="*40 + "\n")
                        
                    elif item["type"] == "command":
                        print(f"\n" + "="*40)
                        print(f"✓ Command: '{item['text']}'")
                        response = self.process_command(item['text'])
                        print(f"LISA: {response}")
                        self.speak(response)
                        print("="*40 + "\n")
                        
                except queue.Empty:
                    pass
                    
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.is_running = False
            self.speak("Goodbye")

def main():
    lisa = SimpleLisa()
    lisa.run()

if __name__ == "__main__":
    main()