import speech_recognition as sr
from mtranslate import translate
from colorama import Fore, init
import time

init(autoreset=True)

def telugu_speech_recognition() -> str | None:

    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 0.8
    recognizer.operation_timeout = None
    recognizer.phrase_threshold = 0.3
    recognizer.energy_threshold = 34000
    recognizer.dynamic_energy_ratio = 1.0
    recognizer.non_speaking_duration = 0.5
    recognizer.dynamic_energy_threshold = True
    recognizer.dynamic_energy_adjustment_damping = 0.010

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        translated_text = "" 
        
        while True:
            print("\r" + "🎙" + Fore.GREEN + "Listening...", end="", flush=True)

            try:
                audio = recognizer.listen(source, timeout=None)
                print("💡" + "\r" + Fore.BLUE + "Recognizing...", end="", flush=True)
                
                recognized_text = recognizer.recognize_google(audio, language="te-IN")
                if recognized_text:
                    translated_text = translate(recognized_text)
                    return translated_text
                else:
                    print("\r" + Fore.RED + "No speech detected, try again.", flush=True)
                    return ""

            except sr.UnknownValueError:
                print("\r" + Fore.YELLOW + "Could not understand the audio. Please speak clearly.", flush=True)

            except sr.RequestError as e:
                print(f"\r{Fore.RED}RequestError: Could not request results; {e}", flush=True)
                return None

            finally:
                print("\r", end="", flush=True)

    return translated_text

if __name__ == "__main__":
    while True:
        st = time.time()
        x = telugu_speech_recognition()
        print(x)
        ed = time.time()
        print(f"Time taken: {ed - st} seconds")







































































############################### V E R S I O N -- 1 ##########################################
import os
import pyaudio
import websocket
import json
import threading
import time
import wave
from urllib.parse import urlencode
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

# --- Configuration ---
YOUR_API_KEY = os.getenv("ASSEMBLY_API")  

CONNECTION_PARAMS = {
    "sample_rate": 16000,
    "format_turns": True,  # Request formatted final transcripts
}
API_ENDPOINT_BASE_URL = "wss://streaming.assemblyai.com/v3/ws"
API_ENDPOINT = f"{API_ENDPOINT_BASE_URL}?{urlencode(CONNECTION_PARAMS)}"

# Audio Configuration
FRAMES_PER_BUFFER = 800  # 50ms of audio (0.05s * 16000Hz)
SAMPLE_RATE = CONNECTION_PARAMS["sample_rate"]
CHANNELS = 1
FORMAT = pyaudio.paInt16

# Global variables for audio stream and websocket
audio = None
stream = None
ws_app = None
audio_thread = None
stop_event = threading.Event()  # To signal the audio thread to stop

# Global variables to store transcripts
current_transcript = ""
final_transcripts = []
transcript_lock = threading.Lock()  # Thread-safe access to transcript variables


# --- WebSocket Event Handlers ---
def on_open(ws):
    """Called when the WebSocket connection is established."""
    print("WebSocket connection opened.")
    print(f"Connected to: {API_ENDPOINT}")
    # Start sending audio data in a separate thread
    def stream_audio():
        global stream
        print("Starting audio streaming...")
        while not stop_event.is_set():
            try:
                audio_data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                
                # Send audio data as binary message
                ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)
            except Exception as e:
                print(f"Error streaming audio: {e}")
                # If stream read fails, likely means it's closed, stop the loop
                break
        print("Audio streaming stopped.")
    
    global audio_thread
    audio_thread = threading.Thread(target=stream_audio)
    audio_thread.daemon = True  # Allow main thread to exit even if this thread is running
    audio_thread.start()


def on_message(ws, message):
    global current_transcript, final_transcripts
    
    try:
        data = json.loads(message)
        msg_type = data.get('type')
        
        if msg_type == "Begin":
            session_id = data.get('id')
            expires_at = data.get('expires_at')
            print(f"Session began: ID={session_id}, ExpiresAt={datetime.fromtimestamp(expires_at)}")
            print("Listening...")
            
        elif msg_type == "Turn":
            transcript = data.get('transcript', '')
            formatted = data.get('turn_is_formatted', False)
            
            with transcript_lock:
                if formatted:
                    # This is a final transcript
                    print(f"\r{transcript}")
                    final_transcripts.append(transcript)
                    current_transcript = transcript
                    # Print each final transcript as it comes in
                    print(f"Final transcript: {transcript}")
                else:
                    # This is a partial transcript
                    print(f"\r{transcript}", end='')
                    current_transcript = transcript
                    
        elif msg_type == "Termination":
            audio_duration = data.get('audio_duration_seconds', 0)
            session_duration = data.get('session_duration_seconds', 0)
            print(f"Session Terminated: Audio Duration={audio_duration}s, Session Duration={session_duration}s")
            
    except json.JSONDecodeError as e:
        print(f"Error decoding message: {e}")
    except Exception as e:
        print(f"Error handling message: {e}")


def on_error(ws, error):
    """Called when a WebSocket error occurs."""
    print(f"WebSocket Error: {error}")
    # Attempt to signal stop on error
    stop_event.set()


def on_close(ws, close_status_code, close_msg):
    """Called when the WebSocket connection is closed."""
    print(f"WebSocket Disconnected: Status={close_status_code}, Msg={close_msg}")

    # Ensure audio resources are released
    global stream, audio
    stop_event.set()  # Signal audio thread just in case it's still running
    if stream:
        if stream.is_active():
            stream.stop_stream()
        stream.close()
        stream = None
    if audio:
        audio.terminate()
        audio = None
    # Try to join the audio thread to ensure clean exit
    if audio_thread and audio_thread.is_alive():
        audio_thread.join(timeout=1.0)


# --- Helper Functions ---
def get_current_transcript():
    """Get the current transcript (thread-safe)"""
    with transcript_lock:
        return current_transcript


def get_all_final_transcripts():
    """Get all final transcripts (thread-safe)"""
    with transcript_lock:
        return final_transcripts.copy()


def get_full_transcript():
    """Get the complete transcript as a single string"""
    with transcript_lock:
        return " ".join(final_transcripts)


# --- Main Execution ---
def run():
    global audio, stream, ws_app
    
    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    
    # Open microphone stream
    try:
        stream = audio.open(
            input=True,
            frames_per_buffer=FRAMES_PER_BUFFER,
            channels=CHANNELS,
            format=FORMAT,
            rate=SAMPLE_RATE,
        )
    except Exception as e:
        print(f"Error opening microphone stream: {e}")
        if audio:
            audio.terminate()
        return  # Exit if microphone cannot be opened
    
    # Create WebSocketApp
    ws_app = websocket.WebSocketApp(
        API_ENDPOINT,
        header={"Authorization": YOUR_API_KEY},
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    
    # Run WebSocketApp in a separate thread to allow main thread to catch KeyboardInterrupt
    ws_thread = threading.Thread(target=ws_app.run_forever)
    ws_thread.daemon = True
    ws_thread.start()
    
    try:
        # Keep main thread alive until interrupted
        while ws_thread.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Ctrl+C received. Stopping...")
        stop_event.set()  # Signal audio thread to stop
        
        # Send termination message to the server
        if ws_app and ws_app.sock and ws_app.sock.connected:
            try:
                terminate_message = {"type": "Terminate"}
                print(f"Sending termination message: {json.dumps(terminate_message)}")
                ws_app.send(json.dumps(terminate_message))
                # Give a moment for messages to process before forceful close
                time.sleep(1)
            except Exception as e:
                print(f"Error sending termination message: {e}")
        
        # Close the WebSocket connection (will trigger on_close)
        if ws_app:
            ws_app.close()
        
        # Wait for WebSocket thread to finish
        ws_thread.join(timeout=2.0)
        
        # Print final transcript summary
        final_transcript = get_full_transcript()
        if final_transcript:
            print(f"\n\nComplete Transcript: {final_transcript}")
        else:
            print(f"\n\nNo final transcript available")
            
        print(f"All final transcripts: {get_all_final_transcripts()}")
        return final_transcript
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        stop_event.set()
        if ws_app:
            ws_app.close()
        ws_thread.join(timeout=2.0)
    finally:
        # Final cleanup (already handled in on_close, but good as a fallback)
        if stream and stream.is_active():
            stream.stop_stream()
        if stream:
            stream.close()
        if audio:
            audio.terminate()
        print("Cleanup complete. Exiting.")


# if __name__ == "__main__":
#     transcript = run()
#     if transcript:
#         print(f"Returned transcript: {transcript}")


































































################################## V E R S I O N -- 2 ##############################
import os
import pyaudio
import websocket
import json
import threading
import time
from urllib.parse import urlencode
from datetime import datetime
from dotenv import load_dotenv


class SpeechToText:
    def __init__(self):
        load_dotenv()
        
        # Configuration
        self.api_key = os.getenv("ASSEMBLY_API")
        self.connection_params = {
            "sample_rate": 16000,
            "format_turns": True,
        }
        self.api_endpoint = f"wss://streaming.assemblyai.com/v3/ws?{urlencode(self.connection_params)}"
        
        # Audio Configuration
        self.frames_per_buffer = 800
        self.sample_rate = self.connection_params["sample_rate"]
        self.channels = 1
        self.format = pyaudio.paInt16
        
        # Instance variables
        self.audio = None
        self.stream = None
        self.ws_app = None
        self.audio_thread = None
        self.stop_event = threading.Event()
        
        # Transcript storage
        self.current_transcript = ""
        self.final_transcripts = []
        self.transcript_lock = threading.Lock()
        
    def on_open(self, ws):
        """Called when the WebSocket connection is established."""
        print("WebSocket connection opened.")
        print(f"Connected to: {self.api_endpoint}")
        
        def stream_audio():
            print("Starting audio streaming...")
            while not self.stop_event.is_set():
                try:
                    audio_data = self.stream.read(self.frames_per_buffer, exception_on_overflow=False)
                    ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)
                except Exception as e:
                    print(f"Error streaming audio: {e}")
                    break
            print("Audio streaming stopped.")
        
        self.audio_thread = threading.Thread(target=stream_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()
    
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == "Begin":
                session_id = data.get('id')
                expires_at = data.get('expires_at')
                print(f"Session began: ID={session_id}, ExpiresAt={datetime.fromtimestamp(expires_at)}")
                print("Listening...")
                
            elif msg_type == "Turn":
                transcript = data.get('transcript', '')
                formatted = data.get('turn_is_formatted', False)
                
                with self.transcript_lock:
                    if formatted:
                        print(f"\r{transcript}")
                        self.final_transcripts.append(transcript)
                        self.current_transcript = transcript
                        # Print each final transcript as it comes in
                        print(f"Final transcript: {transcript}")
                    else:
                        print(f"\r{transcript}", end='')
                        self.current_transcript = transcript
                        
            elif msg_type == "Termination":
                audio_duration = data.get('audio_duration_seconds', 0)
                session_duration = data.get('session_duration_seconds', 0)
                print(f"Session Terminated: Audio Duration={audio_duration}s, Session Duration={session_duration}s")
                
        except json.JSONDecodeError as e:
            print(f"Error decoding message: {e}")
        except Exception as e:
            print(f"Error handling message: {e}")
    
    def on_error(self, ws, error):
        """Called when a WebSocket error occurs."""
        print(f"WebSocket Error: {error}")
        self.stop_event.set()
    
    def on_close(self, ws, close_status_code, close_msg):
        """Called when the WebSocket connection is closed."""
        print(f"WebSocket Disconnected: Status={close_status_code}, Msg={close_msg}")
        self.cleanup()
    
    def cleanup(self):
        """Clean up audio resources"""
        self.stop_event.set()
        if self.stream:
            if self.stream.is_active():
                self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        if self.audio:
            self.audio.terminate()
            self.audio = None
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1.0)
    
    def get_current_transcript(self):
        """Get the current transcript (thread-safe)"""
        with self.transcript_lock:
            return self.current_transcript
    
    def get_all_final_transcripts(self):
        """Get all final transcripts (thread-safe)"""
        with self.transcript_lock:
            return self.final_transcripts.copy()
    
    def get_full_transcript(self):
        """Get the complete transcript as a single string"""
        with self.transcript_lock:
            return " ".join(self.final_transcripts)
    
    def start_recording(self):
        """Start the speech-to-text recording session"""
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        
        # Open microphone stream
        try:
            self.stream = self.audio.open(
                input=True,
                frames_per_buffer=self.frames_per_buffer,
                channels=self.channels,
                format=self.format,
                rate=self.sample_rate,
            )
        except Exception as e:
            print(f"Error opening microphone stream: {e}")
            if self.audio:
                self.audio.terminate()
            return None
        
        # Create WebSocketApp
        self.ws_app = websocket.WebSocketApp(
            self.api_endpoint,
            header={"Authorization": self.api_key},
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        
        # Run WebSocketApp in a separate thread
        ws_thread = threading.Thread(target=self.ws_app.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
        
        try:
            print("Listening... Press Ctrl+C to stop.")
            while ws_thread.is_alive():
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Ctrl+C received. Stopping...")
            self.stop_recording()
            
        # Wait for WebSocket thread to finish
        ws_thread.join(timeout=2.0)
        
        # Return the final transcript
        final_transcript = self.get_full_transcript()
        if final_transcript:
            print(f"\n\nComplete Transcript: {final_transcript}")
        else:
            print(f"\n\nNo final transcript available")
            
        print(f"All final transcripts: {self.get_all_final_transcripts()}")
        return final_transcript
    
    def stop_recording(self):
        """Stop the recording session"""
        self.stop_event.set()
        
        # Send termination message to the server
        if self.ws_app and self.ws_app.sock and self.ws_app.sock.connected:
            try:
                terminate_message = {"type": "Terminate"}
                print(f"Sending termination message: {json.dumps(terminate_message)}")
                self.ws_app.send(json.dumps(terminate_message))
                time.sleep(1)
            except Exception as e:
                print(f"Error sending termination message: {e}")
        
        # Close the WebSocket connection
        if self.ws_app:
            self.ws_app.close()
        
        self.cleanup()


def main():
    """Main function to run the speech-to-text application"""
    stt = SpeechToText()
    transcript = stt.start_recording()
    
    if transcript:
        print(f"Returned transcript: {transcript}")
        return transcript
    else:
        print("No transcript available")
        return None


# if __name__ == "__main__":
#     main()



import os
import pyaudio
import websocket
import json
import threading
import time
from urllib.parse import urlencode
from datetime import datetime
from dotenv import load_dotenv


class SpeechToText:
    def __init__(self, on_final_transcript=None, on_partial_transcript=None):
        load_dotenv()
        
        # Configuration
        self.api_key = os.getenv("ASSEMBLY_API")
        self.connection_params = {
            "sample_rate": 16000,
            "format_turns": True,
        }
        self.api_endpoint = f"wss://streaming.assemblyai.com/v3/ws?{urlencode(self.connection_params)}"
        
        # Audio Configuration
        self.frames_per_buffer = 800
        self.sample_rate = self.connection_params["sample_rate"]
        self.channels = 1
        self.format = pyaudio.paInt16
        
        # Instance variables
        self.audio = None
        self.stream = None
        self.ws_app = None
        self.audio_thread = None
        self.stop_event = threading.Event()
        
        # Transcript storage
        self.current_transcript = ""
        self.final_transcripts = []
        self.transcript_lock = threading.Lock()
        
        # Callback functions
        self.on_final_transcript = on_final_transcript
        self.on_partial_transcript = on_partial_transcript
        
    def on_open(self, ws):
        """Called when the WebSocket connection is established."""
        print("WebSocket connection opened.")
        print(f"Connected to: {self.api_endpoint}")
        
        def stream_audio():
            print("Starting audio streaming...")
            while not self.stop_event.is_set():
                try:
                    audio_data = self.stream.read(self.frames_per_buffer, exception_on_overflow=False)
                    ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)
                except Exception as e:
                    print(f"Error streaming audio: {e}")
                    break
            print("Audio streaming stopped.")
        
        self.audio_thread = threading.Thread(target=stream_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()
    
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == "Begin":
                session_id = data.get('id')
                expires_at = data.get('expires_at')
                print(f"Session began: ID={session_id}, ExpiresAt={datetime.fromtimestamp(expires_at)}")
                print("Listening...")
                
            elif msg_type == "Turn":
                transcript = data.get('transcript', '')
                formatted = data.get('turn_is_formatted', False)
                
                with self.transcript_lock:
                    if formatted:
                        # This is a final transcript
                        print(f"\r{transcript}")
                        self.final_transcripts.append(transcript)
                        self.current_transcript = transcript
                        
                        # Print each final transcript as it comes in
                        print(f"Final transcript: {transcript}")
                        
                        # Call the callback if provided
                        if self.on_final_transcript:
                            self.on_final_transcript(transcript)
                    else:
                        # This is a partial transcript
                        print(f"\r{transcript}", end='')
                        self.current_transcript = transcript
                        
                        # Call the callback if provided
                        if self.on_partial_transcript:
                            self.on_partial_transcript(transcript)
                        
            elif msg_type == "Termination":
                audio_duration = data.get('audio_duration_seconds', 0)
                session_duration = data.get('session_duration_seconds', 0)
                print(f"Session Terminated: Audio Duration={audio_duration}s, Session Duration={session_duration}s")
                
        except json.JSONDecodeError as e:
            print(f"Error decoding message: {e}")
        except Exception as e:
            print(f"Error handling message: {e}")
    
    def on_error(self, ws, error):
        """Called when a WebSocket error occurs."""
        print(f"WebSocket Error: {error}")
        self.stop_event.set()
    
    def on_close(self, ws, close_status_code, close_msg):
        """Called when the WebSocket connection is closed."""
        print(f"WebSocket Disconnected: Status={close_status_code}, Msg={close_msg}")
        self.cleanup()
    
    def cleanup(self):
        """Clean up audio resources"""
        self.stop_event.set()
        if self.stream:
            if self.stream.is_active():
                self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        if self.audio:
            self.audio.terminate()
            self.audio = None
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1.0)
    
    def get_current_transcript(self):
        """Get the current transcript (thread-safe)"""
        with self.transcript_lock:
            return self.current_transcript
    
    def get_all_final_transcripts(self):
        """Get all final transcripts (thread-safe)"""
        with self.transcript_lock:
            return self.final_transcripts.copy()
    
    def get_full_transcript(self):
        """Get the complete transcript as a single string"""
        with self.transcript_lock:
            return " ".join(self.final_transcripts)
    
    def start_recording(self):
        """Start the speech-to-text recording session"""
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        
        # Open microphone stream
        try:
            self.stream = self.audio.open(
                input=True,
                frames_per_buffer=self.frames_per_buffer,
                channels=self.channels,
                format=self.format,
                rate=self.sample_rate,
            )
        except Exception as e:
            print(f"Error opening microphone stream: {e}")
            if self.audio:
                self.audio.terminate()
            return None
        
        # Create WebSocketApp
        self.ws_app = websocket.WebSocketApp(
            self.api_endpoint,
            header={"Authorization": self.api_key},
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        
        # Run WebSocketApp in a separate thread
        ws_thread = threading.Thread(target=self.ws_app.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
        
        try:
            print("Listening... Press Ctrl+C to stop.")
            while ws_thread.is_alive():
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Ctrl+C received. Stopping...")
            self.stop_recording()
            
        # Wait for WebSocket thread to finish
        ws_thread.join(timeout=2.0)
        
        # Return the final transcript
        final_transcript = self.get_full_transcript()
        all_transcripts = self.get_all_final_transcripts()
        
        print(f"\n\nComplete Transcript: {final_transcript}")
        print(f"All final transcripts: {all_transcripts}")
        
        return {
            "full_transcript": final_transcript,
            "all_transcripts": all_transcripts
        }
    
    def stop_recording(self):
        """Stop the recording session"""
        self.stop_event.set()
        
        # Send termination message to the server
        if self.ws_app and self.ws_app.sock and self.ws_app.sock.connected:
            try:
                terminate_message = {"type": "Terminate"}
                print(f"Sending termination message: {json.dumps(terminate_message)}")
                self.ws_app.send(json.dumps(terminate_message))
                time.sleep(1)
            except Exception as e:
                print(f"Error sending termination message: {e}")
        
        # Close the WebSocket connection
        if self.ws_app:
            self.ws_app.close()
        
        self.cleanup()


# Example usage with callbacks
def handle_final_transcript(transcript):
    """Called whenever a final transcript is received"""
    return f"📝 FINAL: {transcript}"
    # You can process the transcript here (save to file, send to API, etc.)

def handle_partial_transcript(transcript):
    """Called whenever a partial transcript is received"""
    # Uncomment this if you want to see partial transcripts
    # print(f"🔄 PARTIAL: {transcript}")
    pass

def main():
    """Main function to run the speech-to-text application"""
    stt = SpeechToText(
        on_final_transcript=handle_final_transcript,
        on_partial_transcript=handle_partial_transcript
    )


    print("stt: ", stt)
    result = stt.start_recording()
    
    if result:
        print(f"\n=== FINAL RESULTS ===")
        print(f"Complete transcript: {result['full_transcript']}")
        print(f"Individual transcripts: {result['all_transcripts']}")
        return result
    else:
        print("No transcript available")
        return None


# if __name__ == "__main__":
#     main()
















































# import os
# import pyaudio
# import websocket
# import json
# import threading
# import time
# import wave
# from urllib.parse import urlencode
# from datetime import datetime
# from dotenv import load_dotenv


# load_dotenv()

# # --- Configuration ---
# YOUR_API_KEY = os.getenv("ASSEMBLY_API")  

# CONNECTION_PARAMS = {
#     "sample_rate": 16000,
#     "format_turns": True,  # Request formatted final transcripts
# }
# API_ENDPOINT_BASE_URL = "wss://streaming.assemblyai.com/v3/ws"
# API_ENDPOINT = f"{API_ENDPOINT_BASE_URL}?{urlencode(CONNECTION_PARAMS)}"
# # Audio Configuration
# FRAMES_PER_BUFFER = 800  # 50ms of audio (0.05s * 16000Hz)
# SAMPLE_RATE = CONNECTION_PARAMS["sample_rate"]
# CHANNELS = 1
# FORMAT = pyaudio.paInt16
# # Global variables for audio stream and websocket
# audio = None
# stream = None
# ws_app = None
# audio_thread = None
# stop_event = threading.Event()  # To signal the audio thread to stop


# # --- WebSocket Event Handlers ---
# def on_open(ws):
#     """Called when the WebSocket connection is established."""
#     print("WebSocket connection opened.")
#     print(f"Connected to: {API_ENDPOINT}")
#     # Start sending audio data in a separate thread
#     def stream_audio():
#         global stream
#         print("Starting audio streaming...")
#         while not stop_event.is_set():
#             try:
#                 audio_data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                
#                 # Send audio data as binary message
#                 ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)
#             except Exception as e:
#                 print(f"Error streaming audio: {e}")
#                 # If stream read fails, likely means it's closed, stop the loop
#                 break
#         print("Audio streaming stopped.")
#     global audio_thread
#     audio_thread = threading.Thread(target=stream_audio)
#     audio_thread.daemon = (
#         True  # Allow main thread to exit even if this thread is running
#     )
#     audio_thread.start()
# def on_message(ws, message):
#     try:
#         data = json.loads(message)
#         msg_type = data.get('type')
#         if msg_type == "Begin":
#             session_id = data.get('id')
#             expires_at = data.get('expires_at')
#             print(f"Session began: ID={session_id}, ExpiresAt={datetime.fromtimestamp(expires_at)}")
#             print("Listening...")
#         elif msg_type == "Turn":
#             transcript = data.get('transcript', '')
#             formatted = data.get('turn_is_formatted', False)
#             # Clear previous line for formatted messages
#             if formatted:
#                 print(f"\r{transcript}")
#                 return transcript
#             else:
#                 print(f"\r{transcript}", end='')
#                 return transcript
#         elif msg_type == "Termination":
#             audio_duration = data.get('audio_duration_seconds', 0)
#             session_duration = data.get('session_duration_seconds', 0)
#             print(f"Session Terminated: Audio Duration={audio_duration}s, Session Duration={session_duration}s")
#     except json.JSONDecodeError as e:
#         print(f"Error decoding message: {e}")
#     except Exception as e:
#         print(f"Error handling message: {e}")
# def on_error(ws, error):
#     """Called when a WebSocket error occurs."""
#     print(f"WebSocket Error: {error}")
#     # Attempt to signal stop on error
#     stop_event.set()
# def on_close(ws, close_status_code, close_msg):
#     """Called when the WebSocket connection is closed."""
#     print(f"WebSocket Disconnected: Status={close_status_code}, Msg={close_msg}")

    
#     # Ensure audio resources are released
#     global stream, audio
#     stop_event.set()  # Signal audio thread just in case it's still running
#     if stream:
#         if stream.is_active():
#             stream.stop_stream()
#         stream.close()
#         stream = None
#     if audio:
#         audio.terminate()
#         audio = None
#     # Try to join the audio thread to ensure clean exit
#     if audio_thread and audio_thread.is_alive():
#         audio_thread.join(timeout=1.0)
# # --- Main Execution ---
# def run():
    
#     global audio, stream, ws_app
#     # Initialize PyAudio
#     audio = pyaudio.PyAudio()
#     # Open microphone stream
#     try:
#         stream = audio.open(
#             input=True,
#             frames_per_buffer=FRAMES_PER_BUFFER,
#             channels=CHANNELS,
#             format=FORMAT,
#             rate=SAMPLE_RATE,
#         )
#         #print("Microphone stream opened successfully.")
#         #print("Speak into your microphone. Press Ctrl+C to stop.")
#     except Exception as e:
#         print(f"Error opening microphone stream: {e}")
#         if audio:
#             audio.terminate()
#         return  # Exit if microphone cannot be opened
#     # Create WebSocketApp
#     ws_app = websocket.WebSocketApp(
#         API_ENDPOINT,
#         header={"Authorization": YOUR_API_KEY},
#         on_open=on_open,
#         on_message=on_message,
#         on_error=on_error,
#         on_close=on_close,
#     )
#     # Run WebSocketApp in a separate thread to allow main thread to catch KeyboardInterrupt
#     ws_thread = threading.Thread(target=ws_app.run_forever)
#     ws_thread.daemon = True
#     ws_thread.start()
#     try:
#         # Keep main thread alive until interrupted
#         print("Listening...")
#         while ws_thread.is_alive():
#             time.sleep(0.1)
#     except KeyboardInterrupt:
#         print("Ctrl+C received. Stopping...")
#         stop_event.set()  # Signal audio thread to stop
#         # Send termination message to the server
#         if ws_app and ws_app.sock and ws_app.sock.connected:
            
#             try:
#                 terminate_message = {"type": "Terminate"}
#                 print(f"Sending termination message: {json.dumps(terminate_message)}")
#                 ws_app.send(json.dumps(terminate_message))
#                 # Give a moment for messages to process before forceful close
#                 time.sleep(5)
#             except Exception as e:
#                 print(f"Error sending termination message: {e}")
#         # Close the WebSocket connection (will trigger on_close)
#         if ws_app:
#             ws_app.close()
#         # Wait for WebSocket thread to finish
#         ws_thread.join(timeout=2.0)
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#         stop_event.set()
#         if ws_app:
#             ws_app.close()
#         ws_thread.join(timeout=2.0)
#     finally:
#         # Final cleanup (already handled in on_close, but good as a fallback)
#         if stream and stream.is_active():
#             stream.stop_stream()
#         if stream:
#             stream.close()
#         if audio:
#             audio.terminate()
#         print("Cleanup complete. Exiting.")
        
# if __name__ == "__main__":
#     run()


