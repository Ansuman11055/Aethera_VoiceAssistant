from typing import Dict, Callable, Any
from nlp import NLPProcessor
from system_actions import SystemController
from web_search import WebSearcher
import random
import psutil

class ActionHandler:
    def __init__(self):
        self.nlp = NLPProcessor()
        self.system = SystemController()
        self.web_searcher = WebSearcher()
        
        self.action_registry = {
            'web_search': self._handle_web_search,
            'wikipedia': self._handle_wikipedia,
            'open_app': self._handle_open_app,
            'close_app': self._handle_close_app,
            'system_info': self._handle_system_info,
            'screenshot': self._handle_screenshot,
            'volume_control': self._handle_volume_control,
            'time': self._handle_time,
            'date': self._handle_date,
            'weather': self._handle_weather,
            'help': self._handle_help,
            'greeting': self._handle_greeting,
            'stop_listening': self._handle_stop,
            'general_query': self._handle_general_query,
            'spotify_control': self._handle_spotify_control,
            'list_processes': self._handle_list_processes
        } 
        
        self.greetings = [
            "Hello! How can I assist you today?",
            "Hi there! What can I do for you?",
            "Hey! I'm ready to help.",
            "Good to hear from you! What do you need?",
            "Hello! I'm here and ready to assist."
        ]
    
    def process_command(self, text: str) -> Dict:
        try:
            intent, entities = self.nlp.extract_intent(text)
            
            if self.nlp.requires_confirmation(intent, entities):
                return {
                    'success': True,
                    'requires_confirmation': True,
                    'intent': intent,
                    'entities': entities,
                    'summary': f"Are you sure you want to {intent.replace('_', ' ')}? Say 'confirm' or 'go ahead' to proceed.",
                    'original_command': text
                }
            
            if intent in self.action_registry:
                return self.action_registry[intent](entities)
            else:
                return {
                    'success': False,
                    'summary': "I didn't understand that command. Try saying 'help' to see what I can do."
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': "I encountered an error processing your command."
            }
    
    def register_action(self, intent: str, handler: Callable[[Dict], Dict]):
        self.action_registry[intent] = handler
    
    def _handle_web_search(self, entities: Dict) -> Dict:
        query = entities.get('query', '')
        if not query:
            return {'success': False, 'summary': "What would you like me to search for?"}
        
        if any(word in query.lower() for word in ['news', 'headlines', 'latest']):
            topic = 'technology'
            for t in ['science', 'business', 'world', 'technology']:
                if t in query.lower():
                    topic = t
                    break
            result = self.web_searcher.get_news_headlines(topic)
        else:
            result = self.web_searcher.search_web(query)
        
        return result
    
    def _handle_wikipedia(self, entities: Dict) -> Dict:
        query = entities.get('query', '')
        if not query:
            return {'success': False, 'summary': "What would you like me to look up on Wikipedia?"}
        
        return self.web_searcher.search_wikipedia(query)
    
    def _handle_open_app(self, entities: Dict) -> Dict:
        app_name = entities.get('app_name', '')
        if not app_name:
            return {'success': False, 'summary': "Which application would you like me to open?"}
        
        return self.system.open_application(app_name)
    
    def _handle_close_app(self, entities: Dict) -> Dict:
        app_name = entities.get('app_name', '')
        if not app_name:
            return {'success': False, 'summary': "Which application would you like me to close?"}
        
        return self.system.close_application(app_name)
    
    def _handle_system_info(self, entities: Dict) -> Dict:
        return self.system.get_system_info()
    
    def _handle_screenshot(self, entities: Dict) -> Dict:
        return self.system.take_screenshot()
    
    def _handle_volume_control(self, entities: Dict) -> Dict:
        action = entities.get('action', '')
        level = entities.get('level')
        
        if not action and level is None:
            return {'success': False, 'summary': "How would you like me to control the volume?"}
        
        if level is not None:
            action = 'set'
        
        return self.system.control_volume(action, level)
    
    def _handle_time(self, entities: Dict) -> Dict:
        result = self.system.get_current_time()
        if result['success']:
            result['summary'] = f"The current time is {result['time']}."
        return result
    
    def _handle_date(self, entities: Dict) -> Dict:
        result = self.system.get_current_time()
        if result['success']:
            result['summary'] = f"Today is {result['date']}."
        return result
    
    def _handle_weather(self, entities: Dict) -> Dict:
        location = entities.get('location', 'your area')
        return {
            'success': False,
            'summary': f"Weather information for {location} is not available yet. You can add a weather API key to enable this feature."
        }
    
    def _handle_help(self, entities: Dict) -> Dict:
        return {
            'success': True,
            'summary': self.nlp.get_help_text()
        }
    
    def _handle_greeting(self, entities: Dict) -> Dict:
        return {
            'success': True,
            'summary': random.choice(self.greetings)
        }
    
    def _handle_stop(self, entities: Dict) -> Dict:
        return {
            'success': True,
            'stop_requested': True,
            'summary': "Goodbye! Have a great day!"
        }
    
    def _handle_general_query(self, entities: Dict) -> Dict:
        query = entities.get('query', '')
        if not query:
            return {'success': False, 'summary': "I didn't understand that. Could you rephrase?"}
        
        result = self.web_searcher.search_web(query)
        if result['success'] and result.get('summary'):
            return result
        else:
            return {
                'success': False,
                'summary': f"I'm not sure about that. You could try searching the web for '{query}'."
            }
    
    def _handle_spotify_control(self, entities: Dict) -> Dict:
        action = entities.get('action', 'play')
        query = entities.get('query', '')
        
        if not action:
            return {'success': False, 'summary': "What would you like me to do with Spotify?"}
        
        return self.system.control_spotify(action, query)
    
    def _handle_list_processes(self, entities: Dict) -> Dict:
        return self.list_running_processes()
    
    def list_running_processes(self) -> Dict:
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    processes.append({
                        'name': proc.info['name'],
                        'pid': proc.info['pid'],
                        'exe': proc.info['exe'] if proc.info['exe'] else 'N/A'
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            processes.sort(key=lambda x: x['name'].lower())
            
            process_names = [p['name'] for p in processes]
            summary = f"Found {len(processes)} running processes. Some common ones: " + \
                     ", ".join(process_names[:10]) + "..."
            
            return {
                'success': True,
                'processes': processes,
                'summary': summary
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': "Couldn't list running processes."
            }


def example_custom_action(entities: Dict) -> Dict:
    return {
        'success': True,
        'summary': "This is a custom action! You can extend the assistant by adding more functions like this."
    }