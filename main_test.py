# core/voice_listener.py
import speech_recognition as sr
import threading
import queue
import time
from typing import Optional, Callable

class VoiceListener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self.listening_thread = None
        self.command_queue = queue.Queue()
        
        # Callbacks
        self.on_wake_word_detected: Optional[Callable] = None
        self.on_command_received: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        self.is_initialized = False
    
    def initialize(self):
        """Initialize the voice listener"""
        try:
            # Get microphone
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            print("Adjusting for ambient noise... Please wait.")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"Microphone initialization error: {e}")
            return False
    
    def start_listening(self):
        """Start listening for voice commands"""
        if not self.is_initialized:
            return False
        
        self.is_listening = True
        self.listening_thread = threading.Thread(target=self._listening_loop, daemon=True)
        self.listening_thread.start()
        return True
    
    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        if self.listening_thread:
            self.listening_thread.join(timeout=2)
    
    def _listening_loop(self):
        """Main listening loop"""
        wake_words = ["hey aegis", "hey aegus", "hey ages", "aegis"]
        
        while self.is_listening:
            try:
                # Listen for audio
                with self.microphone as source:
                    print("\n[Listening...]")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                # Recognize speech
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"Heard: {text}")
                    
                    # Check for wake word
                    for wake_word in wake_words:
                        if wake_word in text:
                            response = "Yes? I'm listening."
                            if self.on_wake_word_detected:
                                self.on_wake_word_detected(text, response)
                            
                            # Listen for command after wake word
                            with self.microphone as source:
                                print("[Listening for command...]")
                                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                                command_text = self.recognizer.recognize_google(audio).lower()
                                
                                if self.on_command_received:
                                    self.on_command_received(command_text)
                            
                            break
                    
                except sr.UnknownValueError:
                    # No speech detected
                    continue
                except sr.RequestError as e:
                    print(f"Speech recognition error: {e}")
                    continue
                    
            except Exception as e:
                if self.on_error:
                    self.on_error(e)
                time.sleep(1)
    
    def get_next_command(self, timeout=0.1):
        """Get next command from queue"""
        try:
            return self.command_queue.get(timeout=timeout)
        except queue.Empty:
            return None