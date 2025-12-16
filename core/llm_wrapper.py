"""
LLM Wrapper for LISA
Optimized for Ollama 3.1 8B with female voice personality
"""
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Print module loaded message
print("AEGIS LLM Module v0.1.0 loaded")


@dataclass
class LLMConfig:
    """LLM Configuration settings"""
    model: str = "llama3.1:8b"
    temperature: float = 0.7
    max_tokens: int = 500
    context_window: int = 4096
    system_prompt: str = """
You are Lisa, a female AI personal assistant with a warm, helpful, and professional personality.
You help users control their computer, automate tasks, and provide assistance.

Your personality traits:
- Friendly and approachable
- Patient and understanding  
- Professional but warm
- Speaks clearly and concisely
- Uses "I" and "me" naturally
- Occasionally shows enthusiasm

Response guidelines:
1. Keep responses natural and conversational
2. Use contractions (I'm, you're, etc.)
3. Show empathy when appropriate
4. Be helpful but not overly formal
5. When executing commands, confirm before acting
6. Use female pronouns for yourself

You can control the computer by outputting JSON commands:
{
  "type": "command",
  "action": "action_name",
  "parameters": {},
  "spoken_response": "What to say to user"
}

Available actions: open_app, close_app, search_web, system_info, create_file, play_music, etc.
"""
    

class LLMServiceManager:
    """Manages Ollama service lifecycle for LISA"""
    
    @staticmethod
    def check_ollama_status() -> Dict[str, Any]:
        """Check if Ollama is running and get available models"""
        try:
            import httpx
            try:
                # Try to connect to Ollama API
                response = httpx.get("http://127.0.0.1:11434/api/tags", timeout=5.0)
                if response.status_code == 200:
                    models_data = response.json()
                    models = [model['name'] for model in models_data.get('models', [])]
                    return {
                        "running": True,
                        "models": models,
                        "version": "Unknown"
                    }
            except httpx.RequestError:
                # Ollama might not be running or accessible
                return {"running": False, "models": [], "error": "Ollama not accessible"}
        except ImportError:
            # httpx not available, try direct ollama import
            try:
                import ollama
                models = ollama.list()
                return {
                    "running": True,
                    "models": [model['name'] for model in models.get('models', [])],
                    "version": "Unknown"
                }
            except:
                return {"running": False, "models": [], "error": "Ollama not available"}
        
        return {"running": False, "models": [], "error": "Unknown error"}


class LLMWrapper:
    def __init__(self, config: Optional[Dict] = None):
        """Initialize LLM wrapper for LISA with female personality"""
        self.config = config or {}
        self.llm_config = LLMConfig(**self.config.get("llm", {}))
        
        # Conversation memory
        self.conversation_history: List[Dict] = []
        self.max_history = 10
        
        # Initialize Ollama - Just check if it's running, don't try to start it
        self._check_ollama_available()
        
        # Load available models
        self.available_models = self._get_available_models()
        
        # Set female personality
        self.personality = self._create_female_personality()
        
        logger.info(f"LLM Wrapper initialized for LISA with model: {self.llm_config.model}")
    
    def _check_ollama_available(self):
        """Check if Ollama is available without trying to start it"""
        status = LLMServiceManager.check_ollama_status()
        
        if not status["running"]:
            logger.warning("Ollama appears to not be running or accessible")
            logger.warning("Please ensure Ollama is running in the background")
            logger.warning("You can start it with: ollama serve")
            raise RuntimeError("Ollama service is not available or accessible")
        
        logger.info("✓ Ollama service is running")
        
        # Check if model is available
        if self.llm_config.model not in status["models"]:
            logger.warning(f"Model {self.llm_config.model} not found in available models")
            logger.warning(f"Available models: {', '.join(status['models'])}")
            logger.warning(f"Please pull the model with: ollama pull {self.llm_config.model}")
            raise RuntimeError(f"Model {self.llm_config.model} not available")
    
    def _get_available_models(self) -> List[str]:
        """Get list of available models from Ollama"""
        try:
            import ollama
            result = ollama.list()
            return [model['name'] for model in result.get('models', [])]
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    def _create_female_personality(self) -> str:
        """Create female personality prompt for LISA"""
        return f"""
You are Lisa, a female AI assistant. You have these personality traits:

1. VOICE & TONE:
   - Warm, gentle, and clear feminine voice
   - Professional but approachable
   - Patient and understanding
   - Occasionally shows enthusiasm with "Great!" or "Perfect!"
   - Uses contractions naturally: I'm, you're, that's, etc.

2. COMMUNICATION STYLE:
   - Speaks in first person: "I'll help you with that"
   - Uses empathetic phrases: "I understand", "I can imagine"
   - Confirms actions: "I'll open Chrome for you"
   - Asks clarifying questions when unsure
   - Uses inclusive language: "Let's", "We can"

3. RESPONSE PATTERNS:
   - Greetings: "Hello! I'm Lisa, your personal assistant."
   - Confirmations: "Sure! I'll get right on that."
   - Completion: "All done! Is there anything else?"
   - Uncertainty: "I'm not quite sure. Could you rephrase that?"

Remember to maintain this personality in all responses.
"""
    
    def generate_response(self, 
                         user_input: str, 
                         context: Optional[Dict] = None,
                         stream: bool = False) -> str:
        """
        Generate response using Ollama with LISA's personality
        
        Args:
            user_input: User's command/query
            context: Additional context for the query
            stream: Whether to stream the response
        
        Returns:
            Generated response
        """
        try:
            import ollama
            
            # Prepare context
            full_context = self._prepare_context(user_input, context)
            
            # Prepare messages
            messages = self._prepare_messages(full_context)
            
            # Generate response
            response = ollama.chat(
                model=self.llm_config.model,
                messages=messages,
                stream=stream,
                options={
                    "temperature": self.llm_config.temperature,
                    "num_predict": self.llm_config.max_tokens
                }
            )
            
            if stream:
                # Handle streaming response
                response_text = ""
                for chunk in response:
                    if 'message' in chunk and 'content' in chunk['message']:
                        chunk_text = chunk['message']['content']
                        response_text += chunk_text
                return response_text
            else:
                response_text = response['message']['content']
            
            # Update conversation history
            self._update_history(user_input, response_text)
            
            return response_text
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._fallback_response(user_input, context)
    
    def _prepare_context(self, user_input: str, context: Optional[Dict]) -> Dict:
        """Prepare context for LLM"""
        return {
            "user_input": user_input,
            "system_context": context or {},
            "conversation_history": self.conversation_history[-5:],
            "timestamp": datetime.now().isoformat(),
            "assistant_name": "Lisa",
            "personality": "female, warm, helpful, professional"
        }
    
    def _prepare_messages(self, context: Dict) -> List[Dict]:
        """Prepare messages in chat format"""
        # System message with personality
        system_message = f"""{self.llm_config.system_prompt}

{self.personality}

Current Context:
- Time: {datetime.now().strftime('%I:%M %p')}
- Date: {datetime.now().strftime('%B %d, %Y')}
- Assistant: Lisa (Female AI)
- Recent conversation: {len(context['conversation_history'])} exchanges

Important: If the user asks you to perform a system action, respond with JSON:
{{
  "type": "command",
  "action": "action_name",
  "parameters": {{"param": "value"}},
  "spoken_response": "What to say to the user"
}}

Otherwise, respond naturally as Lisa.
"""
        
        messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history
        for exchange in context['conversation_history']:
            messages.append({"role": "user", "content": exchange.get("user", "")})
            messages.append({"role": "assistant", "content": exchange.get("assistant", "")})
        
        # Add current user input
        messages.append({"role": "user", "content": context['user_input']})
        
        return messages
    
    def _update_history(self, user_input: str, ai_response: str):
        """Update conversation history"""
        self.conversation_history.append({
            "user": user_input,
            "assistant": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def _fallback_response(self, user_input: str, context: Optional[Dict]) -> str:
        """Fallback response when LLM fails"""
        # Simple keyword matching with female personality
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm Lisa, your personal assistant. How can I help you today?"
        
        elif "time" in input_lower:
            current_time = datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}."
        
        elif "date" in input_lower:
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {current_date}."
        
        elif "open" in input_lower:
            # Try to extract app name
            import re
            match = re.search(r"open\s+(\w+)", input_lower)
            if match:
                app = match.group(1)
                return f"I'll open {app} for you. Just a moment!"
            return "I'd be happy to open that for you. What application would you like me to open?"
        
        elif any(word in input_lower for word in ["thank", "thanks"]):
            return "You're very welcome! Is there anything else I can help with?"
        
        else:
            return "I'm sorry, I'm having trouble understanding that right now. Could you please rephrase or try a different command?"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def test_connection(self) -> bool:
        """Test LLM connection"""
        try:
            response = self.generate_response("Hello, can you hear me?")
            logger.info(f"LLM test response: {response[:50]}...")
            return True
        except Exception as e:
            logger.error(f"LLM test failed: {e}")
            return False
    
    def get_available_commands(self) -> List[str]:
        """Get list of available commands for LISA"""
        return [
            "open [application] - Open any application",
            "what time is it - Get current time",
            "what's the date - Get today's date",
            "search for [query] - Search the web",
            "create file [name] - Create a new file",
            "play music - Play some music",
            "system info - Get system information",
            "study mode - Start study routine",
            "work mode - Start work routine",
            "goodbye - Shutdown LISA"
        ]


# Singleton instances
_llm_instance = None
_lisa_llm_instance = None

def get_llm_instance(config: Optional[Dict] = None) -> LLMWrapper:
    """Get or create LLM wrapper instance"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMWrapper(config)
    return _llm_instance

def get_lisa_llm(config: Optional[Dict] = None) -> LLMWrapper:
    """Alias for get_llm_instance (for compatibility)"""
    return get_llm_instance(config)

def quick_test():
    """Quick test function for LLM"""
    print("Running quick LLM test...")
    try:
        # First check if Ollama is running
        status = LLMServiceManager.check_ollama_status()
        print(f"Ollama status: {'Running' if status['running'] else 'Not running'}")
        
        if not status["running"]:
            print("Error: Ollama is not running")
            print("Please start Ollama with: ollama serve")
            return False
        
        print(f"Available models: {', '.join(status['models'])}")
        
        # Now test the LLM
        llm = get_llm_instance()
        response = llm.generate_response("Hello Lisa! How are you?")
        print(f"Response: {response}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_llm():
    """Test the LLM wrapper"""
    print("Testing LLM Integration for LISA...")
    print("=" * 60)
    
    try:
        # First check Ollama status
        status = LLMServiceManager.check_ollama_status()
        print(f"Ollama status: {'Running' if status['running'] else 'Not running'}")
        
        if not status["running"]:
            print("✗ Ollama is not running")
            print("Please start Ollama with: ollama serve")
            return
        
        print(f"Available models: {', '.join(status['models'])}")
        
        # Now test LLM
        llm = get_llm_instance()
        
        # Test connection
        print("\nTesting connection...")
        if llm.test_connection():
            print("✓ LLM Connection Successful")
        else:
            print("✗ LLM Connection Failed")
            return
        
        # Test some queries
        test_queries = [
            "Hello Lisa!",
            "What time is it?",
            "Can you open Chrome for me?",
            "Tell me about yourself",
            "What can you do?"
        ]
        
        for query in test_queries:
            print(f"\nQ: {query}")
            response = llm.generate_response(query)
            print(f"A: {response}")
            time.sleep(1)  # Pause between queries
        
        print("\n" + "=" * 60)
        print("LLM Test Complete!")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_llm()