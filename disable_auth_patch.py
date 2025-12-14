#!/usr/bin/env python3
"""
Quick patch to disable authentication temporarily
"""

import sys
from pathlib import Path

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

print("Applying authentication disable patch...")
print("="*60)

# Read main.py
main_py_path = Path("main.py")
if not main_py_path.exists():
    print("Error: main.py not found!")
    sys.exit(1)

with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace initialize_auth_system method
old_method = '''def initialize_auth_system(self):
    """Initialize the authentication system"""
    self.logger.info("Initializing authentication system...")
    
    try:
        from security.auth import VoiceAuthenticator
        
        self.auth_system = VoiceAuthenticator()
        
        # Setup authentication (enroll or load)
        if self.auth_system.setup_authentication():
            self.logger.info(f"{Colors.GREEN}✓ Authentication system ready{Colors.ENDC}")
            return True
        else:
            self.logger.warning("Authentication setup failed")
            return False
            
    except Exception as e:
        self.logger.error(f"Auth system initialization failed: {e}")
        return False'''

new_method = '''def initialize_auth_system(self):
    """Initialize the authentication system - TEMPORARILY DISABLED"""
    self.logger.info("Initializing authentication system...")
    
    # TEMPORARY: Skip authentication due to memory errors
    print(f"{Colors.YELLOW}⚠ Authentication temporarily disabled (memory errors){Colors.ENDC}")
    print(f"{Colors.YELLOW}⚠ Running in unsecured mode - anyone can use commands{Colors.ENDC}")
    
    # Create a dummy auth system that always returns True
    class DummyAuth:
        def requires_authentication(self, command):
            return False  # No commands require auth
        
        def authenticate_command(self, command):
            return True  # Always allow
    
    self.auth_system = DummyAuth()
    self.logger.info(f"{Colors.YELLOW}✓ Using dummy authentication (disabled){Colors.ENDC}")
    return True'''

if old_method in content:
    content = content.replace(old_method, new_method)
    print("✓ Updated initialize_auth_system method")
else:
    print("✗ Could not find old method - might already be patched")

# Also comment out authentication check in _process_basic_command
# Look for the authentication check and comment it
lines = content.split('\n')
new_lines = []
in_process_method = False
auth_check_found = False

for i, line in enumerate(lines):
    if 'def _process_basic_command' in line:
        in_process_method = True
    
    if in_process_method and 'if hasattr(self, \'auth_system\')' in line and 'requires_authentication' in line:
        # Comment out the next 15 lines (the whole auth block)
        auth_check_found = True
        new_lines.append('    # TEMPORARILY DISABLED AUTHENTICATION DUE TO MEMORY ERRORS')
        new_lines.append('    # ' + line)
        
        # Comment out the next lines until we see 'return' or another significant line
        j = i + 1
        while j < len(lines) and j < i + 20:  # Comment next 20 lines max
            indent = len(lines[j]) - len(lines[j].lstrip())
            if indent < 4:  # End of the block
                break
            new_lines.append('    # ' + lines[j])
            j += 1
        # Skip these lines in the original
        continue
    
    if auth_check_found and i > auth_check_found:
        # We're already processing commented lines, skip
        continue
    
    new_lines.append(line)

if auth_check_found:
    content = '\n'.join(new_lines)
    print("✓ Commented out authentication check in _process_basic_command")

# Write back
with open(main_py_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✓ Patch applied successfully!")
print("\nNow you can test security levels without authentication.")
print("Run: python main.py")
print("Then say: 'Hey Lisa, security level 2'")