"""
Command Parser for LISA
Better natural language understanding and command routing
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from utils.constants import Colors

class CommandParser:
    """Parses and routes voice commands"""
    
    def __init__(self):
        self.logger = logging.getLogger("LISA.CommandParser")
        self.command_patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict[str, List[Tuple[str, callable]]]:
        """Load command patterns and their handlers"""
        return {
            "greeting": [
                (r"(hello|hi|hey)\s*lisa", "greeting"),
                (r"good\s*morning", "greeting"),
                (r"good\s*evening", "greeting"),
            ],
            "farewell": [
                (r"(good\s*bye|bye|exit|quit|stop|shut\s*down)", "farewell"),
                (r"see\s*you", "farewell"),
                (r"go\s*to\s*sleep", "farewell"),
            ],
            "time_date": [
                (r"what('?s| is) the time", "time"),
                (r"current time", "time"),
                (r"what('?s| is) the date", "date"),
                (r"today('?s)? date", "date"),
            ],
            "identity": [  
                (r"who\s*(are|r)\s*you", "who_are_you"),
                (r"what('?s| is) your name", "your_name"),
                (r"what('?s| is) my name", "my_name"),
                (r"tell\s*me\s*about\s*yourself", "who_are_you"),
                (r"introduce\s*yourself", "who_are_you"),
            ],
            "system": [
                (r"shut\s*down\s*(laptop|computer)", "shutdown"),
                (r"restart\s*(laptop|computer)", "restart"),
                (r"lock\s*(computer|laptop)", "lock"),
                (r"sleep\s*mode", "sleep"),
            ],
            "applications": [
                (r"open\s+(microsoft\s+)?word", "open_word"),
                (r"open\s+(google\s+)?chrome", "open_chrome"),
                (r"open\s+notepad", "open_notepad"),
                (r"open\s+calculator", "open_calculator"),
                (r"open\s+(vs\s*)?code", "open_vscode"),
                (r"open\s+(file\s+)?explorer", "open_explorer"),
                (r"open\s+(command\s+)?prompt", "open_cmd"),
                (r"open\s+cmd", "open_cmd"), 
                (r"open\s+terminal", "open_terminal"),
                (r"open\s+powershell", "open_powershell"),
            ],
            "routines": [
                (r"study\s+cyber", "study_cyber"),
                (r"cyber\s+mode", "study_cyber"),
                (r"work\s+mode", "work_mode"),
                (r"start\s+working", "work_mode"),
            ],
            "help": [
                (r"what\s+can\s+you\s+do", "help"),
                (r"help\s+me", "help"),
                (r"list\s+commands", "help"),
                (r"show\s+commands", "help"),
            ]
        }
    
    def parse_command(self, command_text: str) -> Dict:
        """Parse a voice command and identify its type"""
        command_text = command_text.lower().strip()
        self.logger.debug(f"Parsing command: '{command_text}'")
        
        result = {
            "original": command_text,
            "type": "unknown",
            "action": None,
            "parameters": {},
            "confidence": 0.0
        }
        
        # Check each pattern category
        for category, patterns in self.command_patterns.items():
            for pattern, action in patterns:
                if re.search(pattern, command_text, re.IGNORECASE):
                    result["type"] = category
                    result["action"] = action
                    result["confidence"] = 1.0
                    
                    # Extract parameters
                    if category == "applications":
                        # Extract app name
                        match = re.search(r"open\s+(\w+)", command_text)
                        if match:
                            result["parameters"]["app_name"] = match.group(1)
                    
                    self.logger.info(f"Parsed as: {category} -> {action}")
                    return result
        
        # If no pattern matched, try to guess
        if "open" in command_text:
            result["type"] = "applications"
            result["action"] = "open_app"
            result["confidence"] = 0.7
            # Extract app name after "open"
            parts = command_text.split("open", 1)
            if len(parts) > 1:
                result["parameters"]["app_name"] = parts[1].strip()
        
        elif "time" in command_text:
            result["type"] = "time_date"
            result["action"] = "time"
            result["confidence"] = 0.8
        
        return result
    
    def get_response(self, parsed_command: Dict) -> str:
        """Get appropriate response for a parsed command"""
        action = parsed_command.get("action")
        
        responses = {
            "greeting": [
                "Hello! How can I help you?",
                "Hi there! What would you like me to do?",
                "Yes, I'm listening. How can I assist you?"
            ],
            "farewell": [
                "Goodbye! Shutting down.",
                "See you later!",
                "Going to sleep now. Say 'Hey Lisa' to wake me up."
            ],
            "who_are_you": [
                "I am Lisa, your personal AI assistant. I'm here to help you with tasks on your computer.",
                "My name is Lisa! I'm your intelligent assistant that can control applications, open files, and help with your routines.",
                "I'm Lisa, your Learning Intelligent System Assistant. I can automate tasks, answer questions, and make your work easier."
            ],
            "your_name": [
                "My name is Lisa. Nice to meet you!",
                "You can call me Lisa. That's short for Learning Intelligent System Assistant.",
                "I'm Lisa, your personal assistant!"
            ],
            "my_name": [
                "You haven't told me your name yet! But I'd love to know what to call you.",
                "I don't know your name yet. You can set it in the user preferences file.",
                "You can tell me your name by saying 'My name is [your name]' and I'll remember it!"
            ],
            "time": "The current time is {time}.",
            "date": "Today's date is {date}.",
            "help": "I can help you with: opening apps, telling time, study routines, answering questions, and system control. Try saying 'study cyber' or 'open chrome'!",
            "study_cyber": "Starting study cyber routine. Opening your study materials...",
            "open_word": "Opening Microsoft Word...",
            "open_chrome": "Opening Google Chrome...",
            "open_browser": "Opening web browser...",
            "open_cmd": "Opening Command Prompt...",
            "open_terminal": "Opening Terminal...",
            "open_powershell": "Opening PowerShell...",
            "unknown": "I'm not sure how to help with that. Try saying 'what can you do' for a list of commands."
        }
        
        import random
        if action in responses:
            if isinstance(responses[action], list):
                return random.choice(responses[action])
            return responses[action]
        
        return responses["unknown"]

# Test function
def test_parser():
    """Test the command parser"""
    import sys
    from pathlib import Path
    
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    logging.basicConfig(level=logging.INFO)
    
    parser = CommandParser()
    
    test_commands = [
        "hello lisa",
        "good bye",
        "what is the time",
        "open microsoft word",
        "study cyber",
        "shutdown laptop",
        "can you open chrome please"
    ]
    
    print("Testing Command Parser...")
    print("="*60)
    
    for cmd in test_commands:
        print(f"\nCommand: '{cmd}'")
        result = parser.parse_command(cmd)
        response = parser.get_response(result)
        print(f"  Parsed as: {result['type']} -> {result['action']}")
        print(f"  Response: {response}")

if __name__ == "__main__":
    test_parser()