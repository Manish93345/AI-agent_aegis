"""
Pattern Analyzer for learning user behavior
"""
import json
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from utils.file_utils import load_json, save_json

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    def __init__(self, data_path: str = "data/learning"):
        self.data_path = data_path
        self.command_history = self._load_history("command_history.json")
        self.user_patterns = self._load_history("user_patterns.json")
        self.session_data = defaultdict(list)
        
    def _load_history(self, filename: str) -> List[Dict]:
        """Load history data"""
        try:
            filepath = f"{self.data_path}/{filename}"
            return load_json(filepath) or []
        except:
            return []
    
    def _save_history(self, filename: str, data: List[Dict]):
        """Save history data"""
        try:
            filepath = f"{self.data_path}/{filename}"
            save_json(filepath, data)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
    
    def record_command(self, command_data: Dict):
        """Record a command execution"""
        record = {
            **command_data,
            "timestamp": datetime.now().isoformat(),
            "session_id": self._get_session_id()
        }
        
        self.command_history.append(record)
        
        # Keep only last 1000 records
        if len(self.command_history) > 1000:
            self.command_history = self.command_history[-1000:]
        
        # Save periodically
        if len(self.command_history) % 10 == 0:
            self._save_history("command_history.json", self.command_history)
        
        # Analyze for patterns
        self._analyze_patterns(record)
    
    def _get_session_id(self) -> str:
        """Generate session ID based on date"""
        return datetime.now().strftime("%Y%m%d")
    
    def _analyze_patterns(self, record: Dict):
        """Analyze command for patterns"""
        command = record.get("command")
        timestamp = datetime.fromisoformat(record["timestamp"])
        
        # Analyze by time of day
        hour = timestamp.hour
        time_slot = self._get_time_slot(hour)
        
        # Update session data
        self.session_data[time_slot].append(command)
        
        # Detect frequent patterns
        if len(self.session_data[time_slot]) >= 5:
            self._detect_frequent_patterns(time_slot)
    
    def _get_time_slot(self, hour: int) -> str:
        """Convert hour to time slot"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"
    
    def _detect_frequent_patterns(self, time_slot: str):
        """Detect frequent command patterns"""
        commands = self.session_data[time_slot]
        
        # Count frequency
        freq = defaultdict(int)
        for cmd in commands:
            freq[cmd] += 1
        
        # Find patterns with high frequency
        for cmd, count in freq.items():
            if count >= 3:  # Command used 3+ times in this slot
                pattern = {
                    "command": cmd,
                    "time_slot": time_slot,
                    "frequency": count,
                    "confidence": min(count / 5, 1.0),  # Normalize confidence
                    "detected_at": datetime.now().isoformat()
                }
                
                # Check if pattern already exists
                existing = False
                for existing_pattern in self.user_patterns:
                    if (existing_pattern["command"] == cmd and 
                        existing_pattern["time_slot"] == time_slot):
                        existing = True
                        # Update confidence
                        existing_pattern["confidence"] = max(
                            existing_pattern["confidence"],
                            pattern["confidence"]
                        )
                        existing_pattern["last_updated"] = datetime.now().isoformat()
                        break
                
                if not existing:
                    self.user_patterns.append(pattern)
        
        # Save patterns
        self._save_history("user_patterns.json", self.user_patterns)
    
    def get_suggestions(self, current_time: datetime = None) -> List[Dict]:
        """Get command suggestions based on patterns"""
        if not current_time:
            current_time = datetime.now()
        
        time_slot = self._get_time_slot(current_time.hour)
        suggestions = []
        
        # Find patterns for current time slot
        for pattern in self.user_patterns:
            if pattern["time_slot"] == time_slot and pattern["confidence"] > 0.5:
                suggestions.append({
                    "command": pattern["command"],
                    "reason": f"Frequently used during {time_slot}",
                    "confidence": pattern["confidence"]
                })
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        return suggestions[:3]  # Top 3 suggestions
    
    def get_user_stats(self) -> Dict:
        """Get user statistics"""
        if not self.command_history:
            return {"total_commands": 0}
        
        # Calculate stats
        total_commands = len(self.command_history)
        
        # Most frequent commands
        freq = defaultdict(int)
        for record in self.command_history[-100:]:  # Last 100 commands
            cmd = record.get("command")
            if cmd:
                freq[cmd] += 1
        
        most_frequent = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Time analysis
        morning_commands = len([c for c in self.command_history 
                              if self._get_time_slot(datetime.fromisoformat(c["timestamp"]).hour) == "morning"])
        afternoon_commands = len([c for c in self.command_history 
                                if self._get_time_slot(datetime.fromisoformat(c["timestamp"]).hour) == "afternoon"])
        
        return {
            "total_commands": total_commands,
            "most_frequent_commands": most_frequent,
            "morning_commands": morning_commands,
            "afternoon_commands": afternoon_commands,
            "learned_patterns": len(self.user_patterns),
            "last_updated": datetime.now().isoformat()
        }