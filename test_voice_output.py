#!/usr/bin/env python3
"""Test Lisa's voice output"""

import sys
import io
import os

# Fix Windows console
if sys.platform == "win32":
    if sys.stdout and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    os.system('chcp 65001 > nul')

# Add project path
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.response_engine import ResponseEngine

print("Testing Lisa's voice...")
engine = ResponseEngine()

if engine.initialize():
    print("✓ Response Engine initialized")
    
    # Test speaking
    test_phrases = [
        "Hello, I am Lisa, your personal assistant.",
        "The time is three fifteen PM.",
        "My name is Lisa. How can I help you today?"
    ]
    
    for phrase in test_phrases:
        print(f"Speaking: {phrase}")
        engine.speak_immediate(phrase)
    
    print("\n✓ Voice test complete!")
else:
    print("✗ Failed to initialize voice")