#!/usr/bin/env python3
"""
AEGIS - Main Entry Point
Adaptive Embedded Guardian & Intelligent System
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from utils.constants import *
from utils.file_utils import FileUtils
from utils.os_utils import OSUtils

class AEGIS:
    """Main AEGIS system class"""
    
    def __init__(self):
        self.start_time = None
        self.system_info = {}
        self.configs = {}
        self.is_running = False
        
        # Setup logging
        self.setup_logging()
        
        # Create directories
        ensure_directories()
    
    def setup_logging(self):
        """Configure logging system"""
        log_file = LOGS_DIR / f"aegis_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("AEGIS")
        self.logger.info("=" * 60)
        self.logger.info("AEGIS System Initializing...")
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
            self.logger.info("✓ Core dependencies available")
        except ImportError as e:
            self.logger.error(f"✗ Missing dependency: {e}")
            return False
        
        return True
    
    def display_banner(self):
        """Display startup banner"""
        banner = """
╔══════════════════════════════════════════════════════════╗
║                  A E G I S   S Y S T E M                 ║
║      Adaptive Embedded Guardian & Intelligent System     ║
║                                                          ║
║     Version: 0.1.0 Alpha          Status: INITIALIZING   ║
╚══════════════════════════════════════════════════════════╝
        """
        print(Colors.BLUE + banner + Colors.ENDC)
    
    def initialize(self):
        """Initialize the AEGIS system"""
        self.display_banner()
        
        # System check
        if not self.system_check():
            print(f"{Colors.FAIL}System check failed. Exiting...{Colors.ENDC}")
            return False
        
        # Load configurations
        if not self.load_configurations():
            print(f"{Colors.WARNING}Some configurations missing{Colors.ENDC}")
        
        # Display system info
        print(f"\n{Colors.GREEN}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}System Information:{Colors.ENDC}")
        print(f"  OS: {self.system_info['system']} {self.system_info['release']}")
        print(f"  Architecture: {self.system_info['machine']}")
        print(f"  Python: {self.system_info['python_version']}")
        print(f"{Colors.GREEN}{'='*60}{Colors.ENDC}")
        
        self.start_time = datetime.now()
        self.is_running = True
        
        self.logger.info("AEGIS initialization complete")
        print(f"\n{Colors.GREEN}✓ AEGIS System Ready!{Colors.ENDC}")
        print(f"{Colors.WARNING}Type 'exit' or press Ctrl+C to quit{Colors.ENDC}")
        
        return True
    
    def run(self):
        """Main run loop"""
        try:
            while self.is_running:
                # For now, just keep running
                # In Phase 1, we'll add voice listening here
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Shutdown signal received...{Colors.ENDC}")
            self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Shutting down AEGIS...")
        
        if self.start_time:
            uptime = datetime.now() - self.start_time
            self.logger.info(f"Uptime: {uptime}")
        
        self.is_running = False
        print(f"{Colors.GREEN}✓ AEGIS System Shutdown Complete{Colors.ENDC}")
        self.logger.info("AEGIS shutdown complete")

def main():
    """Main entry point"""
    try:
        # Create AEGIS instance
        aegis = AEGIS()
        
        # Initialize system
        if aegis.initialize():
            # Run main loop
            aegis.run()
        else:
            print(f"{Colors.FAIL}Failed to initialize AEGIS{Colors.ENDC}")
            return 1
            
    except Exception as e:
        print(f"{Colors.FAIL}Critical error: {e}{Colors.ENDC}")
        logging.error(f"Critical error: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())