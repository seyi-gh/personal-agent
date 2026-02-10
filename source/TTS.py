import time
import json
import base64
import requests
import threading
import subprocess
from config import config

openai_key = config['api_key']['openai']

class TTS:
  def __init__(self):
    self.main_breaker = False
    self.main_thread = None
    self.time_gap = 0.25
    self.triggered = False
    self.ffplay_proc = None
    # self.queue = []
    self.message = ''

  def request_audio_stream(self, message: str):
    response = requests.post(
      'https://api.openai.com/v1/audio/speech',
      headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_key}'
      },
      json={
        'model': 'gpt-4o-mini-tts',
        'input': message,
        'voice': 'marin',
        'stream_format': 'sse'
      }
    )
    return response

  def play_audio_stream(self, response: requests.Response):
    self.ffplay_proc = subprocess.Popen(
      ['ffplay', '-nodisp', '-autoexit', '-i', 'pipe:0'],
      stdin=subprocess.PIPE,
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL
    )

    try:
      for line in response.iter_lines():
        if line and line.startswith(b'data: '):
          json_str = line[len(b'data: '):].decode('utf-8').strip()
          if not json_str or not (json_str.startswith('{')) and json_str.endswith('}'):
            continue
          try:
            audio = json.loads(json_str)
          except json.JSONDecodeError as e:
            #! print('Error jsondecode', e)
            continue
        
          audio_data = audio.get('audio', None)
          if audio_data is None: continue

          audio_bytes = base64.b64decode(audio_data)
          self.ffplay_proc.stdin.write(audio_bytes)
      self.ffplay_proc.stdin.close()
      self.ffplay_proc.wait()
    except Exception as e:
      print('Error playing the audio: ', e)
      self.ffplay_proc.terminate()

  def trigger(self):
    self.triggered = True
    if self.ffplay_proc != None:
      self.ffplay_proc.terminate()
      self.ffplay_proc = None
      self.triggered = False

  def runner(self):
    temp_message = open('temp.txt', 'r').read()
    while True:
      if self.main_breaker: break
      time.sleep(self.time_gap)

      self.message = open('temp.txt', 'r').read()
      print('Readed messaged:', temp_message)

      if temp_message == self.message: continue
      
      print(f'Entering creating response <{self.message}>')


      response = self.request_audio_stream(self.message)
      self.play_audio_stream(response)

      temp_message = self.message

  def start(self):
    if self.main_thread != None: return
    try:
      self.main_thread = threading.Thread(target=self.runner)
      self.main_thread.start()
    except Exception as e:
      print(e)
      if not self.main_thread.is_alive():
        self.main_thread.join()