#!/usr/bin/env python3
"""
Check if Ollama is running and accessible
"""
import sys
import subprocess
import json

def check_ollama():
    """Check if Ollama is running and accessible"""
    print("Checking Ollama status...")
    
    # Method 1: Check if ollama command exists
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, 
                              text=True)
        print(f"✓ Ollama CLI: {result.stdout.strip()}")
    except FileNotFoundError:
        print("✗ Ollama CLI not found in PATH")
        print("Make sure Ollama is installed and in your PATH")
        return False
    
    # Method 2: Check if service is running
    try:
        import httpx
        try:
            response = httpx.get("http://127.0.0.1:11434/api/tags", timeout=5.0)
            if response.status_code == 200:
                print("✓ Ollama service is running")
                
                # List available models
                models_data = response.json()
                models = [model['name'] for model in models_data.get('models', [])]
                print(f"Available models: {', '.join(models)}")
                return True
            else:
                print(f"✗ Ollama service error: HTTP {response.status_code}")
                return False
        except httpx.RequestError as e:
            print(f"✗ Cannot connect to Ollama service: {e}")
            print("Make sure Ollama service is running: ollama serve")
            return False
    except ImportError:
        print("✗ httpx not installed, using alternative check")
        try:
            import ollama
            models = ollama.list()
            print("✓ Ollama service is running")
            print(f"Available models: {', '.join([m['name'] for m in models.get('models', [])])}")
            return True
        except Exception as e:
            print(f"✗ Cannot connect to Ollama: {e}")
            return False
    
    return False


if __name__ == "__main__":
    if check_ollama():
        print("\n✓ Ollama is ready to use!")
        sys.exit(0)
    else:
        print("\n✗ Ollama is not ready")
        print("\nTroubleshooting steps:")
        print("1. Make sure Ollama is installed")
        print("2. Start Ollama service: ollama serve")
        print("3. Check if it's running: ollama list")
        print("4. Pull a model: ollama pull llama3.1:8b")
        sys.exit(1)