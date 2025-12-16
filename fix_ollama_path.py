#!/usr/bin/env python3
"""
Fix Ollama PATH issues on Windows
"""
import os
import sys
import subprocess

def find_ollama():
    """Find Ollama installation on Windows"""
    print("Searching for Ollama installation...")
    
    # Common installation paths
    common_paths = [
        r"C:\Program Files\Ollama",
        r"C:\Users\{}\AppData\Local\Programs\Ollama".format(os.getenv('USERNAME')),
        r"C:\Ollama",
        os.path.join(os.getenv('LOCALAPPDATA', ''), "Programs", "Ollama"),
        os.path.join(os.getenv('PROGRAMFILES', ''), "Ollama"),
        os.path.join(os.getenv('PROGRAMFILES(X86)', ''), "Ollama"),
    ]
    
    for path in common_paths:
        ollama_exe = os.path.join(path, "ollama.exe")
        if os.path.exists(ollama_exe):
            print(f"✓ Found Ollama at: {ollama_exe}")
            return path
    
    print("✗ Ollama not found in common locations")
    
    # Try to find it in PATH
    try:
        result = subprocess.run(["where", "ollama"], 
                              capture_output=True, 
                              text=True, 
                              shell=True)
        if result.returncode == 0:
            ollama_path = os.path.dirname(result.stdout.strip())
            print(f"✓ Found Ollama in PATH: {ollama_path}")
            return ollama_path
    except:
        pass
    
    return None

def add_to_path(ollama_path):
    """Add Ollama to PATH"""
    print(f"\nAdding {ollama_path} to PATH...")
    
    # Update current process PATH
    os.environ["PATH"] = ollama_path + ";" + os.environ["PATH"]
    
    print(f"Updated PATH: {ollama_path}")
    return True

def test_ollama():
    """Test if ollama command works"""
    print("\nTesting ollama command...")
    try:
        result = subprocess.run(["ollama", "list"], 
                              capture_output=True, 
                              text=True, 
                              shell=True)
        if result.returncode == 0:
            print("✓ Ollama command works!")
            print(f"Output: {result.stdout}")
            return True
        else:
            print(f"✗ Ollama command failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error running ollama: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Ollama PATH Fixer for Windows")
    print("=" * 60)
    
    # Find Ollama
    ollama_path = find_ollama()
    
    if not ollama_path:
        print("\n✗ Could not find Ollama installation")
        print("\nPlease install Ollama from: https://ollama.com/download/windows")
        input("Press Enter after installing Ollama...")
        ollama_path = find_ollama()
    
    if ollama_path:
        # Add to PATH
        add_to_path(ollama_path)
        
        # Test
        if test_ollama():
            print("\n✓ Ollama is ready!")
        else:
            print("\n✗ Ollama still not working")
            print("Try running: ollama serve")
    else:
        print("\n✗ Ollama installation not found")
        sys.exit(1)