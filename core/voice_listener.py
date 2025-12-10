"""
Voice Listener Module
Handles microphone input, wake word detection, and speech recognition
"""

import speech_recognition as sr
import queue
import threading
import time
import logging
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum

from utils.constants import Colors

class ListeningState(Enum):
    """Current state of the voice listener"""
    SLEEPING = "sleeping"      # Waiting for wake word
    LISTENING = "listening"    # Listening for command
    PROCESSING = "processing"  # Processing command
    ERROR = "error"            # Error state

@dataclass
class AudioConfig:
    """Audio configuration settings"""
    sample_rate: int = 16000
    chunk_size: int = 1024
    pause_threshold: float = 0.8
    energy_threshold: int = 300
    dynamic_energy_threshold: bool = True
    phrase_time_limit: float = 10.0  # Max seconds to listen

class VoiceListener:
    """Main voice listening and recognition class"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger("AEGIS.VoiceListener")
        self.state = ListeningState.SLEEPING
        
        # Audio configuration
        self.config = AudioConfig()
        if config:
            for key, value in config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
        
        # Speech recognition components
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        
        # Command queue for async processing
        self.command_queue = queue.Queue()
        
        # Callbacks
        self.on_wake_word_detected = None
        self.on_command_received = None
        self.on_error = None
        
        # Statistics
        self.stats = {
            "wake_word_detections": 0,
            "commands_processed": 0,
            "errors": 0,
            "listening_time": 0.0
        }
    
    def initialize(self) -> bool:
        """Initialize the voice listener"""
        self.logger.info("Initializing Voice Listener...")
        
        try:
            # Get microphone
            self.microphone = sr.Microphone()
            
            # Configure recognizer
            self.recognizer.pause_threshold = self.config.pause_threshold
            self.recognizer.energy_threshold = self.config.energy_threshold
            self.recognizer.dynamic_energy_threshold = self.config.dynamic_energy_threshold
            
            # Adjust for ambient noise
            self.logger.info("Adjusting for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.logger.info(f"{Colors.GREEN}✓ Voice Listener initialized{Colors.ENDC}")
            return True
            
        except Exception as e:
            self.logger.error(f"{Colors.FAIL}✗ Failed to initialize Voice Listener: {e}{Colors.ENDC}")
            self.state = ListeningState.ERROR
            return False
    
    def start_listening(self) -> bool:
        """Start the continuous listening loop"""
        if self.microphone is None:
            self.logger.error("Microphone not initialized")
            return False
        
        self.is_listening = True
        self.state = ListeningState.SLEEPING
        
        # Start listening thread
        listen_thread = threading.Thread(
            target=self._listening_loop,
            daemon=True,
            name="VoiceListener-Thread"
        )
        listen_thread.start()
        
        self.logger.info("Voice Listener started (waiting for wake word)")
        return True
    
    def stop_listening(self):
        """Stop the listening loop"""
        self.is_listening = False
        self.state = ListeningState.SLEEPING
        self.logger.info("Voice Listener stopped")
    
    def _listening_loop(self):
        """Main listening loop - runs in separate thread"""
        self.logger.debug("Listening loop started")
        
        while self.is_listening:
            try:
                # Listen for audio
                with self.microphone as source:
                    if self.state == ListeningState.SLEEPING:
                        self.logger.debug("Sleeping - listening for wake word...")
                    else:
                        self.logger.debug("Awake - listening for command...")
                    
                    audio = self.recognizer.listen(
                        source,
                        timeout=1,  # Shorter timeout to be more responsive
                        phrase_time_limit=5  # Limit phrase length
                    )
                
                # Convert speech to text
                self.state = ListeningState.PROCESSING
                text = self._recognize_speech(audio)
                
                if text:
                    text = text.lower().strip()
                    self.logger.debug(f"Heard: '{text}'")
                    
                    # Check for wake word (anytime)
                    if self._is_wake_word(text):
                        self._handle_wake_word(text)
                    # If we're in LISTENING state, treat everything as command
                    elif self.state == ListeningState.LISTENING:
                        self._handle_command(text)
                        
            except sr.WaitTimeoutError:
                # No speech detected
                if self.state == ListeningState.LISTENING:
                    # If we're waiting for a command and nothing comes, go back to sleep
                    time.sleep(0.5)  # Wait a bit more for command
                    if self.state == ListeningState.LISTENING:  # Still no command
                        self.state = ListeningState.SLEEPING
                        self.logger.debug("No command received, going back to sleep")
                continue
            except Exception as e:
                self.stats["errors"] += 1
                self.logger.error(f"Error in listening loop: {e}")
                if self.on_error:
                    self.on_error(e)
                
                # Wait before retrying
                time.sleep(1)
        
    def _recognize_speech(self, audio) -> Optional[str]:
        """Convert audio to text using multiple engines"""
        text = None
        
        # Try Google Speech Recognition (online, more accurate)
        try:
            text = self.recognizer.recognize_google(audio)
            self.logger.debug("Used Google Speech Recognition")
            return text
        except sr.UnknownValueError:
            self.logger.debug("Google could not understand audio")
        except sr.RequestError as e:
            self.logger.warning(f"Google API error: {e}")
        
        # Fallback: Try offline recognition (Sphinx)
        try:
            text = self.recognizer.recognize_sphinx(audio)
            self.logger.debug("Used Sphinx (offline)")
            return text
        except sr.UnknownValueError:
            self.logger.debug("Sphinx could not understand audio")
        except Exception as e:
            self.logger.debug(f"Sphinx error: {e}")
        
        return text
    
    def _is_wake_word(self, text: str) -> bool:
        """Check if text contains wake word"""
        text = text.lower().strip()
        
        # Wake words for "Lisa" - much easier to recognize!
        wake_words = [
            "hey lisa", "hello lisa", "wake up lisa", 
            "lisa", "hey leesa", "hey lease", "hey lis",
            "listen", "hey listen", "hey lee"
        ]
        
        # Check for exact or partial matches
        for wake_word in wake_words:
            if wake_word in text:
                self.logger.debug(f"Wake word matched: '{wake_word}' in '{text}'")
                return True
        
        # Also check for "hey" followed by something similar to "lisa"
        if "hey" in text:
            words = text.split()
            for i, word in enumerate(words):
                if word == "hey" and i + 1 < len(words):
                    next_word = words[i + 1].lower()
                    # Check if next word sounds like "lisa"
                    if any(sound in next_word for sound in ["lisa", "leesa", "lease", "lees", "liza", "lis"]):
                        self.logger.debug(f"Similar wake word: 'hey {next_word}' in '{text}'")
                        return True
        
        return False
    
    def _handle_wake_word(self, text: str):
        """Handle wake word detection"""
        self.stats["wake_word_detections"] += 1
        self.state = ListeningState.LISTENING
        
        self.logger.info(f"{Colors.GREEN}✓ Wake word detected: '{text}'{Colors.ENDC}")
        
        # Female responses for Lisa
        responses = [
            "Yes, I'm listening",
            "How can I help you?",
            "I'm here, what do you need?",
            "Hello! What would you like me to do?",
            "Yes? I'm ready to help"
        ]
        
        import random
        response = random.choice(responses)
        
        # Add to command queue for processing
        self.command_queue.put({
            "type": "wake_word",
            "text": text,
            "response": response,
            "timestamp": time.time()
        })
        
        # Call callback if set
        if self.on_wake_word_detected:
            self.on_wake_word_detected(text, response)
        
        # Log that we're now listening for commands
        self.logger.debug("Now listening for commands...")

    def _handle_command(self, text: str):
        """Handle command after wake word"""
        self.stats["commands_processed"] += 1
        
        self.logger.info(f"{Colors.BLUE}→ Command: '{text}'{Colors.ENDC}")
        
        # Add to command queue
        self.command_queue.put({
            "type": "command",
            "text": text,
            "timestamp": time.time()
        })
        
        # Call callback if set
        if self.on_command_received:
            self.on_command_received(text)
        
        # Return to sleep state after command
        self.state = ListeningState.SLEEPING
    
    def get_next_command(self, timeout: float = 1.0) -> Optional[Dict]:
        """Get next command from queue (non-blocking)"""
        try:
            return self.command_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def clear_queue(self):
        """Clear all pending commands"""
        while not self.command_queue.empty():
            try:
                self.command_queue.get_nowait()
            except queue.Empty:
                break
    
    def get_stats(self) -> Dict:
        """Get listening statistics"""
        return self.stats.copy()
    
    def get_state(self) -> str:
        """Get current state as string"""
        return self.state.value