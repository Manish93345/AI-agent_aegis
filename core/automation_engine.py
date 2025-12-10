"""
Automation Engine for LISA
Handles application launching, browser control, file operations, and routines
"""

import os
import sys
import subprocess
import webbrowser
import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass

import pyautogui
import psutil

from utils.constants import Colors
from utils.os_utils import OSUtils

@dataclass
class AppConfig:
    """Application configuration"""
    name: str
    path: str
    args: List[str] = None
    wait_seconds: int = 2

@dataclass  
class BrowserTab:
    """Browser tab configuration"""
    title: str
    url: str
    new_tab: bool = True

class AutomationEngine:
    """Handles all automation tasks"""
    
    def __init__(self):
        self.logger = logging.getLogger("LISA.Automation")
        self.os_utils = OSUtils()
        self.running_processes = []
        
    def open_application(self, app_name: str, app_path: str = None) -> bool:
        """Open an application by name or path"""
        self.logger.info(f"Opening application: {app_name}")
        
        try:
            # If path is provided, use it
            if app_path and os.path.exists(app_path):
                self.logger.debug(f"Using provided path: {app_path}")
                if self.os_utils.is_windows():
                    os.startfile(app_path)
                else:
                    subprocess.Popen([app_path])
                return True
            
            # Try common applications
            app_commands = {
                "notepad": self._open_notepad,
                "word": self._open_word,
                "chrome": self._open_chrome,
                "browser": self._open_browser,
                "calculator": self._open_calculator,
                "vscode": self._open_vscode,
                "visual studio code": self._open_vscode,
                "explorer": self._open_explorer,
                "file explorer": self._open_explorer,
                "cmd": self._open_cmd,
                "command prompt": self._open_cmd,
                "powershell": self._open_powershell,
                "terminal": self._open_terminal,
            }
            
            app_name_lower = app_name.lower()
            
            # Check if we have a handler for this app
            if app_name_lower in app_commands:
                return app_commands[app_name_lower]()
            
            # Try to open by name as fallback
            return self.os_utils.open_application(app_name)
            
        except Exception as e:
            self.logger.error(f"Failed to open {app_name}: {e}")
            return False
    
    def open_url(self, url: str, browser: str = "chrome") -> bool:
        """Open a URL in browser"""
        self.logger.info(f"Opening URL: {url}")
        
        try:
            # Clean the URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Open in default browser
            webbrowser.open(url)
            
            # Wait for browser to load
            time.sleep(2)
            
            self.logger.info(f"✓ Opened URL: {url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open URL {url}: {e}")
            return False
    
    def open_multiple_tabs(self, urls: List[str], browser: str = "chrome") -> bool:
        """Open multiple URLs in tabs"""
        self.logger.info(f"Opening {len(urls)} tabs")
        
        try:
            # Open first URL in new window
            if urls:
                self.open_url(urls[0])
                time.sleep(1)
            
            # Open remaining URLs in new tabs
            for url in urls[1:]:
                # Simulate Ctrl+T for new tab and navigate
                pyautogui.hotkey('ctrl', 't')
                time.sleep(0.5)
                pyautogui.hotkey('ctrl', 'l')  # Focus address bar
                time.sleep(0.2)
                pyautogui.write(url)
                pyautogui.press('enter')
                time.sleep(1)
            
            self.logger.info(f"✓ Opened {len(urls)} tabs")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open multiple tabs: {e}")
            return False
    
    def open_folder(self, folder_path: str) -> bool:
        """Open a folder in file explorer"""
        self.logger.info(f"Opening folder: {folder_path}")
        
        try:
            # Expand user directory if needed
            folder_path = os.path.expanduser(folder_path)
            
            # Create folder if it doesn't exist
            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
                self.logger.info(f"Created folder: {folder_path}")
            
            # Open folder
            if self.os_utils.is_windows():
                os.startfile(folder_path)
            elif self.os_utils.is_mac():
                subprocess.Popen(['open', folder_path])
            else:  # Linux
                subprocess.Popen(['xdg-open', folder_path])
            
            self.logger.info(f"✓ Opened folder: {folder_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open folder {folder_path}: {e}")
            return False
    
    def play_music(self, source: str = "youtube") -> bool:
        """Play background music"""
        self.logger.info(f"Playing music from {source}")
        
        try:
            if source.lower() == "youtube":
                # Open YouTube study music
                url = "https://youtube.com/playlist?list=PLkd-lH9-8EJVtcCMbApQ_5uANEUvu7sAn&si=0yqTYbA1P1mG3tm1"  # Lo-fi study music
                return self.open_url(url)
            elif source.lower() == "spotify":
                # Would need Spotify integration
                self.logger.warning("Spotify integration not implemented yet")
                return False
            else:
                # Default to YouTube
                return self.play_music("youtube")
                
        except Exception as e:
            self.logger.error(f"Failed to play music: {e}")
            return False
    
    def execute_study_cyber_routine(self, config: Dict[str, Any] = None) -> bool:
        """Execute the 'study cyber' routine"""
        self.logger.info("Executing 'study cyber' routine")
        
        # Default configuration
        default_config = {
            "apps_to_open": [
                {"name": "Microsoft Word", "path": ""},
                # {"name": "Chrome", "path": ""},
                # {"name": "VS Code", "path": ""}
            ],
            "urls_to_open": [
                "https://chatgpt.com/",
                "https://chat.deepseek.com/"
                # "https://tryhackme.com",
                # "https://hackthebox.com",
                # "https://cybrary.it"
            ],
            "folders_to_open": [
                r"D:\CyberSecurity\CyberSecurity\Self-Study"
                
            ],
            "play_music": True,
            "music_source": "youtube"
        }
        
        # Merge with provided config
        if config:
            for key, value in config.items():
                if key in default_config:
                    default_config[key] = value
        
        config = default_config
        
        success_count = 0
        total_tasks = 0
        
        # Open applications
        for app_config in config["apps_to_open"]:
            total_tasks += 1
            if self.open_application(app_config["name"], app_config.get("path", "")):
                success_count += 1
                time.sleep(1)  # Wait between app launches
        
        # Open browser tabs
        if config["urls_to_open"]:
            total_tasks += 1
            if self.open_multiple_tabs(config["urls_to_open"]):
                success_count += 1
        
        # Open folders
        for folder_path in config["folders_to_open"]:
            total_tasks += 1
            if self.open_folder(folder_path):
                success_count += 1
                time.sleep(0.5)
        
        # Play music
        if config["play_music"]:
            total_tasks += 1
            if self.play_music(config.get("music_source", "youtube")):
                success_count += 1
        
        success_rate = (success_count / total_tasks * 100) if total_tasks > 0 else 0
        self.logger.info(f"Routine complete: {success_count}/{total_tasks} tasks successful ({success_rate:.1f}%)")
        
        return success_count > 0
    
    # Application-specific handlers
    def _open_notepad(self) -> bool:
        """Open Notepad"""
        if self.os_utils.is_windows():
            os.system("notepad")
            return True
        return False
    
    def _open_word(self) -> bool:
        """Open Microsoft Word"""
        # Common Word paths on Windows
        word_paths = [
            "C:/Program Files/Microsoft Office/root/Office16/WINWORD.EXE"
        ]
        
        for path in word_paths:
            if os.path.exists(path):
                os.startfile(path)
                return True
        
        # Try to open by name
        return self.os_utils.open_application("Word")
    
    def _open_chrome(self) -> bool:
        """Open Chrome browser"""
        chrome_paths = [
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                os.startfile(path)
                return True
        
        return self.os_utils.open_application("chrome")
    
    def _open_browser(self) -> bool:
        """Open default browser"""
        webbrowser.open("about:blank")
        return True
    
    def _open_calculator(self) -> bool:
        """Open Calculator"""
        if self.os_utils.is_windows():
            os.system("calc")
            return True
        return False
    
    def _open_vscode(self) -> bool:
        """Open Visual Studio Code"""
        vscode_paths = [
            "C:/Users/%USERNAME%/AppData/Local/Programs/Microsoft VS Code/Code.exe",
        ]
        
        for path in vscode_paths:
            if os.path.exists(path):
                os.startfile(path)
                return True
        
        return self.os_utils.open_application("code")
    
    def _open_explorer(self) -> bool:
        """Open File Explorer"""
        if self.os_utils.is_windows():
            os.system("explorer")
            return True
        return False
    
    def _open_cmd(self) -> bool:
        """Open Command Prompt"""
        if self.os_utils.is_windows():
            os.system("cmd")
            return True
        return False
    
    def _open_powershell(self) -> bool:
        """Open PowerShell"""
        if self.os_utils.is_windows():
            os.system("powershell")
            return True
        return False
    
    def _open_terminal(self) -> bool:
        """Open Terminal"""
        if self.os_utils.is_windows():
            os.system("wt")  # Windows Terminal
            return True
        elif self.os_utils.is_mac():
            subprocess.Popen(['open', '-a', 'Terminal'])
            return True
        else:  # Linux
            subprocess.Popen(['gnome-terminal'])
            return True

# Test function
def test_automation():
    """Test the automation engine"""
    import sys
    from pathlib import Path
    
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    # Basic logging
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Automation Engine...")
    print("="*60)
    
    engine = AutomationEngine()
    
    # Test opening apps
    test_apps = ["notepad", "chrome", "calculator"]
    
    for app in test_apps:
        print(f"\nOpening {app}...")
        if engine.open_application(app):
            print(f"✓ {app} opened successfully")
            time.sleep(1)
        else:
            print(f"✗ Failed to open {app}")
    
    # Test opening URL
    print("\nOpening URL...")
    if engine.open_url("https://google.com"):
        print("✓ URL opened successfully")
    else:
        print("✗ Failed to open URL")
    
    print("\n✓ Automation Engine test complete")

if __name__ == "__main__":
    test_automation()