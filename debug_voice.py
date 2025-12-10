#!/usr/bin/env python3
"""
Debug script to test voice recognition
"""

import speech_recognition as sr
import time
import sys
import io
import os

# Fix Windows console encoding
if sys.platform == "win32":
    if sys.stdout and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    os.system('chcp 65001 > nul')

def list_microphones():
    """List all available microphones"""
    print("\n" + "="*60)
    print("AVAILABLE MICROPHONES:")
    print("="*60)
    
    try:
        mic_list = sr.Microphone.list_microphone_names()
        for i, mic in enumerate(mic_list):
            print(f"[{i}] {mic}")
        
        if mic_list:
            print(f"\n✓ Found {len(mic_list)} microphone(s)")
            return mic_list
        else:
            print("✗ No microphones found!")
            return []
            
    except Exception as e:
        print(f"✗ Error listing microphones: {e}")
        return []

def test_microphone(mic_index=0, duration=5):
    """Test a specific microphone"""
    print(f"\n" + "="*60)
    print(f"TESTING MICROPHONE [{mic_index}] FOR {duration} SECONDS")
    print("="*60)
    
    r = sr.Recognizer()
    
    try:
        with sr.Microphone(device_index=mic_index) as source:
            print("Adjusting for ambient noise...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("✓ Adjusted")
            
            print(f"\n🎤 Speak now (listening for {duration} seconds)...")
            
            # Listen with timeout
            start_time = time.time()
            audio = None
            
            try:
                audio = r.listen(source, timeout=duration, phrase_time_limit=duration)
                print("✓ Audio captured")
            except sr.WaitTimeoutError:
                print("✗ No speech detected (timeout)")
                return False
            
            if audio:
                print("\nProcessing audio...")
                
                # Try Google Speech Recognition
                try:
                    text = r.recognize_google(audio)
                    print(f"\n✅ GOOGLE UNDERSTOOD: '{text}'")
                    
                    # Check for wake words
                    text_lower = text.lower()
                    wake_words = ["hey aegis", "hello aegis", "wake up", "aegis", "hey agis"]
                    
                    for wake_word in wake_words:
                        if wake_word in text_lower:
                            print(f"\n🎯 WAKE WORD DETECTED: '{wake_word}' in '{text}'")
                            return True
                    
                    print(f"\nℹ️ No wake word found in: '{text}'")
                    print(f"Looking for: {wake_words}")
                    
                except sr.UnknownValueError:
                    print("✗ Google could not understand audio")
                except sr.RequestError as e:
                    print(f"✗ Google API error: {e}")
                
                # Try Sphinx (offline)
                try:
                    text = r.recognize_sphinx(audio)
                    print(f"\n📦 SPHINX UNDERSTOOD: '{text}'")
                    
                    text_lower = text.lower()
                    wake_words = ["hey aegis", "hello aegis", "wake up", "aegis", "hey agis"]
                    
                    for wake_word in wake_words:
                        if wake_word in text_lower:
                            print(f"\n🎯 WAKE WORD DETECTED: '{wake_word}' in '{text}'")
                            return True
                    
                    print(f"\nℹ️ No wake word found in: '{text}'")
                    
                except sr.UnknownValueError:
                    print("✗ Sphinx could not understand audio")
                except Exception as e:
                    print(f"✗ Sphinx error: {e}")
        
        return False
        
    except Exception as e:
        print(f"✗ Microphone error: {e}")
        return False

def real_time_listening(mic_index=0):
    """Real-time listening test"""
    print("\n" + "="*60)
    print("REAL-TIME LISTENING TEST")
    print("="*60)
    print("Speak 'Hey Aegis' clearly")
    print("Press Ctrl+C to stop\n")
    
    r = sr.Recognizer()
    
    try:
        with sr.Microphone(device_index=mic_index) as source:
            print("Adjusting for ambient noise...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("✓ Ready! Start speaking...\n")
            
            while True:
                try:
                    print("🎤 Listening...", end="", flush=True)
                    audio = r.listen(source, timeout=3, phrase_time_limit=3)
                    print("\r✅ Heard something, processing...")
                    
                    try:
                        text = r.recognize_google(audio)
                        text_lower = text.lower()
                        print(f"   Text: '{text}'")
                        
                        # Check for wake words
                        if "hey aegis" in text_lower or "hello aegis" in text_lower:
                            print(f"\n🎯🎯🎯 WAKE WORD DETECTED! 🎯🎯🎯")
                            print(f"   Full text: '{text}'")
                            print("\n✓ SUCCESS! Voice system should work!")
                            return True
                            
                    except sr.UnknownValueError:
                        print("\r✗ Could not understand audio")
                    except sr.RequestError:
                        print("\r✗ API error")
                        
                except sr.WaitTimeoutError:
                    print("\r⏳ No speech detected...", end="", flush=True)
                    
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\nError: {e}")
    
    return False

def main():
    print("AEGIS VOICE SYSTEM DEBUGGER")
    print("="*60)
    
    # Step 1: List microphones
    mics = list_microphones()
    
    if not mics:
        print("\nNo microphones found. Check your audio devices!")
        return
    
    # Step 2: Test default microphone
    print("\n" + "="*60)
    print("TEST 1: DEFAULT MICROPHONE")
    print("="*60)
    
    if not test_microphone(0, 5):
        print("\n⚠️ Default microphone test failed!")
    
    # Step 3: Test all microphones
    print("\n" + "="*60)
    print("TEST 2: ALL MICROPHONES")
    print("="*60)
    
    working_mic = -1
    for i in range(len(mics)):
        print(f"\nTesting microphone {i}: {mics[i][:50]}...")
        if test_microphone(i, 3):
            working_mic = i
            print(f"✓ This microphone works! (Index: {i})")
            break
    
    # Step 4: Real-time test with working microphone
    if working_mic >= 0:
        print("\n" + "="*60)
        print(f"TEST 3: REAL-TIME WITH MIC {working_mic}")
        print("="*60)
        
        real_time_listening(working_mic)
    else:
        print("\n⚠️ No working microphone found!")
        
        # Try real-time with default anyway
        response = input("\nTry real-time test with default microphone? (y/n): ")
        if response.lower() == 'y':
            real_time_listening(0)

if __name__ == "__main__":
    main()