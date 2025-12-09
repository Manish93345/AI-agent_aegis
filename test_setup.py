#!/usr/bin/env python3
"""
AEGIS Setup Test Script
Run this to verify your Phase 0 setup
"""

import os
import sys
import json

def test_directory_structure():
    """Test if all required directories exist"""
    print("Testing directory structure...")
    
    required_dirs = [
        'core',
        'security',
        'learning',
        'config',
        'data/logs',
        'data/voice_samples',
        'data/encrypted'
    ]
    
    all_good = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✓ {directory}/")
        else:
            print(f"  ✗ {directory}/ - MISSING")
            all_good = False
    
    return all_good

def test_config_files():
    """Test if all config files exist and are valid JSON"""
    print("\nTesting configuration files...")
    
    config_files = [
        'config/commands.json',
        'config/security_profiles.json',
        'config/user_prefs.json'
    ]
    
    all_good = True
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    json.load(f)
                print(f"  ✓ {config_file} (Valid JSON)")
            except json.JSONDecodeError as e:
                print(f"  ✗ {config_file} - Invalid JSON: {e}")
                all_good = False
        else:
            print(f"  ✗ {config_file} - File not found")
            all_good = False
    
    return all_good

def test_python_files():
    """Test if core Python files exist"""
    print("\nTesting Python modules...")
    
    python_files = [
        'main.py',
        'core/command_handler.py',
        'core/__init__.py'
    ]
    
    all_good = True
    for py_file in python_files:
        if os.path.exists(py_file):
            print(f"  ✓ {py_file}")
        else:
            print(f"  ✗ {py_file} - MISSING")
            all_good = False
    
    return all_good

def run_tests():
    """Run all setup tests"""
    print("=" * 60)
    print("AEGIS SETUP VALIDATION TEST")
    print("=" * 60)
    
    tests = [
        test_directory_structure,
        test_config_files,
        test_python_files
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    
    if all(results):
        print("✅ ALL TESTS PASSED!")
        print("Your AEGIS project structure is correctly set up.")
        print("\nNext, install dependencies:")
        print("  pip install -r requirements.txt")
        print("\nThen test the system:")
        print("  python main.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please fix the issues above before proceeding.")
    
    print("=" * 60)

if __name__ == "__main__":
    run_tests()