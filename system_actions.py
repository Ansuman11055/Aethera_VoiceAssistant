import os
import sys
import subprocess
import platform
import psutil
import time
import comtypes
from datetime import datetime
from PIL import ImageGrab
from typing import Dict, Optional, List
from config import SCREENSHOTS_DIR
from ctypes import cast, POINTER

class SystemController:
    def __init__(self):
        self.os_type = platform.system().lower()
        self.ensure_directories()
        
        # Initialize Windows volume control interface
        self._volume_interface = None
        if self.os_type == 'windows':
            self._initialize_volume()

    def ensure_directories(self):
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    def _initialize_volume(self):
        """Initialize Windows volume control interface"""
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            
            # Initialize COM
            comtypes.CoInitialize()
            
            # Get the default audio device
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self._volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            
            print("✅ Windows volume control initialized successfully")
            
        except ImportError:
            print("⚠️ pycaw not available. Install with: pip install pycaw")
            self._volume_interface = None
            
        except Exception as e:
            print(f"⚠️ Failed to initialize volume control: {e}")
            self._volume_interface = None

    def get_system_info(self) -> Dict:
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_total = self._bytes_to_gb(memory.total)
            memory_available = self._bytes_to_gb(memory.available)
            
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_total = self._bytes_to_gb(disk.total)
            disk_free = self._bytes_to_gb(disk.free)
            
            system_info = {
                'system': platform.system(),
                'release': platform.release(),
                'processor': platform.processor(),
                'cpu_cores': cpu_count,
                'cpu_usage': f"{cpu_percent}%",
                'memory_total': f"{memory_total:.1f} GB",
                'memory_used': f"{memory_percent}%",
                'memory_available': f"{memory_available:.1f} GB",
                'disk_total': f"{disk_total:.1f} GB",
                'disk_used': f"{disk_percent:.1f}%",
                'disk_free': f"{disk_free:.1f} GB"
            }
            
            summary = f"System: {system_info['system']} {system_info['release']}. " \
                     f"CPU usage: {system_info['cpu_usage']}, " \
                     f"Memory usage: {system_info['memory_used']}, " \
                     f"Disk usage: {system_info['disk_used']}"
            
            return {
                'success': True,
                'info': system_info,
                'summary': summary
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': "I couldn't retrieve system information."
            }

    def open_application(self, app_name: str) -> Dict:
        try:
            app_name = app_name.lower().strip()
            
            app_mappings = {
                'notepad': 'notepad.exe' if self.os_type == 'windows' else 'gedit',
                'calculator': 'calc.exe' if self.os_type == 'windows' else 'gnome-calculator',
                'browser': 'start chrome' if self.os_type == 'windows' else 'google-chrome',
                'chrome': 'start chrome' if self.os_type == 'windows' else 'google-chrome',
                'firefox': 'start firefox' if self.os_type == 'windows' else 'firefox',
                'file manager': 'explorer' if self.os_type == 'windows' else 'nautilus',
                'terminal': 'cmd' if self.os_type == 'windows' else 'gnome-terminal',
                'command prompt': 'cmd' if self.os_type == 'windows' else 'gnome-terminal',
                'spotify': 'start spotify' if self.os_type == 'windows' else 'spotify',
                'discord': 'start discord' if self.os_type == 'windows' else 'discord',
                'steam': 'start steam' if self.os_type == 'windows' else 'steam',
                'word': 'start winword' if self.os_type == 'windows' else 'libreoffice --writer',
                'excel': 'start excel' if self.os_type == 'windows' else 'libreoffice --calc',
                'powerpoint': 'start powerpnt' if self.os_type == 'windows' else 'libreoffice --impress'
            }
            
            command = app_mappings.get(app_name, app_name)
            
            if self.os_type == 'windows':
                subprocess.Popen(command, shell=True)
            else:
                subprocess.Popen(command.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return {
                'success': True,
                'summary': f"Opening {app_name}."
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': f"I couldn't open {app_name}. Make sure it's installed."
            }

    def close_application(self, app_name: str) -> Dict:
        try:
            app_name = app_name.lower().strip()
            print(f"DEBUG: Trying to close app: '{app_name}'")
            
            app_keywords = {
                'spotify': 'spotify',
                'chrome': 'chrome',
                'browser': 'chrome',
                'firefox': 'firefox',
                'brave': 'brave',
                'brave browser': 'brave',
                'edge': 'msedge',
                'notepad': 'notepad',
                'calculator': 'calc',
                'word': 'winword',
                'excel': 'excel',
                'powerpoint': 'powerpnt',
                'discord': 'discord',
                'steam': 'steam',
                'vlc': 'vlc',
                'vs code': 'code',
                'visual studio code': 'code',
                'teams': 'teams',
                'zoom': 'zoom'
            }
            
            search_keyword = app_keywords.get(app_name, app_name)
            print(f"DEBUG: Searching for processes containing: '{search_keyword}'")
            
            closed_processes = []
            found_processes = []
            
            for proc in psutil.process_iter():
                try:
                    proc_name = proc.name().lower()
                    if search_keyword in proc_name:
                        found_processes.append(proc.name())
                        print(f"DEBUG: Found matching process: {proc.name()}")
                        proc.terminate()
                        closed_processes.append(proc.name())
                        print(f"DEBUG: Successfully terminated: {proc.name()}")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    print(f"DEBUG: Error with process {proc}: {e}")
                    continue
                except Exception as e:
                    print(f"DEBUG: Unexpected error with process: {e}")
                    continue
            
            print(f"DEBUG: Found {len(found_processes)} processes, closed {len(closed_processes)}")
            
            if closed_processes:
                unique_closed = list(set(closed_processes))
                return {
                    'success': True,
                    'summary': f"Closed {', '.join(unique_closed)}."
                }
            elif found_processes:
                return {
                    'success': False,
                    'summary': f"Found {app_name} but couldn't close it due to permissions."
                }
            else:
                return {
                    'success': False,
                    'summary': f"I couldn't find any running process for '{app_name}'. Make sure it's running first."
                }
                
        except Exception as e:
            print(f"DEBUG: Exception in close_application: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'summary': f"Error trying to close {app_name}: {str(e)}"
            }

    def control_spotify(self, action: str, query: str = "") -> Dict:
        try:
            if self.os_type == 'windows':
                return self._control_spotify_windows(action, query)
            elif self.os_type == 'linux':
                return self._control_spotify_linux(action, query)
            elif self.os_type == 'darwin':
                return self._control_spotify_macos(action, query)
            else:
                return {
                    'success': False,
                    'summary': f"Spotify control is not supported on {self.os_type}."
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': f"Error controlling Spotify: {str(e)}"
            }

    def _control_spotify_windows(self, action: str, query: str = "") -> Dict:
        try:
            spotify_running = any('spotify' in proc.name().lower() for proc in psutil.process_iter(['name']))
            
            if not spotify_running and action not in ['search_and_play', 'play']:
                return {
                    'success': False,
                    'summary': "Spotify is not running. Please open Spotify first."
                }
                
            # If Spotify is not running but action is 'play', try to start it
            if not spotify_running and action == 'play':
                try:
                    subprocess.Popen(['start', 'spotify'], shell=True)
                    time.sleep(2)  # Wait for Spotify to start
                    return {'success': True, 'summary': "Starting Spotify."}
                except:
                    return {'success': False, 'summary': "Could not start Spotify. Please make sure it's installed."}
            
            try:
                import win32api
                import win32con
                
                if action in ['play', 'pause']:
                    win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
                    win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0)
                    action_text = "Playing" if action == 'play' else "Pausing"
                    return {'success': True, 'summary': f"{action_text} Spotify."}
                    
                elif action == 'next':
                    win32api.keybd_event(win32con.VK_MEDIA_NEXT_TRACK, 0, 0, 0)
                    win32api.keybd_event(win32con.VK_MEDIA_NEXT_TRACK, 0, win32con.KEYEVENTF_KEYUP, 0)
                    return {'success': True, 'summary': "Skipped to next track."}
                    
                elif action == 'previous':
                    win32api.keybd_event(win32con.VK_MEDIA_PREV_TRACK, 0, 0, 0)
                    win32api.keybd_event(win32con.VK_MEDIA_PREV_TRACK, 0, win32con.KEYEVENTF_KEYUP, 0)
                    return {'success': True, 'summary': "Went to previous track."}
                    
            except ImportError:
                pass
            
            try:
                import keyboard
                
                if action in ['play', 'pause']:
                    keyboard.send('play/pause media')
                    action_text = "Playing" if action == 'play' else "Pausing"
                    return {'success': True, 'summary': f"{action_text} Spotify."}
                    
                elif action == 'next':
                    keyboard.send('next track')
                    return {'success': True, 'summary': "Skipped to next track."}
                    
                elif action == 'previous':
                    keyboard.send('previous track')
                    return {'success': True, 'summary': "Went to previous track."}
                    
            except ImportError:
                pass
            
            try:
                if action in ['play', 'pause']:
                    subprocess.run(['nircmd', 'sendkeypress', 'media_play_pause'], check=True, capture_output=True)
                    action_text = "Playing" if action == 'play' else "Pausing"
                    return {'success': True, 'summary': f"{action_text} Spotify."}
                    
                elif action == 'next':
                    subprocess.run(['nircmd', 'sendkeypress', 'media_next'], check=True, capture_output=True)
                    return {'success': True, 'summary': "Skipped to next track."}
                    
                elif action == 'previous':
                    subprocess.run(['nircmd', 'sendkeypress', 'media_prev'], check=True, capture_output=True)
                    return {'success': True, 'summary': "Went to previous track."}
                    
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
            
            if self._focus_spotify_and_send_keys(action):
                action_messages = {
                    'play': "Started Spotify playback.",
                    'pause': "Paused Spotify playback.",
                    'next': "Skipped to next track.",
                    'previous': "Went to previous track."
                }
                return {'success': True, 'summary': action_messages.get(action, "Spotify command sent.")}
            
            if action == 'search_and_play':
                if not query:
                    return {'success': False, 'summary': "What would you like me to search for on Spotify?"}
                    
                spotify_search_url = f"spotify:search:{query.replace(' ', '%20')}"
                subprocess.run(['start', '', spotify_search_url], shell=True)
                return {'success': True, 'summary': f"Opening Spotify and searching for '{query}'."}
            
            return {
                'success': False,
                'summary': f"Could not control Spotify. Try installing 'pip install pywin32' or 'pip install keyboard' for better media control, or use 'nircmd' utility."
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': f"Windows Spotify control failed: {str(e)}"
            }

    def _focus_spotify_and_send_keys(self, action: str) -> bool:
        try:
            subprocess.run(['powershell', '-c',
                          '(New-Object -ComObject Shell.Application).Windows() | Where-Object {$_.Name -like "*Spotify*"} | ForEach-Object {$_.Visible = $true}'],
                          capture_output=True, timeout=5)
            time.sleep(0.5)
            
            if action in ['play', 'pause']:
                subprocess.run(['powershell', '-c',
                              'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait(" ")'],
                              capture_output=True, timeout=5)
                return True
                
            elif action == 'next':
                subprocess.run(['powershell', '-c',
                              'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait("^{RIGHT}")'],
                              capture_output=True, timeout=5)
                return True
                
            elif action == 'previous':
                subprocess.run(['powershell', '-c',
                              'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait("^{LEFT}")'],
                              capture_output=True, timeout=5)
                return True
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass
        
        return False

    def _control_spotify_linux(self, action: str, query: str = "") -> Dict:
        try:
            spotify_service = "org.mpris.MediaPlayer2.spotify"
            player_interface = f"{spotify_service}/org/mpris/MediaPlayer2/Player"
            
            if action == 'play':
                subprocess.run(['dbus-send', '--print-reply', '--dest=' + spotify_service,
                               player_interface, 'org.mpris.MediaPlayer2.Player.Play'],
                               capture_output=True, check=True)
                return {'success': True, 'summary': "Playing Spotify."}
                
            elif action == 'pause':
                subprocess.run(['dbus-send', '--print-reply', '--dest=' + spotify_service,
                               player_interface, 'org.mpris.MediaPlayer2.Player.Pause'],
                               capture_output=True, check=True)
                return {'success': True, 'summary': "Paused Spotify."}
                
            elif action == 'next':
                subprocess.run(['dbus-send', '--print-reply', '--dest=' + spotify_service,
                               player_interface, 'org.mpris.MediaPlayer2.Player.Next'],
                               capture_output=True, check=True)
                return {'success': True, 'summary': "Skipped to next track."}
                
            elif action == 'previous':
                subprocess.run(['dbus-send', '--print-reply', '--dest=' + spotify_service,
                               player_interface, 'org.mpris.MediaPlayer2.Player.Previous'],
                               capture_output=True, check=True)
                return {'success': True, 'summary': "Went to previous track."}
                
            elif action == 'search_and_play':
                if not query:
                    return {'success': False, 'summary': "What would you like me to search for on Spotify?"}
                    
                spotify_search_url = f"spotify:search:{query.replace(' ', '%20')}"
                subprocess.Popen(['xdg-open', spotify_search_url])
                return {'success': True, 'summary': f"Searching for '{query}' on Spotify."}
                
            else:
                return {'success': False, 'summary': f"Unknown Spotify action: {action}"}
                
        except subprocess.CalledProcessError:
            return {
                'success': False,
                'summary': "Spotify is not running or dbus control is not available."
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': f"Linux Spotify control failed: {str(e)}"
            }

    def _control_spotify_macos(self, action: str, query: str = "") -> Dict:
        try:
            if action == 'play':
                subprocess.run(['osascript', '-e', 'tell application "Spotify" to play'],
                               capture_output=True, check=True)
                return {'success': True, 'summary': "Playing Spotify."}
                
            elif action == 'pause':
                subprocess.run(['osascript', '-e', 'tell application "Spotify" to pause'],
                               capture_output=True, check=True)
                return {'success': True, 'summary': "Paused Spotify."}
                
            elif action == 'next':
                subprocess.run(['osascript', '-e', 'tell application "Spotify" to next track'],
                               capture_output=True, check=True)
                return {'success': True, 'summary': "Skipped to next track."}
                
            elif action == 'previous':
                subprocess.run(['osascript', '-e', 'tell application "Spotify" to previous track'],
                               capture_output=True, check=True)
                return {'success': True, 'summary': "Went to previous track."}
                
            elif action == 'search_and_play':
                if not query:
                    return {'success': False, 'summary': "What would you like me to search for on Spotify?"}
                    
                spotify_search_url = f"spotify:search:{query.replace(' ', '%20')}"
                subprocess.run(['open', spotify_search_url])
                return {'success': True, 'summary': f"Searching for '{query}' on Spotify."}
                
            else:
                return {'success': False, 'summary': f"Unknown Spotify action: {action}"}
                
        except subprocess.CalledProcessError:
            return {
                'success': False,
                'summary': "Spotify is not running or AppleScript control failed."
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': f"macOS Spotify control failed: {str(e)}"
            }

    def take_screenshot(self) -> Dict:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(SCREENSHOTS_DIR, filename)
            
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            
            return {
                'success': True,
                'filepath': filepath,
                'summary': f"Screenshot saved as {filename}."
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': "I couldn't take a screenshot."
            }

    def control_volume(self, action: str, level: Optional[int] = None) -> Dict:
        try:
            if self.os_type == 'windows':
                return self._control_volume_windows(action, level)
            elif self.os_type == 'linux':
                return self._control_volume_linux(action, level)
            elif self.os_type == 'darwin':
                return self._control_volume_macos(action, level)
            else:
                return {
                    'success': False,
                    'summary': f"Volume control is not supported on {self.os_type}."
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': f"Error controlling volume: {str(e)}"
            }

    def _control_volume_windows(self, action: str, level: Optional[int] = None) -> Dict:
        """FIXED Windows volume control with proper pycaw integration"""
        
        # Method 1: Use pycaw (most reliable) - CORRECTED
        if self._volume_interface:
            try:
                if action == 'mute':
                    self._volume_interface.SetMute(1, None)
                    return {'success': True, 'summary': "Volume muted."}
                    
                elif action == 'unmute':
                    self._volume_interface.SetMute(0, None)
                    return {'success': True, 'summary': "Volume unmuted."}
                    
                elif action == 'set' and level is not None:
                    # Convert percentage to decibel range
                    min_db, max_db, _ = self._volume_interface.GetVolumeRange()
                    volume_db = min_db + (max_db - min_db) * (level / 100.0)
                    self._volume_interface.SetMasterVolumeLevel(volume_db, None)
                    return {'success': True, 'summary': f"Volume set to {level}%."}
                    
                elif action == 'up':
                    # Get current volume level
                    current_db = self._volume_interface.GetMasterVolumeLevel()
                    min_db, max_db, _ = self._volume_interface.GetVolumeRange()
                    # Increase by 10% of the range
                    step_db = (max_db - min_db) * 0.1
                    new_db = min(max_db, current_db + step_db)
                    self._volume_interface.SetMasterVolumeLevel(new_db, None)
                    
                    # Convert back to percentage for display
                    volume_percent = int(((new_db - min_db) / (max_db - min_db)) * 100)
                    return {'success': True, 'summary': f"Volume increased to {volume_percent}%."}
                    
                elif action == 'down':
                    # Get current volume level
                    current_db = self._volume_interface.GetMasterVolumeLevel()
                    min_db, max_db, _ = self._volume_interface.GetVolumeRange()
                    # Decrease by 10% of the range
                    step_db = (max_db - min_db) * 0.1
                    new_db = max(min_db, current_db - step_db)
                    self._volume_interface.SetMasterVolumeLevel(new_db, None)
                    
                    # Convert back to percentage for display
                    volume_percent = int(((new_db - min_db) / (max_db - min_db)) * 100)
                    return {'success': True, 'summary': f"Volume decreased to {volume_percent}%."}
                    
            except Exception as e:
                print(f"pycaw method failed: {e}")
                # Continue to fallback methods below
        
        # Method 2: Use NirCmd utility (most reliable fallback)
        try:
            if action == 'mute':
                subprocess.run(['nircmd', 'mutesysvolume', '2'], 
                             check=True, capture_output=True, timeout=5)
                return {'success': True, 'summary': "Volume muted/unmuted."}
                
            elif action == 'up':
                subprocess.run(['nircmd', 'changesysvolume', '6553'], 
                             check=True, capture_output=True, timeout=5)
                return {'success': True, 'summary': "Volume increased."}
                
            elif action == 'down':
                subprocess.run(['nircmd', 'changesysvolume', '-6553'], 
                             check=True, capture_output=True, timeout=5)
                return {'success': True, 'summary': "Volume decreased."}
                
            elif action == 'set' and level is not None:
                volume_value = int((level / 100.0) * 65535)
                subprocess.run(['nircmd', 'setsysvolume', str(volume_value)], 
                             check=True, capture_output=True, timeout=5)
                return {'success': True, 'summary': f"Volume set to {level}%."}
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("NirCmd not available")
        except Exception as e:
            print(f"NirCmd error: {e}")
        
        # Method 3: PowerShell with proper key simulation
        try:
            if action == 'mute':
                ps_script = '''
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.SendKeys]::SendWait("{VOLUME_MUTE}")
                '''
                subprocess.run(['powershell', '-Command', ps_script], 
                             check=True, capture_output=True, timeout=5)
                return {'success': True, 'summary': "Volume muted/unmuted."}
                
            elif action == 'up':
                ps_script = '''
                Add-Type -AssemblyName System.Windows.Forms
                for ($i = 0; $i -lt 5; $i++) {
                    [System.Windows.Forms.SendKeys]::SendWait("{VOLUME_UP}")
                    Start-Sleep -Milliseconds 50
                }
                '''
                subprocess.run(['powershell', '-Command', ps_script], 
                             check=True, capture_output=True, timeout=5)
                return {'success': True, 'summary': "Volume increased."}
                
            elif action == 'down':
                ps_script = '''
                Add-Type -AssemblyName System.Windows.Forms
                for ($i = 0; $i -lt 5; $i++) {
                    [System.Windows.Forms.SendKeys]::SendWait("{VOLUME_DOWN}")
                    Start-Sleep -Milliseconds 50
                }
                '''
                subprocess.run(['powershell', '-Command', ps_script], 
                             check=True, capture_output=True, timeout=5)
                return {'success': True, 'summary': "Volume decreased."}
                
        except subprocess.CalledProcessError as e:
            print(f"PowerShell method failed: {e}")
        except Exception as e:
            print(f"PowerShell method error: {e}")
        
        # Method 4: Direct Windows API calls (last resort)
        try:
            import ctypes
            user32 = ctypes.windll.user32
            
            if action == 'mute':
                # VK_VOLUME_MUTE = 0xAD
                user32.keybd_event(0xAD, 0, 0, 0)
                user32.keybd_event(0xAD, 0, 2, 0)
                return {'success': True, 'summary': "Volume muted/unmuted."}
                
            elif action == 'up':
                # VK_VOLUME_UP = 0xAF
                for _ in range(5):
                    user32.keybd_event(0xAF, 0, 0, 0)
                    user32.keybd_event(0xAF, 0, 2, 0)
                return {'success': True, 'summary': "Volume increased."}
                
            elif action == 'down':
                # VK_VOLUME_DOWN = 0xAE
                for _ in range(5):
                    user32.keybd_event(0xAE, 0, 0, 0)
                    user32.keybd_event(0xAE, 0, 2, 0)
                return {'success': True, 'summary': "Volume decreased."}
                
        except Exception as e:
            print(f"Windows API method failed: {e}")
        
        return {
            'success': False,
            'summary': "Could not control volume. Try installing: pip install pycaw, or download nircmd.exe"
        }

    def _control_volume_linux(self, action: str, level: Optional[int] = None) -> Dict:
        """Linux volume control using ALSA/PulseAudio"""
        try:
            # Try PulseAudio first
            if action == 'mute':
                result = subprocess.run(['pactl', 'set-sink-mute', '@DEFAULT_SINK@', 'toggle'],
                                       capture_output=True, timeout=5)
                if result.returncode == 0:
                    return {'success': True, 'summary': "Volume muted/unmuted."}
                    
            elif action == 'unmute':
                subprocess.run(['pactl', 'set-sink-mute', '@DEFAULT_SINK@', '0'],
                              check=True, capture_output=True, timeout=5)
                return {'success': True, 'summary': "Volume unmuted."}
                
            elif action == 'up':
                subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '+10%'],
                              check=True, capture_output=True, timeout=5)
                return {'success': True, 'summary': "Volume increased."}
                
            elif action == 'down':
                subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '-10%'],
                              check=True, capture_output=True, timeout=5)
                return {'success': True, 'summary': "Volume decreased."}
                
            elif action == 'set' and level is not None:
                subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{level}%'],
                              check=True, capture_output=True, timeout=5)
                return {'success': True, 'summary': f"Volume set to {level}%."}
                
        except subprocess.CalledProcessError:
            # Fallback to ALSA
            try:
                if action == 'mute':
                    subprocess.run(['amixer', 'set', 'Master', 'toggle'],
                                  check=True, capture_output=True)
                    return {'success': True, 'summary': "Volume muted/unmuted."}
                    
                elif action == 'unmute':
                    subprocess.run(['amixer', 'set', 'Master', 'unmute'],
                                  check=True, capture_output=True)
                    return {'success': True, 'summary': "Volume unmuted."}
                    
                elif action == 'up':
                    subprocess.run(['amixer', 'set', 'Master', '10%+'],
                                  check=True, capture_output=True)
                    return {'success': True, 'summary': "Volume increased."}
                    
                elif action == 'down':
                    subprocess.run(['amixer', 'set', 'Master', '10%-'],
                                  check=True, capture_output=True)
                    return {'success': True, 'summary': "Volume decreased."}
                    
                elif action == 'set' and level is not None:
                    subprocess.run(['amixer', 'set', 'Master', f'{level}%'],
                                  check=True, capture_output=True)
                    return {'success': True, 'summary': f"Volume set to {level}%."}
                    
            except subprocess.CalledProcessError:
                pass
        
        return {'success': False, 'summary': "Linux volume control failed. Make sure alsa-utils or pulseaudio is installed."}

    def _control_volume_macos(self, action: str, level: Optional[int] = None) -> Dict:
        """macOS volume control using AppleScript"""
        try:
            if action == 'mute':
                subprocess.run(['osascript', '-e', 'set volume output muted true'],
                              check=True, capture_output=True)
                return {'success': True, 'summary': "Volume muted."}
                
            elif action == 'unmute':
                subprocess.run(['osascript', '-e', 'set volume output muted false'],
                              check=True, capture_output=True)
                return {'success': True, 'summary': "Volume unmuted."}
                
            elif action == 'up':
                subprocess.run(['osascript', '-e',
                               'set volume output volume (output volume of (get volume settings) + 10)'],
                               check=True, capture_output=True)
                return {'success': True, 'summary': "Volume increased."}
                
            elif action == 'down':
                subprocess.run(['osascript', '-e',
                               'set volume output volume (output volume of (get volume settings) - 10)'],
                               check=True, capture_output=True)
                return {'success': True, 'summary': "Volume decreased."}
                
            elif action == 'set' and level is not None:
                subprocess.run(['osascript', '-e', f'set volume output volume {level}'],
                              check=True, capture_output=True)
                return {'success': True, 'summary': f"Volume set to {level}%."}
                
        except subprocess.CalledProcessError as e:
            return {'success': False, 'summary': f"macOS volume control failed: {e}"}
        
        return {'success': False, 'summary': "Invalid macOS volume action."}

    def get_current_time(self) -> Dict:
        try:
            now = datetime.now()
            current_time = now.strftime("%I:%M %p")
            current_date = now.strftime("%A, %B %d, %Y")
            
            return {
                'success': True,
                'time': current_time,
                'date': current_date,
                'summary': f"It's currently {current_time} on {current_date}."
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': "I couldn't get the current time."
            }

    def list_running_processes(self) -> Dict:
        """List all running processes"""
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

    def _bytes_to_gb(self, bytes_value: int) -> float:
        """Convert bytes to gigabytes"""
        return bytes_value / (1024 ** 3)

    def example_custom_action(self, entities: Dict) -> Dict:
        """Example of how to add custom actions"""
        return {
            'success': True,
            'summary': "This is a custom action! You can extend the assistant by adding more functions like this."
        }
