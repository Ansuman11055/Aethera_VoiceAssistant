import sys
import io
import struct

class MockAifc:
    def __init__(self):
        pass
    
    def open(self, file, mode=None):
        return MockAifcFile()
    
    Error = Exception

class MockAifcFile:
    def __init__(self):
        self._framerate = 16000
        self._nchannels = 1
        self._sampwidth = 2
        
    def getframerate(self):
        return self._framerate
    
    def getnchannels(self):
        return self._nchannels
    
    def getsampwidth(self):
        return self._sampwidth
    
    def readframes(self, nframes):
        return b''
    
    def close(self):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

sys.modules['aifc'] = MockAifc()