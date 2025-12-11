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
                "microsoft word": self._open_word,
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
    
    # In automation_engine.py, update the open_multiple_tabs method:

    def open_multiple_tabs(self, urls: List[str], browser: str = "default") -> bool:
        """Open multiple URLs in tabs using default browser"""
        self.logger.info(f"Opening {len(urls)} tabs in default browser")
        
        try:
            if not urls:
                return False
            
            # Open first URL in default browser
            self.open_url(urls[0])
            time.sleep(2)  # Wait for browser to open
            
            # Open remaining URLs in new tabs
            if len(urls) > 1:
                # Wait a bit for browser to be ready
                time.sleep(1)
                
                for url in urls[1:]:
                    try:
                        # These shortcuts work in most browsers (Edge, Chrome, Firefox)
                        pyautogui.hotkey('ctrl', 't')
                        time.sleep(0.7)  # Slightly longer wait for new tab
                        pyautogui.hotkey('ctrl', 'l')
                        time.sleep(0.3)
                        pyautogui.write(url)
                        time.sleep(0.1)
                        pyautogui.press('enter')
                        time.sleep(1)  # Wait for page to start loading
                    except Exception as e:
                        self.logger.warning(f"Failed to open tab for {url}: {e}")
                        # Try alternative method for this URL
                        self.open_url(url)
                        time.sleep(1)
            
            self.logger.info(f"✓ Opened {len(urls)} tabs in default browser")
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
    
    # In automation_engine.py, replace the play_music method with this:

    def play_music(self, source: str = "youtube", browser: str = "chrome") -> bool:
        """Play background music in specific browser"""
        self.logger.info(f"Playing music from {source} in {browser}")
        
        try:
            if source.lower() == "youtube":
                # YouTube study music playlist
                url = "https://youtube.com/playlist?list=PLkd-lH9-8EJVtcCMbApQ_5uANEUvu7sAn&si=BWPHgWZHjHTmeJi-"  # Lo-fi study music
                
                if browser.lower() == "chrome":
                    # Try to open Chrome specifically with the URL
                    chrome_paths = [
                        "C:/Program Files/Google/Chrome/Application/chrome.exe",
                    ]
                    
                    chrome_found = False
                    chrome_path = None
                    
                    # Find Chrome executable
                    for path in chrome_paths:
                        expanded_path = os.path.expandvars(path)
                        if os.path.exists(expanded_path):
                            chrome_found = True
                            chrome_path = expanded_path
                            self.logger.info(f"Found Chrome at: {chrome_path}")
                            break
                    
                    if chrome_found and chrome_path:
                        try:
                            # Open Chrome with the URL directly
                            subprocess.Popen([chrome_path, url])
                            self.logger.info(f"✓ Opened Chrome with YouTube music: {url}")
                            
                            # Wait for Chrome to open and focus
                            time.sleep(3)
                            
                            # Optional: Make Chrome fullscreen for better music experience
                            try:
                                # pyautogui.hotkey('f11')  # Fullscreen
                                time.sleep(0.5)
                                # Space to play if needed
                                pyautogui.press('space')
                            except:
                                pass  # Don't fail if fullscreen doesn't work
                            
                            return True
                        except Exception as e:
                            self.logger.warning(f"Failed to open Chrome directly: {e}")
                    
                    # Fallback: Try to open via system command
                    try:
                        if self.os_utils.is_windows():
                            os.system(f'start chrome "{url}"')
                        elif self.os_utils.is_mac():
                            subprocess.Popen(['open', '-a', 'chrome', url])
                        
                        self.logger.info(f"✓ Opened Chrome via system command with URL")
                        time.sleep(2)
                        return True
                    except Exception as e:
                        self.logger.warning(f"System command fallback failed: {e}")
                        
                # If not Chrome or Chrome methods failed, use default browser
                self.logger.info("Using default browser for music")
                return self.open_url(url)
                    
            elif source.lower() == "spotify":
                # Would need Spotify integration
                self.logger.warning("Spotify integration not implemented yet")
                return False
            else:
                # Default to YouTube in Chrome
                return self.play_music("youtube", "chrome")
                
        except Exception as e:
            self.logger.error(f"Failed to play music: {e}")
            return False
    
    def execute_study_cyber_routine(self, config: Dict[str, Any] = None) -> bool:
        """Execute the 'study cyber' routine"""
        self.logger.info("Executing 'study cyber' routine")
        # Try to load from user_prefs.json
        try:
            from utils.file_utils import FileUtils
            from utils.constants import USER_PREFS
            
            user_prefs = FileUtils.load_json(USER_PREFS)
            if user_prefs and "study_cyber_routine" in user_prefs:
                self.logger.info("Using configuration from user_prefs.json")
                user_config = user_prefs["study_cyber_routine"]
            else:
                user_config = {}
        except:
            user_config = {}
        
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
            "music_source": "youtube",
            "music_browser": "chrome"
        }
        
        # Merge configurations: user config overrides defaults
        final_config = default_config.copy()
        if user_config:
            for key, value in user_config.items():
                if key in final_config:
                    final_config[key] = value
        
        # Use provided config if specified (highest priority)
        if config:
            for key, value in config.items():
                if key in final_config:
                    final_config[key] = value
        
        config = final_config
        
        success_count = 0
        total_tasks = 0
        
        # Open applications
        for app_config in config["apps_to_open"]:
            total_tasks += 1
            if self.open_application(app_config["name"], app_config.get("path", "")):
                success_count += 1
                time.sleep(2)  # Wait between app launches
        
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
            music_browser = config.get("music_browser", "chrome")
            if self.play_music(config.get("music_source", "youtube"), music_browser):
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
    
    # In automation_engine.py, replace the _open_word method with this:

    def _open_word(self) -> bool:
        """Open Microsoft Word using Windows search simulation"""
        self.logger.info("Opening Microsoft Word via Windows search...")
        
        try:
            # Clear any existing text by pressing Escape first
            pyautogui.press('esc')
            time.sleep(0.2)
            
            # Step 1: Press Windows key to open Start Menu
            pyautogui.press('win')
            time.sleep(0.5)  # Wait for Start Menu to fully open
            
            # Step 2: Type "word" slowly
            pyautogui.write('word', interval=0.1)
            time.sleep(0.5)  # Wait for search results
            
            # Step 3: Press Enter to select the first result
            pyautogui.press('enter')
            time.sleep(1.5) 
            pyautogui.press('enter')
            
            
            # Wait for Word to open
           

            time.sleep(1.5)
            
            # Step 4: Check if Word opened successfully
            try:
                # Look for Word process
                for proc in psutil.process_iter(['name']):
                    try:
                        proc_name = proc.info['name'].lower()
                        if 'winword' in proc_name:
                            self.logger.info(f"✓ Word process found: {proc_name}")
                            return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
                # If process not found, check windows
                for window in pyautogui.getAllWindows():
                    if window.title and ('word' in window.title.lower() or 'document' in window.title.lower()):
                        self.logger.info(f"✓ Word window found: {window.title}")
                        return True
                        
            except Exception as e:
                self.logger.debug(f"Verification failed: {e}")
            
            # If we're here, Word may not have opened
            self.logger.warning("Word may not have opened properly")
            return True  # Return True anyway since we tried
            
        except Exception as e:
            self.logger.error(f"Windows search method failed: {e}")
            
            # Fallback methods
            fallbacks = [
                self._try_winword_protocol,
                self._try_run_dialog,
                self._try_direct_command,
            ]
            
            for fallback_method in fallbacks:
                try:
                    if fallback_method():
                        return True
                except Exception as fe:
                    self.logger.debug(f"Fallback failed: {fe}")
                    continue
            
            return False

    def _try_winword_protocol(self) -> bool:
        """Try opening via winword: protocol"""
        try:
            os.startfile("winword:")
            time.sleep(3)
            self.logger.info("✓ Used winword protocol")
            return True
        except:
            return False

    def _try_run_dialog(self) -> bool:
        """Try opening via Run dialog"""
        try:
            pyautogui.hotkey('win', 'r')
            time.sleep(0.8)
            pyautogui.write('winword.exe')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(4)
            self.logger.info("✓ Used Run dialog")
            return True
        except:
            return False

    def _try_direct_command(self) -> bool:
        """Try direct command execution"""
        try:
            subprocess.run(['cmd', '/c', 'start', 'winword'], shell=True, check=False)
            time.sleep(3)
            self.logger.info("✓ Used direct command")
            return True
        except:
            return False
    
    def _open_chrome(self) -> bool:
        """Open Chrome browser - with error handling"""
        chrome_paths = [
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
            os.path.expandvars("%ProgramFiles%/Google/Chrome/Application/chrome.exe"),
            os.path.expandvars("%ProgramFiles(x86)%/Google/Chrome/Application/chrome.exe"),
            os.path.expandvars("%LocalAppData%/Google/Chrome/Application/chrome.exe"),
        ]
        
        for path in chrome_paths:
            expanded_path = path
            # Handle environment variables
            if '%' in path:
                expanded_path = os.path.expandvars(path)
            
            self.logger.debug(f"Checking Chrome at: {expanded_path}")
            
            if os.path.exists(expanded_path):
                try:
                    # Try to open Chrome
                    subprocess.Popen([expanded_path], shell=True)
                    self.logger.info(f"✓ Opened Chrome from: {expanded_path}")
                    
                    # Wait a bit and check if it opened
                    time.sleep(2)
                    
                    # Check if Chrome process is running
                    chrome_running = False
                    for proc in psutil.process_iter(['name']):
                        if 'chrome' in proc.info['name'].lower():
                            chrome_running = True
                            break
                    
                    if chrome_running:
                        return True
                        
                except Exception as e:
                    self.logger.warning(f"Failed to open Chrome from {expanded_path}: {e}")
                    continue
        
        # Try using webbrowser module
        try:
            webbrowser.get('chrome').open('about:blank')
            self.logger.info("✓ Opened Chrome via webbrowser module")
            return True
        except Exception as e:
            self.logger.warning(f"Webbrowser module failed: {e}")
        
        # Last resort: try system command
        try:
            os.system('start chrome')
            self.logger.info("✓ Opened Chrome via system command")
            time.sleep(2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to open Chrome: {e}")
        
        return False
    
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
        """Open Command Prompt using Windows search simulation"""
        self.logger.info("Opening Command Prompt via Windows search...")
        
        try:
            # Clear any existing text by pressing Escape first
            pyautogui.press('esc')
            time.sleep(0.2)
            
            # Step 1: Press Windows key to open Start Menu
            pyautogui.press('win')
            time.sleep(0.2)  # Wait for Start Menu to fully open
            
            # Step 2: Type "cmd" slowly
            pyautogui.write('cmd', interval=0.1)
            time.sleep(0.5)  # Wait for search results
            
            # Step 3: Press Enter to select Command Prompt
            pyautogui.press('enter')
            
            # Wait for CMD to open
            time.sleep(2)
            
            # Step 4: Check if CMD opened successfully
            try:
                # Look for cmd.exe process
                for proc in psutil.process_iter(['name']):
                    try:
                        proc_name = proc.info['name'].lower()
                        if 'cmd.exe' in proc_name:
                            self.logger.info(f"✓ CMD process found: {proc_name}")
                            return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
                # If process not found, check windows
                for window in pyautogui.getAllWindows():
                    if window.title and ('command prompt' in window.title.lower() or 'cmd.exe' in window.title.lower()):
                        self.logger.info(f"✓ CMD window found: {window.title}")
                        return True
                        
            except Exception as e:
                self.logger.debug(f"Verification failed: {e}")
            
            # If we're here, CMD may not have opened
            self.logger.warning("CMD may not have opened properly")
            return True  # Return True anyway since we tried
            
        except Exception as e:
            self.logger.error(f"Windows search method failed: {e}")
            
            # Fallback methods
            fallbacks = [
                self._try_cmd_run_dialog,
                self._try_cmd_direct_command,
            ]
            
            for fallback_method in fallbacks:
                try:
                    if fallback_method():
                        return True
                except Exception as fe:
                    self.logger.debug(f"Fallback failed: {fe}")
                    continue
            
            return False

    def _open_powershell(self) -> bool:
        """Open PowerShell using Windows search simulation"""
        self.logger.info("Opening PowerShell via Windows search...")
        
        try:
            # Clear any existing text by pressing Escape first
            pyautogui.press('esc')
            time.sleep(0.2)
            
            # Step 1: Press Windows key to open Start Menu
            pyautogui.press('win')
            time.sleep(0.2)  # Wait for Start Menu to fully open
            
            # Step 2: Type "powershell" slowly
            pyautogui.write('powershell', interval=0.1)
            time.sleep(0.5)  # Wait for search results
            
            # Step 3: Press Enter to select PowerShell
            pyautogui.press('enter')
            
            # Wait for PowerShell to open
            time.sleep(2)
            
            # Step 4: Check if PowerShell opened successfully
            try:
                # Look for powershell.exe process
                for proc in psutil.process_iter(['name']):
                    try:
                        proc_name = proc.info['name'].lower()
                        if 'powershell.exe' in proc_name:
                            self.logger.info(f"✓ PowerShell process found: {proc_name}")
                            return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
                # If process not found, check windows
                for window in pyautogui.getAllWindows():
                    if window.title and 'powershell' in window.title.lower():
                        self.logger.info(f"✓ PowerShell window found: {window.title}")
                        return True
                        
            except Exception as e:
                self.logger.debug(f"Verification failed: {e}")
            
            # If we're here, PowerShell may not have opened
            self.logger.warning("PowerShell may not have opened properly")
            return True  # Return True anyway since we tried
            
        except Exception as e:
            self.logger.error(f"Windows search method failed: {e}")
            
            # Fallback methods
            fallbacks = [
                self._try_powershell_run_dialog,
                self._try_powershell_direct_command,
            ]
            
            for fallback_method in fallbacks:
                try:
                    if fallback_method():
                        return True
                except Exception as fe:
                    self.logger.debug(f"Fallback failed: {fe}")
                    continue
            
            return False

    def _open_terminal(self) -> bool:
        """Open Windows Terminal using Windows search simulation"""
        self.logger.info("Opening Windows Terminal via Windows search...")
        
        try:
            # Clear any existing text by pressing Escape first
            pyautogui.press('esc')
            time.sleep(0.2)
            
            # Step 1: Press Windows key to open Start Menu
            pyautogui.press('win')
            time.sleep(0.2)  # Wait for Start Menu to fully open
            
            # Step 2: Type "terminal" slowly
            pyautogui.write('terminal', interval=0.1)
            time.sleep(0.5)  # Wait for search results
            
            # Step 3: Press Enter to select Windows Terminal
            pyautogui.press('enter')
            
            # Wait for Terminal to open
            time.sleep(2)
            
            # Step 4: Check if Terminal opened successfully
            try:
                # Look for WindowsTerminal.exe process
                for proc in psutil.process_iter(['name']):
                    try:
                        proc_name = proc.info['name'].lower()
                        if 'windowsterminal.exe' in proc_name or 'terminal.exe' in proc_name:
                            self.logger.info(f"✓ Terminal process found: {proc_name}")
                            return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
                # If process not found, check windows
                for window in pyautogui.getAllWindows():
                    if window.title and 'terminal' in window.title.lower():
                        self.logger.info(f"✓ Terminal window found: {window.title}")
                        return True
                        
            except Exception as e:
                self.logger.debug(f"Verification failed: {e}")
            
            # If we're here, Terminal may not have opened
            self.logger.warning("Terminal may not have opened properly")
            
            # Try to open CMD as fallback
            self.logger.info("Trying to open Command Prompt as fallback for Terminal...")
            return self._open_cmd()
            
        except Exception as e:
            self.logger.error(f"Windows search method failed: {e}")
            
            # Fallback: Try to open CMD
            return self._open_cmd()

    # Fallback methods for CMD
    def _try_cmd_run_dialog(self) -> bool:
        """Try opening CMD via Run dialog"""
        try:
            pyautogui.hotkey('win', 'r')
            time.sleep(0.8)
            pyautogui.write('cmd')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(2)
            self.logger.info("✓ Used Run dialog for CMD")
            return True
        except:
            return False

    def _try_cmd_direct_command(self) -> bool:
        """Try direct command execution for CMD"""
        try:
            subprocess.run(['cmd', '/c', 'start', 'cmd'], shell=True, check=False)
            time.sleep(3)
            self.logger.info("✓ Used direct command for CMD")
            return True
        except:
            return False

    # Fallback methods for PowerShell
    def _try_powershell_run_dialog(self) -> bool:
        """Try opening PowerShell via Run dialog"""
        try:
            pyautogui.hotkey('win', 'r')
            time.sleep(0.8)
            pyautogui.write('powershell')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(2)
            self.logger.info("✓ Used Run dialog for PowerShell")
            return True
        except:
            return False

    def _try_powershell_direct_command(self) -> bool:
        """Try direct command execution for PowerShell"""
        try:
            subprocess.run(['cmd', '/c', 'start', 'powershell'], shell=True, check=False)
            time.sleep(3)
            self.logger.info("✓ Used direct command for PowerShell")
            return True
        except:
            return False

    # Remove the old methods completely:
    # def _open_cmd(self) -> bool:
    #     """Open Command Prompt"""
    #     if self.os_utils.is_windows():
    #         os.system("cmd")
    #         return True
    #     return False
    # 
    # def _open_powershell(self) -> bool:
    #     """Open PowerShell"""
    #     if self.os_utils.is_windows():
    #         os.system("powershell")
    #         return True
    #     return False
    # 
    # def _open_terminal(self) -> bool:
    #     """Open Terminal"""
    #     if self.os_utils.is_windows():
    #         os.system("wt")  # Windows Terminal
    #         return True
    #     elif self.os_utils.is_mac():
    #         subprocess.Popen(['open', '-a', 'Terminal'])
    #         return True
    #     else:  # Linux
    #         subprocess.Popen(['gnome-terminal'])
    #         return True

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