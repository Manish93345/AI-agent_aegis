"""
Security Level System for LISA
Implements Levels 1-3 with file protection, app blocking, and emergency commands
"""

import os
import sys
import ctypes
import subprocess
import logging
import time
import tempfile
import shutil
import psutil
from typing import List, Dict, Set, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import threading
import hashlib

from cryptography.fernet import Fernet
import pyautogui

from utils.constants import Colors
from utils.file_utils import FileUtils
from utils.os_utils import OSUtils

class SecurityLevel(Enum):
    """Security levels as requested"""
    LEVEL_1 = 1  # Normal - Everything accessible
    LEVEL_2 = 2  # Restricted - Monitor sensitive apps/files
    LEVEL_3 = 3  # Lockdown - Encrypt files, block apps, disable features

@dataclass
class SecurityAction:
    """Individual security action"""
    name: str
    description: str
    level: SecurityLevel
    enabled: bool = False
    parameters: Dict = field(default_factory=dict)

class SecurityMonitor:
    """Monitors system for security violations"""
    
    def __init__(self):
        self.logger = logging.getLogger("LISA.Security")
        self.os_utils = OSUtils()
        self.current_level = SecurityLevel.LEVEL_1
        self.blocked_apps: Set[str] = set()
        self.protected_folders: Set[Path] = set()
        self.running_monitors: List[threading.Thread] = []
        self.is_monitoring = False
        
        # Encryption
        self.encryption_key: Optional[bytes] = None
        self.cipher: Optional[Fernet] = None
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load security configuration from JSON"""
        try:
            from utils.constants import SECURITY_CONFIG
            config = FileUtils.load_json(SECURITY_CONFIG)
            
            if not config:
                self.logger.warning("No security config found, using defaults")
                return
            
            # Load protected folders
            if "level_2" in config and "protected_folders" in config["level_2"]:
                for folder in config["level_2"]["protected_folders"]:
                    # Replace [USER] with actual username
                    folder = folder.replace("kumar", os.getlogin())
                    self.protected_folders.add(Path(folder))
            
            self.logger.info(f"Loaded {len(self.protected_folders)} protected folders")
            
        except Exception as e:
            self.logger.error(f"Failed to load security config: {e}")
    
    def set_security_level(self, level: int) -> bool:
        """Set security level (1, 2, or 3)"""
        try:
            if level not in [1, 2, 3]:
                self.logger.error(f"Invalid security level: {level}")
                return False
            
            new_level = SecurityLevel(level)
            old_level = self.current_level
            
            # Don't do anything if level isn't changing
            if new_level == self.current_level:
                self.logger.info(f"Already at security level {level}")
                return True
            
            self.logger.info(f"Changing security level: {old_level.value} → {new_level.value}")
            
            # Stop existing monitors
            self.stop_monitoring()
            
            # Apply new level
            self.current_level = new_level
            
            if new_level == SecurityLevel.LEVEL_1:
                success = self._apply_level_1()
            elif new_level == SecurityLevel.LEVEL_2:
                success = self._apply_level_2()
            elif new_level == SecurityLevel.LEVEL_3:
                success = self._apply_level_3()
            
            if success:
                self.logger.info(f"{Colors.GREEN}✓ Security level {level} activated{Colors.ENDC}")
                
                # Start monitoring for this level
                self.start_monitoring()
                
                # Log the change
                self._log_security_event(
                    f"Security level changed from {old_level.value} to {new_level.value}"
                )
                
                return True
            else:
                self.logger.error(f"Failed to apply security level {level}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting security level: {e}")
            return False
    
    def _apply_level_1(self) -> bool:
        """Apply Level 1: Normal Mode - Minimal restrictions"""
        self.logger.info("Applying Security Level 1: Normal Mode")
        
        try:
            # Unblock all apps
            self.blocked_apps.clear()
            
            # Stop any active protection
            self._stop_folder_protection()
            
            # Release any locked files
            self._release_locked_files()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying level 1: {e}")
            return False
    
    def _apply_level_2(self) -> bool:
        """Apply Level 2: Restricted Mode - Monitor sensitive activities"""
        self.logger.info("Applying Security Level 2: Restricted Mode")
        
        try:
            # Block sensitive system apps
            sensitive_apps = [
                "taskmgr.exe",  # Task Manager
                "regedit.exe",  # Registry Editor
                "msconfig.exe",  # System Configuration
                "compmgmt.msc",  # Computer Management
                "diskmgmt.msc",  # Disk Management
            ]
            
            self.blocked_apps.update(sensitive_apps)
            
            # Start folder monitoring
            # self._start_folder_monitoring()
            
            # Log all process creations
            self._log_process_creations = True
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying level 2: {e}")
            return False
    
    def _apply_level_3(self) -> bool:
        """Apply Level 3: Lockdown Mode - Maximum security"""
        self.logger.info("Applying Security Level 3: Lockdown Mode")
        
        try:
            # Block ALL non-essential apps
            essential_apps = [
                "notepad.exe",
                "wordpad.exe",
                "calculator.exe",
                "explorer.exe",  # File Explorer
            ]
            
            # Get all running processes and block non-essential ones
            for proc in psutil.process_iter(['name']):
                proc_name = proc.info['name'].lower()
                if proc_name not in essential_apps and proc_name not in ["python.exe", "pythonw.exe"]:
                    self.blocked_apps.add(proc_name)
            
            # Encrypt protected folders
            self._encrypt_protected_folders()
            
            # Disable USB ports (Windows)
            if self.os_utils.is_windows():
                self._disable_usb_ports()
            
            # Disable network (optional - can be too restrictive)
            # self._disable_network()
            
            # Hide sensitive files
            self._hide_sensitive_files()
            
            # Start intensive monitoring
            self._start_intensive_monitoring()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying level 3: {e}")
            return False
    
    def start_monitoring(self):
        """Start security monitoring based on current level"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        
        if self.current_level == SecurityLevel.LEVEL_2:
            # Start process monitor thread
            process_monitor = threading.Thread(
                target=self._monitor_processes_level_2,
                daemon=True,
                name="SecurityMonitor-Level2"
            )
            process_monitor.start()
            self.running_monitors.append(process_monitor)
            
            # Start folder monitor thread
            folder_monitor = threading.Thread(
                target=self._monitor_protected_folders,
                daemon=True,
                name="FolderMonitor"
            )
            folder_monitor.start()
            self.running_monitors.append(folder_monitor)
        
        elif self.current_level == SecurityLevel.LEVEL_3:
            # Start intensive monitoring
            intensive_monitor = threading.Thread(
                target=self._intensive_monitoring_level_3,
                daemon=True,
                name="SecurityMonitor-Level3"
            )
            intensive_monitor.start()
            self.running_monitors.append(intensive_monitor)
            
            # Start encryption monitor
            encryption_monitor = threading.Thread(
                target=self._monitor_encryption_status,
                daemon=True,
                name="EncryptionMonitor"
            )
            encryption_monitor.start()
            self.running_monitors.append(encryption_monitor)
        
        self.logger.info(f"Started {len(self.running_monitors)} security monitors")
    
    def stop_monitoring(self):
        """Stop all security monitoring"""
        self.is_monitoring = False
        
        # Let threads finish
        for monitor in self.running_monitors:
            if monitor.is_alive():
                monitor.join(timeout=2)
        
        self.running_monitors.clear()
        self.logger.info("Stopped all security monitors")
    
    def _monitor_processes_level_2(self):
        """Monitor processes for Level 2 restrictions"""
        self.logger.info("Starting process monitor (Level 2)")
        
        while self.is_monitoring and self.current_level == SecurityLevel.LEVEL_2:
            try:
                # Check for blocked apps
                for proc in psutil.process_iter(['pid', 'name']):
                    proc_name = proc.info['name'].lower()
                    
                    if proc_name in self.blocked_apps:
                        self.logger.warning(f"Blocked app detected: {proc_name}")
                        
                        # Kill the process
                        try:
                            proc.terminate()
                            proc.wait(timeout=3)
                            self._log_security_event(f"Terminated blocked process: {proc_name}")
                        except:
                            try:
                                proc.kill()
                                self._log_security_event(f"Killed blocked process: {proc_name}")
                            except:
                                pass
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Process monitor error: {e}")
                time.sleep(10)
    
    def _monitor_protected_folders(self):
        """Monitor protected folders for unauthorized access"""
        self.logger.info("Starting folder monitor")
        
        # Track which files were accessed
        accessed_files = set()
        
        while self.is_monitoring and self.current_level == SecurityLevel.LEVEL_2:
            try:
                for folder in self.protected_folders:
                    if not folder.exists():
                        continue
                    
                    # Check for recent file accesses (simplified)
                    for file_path in folder.rglob("*"):
                        if file_path.is_file():
                            try:
                                # Check if file was modified recently
                                stat = file_path.stat()
                                current_time = time.time()
                                
                                # If modified in last 10 seconds
                                if current_time - stat.st_mtime < 10:
                                    if file_path not in accessed_files:
                                        accessed_files.add(file_path)
                                        self._log_security_event(
                                            f"File accessed in protected folder: {file_path}"
                                        )
                            except:
                                pass
                
                # Clean up old entries
                if len(accessed_files) > 100:
                    accessed_files = set(list(accessed_files)[-50:])
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Folder monitor error: {e}")
                time.sleep(30)
    
    def _intensive_monitoring_level_3(self):
        """Intensive monitoring for Level 3"""
        self.logger.info("Starting intensive monitoring (Level 3)")
        
        while self.is_monitoring and self.current_level == SecurityLevel.LEVEL_3:
            try:
                # Monitor USB device connections
                self._monitor_usb_devices()
                
                # Monitor network connections
                self._monitor_network_connections()
                
                # Monitor screen capture attempts
                self._monitor_screen_capture()
                
                # Monitor clipboard for sensitive data
                self._monitor_clipboard()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Intensive monitor error: {e}")
                time.sleep(60)
    
    def emergency_shutdown(self, immediate: bool = False) -> bool:
        """Emergency shutdown command - works even if someone else is using it"""
        self.logger.info(f"Emergency shutdown requested (immediate: {immediate})")
        
        try:
            if immediate:
                # Immediate shutdown - no warning
                self._log_security_event("EMERGENCY SHUTDOWN - IMMEDIATE")
                
                if self.os_utils.is_windows():
                    os.system("shutdown /s /f /t 0")
                elif self.os_utils.is_mac():
                    os.system("shutdown -h now")
                else:  # Linux
                    os.system("shutdown now")
                
                return True
            
            else:
                # Give user 5 second warning
                self._log_security_event("EMERGENCY SHUTDOWN - 5 SECOND WARNING")
                
                # Show warning message
                self._show_shutdown_warning()
                
                # Countdown
                for i in range(5, 0, -1):
                    print(f"{Colors.FAIL}Shutting down in {i}...{Colors.ENDC}")
                    time.sleep(1)
                
                # Execute shutdown
                if self.os_utils.is_windows():
                    os.system("shutdown /s /f /t 0")
                elif self.os_utils.is_mac():
                    os.system("shutdown -h now")
                else:
                    os.system("shutdown now")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Emergency shutdown failed: {e}")
            return False
    
    def panic_mode(self) -> bool:
        """Activate panic mode - hide everything, fake crash, etc."""
        self.logger.info("Activating panic mode")
        
        try:
            # 1. Hide all windows
            self._hide_all_windows()
            
            # 2. Show fake crash screen
            self._show_fake_crash()
            
            # 3. Lock workstation
            self._lock_workstation()
            
            # 4. Encrypt sensitive files if not already
            if self.current_level != SecurityLevel.LEVEL_3:
                self._encrypt_critical_files()
            
            # 5. Log the event
            self._log_security_event("PANIC MODE ACTIVATED")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Panic mode failed: {e}")
            return False
    
    def _hide_all_windows(self):
        """Minimize all windows"""
        try:
            import pyautogui
            pyautogui.hotkey('win', 'd')  # Show desktop (minimize all)
            time.sleep(0.5)
        except:
            pass
    
    def _show_fake_crash(self):
        """Show a fake crash/BSOD screen"""
        try:
            if self.os_utils.is_windows():
                # Windows fake BSOD
                print(f"\n{Colors.FAIL}{'='*60}{Colors.ENDC}")
                print(f"{Colors.FAIL}SYSTEM CRITICAL ERROR{Colors.ENDC}")
                print(f"{Colors.FAIL}{'='*60}{Colors.ENDC}")
                print(f"{Colors.FAIL}Your PC ran into a problem and needs to restart.{Colors.ENDC}")
                print(f"{Colors.FAIL}We're just collecting some error info, and then we'll restart for you.{Colors.ENDC}")
                print(f"{Colors.FAIL}0% complete{Colors.ENDC}")
                print(f"{Colors.FALE}Stop code: SYSTEM_THREAD_EXCEPTION_NOT_HANDLED{Colors.ENDC}")
                
                # Simulate BSOD "freeze"
                for i in range(100):
                    print(f"{Colors.FAIL}Collecting error data... {i}%{Colors.ENDC}", end='\r')
                    time.sleep(0.05)
                
                print("\n" + " " * 50)  # Clear line
                
        except:
            pass
    
    def _lock_workstation(self):
        """Lock the workstation"""
        try:
            if self.os_utils.is_windows():
                ctypes.windll.user32.LockWorkStation()
            elif self.os_utils.is_mac():
                os.system("pmset displaysleepnow")
            else:  # Linux
                os.system("gnome-screensaver-command -l")
        except:
            pass
    
    def _encrypt_protected_folders(self):
        """Encrypt files in protected folders"""
        self.logger.info("Encrypting protected folders")
        
        try:
            # Generate encryption key if not exists
            if self.encryption_key is None:
                self.encryption_key = Fernet.generate_key()
                self.cipher = Fernet(self.encryption_key)
                
                # Save key securely
                self._save_encryption_key()
            
            # Encrypt files
            encrypted_count = 0
            for folder in self.protected_folders:
                if folder.exists():
                    for file_path in folder.rglob("*"):
                        if file_path.is_file() and file_path.suffix not in ['.encrypted', '.key']:
                            try:
                                self._encrypt_file(file_path)
                                encrypted_count += 1
                            except Exception as e:
                                self.logger.error(f"Failed to encrypt {file_path}: {e}")
            
            self.logger.info(f"Encrypted {encrypted_count} files")
            
        except Exception as e:
            self.logger.error(f"Folder encryption failed: {e}")
    
    def _encrypt_file(self, file_path: Path):
        """Encrypt a single file"""
        try:
            # Read file
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Encrypt
            if self.cipher:
                encrypted_data = self.cipher.encrypt(data)
                
                # Write encrypted file
                encrypted_path = file_path.with_suffix(file_path.suffix + '.encrypted')
                with open(encrypted_path, 'wb') as f:
                    f.write(encrypted_data)
                
                # Remove original
                file_path.unlink()
                
                self.logger.debug(f"Encrypted: {file_path} → {encrypted_path}")
        
        except Exception as e:
            self.logger.error(f"File encryption error for {file_path}: {e}")
            raise
    
    def _save_encryption_key(self):
        """Save encryption key securely"""
        try:
            key_dir = Path("data/encrypted/keys")
            key_dir.mkdir(parents=True, exist_ok=True)
            
            # Save key
            key_file = key_dir / "master.key"
            with open(key_file, 'wb') as f:
                f.write(self.encryption_key)
            
            # Set restrictive permissions
            if self.os_utils.is_windows():
                os.system(f'icacls "{key_file}" /deny Everyone:(R,W)')
            
            self.logger.info(f"Encryption key saved to {key_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save encryption key: {e}")
    
    def _log_security_event(self, message: str):
        """Log a security event"""
        try:
            log_file = Path("data/logs/security.log")
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{self.current_level.name}] {message}\n"
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            self.logger.info(f"Security event: {message}")
            
        except Exception as e:
            self.logger.error(f"Failed to log security event: {e}")
    
    def _show_shutdown_warning(self):
        """Show shutdown warning to user"""
        try:
            # Create a simple popup (could use tkinter for better UI)
            warning_msg = """
            ⚠️  EMERGENCY SHUTDOWN INITIATED ⚠️
            
            This computer will shut down in 5 seconds.
            
            All unsaved work will be lost.
            
            This is a security measure.
            """
            
            print(f"\n{Colors.FAIL}{'='*60}{Colors.ENDC}")
            print(f"{Colors.FAIL}{warning_msg}{Colors.ENDC}")
            print(f"{Colors.FAIL}{'='*60}{Colors.ENDC}")
            
        except:
            pass

# Helper functions (simplified implementations)
    def _disable_usb_ports(self):
        """Disable USB ports on Windows"""
        if self.os_utils.is_windows():
            try:
                # Disable USB storage via registry
                reg_cmd = '''reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\USBSTOR" /v "Start" /t REG_DWORD /d 4 /f'''
                subprocess.run(reg_cmd, shell=True, capture_output=True)
                self.logger.info("USB ports disabled")
            except:
                pass
    
    def _hide_sensitive_files(self):
        """Hide sensitive files"""
        try:
            sensitive_extensions = ['.txt', '.doc', '.docx', '.pdf', '.xlsx', '.pptx']
            
            for folder in self.protected_folders:
                if folder.exists():
                    for file_path in folder.rglob("*"):
                        if file_path.suffix.lower() in sensitive_extensions:
                            # Hide file
                            if self.os_utils.is_windows():
                                subprocess.run(f'attrib +h "{file_path}"', shell=True)
            
            self.logger.info("Hidden sensitive files")
        except Exception as e:
            self.logger.error(f"Failed to hide files: {e}")

# Test function
def test_security():
    """Test the security system"""
    import sys
    from pathlib import Path
    
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Security System...")
    print("="*60)
    
    security = SecurityMonitor()
    
    print("\n1. Testing Level 1 (Normal)...")
    if security.set_security_level(1):
        print(f"{Colors.GREEN}✓ Level 1 activated{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}✗ Failed to activate Level 1{Colors.ENDC}")
    
    time.sleep(2)
    
    print("\n2. Testing Level 2 (Restricted)...")
    if security.set_security_level(2):
        print(f"{Colors.GREEN}✓ Level 2 activated{Colors.ENDC}")
        print("Monitoring sensitive activities...")
    else:
        print(f"{Colors.FAIL}✗ Failed to activate Level 2{Colors.ENDC}")
    
    time.sleep(3)
    
    print("\n3. Testing Level 3 (Lockdown)...")
    confirm = input(f"{Colors.YELLOW}WARNING: This will encrypt files. Continue? (y/n): {Colors.ENDC}")
    
    if confirm.lower() == 'y':
        if security.set_security_level(3):
            print(f"{Colors.GREEN}✓ Level 3 activated{Colors.ENDC}")
            print("System locked down. Files encrypted.")
        else:
            print(f"{Colors.FAIL}✗ Failed to activate Level 3{Colors.ENDC}")
    
    time.sleep(2)
    
    print("\n4. Testing emergency shutdown...")
    confirm = input(f"{Colors.YELLOW}Test emergency shutdown? (y/n): {Colors.ENDC}")
    
    if confirm.lower() == 'y':
        print(f"{Colors.FAIL}Shutting down in 3 seconds...{Colors.ENDC}")
        time.sleep(3)
        # security.emergency_shutdown()  # Uncomment to actually test
    
    print("\n" + "="*60)
    print("Security test complete.")
    
    # Clean up - return to normal
    security.set_security_level(1)
    security.stop_monitoring()

if __name__ == "__main__":
    test_security()