"""
AEGIS Core Module
Version: 0.1.0
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

__version__ = "0.1.0"
__author__ = "AEGIS Developer"

print(f"AEGIS Core Module v{__version__} loaded")