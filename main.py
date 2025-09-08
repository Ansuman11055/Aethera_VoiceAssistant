import sys
import time
import signal
from typing import Dict, Optional
from speech import SpeechHandler
from actions import ActionHandler
from config import ASSISTANT_NAME, WAKE_WORDS

class AetheraAssistant:
    def __init__(self):
        print(f"🤖 Initializing {ASSISTANT_NAME} AI Assistant...")
        
        try:
            self.speech = SpeechHandler()
            self.actions = ActionHandler()
            
            self.is_listening = True
            self.awaiting_confirmation = False
            self.pending_action = None
            
            print(f"✅ {ASSISTANT_NAME} is ready!")
            print("🔊 Always listening for commands...")
            
        except Exception as e:
            print(f"❌ Error initializing {ASSISTANT_NAME}: {e}")
            sys.exit(1)
    
    def run(self):
        self.speech.speak(f"Hello! {ASSISTANT_NAME} is now active and ready to assist you.")
        
        try:
            while self.is_listening:
                self._listen_and_process()
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            self._shutdown()
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            self.speech.speak("I encountered an unexpected error and need to restart.")
            self._shutdown()
    
    def _listen_and_process(self):
        try:
            success, text = self.speech.listen()
            
            if not success:
                if "timeout" not in text.lower():
                    print(f"⚠️ Listening issue: {text}")
                return
            
            if self.awaiting_confirmation:
                self._handle_confirmation(text)
            else:
                self._handle_command(text)
                
        except Exception as e:
            print(f"❌ Error in listen_and_process: {e}")
            self.speech.speak("I had trouble processing that command.")
    
    def _handle_command(self, text: str):
        command = text.strip()
        
        if not command:
            return
        
        print(f"🎯 Processing command: {command}")
        
        result = self.actions.process_command(command)
        
        self._handle_action_result(result)
    
    def _handle_confirmation(self, text: str):
        text = text.lower().strip()
        
        print(f"Handling confirmation for: '{text}'")
        
        if any(phrase in text for phrase in ['confirm', 'yes', 'go ahead', 'proceed', 'do it']):
            if self.pending_action:
                print("✅ Action confirmed, executing...")
                original_command_text = self.pending_action
                
                self.awaiting_confirmation = False
                self.pending_action = None
                
                intent, entities = self.actions.nlp.extract_intent(original_command_text)
                
                if intent in self.actions.action_registry:
                    result = self.actions.action_registry[intent](entities)
                    self._handle_action_result(result)
                else:
                    self.speech.speak("I couldn't process that command.")
            else:
                self.speech.speak("I don't have a pending action to confirm.")
                self.awaiting_confirmation = False
        
        elif any(word in text for word in ['no', 'nope', 'cancel', 'abort', 'nevermind']):
            self.speech.speak("Okay, I've cancelled that action.")
            self.awaiting_confirmation = False
            self.pending_action = None
        
        else:
            self.speech.speak("Please say 'confirm' or 'yes' to proceed, or 'no' to cancel.")
    
    def _handle_action_result(self, result: Dict):
        try:
            if result.get('requires_confirmation'):
                self.awaiting_confirmation = True
                self.pending_action = result.get('original_command', '')
                self.speech.speak(result.get('summary', 'Do you want me to proceed?'))
                return
            
            if result.get('stop_requested'):
                self.speech.speak(result.get('summary', 'Goodbye!'))
                self._shutdown()
                return
            
            summary = result.get('summary', '')
            if summary:
                self.speech.speak(summary)
            
            if result.get('success'):
                print(f"✅ Action completed: {summary[:100]}...")
            else:
                print(f"❌ Action failed: {summary[:100]}...")
                
        except Exception as e:
            print(f"❌ Error handling action result: {e}")
            self.speech.speak("I completed the action but had trouble reporting the result.")
    
    def _shutdown(self):
        print(f"\n🔥 Shutting down {ASSISTANT_NAME}...")
        self.is_listening = False
        self.speech.speak("Shutting down. Goodbye!")
        print("👋 Goodbye!")
        sys.exit(0)

def signal_handler(sig, frame):
    print(f"\n🛑 Received interrupt signal, shutting down...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 50)
    print("🤖 AETHERA AI DESKTOP ASSISTANT")
    print("=" * 50)
    print("Version 1.0 - Voice Controlled AI Assistant")
    print("Features: Voice Recognition, Web Search, System Control")
    print("=" * 50)
    
    try:
        assistant = AetheraAssistant()
        assistant.run()
        
    except Exception as e:
        print(f"❌ Failed to start Aethera: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure your microphone is connected and working")
        print("2. Check that all required packages are installed: pip install -r requirements.txt")
        print("3. On Linux, you might need: sudo apt-get install portaudio19-dev python3-pyaudio")
        print("4. On Windows, you might need to install PyAudio manually")
        sys.exit(1)

if __name__ == "__main__":
    main()  