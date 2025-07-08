import requests
import base64
import logging
import re
import threading
import queue
import time
import os
import hashlib
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, wait, TimeoutError
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class SpeechSynthesizer:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.cache_dir = "core/assets/audio_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        threading.Thread(target=self._audio_playback_handler, daemon=True).start()

    def _get_hash(self, text, voice_model):
        return hashlib.md5(f"{voice_model}:{text}".encode()).hexdigest()

    def _generate_audio_chunk(self, text, voice_model, chunk_id):
        url = "https://deepgram.com/api/ttsAudioGeneration"
        headers = {"accept": "*/*", "content-type": "application/json"}

        text_hash = self._get_hash(text, voice_model)
        cached_file = os.path.join(self.cache_dir, f"{text_hash}.mp3")

        if os.path.exists(cached_file):
            logging.info(f"Cache hit for chunk {chunk_id}")
            with open(cached_file, 'rb') as f:
                return chunk_id, f.read()

        while True:
            try:
                payload = {"text": text, "model": voice_model}
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                audio_data = response.json().get("data")
                if audio_data:
                    audio_bytes = base64.b64decode(audio_data)
                    with open(cached_file, 'wb') as f:
                        f.write(audio_bytes)
                    return chunk_id, audio_bytes
                else:
                    time.sleep(1)
            except requests.RequestException as e:
                logging.warning(f"Retrying chunk {chunk_id}: {e}")
                time.sleep(1)

    def speak(self, text, voice_name="Athena", output_file=os.getcwd() + "\\core\\assets\\output_audio.mp3", max_wait=60, fallback_language="en"):        
        available_voices = {
            "Asteria": "aura-asteria-en", "Arcas": "aura-arcas-en", "Luna": "aura-luna-en",
            "Zeus": "aura-zeus-en", "Orpheus": "aura-orpheus-en", "Angus": "aura-angus-en",
            "Athena": "aura-athena-en", "Helios": "aura-helios-en", "Hera": "aura-hera-en",
            "Orion": "aura-orion-en", "Perseus": "aura-perseus-en", "Stella": "aura-stella-en",
            "Jupiter": "aura-2-jupiter-en", "Thalia": "aura-2-thalia-en", "apollo":"aura-2-apollo-en"
        }

        if voice_name not in available_voices:
            logging.error(f"Invalid voice name: {voice_name}. Available voices are: {list(available_voices)}")
            return

        model = available_voices[voice_name]
        sentences = re.split(r'(?<!\b\w\.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text.strip())

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._generate_audio_chunk, sentence.strip(), model, idx)
                for idx, sentence in enumerate(sentences)
            ]

            try:
                done, _ = wait(futures, timeout=max_wait)
                if not done:
                    raise TimeoutError("TTS generation timed out.")

                audio_parts = {}
                for future in done:
                    idx, data = future.result()
                    audio_parts[idx] = data

                combined = BytesIO()
                for idx in sorted(audio_parts.keys()):
                    combined.write(audio_parts[idx])

                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, 'wb') as f:
                    f.write(combined.getvalue())

                logging.info(f"Final TTS audio saved to {output_file}")
                self.queue_audio(output_file)

            except TimeoutError:
                logging.error("Speech generation timed out.")
                if fallback_language != "en":
                    logging.info(f"Attempting fallback to {fallback_language} voice...")
                    self.speak(text, voice_name="Athena", output_file=output_file, max_wait=max_wait, fallback_language="en")

    async def speak_async(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.speak, *args, **kwargs)

    def _audio_playback_handler(self):
        from playsound import playsound
        while True:
            filename = self.audio_queue.get()
            if filename is None:
                break
            while not os.path.exists(filename):
                time.sleep(0.1)
            try:
                playsound(filename)
            except Exception as e:
                logging.error(f"Error playing {filename}: {e}")
            finally:
                try:
                    os.remove(filename)
                except Exception:
                    pass
                self.audio_queue.task_done()

    def queue_audio(self, filename):
        self.audio_queue.put(filename)

    def wait_for_playback_completion(self):
        self.audio_queue.join()



# Example usage
if __name__ == "__main__":
    speaker = SpeechSynthesizer()
    #speaker.speak('Sir! Should I send the message right now? Are we working on a new project? shall I store in chandu database?', voice_name="apollo", max_wait=60)
    #speaker.speak('I understood sir. We are under trouble. I find some ways to solve!', voice_name="Jupiter", max_wait=60)
    speaker.speak('Hello Sir!, Good Evening. I am your personal assistant. How can I help you?')
    speaker.wait_for_playback_completion()


































































































# import requests
# import base64
# import logging
# import re
# import threading
# import queue
# import time
# import os
# import hashlib
# from io import BytesIO
# from concurrent.futures import ThreadPoolExecutor, as_completed, wait, TimeoutError

# # Setup logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# class SpeechSynthesizer:
#     def __init__(self):
#         self.audio_queue = queue.Queue()
#         self.cache_dir = "core/assets/audio_cache"
#         os.makedirs(self.cache_dir, exist_ok=True)
#         threading.Thread(target=self._audio_playback_handler, daemon=True).start()

#     def _get_hash(self, text, voice_model):
#         return hashlib.md5(f"{voice_model}:{text}".encode()).hexdigest()

#     def _generate_audio_chunk(self, text, voice_model, chunk_id):
#         url = "https://deepgram.com/api/ttsAudioGeneration"
#         headers = {"accept": "*/*", "content-type": "application/json"}

#         text_hash = self._get_hash(text, voice_model)
#         cached_file = os.path.join(self.cache_dir, f"{text_hash}.mp3")

#         if os.path.exists(cached_file):
#             logging.info(f"Cache hit for chunk {chunk_id}")
#             with open(cached_file, 'rb') as f:
#                 return chunk_id, f.read()

#         while True:
#             try:
#                 payload = {"text": text, "model": voice_model}
#                 response = requests.post(url, headers=headers, json=payload, timeout=30)
#                 response.raise_for_status()
#                 audio_data = response.json().get("data")
#                 if audio_data:
#                     audio_bytes = base64.b64decode(audio_data)
#                     with open(cached_file, 'wb') as f:
#                         f.write(audio_bytes)
#                     return chunk_id, audio_bytes
#                 else:
#                     time.sleep(1)
#             except requests.RequestException as e:
#                 logging.warning(f"Retrying chunk {chunk_id}: {e}")
#                 time.sleep(1)

#     def speak(self, text, voice_name="Athena", output_file="core/assets/output_audio.mp3", max_wait=60, fallback_language="en"):
#         available_voices = {
#             "Asteria": "aura-asteria-en", "Arcas": "aura-arcas-en", "Luna": "aura-luna-en",
#             "Zeus": "aura-zeus-en", "Orpheus": "aura-orpheus-en", "Angus": "aura-angus-en",
#             "Athena": "aura-athena-en", "Helios": "aura-helios-en", "Hera": "aura-hera-en",
#             "Orion": "aura-orion-en", "Perseus": "aura-perseus-en", "Stella": "aura-stella-en",
#             "Jupiter": "aura-2-jupiter-en", "Thalia": "aura-2-thalia-en"
#         }

#         if voice_name not in available_voices:
#             logging.error(f"Invalid voice name: {voice_name}. Available voices are: {list(available_voices)}")
#             return

#         model = available_voices[voice_name]
#         sentences = re.split(r'(?<!\b\w\.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text.strip())

#         with ThreadPoolExecutor() as executor:
#             futures = [
#                 executor.submit(self._generate_audio_chunk, sentence.strip(), model, idx)
#                 for idx, sentence in enumerate(sentences)
#             ]

#             try:
#                 done, _ = wait(futures, timeout=max_wait)
#                 if not done:
#                     raise TimeoutError("TTS generation timed out.")

#                 audio_parts = {}
#                 for future in done:
#                     idx, data = future.result()
#                     audio_parts[idx] = data

#                 # Combine audio
#                 combined = BytesIO()
#                 for idx in sorted(audio_parts.keys()):
#                     combined.write(audio_parts[idx])

#                 os.makedirs(os.path.dirname(output_file), exist_ok=True)
#                 with open(output_file, 'wb') as f:
#                     f.write(combined.getvalue())

#                 logging.info(f"Final TTS audio saved to {output_file}")
#                 self.queue_audio(output_file)

#             except TimeoutError:
#                 logging.error("Speech generation timed out.")
#                 if fallback_language != "en":
#                     logging.info(f"Attempting fallback to {fallback_language} voice...")
#                     self.speak(text, voice_name="Athena", output_file=output_file, max_wait=max_wait, fallback_language="en")

#     def _audio_playback_handler(self):
#         from playsound import playsound
#         while True:
#             filename = self.audio_queue.get()
#             if filename is None:
#                 break
#             while not os.path.exists(filename):
#                 time.sleep(0.1)
#             try:
#                 playsound(filename)
#             except Exception as e:
#                 logging.error(f"Error playing {filename}: {e}")
#             finally:
#                 try:
#                     os.remove(filename)
#                 except Exception:
#                     pass
#                 self.audio_queue.task_done()

#     def queue_audio(self, filename):
#         self.audio_queue.put(filename)

#     def wait_for_playback_completion(self):
#         self.audio_queue.join()



# # Example usage
# if __name__ == "__main__":
#     speaker = SpeechSynthesizer()
#     speaker.speak('Boss! Should I send the message right now?')
#     speaker.wait_for_playback_completion()








































# import requests
# import base64
# import re
# import time
# import os
# import sys
# import threading
# import queue
# import tempfile
# from io import BytesIO
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from nltk.tokenize import sent_tokenize 

# # Add the path to include the custom module
# sys.path.insert(0, os.getcwd())
# from core.assets.interupt_playsound import play_audio

# # import nltk
# # nltk.download('punkt_tab')      # For intial download


# class SpeechSynthesizer:
#     def __init__(self):
#         self.audio_queue = queue.Queue()
#         self.available_voices = {
#             "Asteria": "aura-asteria-en", "Arcas": "aura-arcas-en", "Luna": "aura-luna-en",
#             "Zeus": "aura-zeus-en", "Orpheus": "aura-orpheus-en", "Angus": "aura-angus-en",
#             "Athena": "aura-athena-en", "Helios": "aura-helios-en", "Hera": "aura-hera-en",
#             "Orion": "aura-orion-en", "Perseus": "aura-perseus-en", "Stella": "aura-stella-en"
#         }
#         threading.Thread(target=self._audio_playback_handler, daemon=True).start()

#     def list_voices(self):
#         """Displays all available voice names."""
#         for name, model in self.available_voices.items():
#             print(f"{name}: {model}")

#     def _audio_playback_handler(self):
#         while True:
#             filename = self.audio_queue.get()
#             if filename is None:
#                 break
#             try:
#                 while not os.path.exists(filename):
#                     time.sleep(0.1)
#                 play_audio(filename)
#             except Exception as e:
#                 print(f"Playback error: {e}")
#             finally:
#                 try:
#                     os.remove(filename)
#                 except:
#                     pass
#                 self.audio_queue.task_done()

#     def speak(self, text, voice_name="Luna"):
#         if not text:
#             raise ValueError("Text cannot be empty.")

#         if voice_name not in self.available_voices:
#             raise ValueError(f"Invalid voice name. Choose from: {list(self.available_voices.keys())}")

#         url = "https://deepgram.com/api/ttsAudioGeneration"
#         headers = {
#             "accept": "*/*",
#             "content-type": "application/json"
#         }
#         model = self.available_voices[voice_name]
#         sentences = sent_tokenize(text)

#         def generate_chunk_audio(sentence, part_number):
#             for attempt in range(3):
#                 try:
#                     payload = {"text": sentence, "model": model}
#                     response = requests.post(url, headers=headers, json=payload, timeout=10)
#                     response.raise_for_status()
#                     audio_data = response.json().get("data")
#                     if audio_data:
#                         return part_number, base64.b64decode(audio_data)
#                     else:
#                         time.sleep(1)
#                 except requests.RequestException as e:
#                     print(f"Retrying part {part_number} (attempt {attempt+1}) due to: {e}")
#                     time.sleep(1)
#             raise Exception(f"Failed after 3 attempts: part {part_number}")

#         with ThreadPoolExecutor() as executor:
#             futures = {executor.submit(generate_chunk_audio, sentence, i): i for i, sentence in enumerate(sentences)}
#             audio_parts = {}
#             for future in as_completed(futures):
#                 part_number = futures[future]
#                 try:
#                     part_number, audio_data = future.result()
#                     audio_parts[part_number] = audio_data
#                 except Exception as e:
#                     print(f"Audio generation failed for part {part_number}: {e}")

#         if not audio_parts:
#             print("No audio generated.")
#             return

#         # Combine all audio chunks
#         final_audio = BytesIO()
#         for part in sorted(audio_parts):
#             final_audio.write(audio_parts[part])

#         with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
#             temp_audio.write(final_audio.getvalue())
#             temp_path = temp_audio.name

#         self.audio_queue.put(temp_path)

#     def wait_until_done(self):
#         self.audio_queue.join()


# if __name__ == "__main__":
#     tts = SpeechSynthesizer()

#     text = "Hello! I am Siri. How are you?"
#     tts.speak(text)

#     # Wait for playback to finish
#     tts.wait_until_done()


# import requests
# import base64
# import logging
# import re
# import threading
# import queue
# import time
# import os
# import hashlib
# from io import BytesIO
# from concurrent.futures import ThreadPoolExecutor, as_completed, wait, TimeoutError

# # Setup logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# class SpeechSynthesizer:
#     def __init__(self):
#         self.audio_queue = queue.Queue()
#         self.cache_dir = "core/assets/audio_cache"
#         os.makedirs(self.cache_dir, exist_ok=True)
#         threading.Thread(target=self._audio_playback_handler, daemon=True).start()

#     def _get_hash(self, text, voice_model):
#         return hashlib.md5(f"{voice_model}:{text}".encode()).hexdigest()

#     def _generate_audio_chunk(self, text, voice_model, chunk_id):
#         url = "https://deepgram.com/api/ttsAudioGeneration"
#         headers = {"accept": "*/*", "content-type": "application/json"}

#         text_hash = self._get_hash(text, voice_model)
#         cached_file = os.path.join(self.cache_dir, f"{text_hash}.mp3")

#         if os.path.exists(cached_file):
#             logging.info(f"Cache hit for chunk {chunk_id}")
#             with open(cached_file, 'rb') as f:
#                 return chunk_id, f.read()

#         while True:
#             try:
#                 payload = {"text": text, "model": voice_model}
#                 response = requests.post(url, headers=headers, json=payload, timeout=10)
#                 response.raise_for_status()
#                 audio_data = response.json().get("data")
#                 if audio_data:
#                     audio_bytes = base64.b64decode(audio_data)
#                     with open(cached_file, 'wb') as f:
#                         f.write(audio_bytes)
#                     return chunk_id, audio_bytes
#                 else:
#                     time.sleep(1)
#             except requests.RequestException as e:
#                 logging.warning(f"Retrying chunk {chunk_id}: {e}")
#                 time.sleep(1)

#     def speak(self, text, voice_name="Athena", output_file="core/assets/output_audio.mp3", max_wait=60):
#         available_voices = {
#             "Asteria": "aura-asteria-en", "Arcas": "aura-arcas-en", "Luna": "aura-luna-en",
#             "Zeus": "aura-zeus-en", "Orpheus": "aura-orpheus-en", "Angus": "aura-angus-en",
#             "Athena": "aura-athena-en", "Helios": "aura-helios-en", "Hera": "aura-hera-en",
#             "Orion": "aura-orion-en", "Perseus": "aura-perseus-en", "Stella": "aura-stella-en",
#             "Jupiter": "aura-2-jupiter-en", "Thalia": "aura-2-thalia-en"
#         }

#         if voice_name not in available_voices:
#             raise ValueError(f"Invalid voice name. Available voices: {list(available_voices)}")

#         model = available_voices[voice_name]
#         sentences = re.split(r'(?<!\b\w\.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text.strip())

#         with ThreadPoolExecutor() as executor:
#             futures = [
#                 executor.submit(self._generate_audio_chunk, sentence.strip(), model, idx)
#                 for idx, sentence in enumerate(sentences)
#             ]

#             try:
#                 done, _ = wait(futures, timeout=max_wait)
#                 if not done:
#                     raise TimeoutError("TTS generation timed out.")

#                 audio_parts = {}
#                 for future in done:
#                     idx, data = future.result()
#                     audio_parts[idx] = data

#                 # Combine audio
#                 combined = BytesIO()
#                 for idx in sorted(audio_parts.keys()):
#                     combined.write(audio_parts[idx])

#                 os.makedirs(os.path.dirname(output_file), exist_ok=True)
#                 with open(output_file, 'wb') as f:
#                     f.write(combined.getvalue())

#                 logging.info(f"Final TTS audio saved to {output_file}")
#                 self.queue_audio(output_file)

#             except TimeoutError:
#                 logging.error("Speech generation timed out.")

#     def _audio_playback_handler(self):
#         from playsound import playsound
#         while True:
#             filename = self.audio_queue.get()
#             if filename is None:
#                 break
#             while not os.path.exists(filename):
#                 time.sleep(0.1)
#             try:
#                 playsound(filename)
#             except Exception as e:
#                 logging.error(f"Error playing {filename}: {e}")
#             finally:
#                 try:
#                     os.remove(filename)
#                 except Exception:
#                     pass
#                 self.audio_queue.task_done()

#     def queue_audio(self, filename):
#         self.audio_queue.put(filename)

#     def wait_for_playback_completion(self):
#         self.audio_queue.join()

# # Example usage
# if __name__ == "__main__":
#     speaker = SpeechSynthesizer()
#     #speaker.speak("Good morning. It's 7 A.M. The weather in Malibu is 72 degrees with scattered clouds. The surf conditions are fair with waist to shoulder highlines, high tide will be at 10:52 a.m")
#     #speaker.speak(" For you sir, always.I'd like to open a new project file, index as: Mark II.Shall I store this on the Stark Industries' central database?I don't know who to trust right now. 'Til further notice, why don't we just keep everything on my private server.Working on a secret project, are we, sir? I don't want this winding up in the wrong hands. Maybe in mine, it could actually do some good.")
#    # speaker.speak('good morning boss. Should I open the file sir?')
#     speaker.speak('amma on the call, should i pick the call sir?')
#     speaker.wait_for_playback_completion()
