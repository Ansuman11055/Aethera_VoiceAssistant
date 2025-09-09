import re
from typing import Dict, List, Tuple

class NLPProcessor:
    def __init__(self):
        self.intent_patterns = {
            'web_search': [
                r'search (?:the web |google |internet )?for (.+)',
                r'look up (.+)',
                r'find (?:information about |info about |)(.+)',
                r'what is (.+)',
                r'who is (.+)',
                r'tell me about (.+)',
                r'google (.+)',
                r'search (.+)',
                r'find (.+)'
            ],
            
            'open_app': [
                r'open (.+)',
                r'launch (.+)',
                r'start (.+)',
                r'run (.+)'
            ],
            
            'close_app': [
                r'close (.+)',
                r'quit (.+)',
                r'exit (.+)',
                r'stop (.+)',
                r'kill (.+)',
                r'end (.+)'
            ],
            
            'system_info': [
                r'system info(?:rmation)?',
                r'computer specs?',
                r'hardware info(?:rmation)?',
                r'memory usage',
                r'cpu usage',
                r'system status',
                r'computer status'
            ],
            
            'screenshot': [
                r'take a screenshot',
                r'capture screen',
                r'screenshot',
                r'screen capture',
                r'capture my screen'
            ],
            
            'volume_control': [
                r'(?:set |change |)volume to (\d+)',
                r'(?:turn |set |)volume (?:up|down)',
                r'(?:increase|raise) (?:the )?volume',
                r'(?:decrease|lower) (?:the )?volume',
                r'mute',
                r'unmute',
                r'volume up',
                r'volume down'
            ],
            
            'time': [
                r'what time is it',
                r'current time',
                r'tell me the time',
                r'what\'s the time',
                r'time please'
            ],
            
            'date': [
                r'what(?:\'s| is) (?:the |today\'s |)date',
                r'today\'s date',
                r'what day is it',
                r'what\'s today',
                r'date please'
            ],
            
            'weather': [
                r'weather(?:\s+in\s+(.+))?',
                r'what\'s the weather(?:\s+in\s+(.+))?',
                r'temperature(?:\s+in\s+(.+))?',
                r'how\'s the weather'
            ],
            
            'wikipedia': [
                r'wikipedia (.+)',
                r'wiki (.+)',
                r'summary of (.+)',
                r'wikipedia search (.+)'
            ],
            
            'spotify_control': [
                # Clear play/pause commands
                r'play spotify',
                r'pause spotify',
                r'stop spotify',
                r'resume spotify',
                r'start spotify',
                
                # Media control
                r'next song',
                r'skip song',
                r'previous song',
                r'spotify next',
                r'spotify skip',
                r'spotify previous',
                
                # Search and play
                r'(?:play|search) (.+) (?:on spotify|spotify)',
                r'spotify (?:play|search) (.+)',
                r'play (.+) on spotify',
                r'spotify (.+)',
                
                # General music command
                r'play music'
            ],
            
            'stop_listening': [
                r'stop listening',
                r'stop',
                r'exit',
                r'quit',
                r'goodbye',
                r'bye',
                r'shutdown',
                r'turn off'
            ],
            
            'help': [
                r'help',
                r'what can you do',
                r'commands',
                r'capabilities',
                r'what are your commands',
                r'show commands',
                r'list commands'
            ],
            
            'greeting': [
                r'hello',
                r'hi',
                r'hey',
                r'good morning',
                r'good afternoon',
                r'good evening',
                r'howdy',
                r'what\'s up'
            ],
            
            'list_processes': [
                r'list processes',
                r'show running processes',
                r'what processes are running',
                r'debug processes',
                r'running programs',
                r'active processes'
            ]
        }
    
    def extract_intent(self, text: str) -> Tuple[str, Dict]:
        text = text.lower().strip()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entities = {}
                    
                    if intent in ['web_search', 'wikipedia']:
                        entities['query'] = match.group(1).strip()
                    elif intent in ['open_app', 'close_app']:
                        entities['app_name'] = match.group(1).strip()
                    elif intent == 'volume_control':
                        if 'volume to' in text and match.groups():
                            entities['level'] = int(match.group(1))
                        elif any(word in text for word in ['volume up', 'increase', 'raise']):
                            entities['action'] = 'up'
                        elif any(word in text for word in ['volume down', 'decrease', 'lower']):
                            entities['action'] = 'down'
                        elif 'mute' in text and 'unmute' not in text:
                            entities['action'] = 'mute'
                        elif 'unmute' in text:
                            entities['action'] = 'unmute'
                    elif intent == 'weather':
                        if match.groups() and match.group(1):
                            entities['location'] = match.group(1).strip()
                        else:
                            entities['location'] = 'current'
                    elif intent == 'spotify_control':
                        text_lower = text.lower()
                        
                        # Clear play/pause commands
                        if text_lower in ['play spotify', 'start spotify', 'resume spotify']:
                            entities['action'] = 'play'
                        elif text_lower in ['pause spotify', 'stop spotify']:
                            entities['action'] = 'pause'
                        elif text_lower == 'play music':
                            entities['action'] = 'play'
                        
                        # Media controls
                        elif any(word in text_lower for word in ['next song', 'skip song', 'spotify next', 'spotify skip']):
                            entities['action'] = 'next'
                        elif any(word in text_lower for word in ['previous song', 'spotify previous']):
                            entities['action'] = 'previous'
                        
                        # Search and play commands
                        elif any(phrase in text_lower for phrase in ['play', 'search']) and 'spotify' in text_lower:
                            entities['action'] = 'search_and_play'
                            if match.groups() and match.group(1):
                                entities['query'] = match.group(1).strip()
                        elif 'spotify' in text_lower and match.groups() and match.group(1):
                            entities['action'] = 'search_and_play'
                            entities['query'] = match.group(1).strip()
                        else:
                            # Default to play action for any unmatched spotify command
                            entities['action'] = 'play'
                    
                    return intent, entities
        
        return 'general_query', {'query': text}
    
    def requires_confirmation(self, intent: str, entities: Dict) -> bool:
        dangerous_intents = ['system_shutdown', 'delete_file', 'format_drive']
        
        if intent in dangerous_intents:
            return True
        
        if 'query' in entities or 'app_name' in entities:
            text = entities.get('query', '') + ' ' + entities.get('app_name', '')
            dangerous_words = ['delete system', 'format drive', 'shutdown computer', 'restart computer', 'delete all']
            return any(dangerous_word in text.lower() for dangerous_word in dangerous_words)
        
        return False
    
    def get_help_text(self) -> str:
        help_lines = [
            "🤖 AETHERA AI ASSISTANT - AVAILABLE COMMANDS",
            "=" * 50,
            "",
            "🔍 WEB SEARCH & INFORMATION:",
            '• "Search for [topic]" - Search the internet',
            '• "What is [something]" - Get definitions/info',
            '• "Tell me about [topic]" - General information',
            '• "Look up [term]" - Find information online',
            '• "Google [query]" - Web search',
            "",
            "📚 KNOWLEDGE & WIKIPEDIA:",
            '• "Wikipedia [topic]" - Search Wikipedia',
            '• "Wiki [subject]" - Wikipedia lookup',
            '• "Summary of [topic]" - Get topic summary',
            "",
            "🎵 SPOTIFY MUSIC CONTROL:",
            '• "Play Spotify" - Start Spotify playback',
            '• "Pause Spotify" - Pause Spotify playback',
            '• "Stop Spotify" - Stop Spotify playback',
            '• "Resume Spotify" - Resume Spotify playback',
            '• "Play [song/artist] on Spotify" - Search and play',
            '• "Next song" - Skip to next track',
            '• "Previous song" - Go to previous track',
            '• "Play music" - Start music playback',
            "",
            "💻 SYSTEM CONTROL:",
            '• "Open [app name]" - Launch applications',
            '• "Close [app name]" - Close applications',
            '• "Take a screenshot" - Capture screen',
            '• "System information" - Get system specs',
            '• "List processes" - Show running programs',
            "",
            "🔊 VOLUME CONTROL:",
            '• "Set volume to [0-100]" - Set specific volume',
            '• "Volume up" - Increase volume',
            '• "Volume down" - Decrease volume',
            '• "Mute" - Mute audio',
            '• "Unmute" - Unmute audio',
            "",
            "⏰ TIME & DATE:",
            '• "What time is it?" - Current time',
            '• "What\'s the date?" - Current date',
            '• "What day is it?" - Current day',
            "",
            "🌤️ WEATHER (Coming Soon):",
            '• "Weather" - Local weather',
            '• "Weather in [city]" - Weather for location',
            "",
            "👋 BASIC INTERACTIONS:",
            '• "Hello" / "Hi" - Greet Aethera',
            '• "Help" - Show this command list',
            '• "What can you do?" - Show capabilities',
            '• "Goodbye" / "Stop" - Exit Aethera',
            "",
            "🎯 EXAMPLE COMMANDS:",
            '• "Search for Python programming tutorials"',
            '• "Open Chrome"',
            '• "Set volume to 75"',
            '• "Play Spotify"',
            '• "Pause Spotify"',
            '• "Play some jazz music on Spotify"',
            '• "What time is it?"',
            '• "Take a screenshot"',
            '• "Wikipedia artificial intelligence"',
            '• "Close Spotify"',
            "",
            "💡 TIPS:",
            "• Speak clearly and naturally",
            "• You can use variations of these commands",
            "• Say 'confirm' when asked for confirmation",
            "• Say 'help' anytime to see this list",
            "",
            "🔧 TROUBLESHOOTING:",
            "• If volume control doesn't work, try installing 'pycaw'",
            "• For better Spotify control, install 'pywin32'",
            "• Make sure apps are installed before opening them",
            "",
            "Ready to assist! Just say any command naturally."
        ]
        
        return "\n".join(help_lines)