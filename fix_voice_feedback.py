import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("Testing voice feedback fixes...")
print("="*60)

from core.response_engine import ResponseEngine
import logging

logging.basicConfig(level=logging.INFO)

engine = ResponseEngine()

if engine.initialize():
    print("✓ Response Engine initialized")

    test_messages = [
        "Hello, I am Lisa!",
        "Voice feedback is working.",
        "I can speak both English and Hindi."
    ]

    for msg in test_messages:
        print("Speaking:", msg)
        engine.speak(msg)

else:
    print("✗ Initialization failed")
