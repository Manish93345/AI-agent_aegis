#!/usr/bin/env python3
"""
Quick test script for LLM integration
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing LLM Integration...")
print("=" * 60)

try:
    from core.llm_wrapper import get_llm_instance, test_llm, quick_test
    
    # Run quick test
    print("Running quick test...")
    if quick_test():
        print("✓ Quick test passed")
    else:
        print("✗ Quick test failed")
    
    print("\n" + "=" * 60)
    
    # Run full test
    print("\nRunning full test...")
    test_llm()
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure ollama is installed: pip install ollama")
except Exception as e:
    print(f"Error: {e}")