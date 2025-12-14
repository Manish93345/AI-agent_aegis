#!/usr/bin/env python3
"""
Simple authentication debug
"""

import sys
from pathlib import Path

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing Authentication System...")
print("="*60)

# First, clean up any corrupted files
import os
import shutil

corrupted_files = [
    "data/models/voice_auth_model.pkl",
    "data/auth/pin.hash"
]

for file in corrupted_files:
    file_path = Path(file)
    if file_path.exists():
        try:
            file_path.unlink()
            print(f"Cleaned up: {file}")
        except:
            pass

# Create directories
Path("data/models").mkdir(parents=True, exist_ok=True)
Path("data/auth").mkdir(parents=True, exist_ok=True)

# Now test
from security.auth import VoiceAuthenticator
import logging

logging.basicConfig(level=logging.INFO)

auth = VoiceAuthenticator()

print("\n1. Testing fresh enrollment...")
print("You'll need to speak 6 phrases for voice enrollment.")

if auth.setup_authentication():
    print("\n✓ Authentication setup successful!")
    
    print("\n2. Testing command authentication...")
    test_command = "security level 2"
    
    if auth.requires_authentication(test_command):
        print(f"Command '{test_command}' requires authentication")
        
        print("\nAuthentication methods available:")
        print("1. Voice")
        print("2. PIN")
        
        choice = input("\nChoose method (1/2): ").strip()
        
        if choice == "1":
            success, confidence = auth.verify_live()
            if success:
                print(f"✓ Voice authentication successful! (confidence: {confidence:.2f})")
            else:
                print("✗ Voice authentication failed")
        elif choice == "2":
            if auth.authenticate_with_pin():
                print("✓ PIN authentication successful!")
            else:
                print("✗ PIN authentication failed")
    else:
        print(f"Command '{test_command}' doesn't require authentication")
else:
    print("\n✗ Authentication setup failed")