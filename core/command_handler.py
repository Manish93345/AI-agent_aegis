import json
import os
from datetime import datetime

class CommandHandler:
    def __init__(self):
        self.commands = self.load_commands()
        self.security_profiles = self.load_security_profiles()
        
    def load_commands(self):
        """Load command mappings from JSON"""
        try:
            with open('config/commands.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Commands config not found. Using defaults.")
            return {}
    
    def load_security_profiles(self):
        """Load security profiles from JSON"""
        try:
            with open('config/security_profiles.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Security profiles config not found.")
            return {}
    
    def match_command(self, text):
        """Match spoken text to a command"""
        text = text.lower().strip()
        
        # Check greetings
        for greeting in self.commands.get('greetings', []):
            if greeting in text:
                return {'type': 'greeting', 'command': 'greeting', 'response': 'Hello! How can I help you?'}
        
        # Check basic commands
        for cmd_key, phrases in self.commands.get('basic_commands', {}).items():
            for phrase in phrases:
                if phrase in text:
                    return {'type': 'basic', 'command': cmd_key, 'matched_phrase': phrase}
        
        # Check routines
        for routine_key, phrases in self.commands.get('routines', {}).items():
            for phrase in phrases:
                if phrase in text:
                    return {'type': 'routine', 'command': routine_key, 'matched_phrase': phrase}
        
        # Check security commands
        for sec_key, phrases in self.commands.get('security_commands', {}).items():
            for phrase in phrases:
                if phrase in text:
                    return {'type': 'security', 'command': sec_key, 'matched_phrase': phrase}
        
        return {'type': 'unknown', 'command': None, 'response': "I didn't understand that command."}
    
    def execute_command(self, command_info):
        """Execute the matched command"""
        cmd_type = command_info['type']
        
        if cmd_type == 'greeting':
            return self._handle_greeting()
        elif cmd_type == 'basic':
            return self._handle_basic(command_info['command'])
        elif cmd_type == 'routine':
            return self._handle_routine(command_info['command'])
        elif cmd_type == 'security':
            return self._handle_security(command_info['command'])
        else:
            return "Command not implemented yet."
    
    def _handle_greeting(self):
        return f"Hello! AEGIS is ready. Current time: {datetime.now().strftime('%H:%M')}"
    
    def _handle_basic(self, command):
        if command == 'open_notepad':
            os.system('notepad')
            return "Opening Notepad"
        elif command == 'open_calculator':
            os.system('calc')
            return "Opening Calculator"
        elif command == 'what_time':
            return f"The time is {datetime.now().strftime('%I:%M %p')}"
        elif command == 'system_info':
            return "System status: Normal"
        return "Basic command executed"
    
    def _handle_routine(self, routine):
        return f"Starting routine: {routine}"
    
    def _handle_security(self, security_cmd):
        return f"Security command: {security_cmd} - To be implemented in Phase 5"

# Test the command handler
if __name__ == "__main__":
    handler = CommandHandler()
    test_commands = ["hey aegis", "open notepad", "what time is it", "study cyber"]
    
    for cmd in test_commands:
        print(f"\nTesting: '{cmd}'")
        matched = handler.match_command(cmd)
        print(f"Matched: {matched}")
        if matched['type'] != 'unknown':
            response = handler.execute_command(matched)
            print(f"Response: {response}")