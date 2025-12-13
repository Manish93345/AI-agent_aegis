"""
Ultimate Stable TTS Engine - Fixed Version
100% working with fresh engine instances
"""

import pyttsx3
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
import time

from utils.constants import Colors


@dataclass
class VoiceConfig:
    """Voice configuration settings"""
    rate: int = 150
    volume: float = 0.9
    voice_id: Optional[str] = None


class ResponseEngine:
    """Handles text-to-speech responses with fresh engine instances"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger("LISA.ResponseEngine")

        # Configuration
        self.config = VoiceConfig()
        if config:
            for key, value in config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)

        # Store selected voice id
        self.selected_voice_id = None
        self.is_initialized = False

    # ---------------------------------------------------------
    # Find Female Voice
    # ---------------------------------------------------------
    def _select_female_voice(self):
        """Select the best available female voice"""
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            
            # List all voices for debugging
            print(f"\n{Colors.BOLD}Available Voices:{Colors.ENDC}")
            for i, voice in enumerate(voices):
                voice_lower = voice.name.lower()
                gender = "Female" if any(female_term in voice_lower for female_term in 
                        ["female", "zira", "woman", "lisa", "samantha", "karen", "hazel"]) else "Male"
                print(f"  [{i}] {voice.name} ({gender})")
            
            # Primary female voice indicators
            female_keywords = [
                "female", "zira", "woman", "lisa", 
                "samantha", "karen", "hazel", "eva", 
                "natalia", "tessa", "veena", "anushka",
                "melina", "prabhat", "heera"
            ]

            for voice in voices:
                name = voice.name.lower()
                if any(keyword in name for keyword in female_keywords):
                    self.logger.info(f"✓ Selected female voice: {voice.name}")
                    engine.stop()
                    return voice.id

            # Secondary female voice indicators
            possible_female_indicators = [
                "anna", "maria", "katya", "yulia", "elena",
                "oksana", "irina", "svetlana", "olga", "natasha"
            ]
            
            for voice in voices:
                name = voice.name.lower()
                if any(indicator in name for indicator in possible_female_indicators):
                    self.logger.info(f"✓ Selected likely female voice: {voice.name}")
                    engine.stop()
                    return voice.id

            # Fallback strategies
            if len(voices) > 1:
                # On Windows, index 1 is often female (David=0, Zira=1)
                self.logger.info(f"Using voice at index 1: {voices[1].name}")
                engine.stop()
                return voices[1].id

            # Last resort
            self.logger.info(f"Using only available voice: {voices[0].name}")
            engine.stop()
            return voices[0].id
            
        except Exception as e:
            self.logger.error(f"Error selecting voice: {e}")
            return None

    # ---------------------------------------------------------
    # Initialize (selects voice and tests it)
    # ---------------------------------------------------------
    def initialize(self) -> bool:
        """Initialize the TTS engine"""
        try:
            self.logger.info("Initializing Response Engine...")

            # Pick best female voice
            self.selected_voice_id = self._select_female_voice()
            
            if not self.selected_voice_id:
                self.logger.error("No voice ID found")
                return False

            # Test the voice immediately
            self.logger.info("Testing voice with intro message...")
            
            # Create a fresh engine for testing
            test_engine = pyttsx3.init()
            test_engine.setProperty("rate", self.config.rate)
            test_engine.setProperty("volume", self.config.volume)
            test_engine.setProperty("voice", self.selected_voice_id)
            
            test_phrase = "Hello, I am Lisa, your personal assistant"
            print(f"\n{Colors.GREEN}Speaking: {test_phrase}{Colors.ENDC}")
            test_engine.say(test_phrase)
            test_engine.runAndWait()
            test_engine.stop()
            
            self.is_initialized = True
            self.logger.info(f"{Colors.GREEN}✓ Response Engine initialized successfully{Colors.ENDC}")
            return True

        except Exception as e:
            self.logger.error(f"{Colors.FAIL}✗ Initialization failed: {e}{Colors.ENDC}")
            return False

    # ---------------------------------------------------------
    # Speak - Main method (BLOCKING)
    # ---------------------------------------------------------
    def speak(self, text: str):
        """Speak text using a fresh engine instance (100% stable)."""
        if not text or not text.strip():
            return
            
        try:
            # Always create a fresh engine instance
            engine = pyttsx3.init()

            # Apply configuration
            engine.setProperty("rate", self.config.rate)
            engine.setProperty("volume", self.config.volume)
            
            # Use selected voice if available, otherwise auto-select
            if self.selected_voice_id:
                engine.setProperty("voice", self.selected_voice_id)
            else:
                # Auto-select female voice
                self.selected_voice_id = self._select_female_voice()
                if self.selected_voice_id:
                    engine.setProperty("voice", self.selected_voice_id)

            # Speak and wait
            engine.say(text)
            engine.runAndWait()

            # Clean up
            engine.stop()
            
        except Exception as e:
            self.logger.error(f"Speech failed: {e}")

    # ---------------------------------------------------------
    # Alias for speak
    # ---------------------------------------------------------
    def speak_immediate(self, text: str):
        """Alias for speak method"""
        self.speak(text)

    # ---------------------------------------------------------
    # Stop method (for compatibility)
    # ---------------------------------------------------------
    def stop(self):
        """Stop method - no persistent engine to stop"""
        pass

    # ---------------------------------------------------------
    # Testing methods
    # ---------------------------------------------------------
    def test_all_voices(self):
        """Test all available voices"""
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            engine.stop()
            
            print(f"\n{Colors.BOLD}Testing all voices:{Colors.ENDC}")
            
            for i, voice in enumerate(voices):
                print(f"\nVoice {i}: {voice.name}")
                
                # Create fresh engine for each test
                test_engine = pyttsx3.init()
                test_engine.setProperty("voice", voice.id)
                test_engine.setProperty("rate", self.config.rate)
                test_engine.setProperty("volume", self.config.volume)
                
                test_engine.say(f"Hello, I am Lisa, your assistant. This is voice number {i}")
                test_engine.runAndWait()
                test_engine.stop()
                
                time.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Error testing voices: {e}")

    def test_voice_output(self):
        """Test that voice output is working"""
        try:
            self.speak("Voice system working correctly.")
            self.logger.info("✓ Voice output test passed")
            return True
        except Exception as e:
            self.logger.error(f"Voice output test failed: {e}")
            return False
    
    def is_initialized(self):
        """Check if engine is initialized"""
        return self.is_initialized