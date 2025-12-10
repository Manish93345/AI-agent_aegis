#!/usr/bin/env python3
"""
Quick test of the fixes
"""

import sys
import os
from pathlib import Path

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

from core.automation_engine import AutomationEngine
import logging

logging.basicConfig(level=logging.INFO)

print("Testing fixes...")
print("="*60)

engine = AutomationEngine()

# Test 1: Open Microsoft Word
print("\nTest 1: Opening Microsoft Word...")
if engine.open_application("microsoft word"):
    print("✓ Microsoft Word opened")
else:
    print("✗ Failed to open Microsoft Word")

# Test 2: Test music in Chrome
print("\nTest 2: Playing music in Chrome...")
if engine.play_music("youtube", "chrome"):
    print("✓ Music playing in Chrome")
else:
    print("✗ Failed to play music in Chrome")

print("\n✓ Fixes tested")