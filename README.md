# 🤖 Aethera – AI Voice Assistant  

Aethera is a **voice-controlled desktop assistant** built with Python.  
It listens to your commands, understands natural language, and performs actions like **web search, Wikipedia lookup, system control, Spotify control, and more**.  

---

## ✨ Features  

- 🗣️ **Speech Recognition** – Listen and transcribe voice commands  
- 🔊 **Text-to-Speech** – Natural voice responses  
- 🌐 **Search & Knowledge** – Google, Wikipedia, and headlines  
- 💻 **System Control** – Open/close apps, take screenshots, show processes  
- 🎵 **Media & Volume** – Control volume and Spotify playback  
- 🛠️ **Utilities** – Time, date, weather (with API key)  

---

## 🚀 Getting Started  

Clone the repository and install dependencies:  

```bash
git clone https://github.com/yourusername/aethera-assistant.git
cd aethera-assistant
pip install -r requirements.txt
python setup.py
python main.py
```

## ⚙️ Dependencies
- 🗣️ **speechrecognition** → Converts spoken commands into text  
- 🔊 **pyttsx3** → Provides text-to-speech so the assistant can talk back  
- 🌐 **requests** → Fetches data from the web (APIs, search results)  
- 📖 **beautifulsoup4** → Parses HTML for web scraping  
- 📚 **wikipedia** → Retrieves summaries directly from Wikipedia  
- 📊 **psutil** → Reads system info (CPU, memory, processes)  
- 🖼️ **pillow (PIL)** → Handles screenshots and image processing  
- 🔑 **python-dotenv** → Loads optional API keys from a `.env` file  
- 📄 **lxml** → Fast XML/HTML parsing for web content  
- 🎙️ **pyaudio** → Captures microphone input  
- 🎚️ **pycaw** → Controls system volume (Windows only)  
- 🪟 **pywin32** → Windows API support for system-level operations  
- ⌨️ **keyboard** → Captures and automates keyboard input  
- 📦 **setuptools** → Packaging and distribution utilities  
- 🛠️ **wheel** → Builds Python wheels for faster installations  

## 🔧 Troubleshooting

* **🎙️ Microphone not working?**
  * Make sure `pyaudio` is installed properly (`pip install pyaudio`).
  * Check your system audio settings to ensure the correct microphone is selected and not muted.
* **🔊 No voice response?**
  * Ensure `pyttsx3` is installed and working correctly.
  * Try switching the speech engine voice by changing the `TTS_VOICE_INDEX` in the `config.py` file.
* **🌐 Web requests failing?**
  * Verify your internet connection is active.
  * Some features may require a valid API key to be stored in the `.env` file.
* **⚙️ Import errors?**
  * Run `pip install -r requirements.txt` again in your terminal to ensure all dependencies are installed.
  * Make sure you are using Python 3.7 or a newer version.

### 💡 Example Commands

Here are some example commands you can try with Aethera:
* 🔎 "Search for Python programming tutorials"
* 🌐 "Open Chrome"
* 📸 "Take a screenshot"
* 📚 "Wikipedia artificial intelligence"
* 🎶 "Play some jazz music on Spotify"
* ⏰ "What time is it?"
