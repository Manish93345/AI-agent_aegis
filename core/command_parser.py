"""
Enhanced Command Parser for LISA with LLM Integration
Better natural language understanding and command routing
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from pathlib import Path

# Import from llm_wrapper
try:
    from core.llm_wrapper import get_llm_instance
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("Warning: LLM not available, using rule-based only")


class CommandParser:
    """Parses and routes voice commands with LLM enhancement"""
    
    def __init__(self):
        self.logger = logging.getLogger("LISA.CommandParser")
        
        # Initialize LLM if available
        if LLM_AVAILABLE:
            try:
                self.llm = get_llm_instance()
                self.llm_enabled = True
                self.logger.info("LLM integration enabled")
            except Exception as e:
                self.logger.warning(f"LLM initialization failed: {e}")
                self.llm_enabled = False
        else:
            self.llm_enabled = False
            self.logger.info("LLM not available, using rule-based only")
        
        self.command_patterns = self._load_patterns()
        
        # Load command mappings from config
        self.command_mappings = self._load_command_mappings()
    
    def _load_patterns(self) -> Dict[str, List[Tuple[str, str]]]:
        """Load command patterns and their handlers"""
        return {
            "greeting": [
                (r"(hello|hi|hey)\s*lisa", "greeting"),
                (r"good\s*morning", "greeting"),
                (r"good\s*evening", "greeting"),
                (r"wake\s*up", "greeting"),
            ],
            "farewell": [
                (r"(good\s*bye|bye|exit|quit|stop|shut\s*down)", "farewell"),
                (r"see\s*you", "farewell"),
                (r"go\s*to\s*sleep", "farewell"),
                (r"rest\s*now", "farewell"),
            ],
            "time_date": [
                (r"what('?s| is) the time", "time"),
                (r"current time", "time"),
                (r"what('?s| is) the date", "date"),
                (r"today('?s)? date", "date"),
                (r"day\s*and\s*time", "time_date"),
            ],
            "identity": [
                (r"who\s*(are|r)\s*you", "who_are_you"),
                (r"what('?s| is) your name", "your_name"),
                (r"what('?s| is) my name", "my_name"),
                (r"tell\s*me\s*about\s*yourself", "who_are_you"),
                (r"introduce\s*yourself", "who_are_you"),
                (r"are\s*you\s*ai", "ai_identity"),
                (r"are\s*you\s*real", "ai_identity"),
            ],
            "system": [
                (r"shut\s*down\s*(laptop|computer)", "shutdown"),
                (r"restart\s*(laptop|computer)", "restart"),
                (r"lock\s*(computer|laptop)", "lock"),
                (r"sleep\s*mode", "sleep"),
                (r"log\s*out", "logout"),
            ],
            "applications": [
                (r"open\s+(microsoft\s+)?word", "open_word"),
                (r"open\s+(google\s+)?chrome", "open_chrome"),
                (r"open\s+(firefox|mozilla)", "open_firefox"),
                (r"open\s+notepad", "open_notepad"),
                (r"open\s+calculator", "open_calculator"),
                (r"open\s+(vs\s*)?code", "open_vscode"),
                (r"open\s+(file\s+)?explorer", "open_explorer"),
                (r"open\s+(command\s+)?prompt", "open_cmd"),
                (r"open\s+cmd", "open_cmd"),
                (r"open\s+terminal", "open_terminal"),
                (r"open\s+powershell", "open_powershell"),
                (r"open\s+spotify", "open_spotify"),
                (r"open\s+youtube", "open_youtube"),
                (r"close\s+(\w+)", "close_app"),
            ],
            "routines": [
                (r"study\s+cyber", "study_cyber"),
                (r"cyber\s+mode", "study_cyber"),
                (r"work\s+mode", "work_mode"),
                (r"start\s+working", "work_mode"),
                (r"entertainment\s+mode", "entertainment_mode"),
                (r"relax\s+mode", "relax_mode"),
            ],
            "help": [
                (r"what\s+can\s+you\s+do", "help"),
                (r"help\s+me", "help"),
                (r"list\s+commands", "help"),
                (r"show\s+commands", "help"),
                (r"how\s+to\s+use", "help"),
                (r"capabilities", "help"),
            ],
            "media": [
                (r"play\s+music", "play_music"),
                (r"stop\s+music", "stop_music"),
                (r"volume\s+(up|down)", "volume_control"),
                (r"mute", "mute"),
                (r"unmute", "unmute"),
            ],
            "search": [
                (r"search\s+for\s+(.+)", "search_web"),
                (r"google\s+(.+)", "search_web"),
                (r"find\s+(.+)", "search_web"),
                (r"look\s+up\s+(.+)", "search_web"),
            ],
            "files": [
                (r"create\s+file\s+(.+)", "create_file"),
                (r"open\s+file\s+(.+)", "open_file"),
                (r"save\s+file", "save_file"),
                (r"delete\s+file\s+(.+)", "delete_file"),
            ],
            "security": [
                (r"security\s+level\s+1", "security_level_1"),
                (r"security\s+level\s+2", "security_level_2"),
                (r"security\s+level\s+3", "security_level_3"),
                (r"lockdown\s+mode", "security_level_3"),
                (r"panic\s+mode", "panic_mode"),
                (r"emergency\s+shutdown", "emergency_shutdown"),
                (r"shutdown\s+laptop", "emergency_shutdown"),
            ]
        }
    
    def _load_command_mappings(self) -> Dict:
        """Load command mappings from config or use defaults"""
        # Default mappings
        mappings = {
            "open_word": {"action": "open_app", "params": {"app": "WINWORD"}},
            "open_chrome": {"action": "open_app", "params": {"app": "chrome"}},
            "open_firefox": {"action": "open_app", "params": {"app": "firefox"}},
            "open_notepad": {"action": "open_app", "params": {"app": "notepad"}},
            "open_calculator": {"action": "open_app", "params": {"app": "calculator"}},
            "open_vscode": {"action": "open_app", "params": {"app": "code"}},
            "open_explorer": {"action": "open_app", "params": {"app": "explorer"}},
            "open_cmd": {"action": "open_app", "params": {"app": "cmd"}},
            "open_terminal": {"action": "open_app", "params": {"app": "wt"}},
            "open_powershell": {"action": "open_app", "params": {"app": "powershell"}},
            "close_app": {"action": "close_app", "params": {}},
            "play_music": {"action": "play_music", "params": {}},
            "search_web": {"action": "search_web", "params": {}},
            "create_file": {"action": "create_file", "params": {}},
            "system_info": {"action": "system_info", "params": {}},
        }
        
        # Try to load from file
        try:
            from utils.file_utils import FileUtils
            import json
            
            mappings_file = Path("config/command_mappings.json")
            if mappings_file.exists():
                file_mappings = FileUtils.load_json(mappings_file)
                if file_mappings:
                    mappings.update(file_mappings)
        except Exception as e:
            self.logger.warning(f"Could not load command mappings: {e}")
        
        return mappings
    
    def parse_command(self, command_text: str, use_llm: bool = True) -> Dict:
        """
        Parse a voice command and identify its type
        Args:
            command_text: The command to parse
            use_llm: Whether to use LLM for complex parsing
        """
        command_text = command_text.lower().strip()
        self.logger.debug(f"Parsing command: '{command_text}'")
        
        # First try rule-based parsing (fast)
        rule_result = self._parse_with_rules(command_text)
        
        # If rule-based parsing gives high confidence, use it
        if rule_result and rule_result.get("confidence", 0) >= 0.8:
            return rule_result
        
        # For complex commands or low confidence, use LLM if available
        if use_llm and self.llm_enabled:
            llm_result = self._parse_with_llm(command_text)
            if llm_result:
                return llm_result
        
        # Fallback to rule-based result
        if rule_result:
            return rule_result
        
        # Unknown command
        return {
            "original": command_text,
            "type": "unknown",
            "action": "unknown",
            "parameters": {},
            "confidence": 0.0,
            "method": "fallback"
        }
    
    def _parse_with_rules(self, command_text: str) -> Optional[Dict]:
        """Parse using rule patterns"""
        best_match = None
        best_confidence = 0
        
        for category, patterns in self.command_patterns.items():
            for pattern, action in patterns:
                match = re.search(pattern, command_text, re.IGNORECASE)
                if match:
                    confidence = 0.9  # High confidence for pattern match
                    
                    # Extract parameters
                    params = {}
                    if category == "applications" and "open" in command_text:
                        # Extract app name from pattern
                        app_match = re.search(r"open\s+(\w+)", command_text)
                        if app_match:
                            params["app_name"] = app_match.group(1)
                    
                    elif category == "search" and match.groups():
                        params["query"] = match.group(1)
                    
                    elif category == "files" and match.groups():
                        params["filename"] = match.group(1)
                    
                    if confidence > best_confidence:
                        best_match = {
                            "original": command_text,
                            "type": category,
                            "action": action,
                            "parameters": params,
                            "confidence": confidence,
                            "method": "rules"
                        }
                        best_confidence = confidence
        
        return best_match
    
    def _parse_with_llm(self, command_text: str) -> Optional[Dict]:
        """Parse using LLM for complex understanding"""
        if not self.llm_enabled:
            return None
        
        try:
            # Get context for LLM
            context = {
                "time": datetime.now().strftime("%H:%M"),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "available_actions": list(self.command_mappings.keys())
            }
            
            # Get LLM response
            llm_response = self.llm.generate_response(command_text, context)
            
            # Try to parse as JSON command
            try:
                if llm_response.strip().startswith("{"):
                    parsed = json.loads(llm_response)
                    
                    if parsed.get("type") == "command":
                        return {
                            "original": command_text,
                            "type": "command",
                            "action": parsed.get("action"),
                            "parameters": parsed.get("parameters", {}),
                            "spoken_response": parsed.get("spoken_response", ""),
                            "confidence": 0.85,
                            "method": "llm"
                        }
            except json.JSONDecodeError:
                pass
            
            # If not JSON, treat as conversational response
            return {
                "original": command_text,
                "type": "conversation",
                "action": "respond",
                "response": llm_response,
                "confidence": 0.8,
                "method": "llm"
            }
            
        except Exception as e:
            self.logger.error(f"LLM parsing failed: {e}")
            return None
    
    def get_response(self, parsed_command: Dict) -> str:
        """Get appropriate response for a parsed command"""
        action = parsed_command.get("action")
        method = parsed_command.get("method", "")
        
        # If LLM already provided a spoken response, use it
        if method == "llm" and parsed_command.get("spoken_response"):
            return parsed_command["spoken_response"]
        
        # Use LLM for conversational responses
        if method == "llm" and parsed_command.get("response"):
            return parsed_command["response"]
        
        # Standard responses
        responses = {
            "greeting": [
                "Hello! I'm Lisa, your personal assistant. How can I help you today?",
                "Hi there! It's good to hear from you. What would you like me to do?",
                "Yes, I'm listening. How can I assist you today?"
            ],
            "farewell": [
                "Goodbye! Shutting down now.",
                "See you later! Have a great day!",
                "Going to sleep now. Just say 'Hey Lisa' whenever you need me."
            ],
            "who_are_you": [
                "I am Lisa, your personal AI assistant. I'm here to help you with tasks on your computer, answer questions, and make your day easier.",
                "My name is Lisa! I'm your intelligent assistant that can control applications, manage files, search the web, and help with your daily routines.",
                "I'm Lisa, your Learning Intelligent System Assistant. I can automate tasks, answer questions, and provide assistance with your computer."
            ],
            "your_name": [
                "My name is Lisa. It's nice to meet you!",
                "You can call me Lisa. That's short for Learning Intelligent System Assistant.",
                "I'm Lisa, your personal assistant! Ready to help."
            ],
            "my_name": [
                "You haven't told me your name yet! I'd love to know what to call you.",
                "I don't know your name yet. You can tell me by saying 'My name is [your name]'.",
                "You can set your name in the user preferences if you'd like me to remember it!"
            ],
            "ai_identity": [
                "Yes, I'm an AI assistant created to help you. But I like to think I'm a helpful friend too!",
                "I'm an artificial intelligence, but I'm here to provide real help with your tasks and questions."
            ],
            "time": "The current time is {time}.",
            "date": "Today is {date}.",
            "help": "I can help you with: opening apps, telling time, managing files, searching the web, controlling music, study routines, answering questions, and system control. Try saying 'study cyber' or 'open chrome'!",
            "study_cyber": "Starting study cyber routine. Opening your study materials...",
            "open_app": "Opening {app} for you...",
            "play_music": "Playing some music for you...",
            "search_web": "Searching for {query}...",
            "create_file": "Creating file {filename}...",
            "system_info": "Getting system information...",
            "unknown": "I'm not quite sure how to help with that. You can say 'what can you do' for a list of commands, or try rephrasing your request."
        }
        
        import random
        if action in responses:
            if isinstance(responses[action], list):
                return random.choice(responses[action])
            
            # Format with parameters if needed
            response = responses[action]
            params = parsed_command.get("parameters", {})
            
            # Replace placeholders
            for key, value in params.items():
                placeholder = "{" + key + "}"
                if placeholder in response:
                    response = response.replace(placeholder, str(value))
            
            return response
        
        return responses["unknown"]
    
    def get_command_execution(self, parsed_command: Dict) -> Optional[Dict]:
        """Get execution details for a parsed command"""
        action = parsed_command.get("action")
        
        if action in self.command_mappings:
            mapping = self.command_mappings[action]
            params = {**mapping.get("params", {}), **parsed_command.get("parameters", {})}
            
            return {
                "action": mapping["action"],
                "parameters": params,
                "requires_confirmation": mapping.get("requires_confirmation", False)
            }
        
        return None