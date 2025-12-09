"""
OS-specific utilities for Windows, macOS, Linux
"""

import os
import sys
import platform
import subprocess
import psutil
from typing import List, Tuple, Optional

class OSUtils:
    """Utility class for OS-specific operations"""
    
    @staticmethod
    def get_os_info() -> dict:
        """Get detailed OS information"""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }
    
    @staticmethod
    def is_windows() -> bool:
        return platform.system() == "Windows"
    
    @staticmethod
    def is_mac() -> bool:
        return platform.system() == "Darwin"
    
    @staticmethod
    def is_linux() -> bool:
        return platform.system() == "Linux"
    
    @staticmethod
    def open_application(app_name: str, app_path: str = None) -> bool:
        """Open an application"""
        try:
            if app_path and os.path.exists(app_path):
                if OSUtils.is_windows():
                    os.startfile(app_path)
                else:
                    subprocess.Popen([app_path])
            else:
                # Try to open by name
                if OSUtils.is_windows():
                    os.system(f'start {app_name}')
                elif OSUtils.is_mac():
                    subprocess.Popen(['open', '-a', app_name])
                else:  # Linux
                    subprocess.Popen([app_name])
            
            print(f"✓ Opened: {app_name}")
            return True
        except Exception as e:
            print(f"✗ Failed to open {app_name}: {e}")
            return False
    
    @staticmethod
    def close_application(process_name: str) -> bool:
        """Close an application by process name"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if process_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    proc.wait(timeout=5)
                    print(f"✓ Closed: {process_name}")
                    return True
            return False
        except Exception as e:
            print(f"✗ Failed to close {process_name}: {e}")
            return False
    
    @staticmethod
    def get_system_usage() -> dict:
        """Get current system resource usage"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent if OSUtils.is_linux() or OSUtils.is_mac() 
                          else psutil.disk_usage('C://').percent,
            "gpu_available": OSUtils.check_gpu_available()
        }
    
    @staticmethod
    def check_gpu_available() -> bool:
        """Check if GPU is available (RTX 3050 in your case)"""
        try:
            if OSUtils.is_windows():
                # Check for NVIDIA GPU on Windows
                result = subprocess.run(
                    ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                    capture_output=True, text=True
                )
                return 'NVIDIA' in result.stdout.upper()
            else:
                # For Linux/macOS
                result = subprocess.run(
                    ['lspci' if OSUtils.is_linux() else 'system_profiler', 'SPDisplaysDataType'],
                    capture_output=True, text=True
                )
                return 'NVIDIA' in result.stdout.upper()
        except:
            return False
    
    @staticmethod
    def run_command(command: str) -> Tuple[bool, str]:
        """Run a system command and return output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return (result.returncode == 0, result.stdout)
        except Exception as e:
            return (False, str(e))