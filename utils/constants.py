
"""
Constants used throughout the LISA system
"""

import os
from pathlib import Path

# Project root path
PROJECT_ROOT = Path(__file__).parent.parent

# Data paths
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = DATA_DIR / "logs"
VOICE_SAMPLES_DIR = DATA_DIR / "voice_samples"
ENCRYPTED_DIR = DATA_DIR / "encrypted"
BACKUPS_DIR = DATA_DIR / "backups"
MODELS_DIR = DATA_DIR / "models"

# Config paths
CONFIG_DIR = PROJECT_ROOT / "config"
COMMANDS_CONFIG = CONFIG_DIR / "commands.json"
SECURITY_CONFIG = CONFIG_DIR / "security_profiles.json"
USER_PREFS = CONFIG_DIR / "user_prefs.json"
SYSTEM_CONFIG = CONFIG_DIR / "system_config.json"

# Wake word
WAKE_WORD = "hey lisa"
ASSISTANT_NAME = "Lisa"

# Security levels
SECURITY_LEVELS = {
    1: "Normal",
    2: "Restricted", 
    3: "Lockdown"
}

# Colors for console output
class Colors:
    HEADER = '\033[95m'
    MAGENTA = '\033[95m'  # For Lisa theme
    CYAN = '\033[96m'     # For listening indicator
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Audio settings
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
RECORD_SECONDS = 5
ENERGY_THRESHOLD = 300

def ensure_directories():
    """Create all necessary directories if they don't exist"""
    directories = [
        DATA_DIR, LOGS_DIR, VOICE_SAMPLES_DIR,
        ENCRYPTED_DIR, BACKUPS_DIR, MODELS_DIR,
        CONFIG_DIR
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True, parents=True)
    
    print(f"{Colors.GREEN}✓ All directories verified{Colors.ENDC}")