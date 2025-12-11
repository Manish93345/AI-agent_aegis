#!/usr/bin/env python3
"""
LISA - Main Entry Point
Learning Intelligent System Assistant
"""

# ============ WINDOWS CONSOLE ENCODING FIX ============
import sys
import io
import os
from core.command_parser import CommandParser

# Fix Windows console encoding for checkmarks/crosses
if sys.platform == "win32":
    # Enable UTF-8 encoding in Windows console
    if sys.stdout and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if sys.stderr and hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # Also try to set console code page
    os.system('chcp 65001 > nul')
# ======================================================

import time
import logging
from pathlib import Path
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from utils.constants import *
from utils.file_utils import FileUtils
from utils.os_utils import OSUtils


class LISA:
    """Main LISA system class"""
    
    def __init__(self):
        self.start_time = None
        self.system_info = {}
        self.configs = {}
        self.is_running = False
        self.voice_listener = None
        self.assistant_name = "Lisa"
        self.command_parser = CommandParser()
        
        # Setup logging
        self.setup_logging()
        
        # Create directories
        ensure_directories()
    
    def setup_logging(self):
        """Configure logging system"""
        log_file = LOGS_DIR / f"lisa_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("LISA")
        self.logger.info("=" * 60)
        self.logger.info("LISA System Initializing...")
        self.logger.info("=" * 60)
    
    def load_configurations(self):
        """Load all configuration files"""
        self.logger.info("Loading configurations...")
        
        config_files = {
            "commands": COMMANDS_CONFIG,
            "security": SECURITY_CONFIG,
            "user_prefs": USER_PREFS,
            "system_config": SYSTEM_CONFIG
        }
        
        for name, path in config_files.items():
            if path.exists():
                self.configs[name] = FileUtils.load_json(path)
                self.logger.info(f"✓ Loaded {name} configuration")
            else:
                self.logger.warning(f"✗ Config file not found: {path}")
                self.configs[name] = {}
        
        return len(self.configs) > 0
    
    def system_check(self):
        """Perform system compatibility check"""
        self.logger.info("Performing system check...")
        
        # Check Python version
        if sys.version_info < (3, 9):
            self.logger.error("Python 3.9+ required")
            return False
        
        # Get OS info
        self.system_info = OSUtils.get_os_info()
        self.logger.info(f"OS: {self.system_info['system']} {self.system_info['release']}")
        self.logger.info(f"Python: {self.system_info['python_version']}")
        
        # Check GPU
        gpu_available = OSUtils.check_gpu_available()
        if gpu_available:
            self.logger.info("✓ NVIDIA GPU detected (RTX 3050 compatible)")
        else:
            self.logger.warning("✗ No NVIDIA GPU detected")
        
        # Check dependencies
        try:
            import speech_recognition
            import pyttsx3
            import pyautogui
            import psutil
            import pyaudio
            self.logger.info("✓ Core dependencies available")
        except ImportError as e:
            self.logger.error(f"✗ Missing dependency: {e}")
            print(f"\n{Colors.FAIL}Missing dependency: {e}{Colors.ENDC}")
            print(f"{Colors.WARNING}Run: pip install speechrecognition pyttsx3 pyautogui psutil pyaudio{Colors.ENDC}")
            return False
        
        return True
    
    def display_banner(self):
        """Display startup banner"""
        banner = """
╔══════════════════════════════════════════════════════════╗
║                   L I S A   S Y S T E M                  ║
║          Learning Intelligent System Assistant           ║
║                                                          ║
║     Version: 0.1.0 Alpha          Status: INITIALIZING   ║
╚══════════════════════════════════════════════════════════╝
        """
        print(Colors.MAGENTA + banner + Colors.ENDC)
    
    def initialize(self):
        """Initialize the LISA system"""
        self.display_banner()
        
        # System check
        if not self.system_check():
            print(f"{Colors.FAIL}System check failed. Exiting...{Colors.ENDC}")
            return False
        
        # Load configurations
        if not self.load_configurations():
            print(f"{Colors.WARNING}Some configurations missing{Colors.ENDC}")
        
        # Initialize voice system
        if not self.initialize_voice_system():
            print(f"{Colors.WARNING}Voice system initialization failed{Colors.ENDC}")
            print(f"{Colors.WARNING}Continuing without voice control...{Colors.ENDC}")

        # Initialize automation system
        if not self.initialize_automation_system():
            print(f"{Colors.WARNING}Automation system initialization failed{Colors.ENDC}")
        
        # Display system info
        print(f"\n{Colors.MAGENTA}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}System Information:{Colors.ENDC}")
        print(f"  OS: {self.system_info['system']} {self.system_info['release']}")
        print(f"  Architecture: {self.system_info['machine']}")
        print(f"  Python: {self.system_info['python_version']}")
        print(f"{Colors.MAGENTA}{'='*60}{Colors.ENDC}")
        
        self.start_time = datetime.now()
        self.is_running = True
        
        self.logger.info("LISA initialization complete")
        print(f"\n{Colors.MAGENTA}✓ LISA System Ready!{Colors.ENDC}")
        print(f"{Colors.BOLD}Assistant: {self.assistant_name}{Colors.ENDC}")
        
        if self.voice_listener:
            print(f"{Colors.WARNING}Speak 'Hey Lisa' to activate{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}Voice system disabled - using text input{Colors.ENDC}")
            print(f"{Colors.WARNING}Type commands or 'exit' to quit{Colors.ENDC}")
        
        return True
    
    def initialize_voice_system(self):
        """Initialize the voice listening system"""
        self.logger.info("Initializing voice system...")
        
        try:
            # Import here to avoid circular imports
            from core.voice_listener import VoiceListener
            from core.response_engine import ResponseEngine
            
            # Create voice listener
            self.voice_listener = VoiceListener()
            
            # Create response engine
            self.response_engine = ResponseEngine()
            
            if self.voice_listener.initialize() and self.response_engine.initialize():
                # Set up callbacks
                self.voice_listener.on_wake_word_detected = self._on_wake_word
                self.voice_listener.on_command_received = self._on_command
                self.voice_listener.on_error = self._on_voice_error
                
                # Start listening
                if self.voice_listener.start_listening():
                    self.logger.info(f"{Colors.GREEN}✓ Voice system active{Colors.ENDC}")
                    return True
                else:
                    self.logger.error("Failed to start listening")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Voice system initialization failed: {e}")
            print(f"{Colors.FAIL}Voice error: {e}{Colors.ENDC}")
            # Don't crash if voice fails
            return False
    
    def _on_wake_word(self, wake_text: str, response: str):
        """Handle wake word detection"""
        self.logger.info(f"Wake word: {wake_text}")
        
        # Add to queue for processing in main loop
        # if self.voice_listener:
        #     self.voice_listener.command_queue.put({
        #         "type": "wake_word",
        #         "text": wake_text,
        #         "response": response,
        #         "timestamp": time.time()
        #     })
    
    def _on_command(self, command_text: str):
        """Handle command received"""
        self.logger.info(f"Command: {command_text}")
        
        # Add to queue for processing in main loop
        # if self.voice_listener:
        #     self.voice_listener.command_queue.put({
        #         "type": "command",
        #         "text": command_text,
        #         "timestamp": time.time()
        #     })
    
    def _on_voice_error(self, error: Exception):
        """Handle voice errors"""
        self.logger.error(f"Voice error: {error}")
        print(f"{Colors.FAIL}Voice error: {error}{Colors.ENDC}")
    
    def _process_basic_command(self, command_text: str):
        """Process basic voice commands using command parser"""
        # Parse the command
        parsed = self.command_parser.parse_command(command_text)
        
        # Get response
        response = self.command_parser.get_response(parsed)
        
        # Execute based on parsed action
        action = parsed.get("action")
        if action == "greeting":
            print(f"{Colors.MAGENTA}LISA: {response}{Colors.ENDC}")
            if hasattr(self, 'response_engine'):
                self.response_engine.speak(response)
        
        elif action == "farewell":
            print(f"{Colors.MAGENTA}LISA: {response}{Colors.ENDC}")
            if hasattr(self, 'response_engine'):
                self.response_engine.speak(response)
            self.is_running = False

        elif action in ["who_are_you", "your_name", "my_name"]:
            print(f"{Colors.MAGENTA}LISA: {response}{Colors.ENDC}")
            if hasattr(self, 'response_engine'):
                self.response_engine.speak(response)
        
        elif action == "time":
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            response = response.format(time=current_time)
            print(f"{Colors.MAGENTA}LISA: {response}{Colors.ENDC}")
            if hasattr(self, 'response_engine'):
                self.response_engine.speak(response)
        
        elif action == "date":
            from datetime import datetime
            current_date = datetime.now().strftime("%B %d, %Y")
            response = response.format(date=current_date)
            print(f"{Colors.MAGENTA}LISA: {response}{Colors.ENDC}")
            if hasattr(self, 'response_engine'):
                self.response_engine.speak(response)
        
        elif action == "study_cyber":
            print(f"{Colors.MAGENTA}LISA: {response}{Colors.ENDC}")
            if hasattr(self, 'response_engine'):
                self.response_engine.speak(response)
            
            # Execute study cyber routine
            if hasattr(self, 'automation_engine'):
                success = self.automation_engine.execute_study_cyber_routine()
                if success:
                    response = "Study cyber routine completed successfully!"
                else:
                    response = "Some parts of the study cyber routine failed."
                print(f"{Colors.MAGENTA}LISA: {response}{Colors.ENDC}")
                if hasattr(self, 'response_engine'):
                    self.response_engine.speak(response)
        
        elif action in ["open_word", "open_chrome", "open_notepad", "open_calculator", "open_vscode", "open_explorer", "open_cmd", "open_terminal", "open_powershell"]:
            app_map = {
                "open_word": "microsoft word",
                "open_chrome": "chrome",
                "open_notepad": "notepad",
                "open_calculator": "calculator",
                "open_vscode": "visual studio code",
                "open_explorer": "file explorer",
                "open_browser": "chrome",
                "open_cmd": "command prompt",
                "open_terminal": "terminal",
                "open_powershell": "powershell"
            }
            
            app_name = app_map.get(action, parsed.get("parameters", {}).get("app_name", ""))
            
            if app_name:
                print(f"{Colors.MAGENTA}LISA: {response}{Colors.ENDC}")
                if hasattr(self, 'response_engine'):
                    self.response_engine.speak(response)
                
                if hasattr(self, 'automation_engine'):
                    success = self.automation_engine.open_application(app_name)
                    if success:
                        response = f"{app_name} opened successfully."
                    else:
                        response = f"Failed to open {app_name}."
                    print(f"{Colors.MAGENTA}LISA: {response}{Colors.ENDC}")
                    if hasattr(self, 'response_engine'):
                        self.response_engine.speak(response)

        elif action == "help":
            print(f"{Colors.MAGENTA}LISA: {response}{Colors.ENDC}")
            # Also list available commands
            print(f"\n{Colors.CYAN}Available commands:{Colors.ENDC}")
            print(f"  • 'What time is it?' - Get current time")
            print(f"  • 'Open [app]' - Open applications (Word, Chrome, Notepad, etc.)")
            print(f"  • 'Study cyber' - Start your study routine")
            print(f"  • 'Who are you?' - Learn about Lisa")
            print(f"  • 'What can you do?' - List all commands")
            print(f"  • 'Goodbye' - Shutdown Lisa")
            if hasattr(self, 'response_engine'):
                self.response_engine.speak(response)
        
        elif action == "shutdown":
            # Actually shutdown the computer
            import os
            print(f"{Colors.MAGENTA}LISA: Shutting down the computer...{Colors.ENDC}")
            if hasattr(self, 'response_engine'):
                self.response_engine.speak("Shutting down the computer in 5 seconds")
            time.sleep(5)
            os.system("shutdown /s /t 1")
        
        elif action == "restart":
            # Restart the computer
            import os
            print(f"{Colors.MAGENTA}LISA: Restarting the computer...{Colors.ENDC}")
            if hasattr(self, 'response_engine'):
                self.response_engine.speak("Restarting the computer in 5 seconds")
            time.sleep(5)
            os.system("shutdown /r /t 1")
        
        elif action == "lock":
            # Lock the computer
            import ctypes
            print(f"{Colors.MAGENTA}LISA: Locking the computer...{Colors.ENDC}")
            if hasattr(self, 'response_engine'):
                self.response_engine.speak("Locking the computer")
            ctypes.windll.user32.LockWorkStation()
        
        else:
            # Unknown command
            print(f"{Colors.MAGENTA}LISA: {response}{Colors.ENDC}")
            if hasattr(self, 'response_engine'):
                self.response_engine.speak(response)
    
    def run(self):
        """Main run loop"""
        try:
            print(f"\n{Colors.MAGENTA}LISA is now running...{Colors.ENDC}")
            print(f"{Colors.WARNING}Speak 'Hey Lisa' followed by a command{Colors.ENDC}")
            print(f"{Colors.WARNING}Press Ctrl+C to exit{Colors.ENDC}")
            
            # Show listening indicator
            print(f"\n{Colors.CYAN}[Sleeping - waiting for 'Hey Lisa']{Colors.ENDC}", end="", flush=True)
            
            last_print_time = time.time()
            dot_count = 0
            last_wake_time = 0
            
            while self.is_running:
                # Process voice commands from queue
                if self.voice_listener:
                    command_data = self.voice_listener.get_next_command(timeout=0.1)
                    
                    if command_data:
                        if command_data["type"] == "wake_word":
                            print(f"\n{Colors.GREEN}✓ Wake word: '{command_data['text']}'{Colors.ENDC}")
                            print(f"{Colors.MAGENTA}LISA: {command_data['response']}{Colors.ENDC}")
                            
                            # Speak the response
                            if hasattr(self, 'response_engine'):
                                self.response_engine.speak(command_data['response'])
                            
                            last_wake_time = time.time()
                            print(f"\n{Colors.CYAN}[Awake - listening for command]{Colors.ENDC}", end="", flush=True)
                                
                        elif command_data["type"] == "command":
                            print(f"\n{Colors.BLUE}✓ Command: '{command_data['text']}'{Colors.ENDC}")
                            
                            # Process basic commands
                            self._process_basic_command(command_data['text'])
                            last_wake_time = time.time()
                            
                            print(f"\n{Colors.CYAN}[Sleeping - waiting for 'Hey Lisa']{Colors.ENDC}", end="", flush=True)
                            dot_count = 0
                        
                
                # If we woke up but no command within 10 seconds, go back to sleep
                if last_wake_time > 0 and time.time() - last_wake_time > 10:
                    print(f"\n{Colors.YELLOW}[Timeout - going back to sleep]{Colors.ENDC}", end="", flush=True)
                    last_wake_time = 0
                    print(f"\n{Colors.CYAN}[Sleeping - waiting for 'Hey Lisa']{Colors.ENDC}", end="", flush=True)
                
                # Animated listening indicator
                current_time = time.time()
                if current_time - last_print_time > 0.5:  # Every 0.5 seconds
                    dot_count = (dot_count + 1) % 4
                    dots = "." * dot_count + " " * (3 - dot_count)
                    
                    if last_wake_time > 0 and time.time() - last_wake_time <= 10:
                        # Awake state
                        print(f"\r{Colors.CYAN}[Awake - listening for command{dots}]{Colors.ENDC}", end="", flush=True)
                    else:
                        # Sleeping state
                        print(f"\r{Colors.CYAN}[Sleeping - waiting for 'Hey Lisa'{dots}]{Colors.ENDC}", end="", flush=True)
                    
                    last_print_time = current_time
                
                # Small sleep to prevent CPU hogging
                time.sleep(0.05)
                    
        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}Shutdown signal received...{Colors.ENDC}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown"""
        self.logger.info(f"Shutting down {self.assistant_name}...")
        
        # Stop voice listener
        if self.voice_listener:
            self.voice_listener.stop_listening()
        
        # Stop response engine
        if hasattr(self, 'response_engine'):
            self.response_engine.stop()
        
        if self.start_time:
            uptime = datetime.now() - self.start_time
            self.logger.info(f"Uptime: {uptime}")
            print(f"{Colors.MAGENTA}Uptime: {uptime}{Colors.ENDC}")
        
        self.is_running = False
        print(f"{Colors.MAGENTA}✓ {self.assistant_name} System Shutdown Complete{Colors.ENDC}")
        self.logger.info(f"{self.assistant_name} shutdown complete")

    def initialize_automation_system(self):
        """Initialize the automation system"""
        self.logger.info("Initializing automation system...")
        
        try:
            from core.automation_engine import AutomationEngine
            
            self.automation_engine = AutomationEngine()
            self.logger.info(f"{Colors.GREEN}✓ Automation system ready{Colors.ENDC}")
            return True
            
        except Exception as e:
            self.logger.error(f"Automation system initialization failed: {e}")
            return False


def main():
    """Main entry point"""
    try:
        # Create LISA instance
        lisa = LISA()
        
        # Initialize system
        if lisa.initialize():
            # Run main loop
            lisa.run()
        else:
            print(f"{Colors.FAIL}Failed to initialize LISA{Colors.ENDC}")
            return 1
            
    except Exception as e:
        print(f"{Colors.FAIL}Critical error: {e}{Colors.ENDC}")
        logging.error(f"Critical error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())