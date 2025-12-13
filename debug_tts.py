#!/usr/bin/env python3
"""Comprehensive TTS Debug Script"""

import sys
import os
import time
import platform
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("TTS SYSTEM DEBUG")
print("="*70)

# Check system info
print(f"\n1. SYSTEM INFORMATION:")
print(f"   OS: {platform.system()} {platform.release()}")
print(f"   Python: {platform.python_version()}")
print(f"   Architecture: {platform.architecture()[0]}")

# Check pyttsx3 installation
print(f"\n2. CHECKING PYTTSX3 INSTALLATION:")
try:
    import pyttsx3
    print(f"   ✓ pyttsx3 imported successfully")
    print(f"   Version: {pyttsx3.__version__ if hasattr(pyttsx3, '__version__') else 'Not specified'}")
except ImportError as e:
    print(f"   ✗ Failed to import pyttsx3: {e}")
    print(f"   Try: pip install pyttsx3")
    sys.exit(1)

# Direct pyttsx3 test
print(f"\n3. DIRECT PYTTSX3 TEST:")
try:
    print("   Initializing pyttsx3 engine...")
    engine = pyttsx3.init()
    
    # Get available voices
    voices = engine.getProperty('voices')
    print(f"   Found {len(voices)} voice(s)")
    
    if len(voices) == 0:
        print("   ✗ NO VOICES FOUND! This is the problem.")
        print("   Possible solutions:")
        print("   1. On Windows: Install Microsoft Speech Platform")
        print("   2. On macOS: Ensure NSSpeechSynthesizer is working")
        print("   3. On Linux: Install espeak or festival")
    else:
        print(f"\n   Available voices:")
        for i, voice in enumerate(voices):
            gender = "Female" if "female" in voice.name.lower() or "zira" in voice.name.lower() else "Male"
            print(f"   [{i}] {voice.name} ({gender})")
        
        # Try each voice
        print(f"\n   Testing each voice (you should hear 3 test phrases):")
        test_phrases = [
            "Testing voice one",
            "Testing voice two", 
            "Testing voice three"
        ]
        
        for i, voice in enumerate(voices[:3]):  # Test first 3 voices max
            if i < len(test_phrases):
                engine.setProperty('voice', voice.id)
                print(f"\n   Speaking with voice {i}: {voice.name}")
                print(f"   Saying: '{test_phrases[i]}'")
                engine.say(test_phrases[i])
                engine.runAndWait()
                time.sleep(1)
    
    engine.stop()
    
except Exception as e:
    print(f"   ✗ Direct pyttsx3 test failed: {e}")
    import traceback
    traceback.print_exc()

# Test ResponseEngine
print(f"\n4. TESTING RESPONSEENGINE CLASS:")
try:
    from response_engine import ResponseEngine
    
    print("   Creating ResponseEngine instance...")
    engine = ResponseEngine()
    
    if hasattr(engine, 'initialize'):
        print("   Initializing ResponseEngine...")
        if engine.initialize():
            print("   ✓ ResponseEngine initialized successfully")
            
            # Test immediate speaking
            print("\n   Testing speak_immediate() method:")
            test_messages = [
                "Hello, I am Lisa!",
                "Voice feedback is working.",
                "I can speak both English and Hindi."
            ]
            
            for msg in test_messages:
                print(f"\n   Speaking: '{msg}'")
                print("   (You should hear this now)")
                engine.speak_immediate(msg)
                time.sleep(1)
        else:
            print("   ✗ ResponseEngine.initialize() returned False")
    else:
        print("   ✗ ResponseEngine has no 'initialize' method")
        
except Exception as e:
    print(f"   ✗ ResponseEngine test failed: {e}")
    import traceback
    traceback.print_exc()

# Audio system check
print(f"\n5. AUDIO SYSTEM CHECK:")
print("   Check these common issues:")

if platform.system() == "Windows":
    print("   - Is your audio device enabled?")
    print("   - Is volume turned up?")
    print("   - Try: Control Panel > Speech Recognition > Text to Speech")
    print("   - Install voices: Settings > Time & Language > Speech")
    
elif platform.system() == "Darwin":  # macOS
    print("   - Check System Preferences > Accessibility > Speech")
    print("   - Try: say 'hello' in terminal to test built-in TTS")
    
elif platform.system() == "Linux":
    print("   - Install espeak: sudo apt-get install espeak")
    print("   - Or install festival: sudo apt-get install festival")

# Alternative TTS test
print(f"\n6. ALTERNATIVE TTS TEST (using say command):")
try:
    if platform.system() == "Windows":
        os.system('echo "Windows TTS test" && timeout 2 > nul')
        # PowerShell test
        os.system('powershell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak(\'Windows TTS working\')"')
    elif platform.system() == "Darwin":
        os.system('say "macOS TTS working"')
    elif platform.system() == "Linux":
        os.system('espeak "Linux TTS working" 2>/dev/null || echo "espeak not installed"')
except:
    pass

print(f"\n" + "="*70)
print("DEBUG COMPLETE")
print("="*70)
print("\nIf you still have no voice output:")
print("1. Check system volume and mute status")
print("2. Try headphones/speakers")
print("3. Run as administrator (Windows)")
print("4. Check if another program is blocking audio")