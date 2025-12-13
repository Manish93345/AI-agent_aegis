"""
Voice Authentication Module for LISA
Secures the system so only you can control it
"""

import os
import pickle
import numpy as np
import soundfile as sf
import logging
import time
import hashlib
import json
from typing import List, Tuple, Optional, Dict
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

import speech_recognition as sr
from sklearn.mixture import GaussianMixture

from utils.constants import Colors

class AuthMethod(Enum):
    """Authentication methods"""
    VOICE = "voice"
    PIN = "pin"
    BOTH = "both"
    NONE = "none"

@dataclass
class VoiceSample:
    """Voice sample data"""
    audio_data: np.ndarray
    sample_rate: int
    text: str
    timestamp: float
    features: Optional[np.ndarray] = None

class VoiceAuthenticator:
    """Handles voice authentication for Lisa"""
    
    def __init__(self):
        self.logger = logging.getLogger("LISA.Auth")
        self.voice_samples: List[VoiceSample] = []
        self.gmm_model: Optional[GaussianMixture] = None
        self.is_trained = False
        self.auth_method = AuthMethod.VOICE
        
        # Configuration
        self.min_samples = 5
        self.auth_threshold = 0.6  # Lower threshold for better accuracy
        self.sample_duration = 3  # seconds
        self.max_auth_attempts = 3
        self.failed_attempts = 0
        self.locked_until = 0
        
        # PIN fallback (hashed)
        self.pin_hash = None
        
        # Secure commands that require auth
        self.secure_commands = [
            "shutdown", "restart", "lock", "sleep",
            "security level", "panic", "emergency",
            "format", "delete", "encrypt", "decrypt"
        ]
    
    def setup_authentication(self) -> bool:
        """Setup authentication - check if enrolled or need enrollment"""
        self.logger.info("Setting up authentication system...")
        
        # Check if model exists
        model_path = Path("data/models/voice_auth_model.pkl")
        pin_path = Path("data/auth/pin.hash")

        model_exists = model_path.exists() and model_path.stat().st_size > 0
        pin_exists = pin_path.exists() and pin_path.stat().st_size > 0
        
        if model_exists and pin_exists:
            print(f"{Colors.CYAN}Found existing voice model.{Colors.ENDC}")
            

            if self.load_model():
                # Show menu with options
                while True:
                    print(f"\n{Colors.BOLD}Authentication Options:{Colors.ENDC}")
                    print("1. Load existing voice model")
                    print("2. Re-enroll voice (requires PIN)")
                    print("3. Use PIN only")
                    print("4. Skip authentication (insecure)")
                    
                    choice = input(f"{Colors.YELLOW}Choose option (1-4): {Colors.ENDC}").strip()
                    
                    if choice == "1":
                        if self.load_model():
                            print(f"{Colors.GREEN}✓ Voice model loaded{Colors.ENDC}")
                            
                            # Quick test
                            print(f"\n{Colors.CYAN}Quick voice test...{Colors.ENDC}")
                            success, _ = self.verify_live(max_attempts=1)
                            
                            if success:
                                print(f"{Colors.GREEN}✓ Voice verification passed!{Colors.ENDC}")
                                return True
                            else:
                                print(f"{Colors.YELLOW}⚠ Voice test failed. Try re-enrollment or PIN.{Colors.ENDC}")
                                continue  # Go back to menu
                        else:
                            print(f"{Colors.FAIL}✗ Failed to load model{Colors.ENDC}")
                            continue
                    
                    elif choice == "2":
                        # PIN-protected re-enrollment
                        if self._verify_pin_for_re_enrollment():
                            print(f"{Colors.GREEN}✓ PIN verified. Starting re-enrollment...{Colors.ENDC}")
                            return self.enroll_user()
                        else:
                            print(f"{Colors.FAIL}✗ PIN verification failed{Colors.ENDC}")
                            continue
                    
                    elif choice == "3":
                        print(f"{Colors.CYAN}Setting up PIN-only authentication...{Colors.ENDC}")
                        return self._setup_pin_only()
                    
                    elif choice == "4":
                        print(f"{Colors.YELLOW}⚠ WARNING: Running without authentication{Colors.ENDC}")
                        confirm = input(f"{Colors.YELLOW}Are you sure? (y/n): {Colors.ENDC}")
                        if confirm.lower() == 'y':
                            self.auth_method = AuthMethod.NONE
                            return True
                        continue
                    
                    else:
                        print(f"{Colors.FAIL}✗ Invalid choice{Colors.ENDC}")


            else:
                # Model exists but couldn't load it (corrupted)
                print(f"{Colors.YELLOW}⚠ Model file is corrupted or empty.{Colors.ENDC}")
                print(f"{Colors.CYAN}Starting fresh enrollment...{Colors.ENDC}")
                return self.enroll_user()

        else:
            # No valid authentication found
            print(f"{Colors.YELLOW}No valid authentication found.{Colors.ENDC}")
            print(f"{Colors.CYAN}Starting fresh enrollment...{Colors.ENDC}")
            return self.enroll_user()

    def emergency_pin_reset(self):
        """Emergency PIN reset (requires security questions)"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}EMERGENCY PIN RESET{Colors.ENDC}")
        print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}")
        print("\n⚠  WARNING: This will delete ALL authentication data!")
        print("Only use if you've forgotten both voice and PIN.")
        
        # Security questions (you should customize these)
        security_questions = {
            "What is your birth city?": "aurangabad",  # Example - CHANGE THIS!
            "What was your first pet's name?": "browny",  # Example - CHANGE THIS!
            "What is your mother's name?": "gudiya"  # Example - CHANGE THIS!
        }
        
        correct_answers = 0
        total_questions = len(security_questions)
        
        print(f"\nAnswer {total_questions} security questions to reset:")
        
        for question, answer in security_questions.items():
            user_answer = input(f"\n{Colors.YELLOW}{question}: {Colors.ENDC}").strip().lower()
            
            if user_answer == answer.lower():
                correct_answers += 1
                print(f"{Colors.GREEN}✓ Correct{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}✗ Incorrect{Colors.ENDC}")
        
        if correct_answers >= total_questions - 1:  # Allow 1 wrong answer
            print(f"\n{Colors.GREEN}✓ Security questions passed ({correct_answers}/{total_questions}){Colors.ENDC}")
            
            # Delete all auth data
            auth_paths = [
                Path("data/models/voice_auth_model.pkl"),
                Path("data/auth/pin.hash"),
                Path("data/voice_samples")
            ]
            
            for path in auth_paths:
                if path.exists():
                    if path.is_file():
                        path.unlink()
                    else:
                        import shutil
                        shutil.rmtree(path)
            
            print(f"{Colors.GREEN}✓ All authentication data deleted{Colors.ENDC}")
            print(f"{Colors.CYAN}You can now set up fresh authentication.{Colors.ENDC}")
            return True
        else:
            print(f"\n{Colors.FAIL}✗ Security verification failed ({correct_answers}/{total_questions}){Colors.ENDC}")
            print(f"{Colors.FAIL}Emergency reset blocked.{Colors.ENDC}")
            return False
    
    def enroll_user(self, num_samples: int = 8) -> bool:
        """Enroll user by recording voice samples"""
        self.logger.info(f"Starting voice enrollment ({num_samples} samples)")
        
        print(f"\n{Colors.CYAN}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}VOICE ENROLLMENT FOR LISA{Colors.ENDC}")
        print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}")
        print(f"\nI need to record {num_samples} samples of your voice.")
        print("This will create your voice fingerprint for security.")
        print("Speak clearly in a quiet environment.\n")
        
        # Clear any existing samples
        self.voice_samples.clear()
        
        phrases = [
            "My voice is my password",
            "Hello Lisa, authenticate me",
            "Only I control this system",
            "Voice recognition security",
            "Personal assistant access",
            "Secure my computer with voice",
            "Biometric voice authentication",
            "Lisa, remember my voice"
        ]
        
        recognizer = sr.Recognizer()
        
        try:
            with sr.Microphone() as source:
                print(f"{Colors.YELLOW}Adjusting for ambient noise...{Colors.ENDC}")
                recognizer.adjust_for_ambient_noise(source, duration=2)
                print(f"{Colors.GREEN}✓ Ready to record{Colors.ENDC}\n")
                
                recorded_count = 0
                
                for i in range(min(num_samples, len(phrases))):
                    print(f"{Colors.BOLD}Sample {i+1}/{num_samples}:{Colors.ENDC}")
                    print(f"Say: '{phrases[i]}'")
                    print(f"{Colors.YELLOW}Speak now...{Colors.ENDC}")
                    
                    try:
                        # Record audio
                        audio = recognizer.listen(
                            source, 
                            timeout=5,
                            phrase_time_limit=self.sample_duration
                        )
                        
                        # Convert to numpy array
                        raw_data = audio.get_raw_data()
                        audio_array = np.frombuffer(raw_data, dtype=np.int16)
                        
                        # Skip if too short
                        if len(audio_array) < 8000:  # Less than 0.5 sec at 16kHz
                            print(f"{Colors.FAIL}✗ Too short, try again{Colors.ENDC}")
                            continue
                        
                        # Extract features
                        features = self._extract_features(audio_array, audio.sample_rate)
                        
                        # Create voice sample
                        sample = VoiceSample(
                            audio_data=audio_array,
                            sample_rate=audio.sample_rate,
                            text=phrases[i],
                            timestamp=time.time(),
                            features=features
                        )
                        
                        self.voice_samples.append(sample)
                        recorded_count += 1
                        
                        print(f"{Colors.GREEN}✓ Sample recorded{Colors.ENDC}")
                        
                        # Optional playback
                        if i < 2:  # Play first 2 samples for verification
                            response = input(f"{Colors.CYAN}Hear playback? (y/n): {Colors.ENDC}")
                            if response.lower() == 'y':
                                self._playback_info(sample)
                        
                        time.sleep(1)
                        
                    except sr.WaitTimeoutError:
                        print(f"{Colors.FAIL}✗ No speech detected{Colors.ENDC}")
                        continue
                    except Exception as e:
                        print(f"{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")
                        continue
                
                # Check if we have enough samples
                if recorded_count >= self.min_samples:
                    print(f"\n{Colors.GREEN}✓ Recorded {recorded_count} samples{Colors.ENDC}")
                    
                    # Train model
                    if self._train_model():
                        # Save model
                        if self.save_model():
                            print(f"{Colors.GREEN}✓ Voice model trained and saved{Colors.ENDC}")
                            
                            # Test immediately
                            print(f"\n{Colors.CYAN}Testing verification...{Colors.ENDC}")
                            success, confidence = self.verify_live()
                            
                            if success:
                                print(f"{Colors.GREEN}✓ Enrollment successful!{Colors.ENDC}")
                                
                                # Setup PIN as backup
                                self._setup_pin_backup()
                                return True
                            else:
                                print(f"{Colors.YELLOW}⚠ Verification test failed{Colors.ENDC}")
                                return False
                    
                    print(f"{Colors.FAIL}✗ Training failed{Colors.ENDC}")
                    return False
                else:
                    print(f"{Colors.FAIL}✗ Not enough samples ({recorded_count}/{self.min_samples}){Colors.ENDC}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Enrollment failed: {e}")
            print(f"{Colors.FAIL}✗ Enrollment error: {e}{Colors.ENDC}")
            return False
    

    def _verify_pin_for_re_enrollment(self) -> bool:
        """Verify PIN to allow re-enrollment"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}PIN VERIFICATION FOR RE-ENROLLMENT{Colors.ENDC}")
        print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}")
        print("\nRe-enrollment requires PIN verification for security.")
        print("This will delete your existing voice model.")
        
        # Check if PIN is set
        pin_path = Path("data/auth/pin.hash")
        if not pin_path.exists():
            print(f"{Colors.YELLOW}No PIN found. Please set a PIN first.{Colors.ENDC}")
            return self._setup_pin_backup()
        
        # Load PIN hash
        try:
            with open(pin_path, 'r') as f:
                pin_data = json.load(f)
                stored_hash = pin_data.get("pin_hash")
        except:
            print(f"{Colors.FAIL}✗ Error reading PIN file{Colors.ENDC}")
            return False
        
        # Verify PIN
        for attempt in range(3):
            pin = input(f"{Colors.YELLOW}Enter PIN (Attempt {attempt+1}/3): {Colors.ENDC}")
            
            # Hash entered PIN
            entered_hash = hashlib.sha256(pin.encode()).hexdigest()
            
            if entered_hash == stored_hash:
                print(f"{Colors.GREEN}✓ PIN verified{Colors.ENDC}")
                
                # Delete old voice model
                model_path = Path("data/models/voice_auth_model.pkl")
                if model_path.exists():
                    model_path.unlink()
                    print(f"{Colors.GREEN}✓ Old voice model deleted{Colors.ENDC}")
                
                # Delete old voice samples
                samples_dir = Path("data/voice_samples")
                if samples_dir.exists():
                    import shutil
                    shutil.rmtree(samples_dir)
                    print(f"{Colors.GREEN}✓ Old voice samples deleted{Colors.ENDC}")
                
                return True
            else:
                print(f"{Colors.FAIL}✗ Incorrect PIN{Colors.ENDC}")
        
        print(f"{Colors.FAIL}✗ Too many failed attempts. Re-enrollment blocked.{Colors.ENDC}")
        return False
    

    def _extract_features(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract features from audio for voice recognition"""
        audio = audio_data.astype(np.float32)
        
        # Normalize
        audio = audio / np.max(np.abs(audio))
        
        # Basic features (in real system, use MFCC)
        features = [
            np.mean(np.abs(audio)),  # Average amplitude
            np.std(audio),  # Standard deviation
            np.sqrt(np.mean(audio**2)),  # RMS energy
            np.max(np.abs(audio)),  # Peak amplitude
            len(audio) / sample_rate,  # Duration
            np.sum(audio**2) / len(audio),  # Energy
        ]
        
        # Add spectral features
        if len(audio) > 0:
            fft = np.fft.rfft(audio)
            magnitude = np.abs(fft)
            
            if len(magnitude) > 0:
                features.append(np.mean(magnitude[:100]))  # Low freq
                features.append(np.mean(magnitude[100:1000]))  # Mid freq
                features.append(np.mean(magnitude[1000:]))  # High freq
                features.append(np.argmax(magnitude) / len(magnitude))  # Dominant freq
        
        return np.array(features)
    
    def _train_model(self) -> bool:
        """Train GMM model on voice samples"""
        self.logger.info("Training voice authentication model...")
        
        try:
            # Extract features from all samples
            features_list = []
            for sample in self.voice_samples:
                if sample.features is not None:
                    features_list.append(sample.features)
                else:
                    # Extract if not already done
                    feats = self._extract_features(sample.audio_data, sample.sample_rate)
                    features_list.append(feats)
            
            if len(features_list) < self.min_samples:
                self.logger.error(f"Not enough samples with features: {len(features_list)}")
                return False
            
            features_array = np.array(features_list)
            
            # Train Gaussian Mixture Model
            n_components = min(3, len(features_list) // 2)
            self.gmm_model = GaussianMixture(
                n_components=n_components,
                random_state=42,
                covariance_type='diag'
            )
            self.gmm_model.fit(features_array)
            
            # Test on training data
            train_scores = self.gmm_model.score_samples(features_array)
            train_accuracy = np.mean(train_scores > -50)  # Threshold
            
            self.is_trained = True
            self.logger.info(f"Voice model trained: {len(features_list)} samples, accuracy: {train_accuracy:.2f}")
            
            return train_accuracy > 0.7
            
        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            return False
    
    def verify_live(self, max_attempts: int = 2) -> Tuple[bool, float]:
        """Verify user with live voice sample"""
        if self._is_locked():
            print(f"{Colors.FAIL}✗ Authentication locked. Try again later.{Colors.ENDC}")
            return False, 0.0
        
        self.logger.info("Live voice verification...")
        
        recognizer = sr.Recognizer()
        
        for attempt in range(max_attempts):
            print(f"\n{Colors.CYAN}Voice Verification (Attempt {attempt+1}/{max_attempts}){Colors.ENDC}")
            print("Say: 'My voice is my password'")
            print(f"{Colors.YELLOW}Listening...{Colors.ENDC}")
            
            try:
                with sr.Microphone() as source:
                    audio = recognizer.listen(
                        source,
                        timeout=5,
                        phrase_time_limit=self.sample_duration
                    )
                    
                    raw_data = audio.get_raw_data()
                    audio_array = np.frombuffer(raw_data, dtype=np.int16)
                    
                    # Extract features
                    features = self._extract_features(audio_array, audio.sample_rate)
                    
                    # Authenticate
                    authenticated, confidence = self.authenticate_with_features(features)
                    
                    if authenticated:
                        print(f"{Colors.GREEN}✓ Voice verified (confidence: {confidence:.2f}){Colors.ENDC}")
                        self.failed_attempts = 0  # Reset on success
                        return True, confidence
                    else:
                        print(f"{Colors.FAIL}✗ Voice not recognized (confidence: {confidence:.2f}){Colors.ENDC}")
                        self.failed_attempts += 1
                        
                        if self.failed_attempts >= self.max_auth_attempts:
                            self._lock_auth(300)  # Lock for 5 minutes
                            print(f"{Colors.FAIL}✗ Too many failed attempts. Locked for 5 minutes.{Colors.ENDC}")
                            return False, confidence
                        
                        if attempt < max_attempts - 1:
                            print(f"{Colors.YELLOW}Try again or use PIN...{Colors.ENDC}")
                            
            except sr.WaitTimeoutError:
                print(f"{Colors.FAIL}✗ No speech detected{Colors.ENDC}")
            except Exception as e:
                self.logger.error(f"Verification error: {e}")
                print(f"{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")
        
        # All attempts failed
        print(f"{Colors.YELLOW}Voice verification failed. Try PIN or re-enroll.{Colors.ENDC}")
        return False, 0.0
    
    def authenticate_with_features(self, features: np.ndarray) -> Tuple[bool, float]:
        """Authenticate using extracted features"""
        if not self.is_trained or self.gmm_model is None:
            self.logger.warning("Authentication model not trained")
            return False, 0.0
        
        try:
            # Reshape for single sample
            features_reshaped = features.reshape(1, -1)
            
            # Get log probability from GMM
            log_prob = self.gmm_model.score_samples(features_reshaped)[0]
            
            # Convert to confidence score (0-1)
            # GMM scores are log probabilities, usually negative
            # Higher (less negative) = more likely
            confidence = min(max((log_prob + 100) / 200, 0.0), 1.0)
            
            is_authenticated = confidence >= self.auth_threshold
            
            self.logger.debug(f"Auth log_prob: {log_prob:.2f}, Confidence: {confidence:.2f}")
            
            return is_authenticated, confidence
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False, 0.0
    
    def _setup_pin_backup(self):
        """Setup PIN as backup authentication"""
        print(f"\n{Colors.CYAN}Setup PIN Backup{Colors.ENDC}")
        print("Set a 4-6 digit PIN for backup authentication.")
        
        while True:
            pin1 = input(f"{Colors.YELLOW}Enter PIN: {Colors.ENDC}")
            pin2 = input(f"{Colors.YELLOW}Confirm PIN: {Colors.ENDC}")
            
            if pin1 == pin2 and pin1.isdigit() and 4 <= len(pin1) <= 6:
                # Hash the PIN
                self.pin_hash = hashlib.sha256(pin1.encode()).hexdigest()
                
                # Save PIN hash
                pin_path = Path("data/auth/pin.hash")
                pin_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(pin_path, 'w') as f:
                    json.dump({"pin_hash": self.pin_hash}, f)
                
                print(f"{Colors.GREEN}✓ PIN backup setup complete{Colors.ENDC}")
                self.auth_method = AuthMethod.BOTH
                break
            else:
                print(f"{Colors.FAIL}✗ PINs don't match or invalid. Must be 4-6 digits.{Colors.ENDC}")
    
    def authenticate_with_pin(self) -> bool:
        """Authenticate using PIN"""
        if self._is_locked():
            print(f"{Colors.FAIL}✗ Authentication locked{Colors.ENDC}")
            return False
        
        print(f"\n{Colors.CYAN}PIN Authentication{Colors.ENDC}")
        
        for attempt in range(self.max_auth_attempts):
            pin = input(f"{Colors.YELLOW}Enter PIN (Attempt {attempt+1}/{self.max_auth_attempts}): {Colors.ENDC}")
            
            # Hash entered PIN
            entered_hash = hashlib.sha256(pin.encode()).hexdigest()
            
            if entered_hash == self.pin_hash:
                print(f"{Colors.GREEN}✓ PIN correct{Colors.ENDC}")
                self.failed_attempts = 0
                return True
            else:
                print(f"{Colors.FAIL}✗ Incorrect PIN{Colors.ENDC}")
                self.failed_attempts += 1
        
        # Too many failed attempts
        self._lock_auth(600)  # Lock for 10 minutes
        print(f"{Colors.FAIL}✗ Too many failed attempts. Locked for 10 minutes.{Colors.ENDC}")
        return False
    
    def requires_authentication(self, command: str) -> bool:
        """Check if a command requires authentication"""
        command_lower = command.lower()
        
        for secure_cmd in self.secure_commands:
            if secure_cmd in command_lower:
                return True
        
        return False
    
    def authenticate_command(self, command: str) -> bool:
        """Authenticate a command based on security level"""
        if not self.requires_authentication(command):
            return True  # No auth needed for non-secure commands
        
        print(f"\n{Colors.YELLOW}⚠ Authentication required for: '{command}'{Colors.ENDC}")
        
        if self.auth_method == AuthMethod.VOICE:
            return self.verify_live()[0]
        elif self.auth_method == AuthMethod.PIN:
            return self.authenticate_with_pin()
        elif self.auth_method == AuthMethod.BOTH:
            print(f"{Colors.CYAN}Choose authentication method:{Colors.ENDC}")
            print("1. Voice")
            print("2. PIN")
            
            choice = input(f"{Colors.YELLOW}Choice (1/2): {Colors.ENDC}")
            
            if choice == "1":
                return self.verify_live()[0]
            elif choice == "2":
                return self.authenticate_with_pin()
            else:
                print(f"{Colors.FAIL}✗ Invalid choice{Colors.ENDC}")
                return False
        
        return False
    
    def _is_locked(self) -> bool:
        """Check if authentication is temporarily locked"""
        return time.time() < self.locked_until
    
    def _lock_auth(self, seconds: int):
        """Lock authentication for specified seconds"""
        self.locked_until = time.time() + seconds
    
    def save_model(self, filepath: Optional[Path] = None) -> bool:
        """Save trained model to file"""
        if filepath is None:
            filepath = Path("data/models/voice_auth_model.pkl")
        
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            save_data = {
                'gmm_model': self.gmm_model,
                'voice_samples': self.voice_samples,
                'is_trained': self.is_trained,
                'auth_method': self.auth_method.value,
                'pin_hash': self.pin_hash
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(save_data, f)
            
            self.logger.info(f"Model saved to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save model: {e}")
            return False
    
    def load_model(self, filepath: Optional[Path] = None) -> bool:
        """Load trained model from file"""
        if filepath is None:
            filepath = Path("data/models/voice_auth_model.pkl")
        
        if not filepath.exists():
            self.logger.warning(f"Model file not found: {filepath}")
            return False
        
        try:
            with open(filepath, 'rb') as f:
                save_data = pickle.load(f)
            
            self.gmm_model = save_data['gmm_model']
            self.voice_samples = save_data['voice_samples']
            self.is_trained = save_data['is_trained']
            self.auth_method = AuthMethod(save_data.get('auth_method', 'voice'))
            self.pin_hash = save_data.get('pin_hash')
            
            self.logger.info(f"Model loaded from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            return False
    
    def _playback_info(self, sample: VoiceSample):
        """Show info about recorded sample (audio playback would need pyaudio)"""
        print(f"{Colors.CYAN}Sample Info:{Colors.ENDC}")
        print(f"  Duration: {len(sample.audio_data)/sample.sample_rate:.2f}s")
        print(f"  Text: '{sample.text}'")
        print(f"  Sample rate: {sample.sample_rate}Hz")
        # Audio playback code would go here
    
    def _setup_pin_fallback(self) -> bool:
        """Setup PIN as fallback when voice fails"""
        print(f"\n{Colors.CYAN}Voice authentication failed. Setting up PIN fallback.{Colors.ENDC}")
        return self._setup_pin_only()
    
    def _setup_pin_only(self) -> bool:
        """Setup PIN-only authentication"""
        self.auth_method = AuthMethod.PIN
        return self._setup_pin_backup()

# Test function
def test_auth():
    """Test the authentication system"""
    import sys
    from pathlib import Path
    
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Authentication System...")
    print("="*60)
    
    auth = VoiceAuthenticator()
    
    # Setup authentication
    if auth.setup_authentication():
        print(f"\n{Colors.GREEN}✓ Authentication setup complete!{Colors.ENDC}")
        
        # Test secure command
        test_command = "shutdown laptop"
        print(f"\nTesting secure command: '{test_command}'")
        
        if auth.requires_authentication(test_command):
            print("This command requires authentication.")
            
            if auth.authenticate_command(test_command):
                print(f"{Colors.GREEN}✓ Command authenticated!{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}✗ Authentication failed{Colors.ENDC}")
        else:
            print("This command doesn't require authentication.")
    else:
        print(f"{Colors.FAIL}✗ Authentication setup failed{Colors.ENDC}")

    print(f"\n{Colors.BOLD}Additional Options:{Colors.ENDC}")
    print("1. Test secure command")
    print("2. Re-enroll voice")
    print("3. Emergency PIN reset")
    print("4. Exit")

    choice = input(f"{Colors.YELLOW}Choose option (1-4): {Colors.ENDC}").strip()

    if choice == "1":
        # Test secure command (existing code)
        pass
    elif choice == "2":
        if auth._verify_pin_for_re_enrollment():
            auth.enroll_user()
    elif choice == "3":
        auth.emergency_pin_reset()

if __name__ == "__main__":
    test_auth()