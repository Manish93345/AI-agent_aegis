"""
Text-to-Speech Response Engine
Handles speaking responses back to the user
"""

import pyttsx3
import threading
import queue
import time
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

from utils.constants import Colors

@dataclass
class VoiceConfig:
    """Voice configuration settings"""
    rate: int = 150           # Words per minute
    volume: float = 0.9       # 0.0 to 1.0
    voice_id: Optional[int] = None  # Specific voice ID
    
class ResponseEngine:
    """Handles text-to-speech responses"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger("LISA.ResponseEngine")
        self.engine = None
        
        # Configuration
        self.config = VoiceConfig()
        if config:
            for key, value in config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
        
        # Response queue for async speaking
        self.response_queue = queue.Queue()
        self.is_speaking = False
        self.speech_thread = None
        
        # Available voices cache
        self.voices = []
    
    def initialize(self) -> bool:
        """Initialize the TTS engine"""
        self.logger.info("Initializing Response Engine...")
        
        try:
            self.engine = pyttsx3.init()
            
            # Configure engine
            self.engine.setProperty('rate', self.config.rate)
            self.engine.setProperty('volume', self.config.volume)
            
            # Get available voices
            self.voices = self.engine.getProperty('voices')
            self.logger.info(f"Found {len(self.voices)} voice(s)")
            
            # FORCE FEMALE VOICE - IMPROVED LOGIC
            female_voice_found = False
            
            # List all voices for debugging
            print(f"\n{Colors.BOLD}Available Voices:{Colors.ENDC}")
            for i, voice in enumerate(self.voices):
                # Check voice gender more comprehensively
                voice_lower = voice.name.lower()
                gender = "Female" if any(female_term in voice_lower for female_term in 
                        ["female", "zira", "woman", "lisa", "samantha", "karen", "hazel"]) else "Male"
                print(f"  [{i}] {voice.name} ({gender})")
                
                # Try to find a female voice - EXPANDED SEARCH
                if not female_voice_found:
                    female_indicators = [
                        "female", "zira", "woman", "lisa", 
                        "samantha", "karen", "hazel", "eva", 
                        "natalia", "tessa", "veena", "anushka",
                        "melina", "prabhat", "heera"
                    ]
                    
                    if any(indicator in voice_lower for indicator in female_indicators):
                        self.engine.setProperty('voice', voice.id)
                        female_voice_found = True
                        self.logger.info(f"✓ Selected female voice: {voice.name}")
                        break  # Stop searching once found
            
            # If no female voice found, try alternative selection
            if not female_voice_found:
                # Try voices that are typically female on different systems
                for i, voice in enumerate(self.voices):
                    voice_lower = voice.name.lower()
                    
                    # Check for voices that might be female but not explicitly labeled
                    possible_female_indicators = [
                        "anna", "maria", "katya", "yulia", "elena",
                        "oksana", "irina", "svetlana", "olga", "natasha"
                    ]
                    
                    if any(indicator in voice_lower for indicator in possible_female_indicators):
                        self.engine.setProperty('voice', voice.id)
                        female_voice_found = True
                        self.logger.info(f"✓ Selected likely female voice: {voice.name}")
                        break
            
            # Last resort: try voice indices that are often female
            if not female_voice_found:
                if len(self.voices) > 1:
                    # On Windows, index 1 is often female (David=0, Zira=1)
                    self.engine.setProperty('voice', self.voices[1].id)
                    self.logger.info(f"Using voice at index 1 (often female): {self.voices[1].name}")
                    female_voice_found = True
                elif len(self.voices) > 0:
                    # If only one voice, use it
                    self.engine.setProperty('voice', self.voices[0].id)
                    self.logger.info(f"Using only available voice: {self.voices[0].name}")
            
            # Start speech processing thread
            self.speech_thread = threading.Thread(
                target=self._speech_processing_loop,
                daemon=True,
                name="SpeechThread"
            )
            self.speech_thread.start()
            
            # Test with female voice - USE THE SELECTED VOICE
            test_phrase = "Hello, I am Lisa, your personal assistant"
            self.engine.say(test_phrase)
            self.engine.runAndWait()
            
            # Verify voice was actually set
            current_voice = self.engine.getProperty('voice')
            self.logger.info(f"Current voice ID: {current_voice}")
            
            self.logger.info(f"{Colors.GREEN}✓ Response Engine initialized with female voice{Colors.ENDC}")
            return True
            
        except Exception as e:
            self.logger.error(f"{Colors.FAIL}✗ Failed to initialize Response Engine: {e}{Colors.ENDC}")
            return False
    

    def speak(self, text: str, priority: int = 0):
        """Add text to speech queue"""
        if self.engine:
            self.response_queue.put({
                "text": text,
                "priority": priority,
                "timestamp": time.time()
            })
        else:
            self.logger.warning("TTS engine not initialized")
    
    def speak_immediate(self, text: str):
        """Speak immediately (blocks until done)"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Error speaking: {e}")
    
    def _speech_processing_loop(self):
        """Process speech queue in background thread"""
        self.logger.debug("Speech processing loop started")
        
        while True:
            try:
                # Get next response from queue
                response = self.response_queue.get(timeout=1.0)
                
                if response:
                    self.is_speaking = True
                    
                    # Speak the text
                    self.logger.debug(f"Speaking: '{response['text']}'")
                    self.engine.say(response['text'])
                    self.engine.runAndWait()
                    
                    self.is_speaking = False
                    self.response_queue.task_done()
                    
            except queue.Empty:
                # No speech pending, continue
                continue
            except Exception as e:
                self.logger.error(f"Error in speech loop: {e}")
                self.is_speaking = False
                time.sleep(1)
    
    def stop(self):
        """Stop the response engine"""
        if self.engine:
            self.engine.stop()


    def test_all_voices(self):
        """Test all available voices"""
        if not self.engine:
            self.initialize()
        
        print(f"\n{Colors.BOLD}Testing all voices:{Colors.ENDC}")
        
        for i, voice in enumerate(self.voices):
            self.engine.setProperty('voice', voice.id)
            gender = "👩 Female" if any(g in voice.name.lower() for g in ["female", "zira", "woman"]) else "👨 Male"
            
            print(f"\nVoice {i}: {voice.name} {gender}")
            self.engine.say(f"Hello, I am Lisa, your assistant. This is voice number {i}")
            self.engine.runAndWait()
            time.sleep(1)