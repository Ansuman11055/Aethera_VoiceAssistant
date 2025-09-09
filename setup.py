import os
import sys
import subprocess
import platform

def check_python_version():
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def setup_system_dependencies():
    system = platform.system().lower()
    print(f"🔧 Setting up dependencies for {system}...")
    
    if system == "linux":
        print("📋 Linux detected. You might need to install:")
        print("   sudo apt-get update")
        print("   sudo apt-get install portaudio19-dev python3-pyaudio")
        print("   sudo apt-get install espeak espeak-data libespeak1 libespeak-dev")
        print("   sudo apt-get install alsa-utils")
        
    elif system == "windows":
        print("📋 Windows detected.")
        print("   Most packages should install automatically.")
        print("   If PyAudio fails, try: pip install pipwin && pipwin install pyaudio")
        
    elif system == "darwin":
        print("📋 macOS detected. You might need to install:")
        print("   brew install portaudio")
        print("   pip install pyaudio")
    
    return True

def create_directories():
    directories = ["screenshots", "downloads", "logs"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    return True

def create_env_file():
    if not os.path.exists(".env"):
        if os.path.exists(".env.template"):
            import shutil
            shutil.copy(".env.template", ".env")
            print("📄 Created .env file from template")
            print("   Edit .env to add your API keys (optional)")
        else:
            with open(".env", "w") as f:
                f.write("# Aethera AI Assistant Environment Variables\n")
                f.write("# Add your API keys here (optional)\n\n")
                f.write("OPENAI_API_KEY=\n")
                f.write("WEATHER_API_KEY=\n")
            print("📄 Created empty .env file")
    else:
        print("📄 .env file already exists")
    
    return True

def test_microphone():
    print("🎤 Testing microphone...")
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        mic = sr.Microphone()
        
        print("   Microphone test: Adjusting for ambient noise...")
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=1)
        
        print("✅ Microphone test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        print("   Make sure your microphone is connected and working")
        return False

def test_speakers():
    print("🔊 Testing text-to-speech...")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say("Aethera setup test successful")
        engine.runAndWait()
        print("✅ Text-to-speech test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Text-to-speech test failed: {e}")
        return False

def main():
    print("🤖 AETHERA AI ASSISTANT SETUP")
    print("=" * 40)
    
    success = True
    
    if not check_python_version():
        success = False
    
    if success and not install_requirements():
        success = False
    
    if success:
        setup_system_dependencies()
    
    if success:
        create_directories()
    
    if success:
        create_env_file()
    
    if success:
        print("\n🧪 Running component tests...")
        if not test_microphone():
            success = False
        if not test_speakers():
            success = False
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Setup completed successfully!")
        print("\n🚀 To start Aethera, run:")
        print("   python main.py")
        print("\n💡 Try saying: 'Aethera, what time is it?'")
        print("               'Aethera, search for Python tutorials'")
        print("               'Aethera, help'")
    else:
        print("❌ Setup encountered some issues.")
        print("   Please check the error messages above.")
        print("   You may need to install system dependencies manually.")
    
    print("=" * 40)

if __name__ == "__main__":
    main()