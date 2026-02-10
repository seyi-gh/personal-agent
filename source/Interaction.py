import json
import requests
from config import config
from source.Colors import Colors


api_key = config['api_key']['deepseek']


def _ignore_chunk(chunk: str):
  return
def _simple_chunk_flush(chunk: str):
  print(chunk, flush=True, end='')


class RoleLabels:
  assistant = 'assistant'
  user = 'user'
  system = 'system'


class Addon:
  def __init__(self, key_name: str, ret_callable: callable):
    self.key_name = key_name
    self.ret_callable = ret_callable

  def _export(self) -> str:
    return f'<Add-On "{self.key_name}": {self.ret_callable()}>'


class GroupAddons:
  def __init__(self, group: list[Addon]):
    self.group = group

  def export(self) -> str:
    ret_str = '< Starting packages of addons data >\n'
    for i in self.group:
      ret_str += i._export() + '\n'
    ret_str += '< Ending packages of addons data >\n'
    return ret_str


class ChatMessage:
  def __init__(self, role: RoleLabels, content: str, meta: dict={}, addons: GroupAddons=None):
    self.role = role
    self.content = content
    self.meta = meta
    self.addons = addons
    self.gap_info = '\n\n'

  def export(self, apply_addons: bool=True) -> dict:
    if apply_addons and self.addons != None:
      self.content = self.__apply_addons()
    return { 'role': self.role, 'content': self.content }

  def raw_json(self):
    exported = self.export()
    exported['meta'] = self.meta
    return exported

  def __apply_addons(self):
    temp_addons = self.addons.export()
    return temp_addons + self.gap_info + self.content


class ChatHistoria:
  def __init__(self, messages: list[ChatMessage]=[]):
    self.messages = messages

  def append(self, message: ChatMessage):
    self.messages.append(message)

  def for_request(self):
    ret_messages = []
    for i in self.messages:
      ret_messages.append(i.export())
    return ret_messages

  def raw(self):
    return self.messages

  def readable(self):
    exported = []
    for i in self.messages:
      exported.append(f'{i.role}: {i.content}')
    return exported


class Interaction:
  def __init__(self, system_content: str=''):
    self.system_message = ChatMessage(RoleLabels.system, system_content)
    self.chat_messages = ChatHistoria([ self.system_message ])
    self.lamda_chunk = None

  def create_response(self, message: str, addons: GroupAddons=None):
    self.chat_messages.append(ChatMessage(RoleLabels.user, message, addons=addons))
    response_message = self.read_stream_request(
      self.create_request(self.chat_messages.for_request()),
      _simple_chunk_flush
    )
    self.chat_messages.append(response_message)
    return response_message

  def read_stream_request(self,
    stream_response: requests.Response,
    lambda_chunk: callable=_ignore_chunk
  ):
    if lambda_chunk != None and lambda_chunk == _ignore_chunk:
      lambda_chunk = self.lamda_chunk
    response_line = ''
    completed_data = None
    for stream_line in stream_response.iter_lines():
      if not stream_line:
        pass
      try:
        data: str = stream_line.decode('utf-8').strip()
        if not data or not data.startswith('data: ') or data.find('[DONE]') != -1:
          continue
        data = json.loads(data.replace('data: ', ''))
        content: str = data['choices'][0]['delta']['content']
        if data['choices'][0]['finish_reason'] != None:
          completed_data: dict = data
        lambda_chunk(content)
        response_line += content
      except Exception as e:
        Colors.format(f'Error generated reading stream request: \n{e}', Colors.error, True)
        return None
    return ChatMessage(RoleLabels.assistant, response_line, completed_data)

  def create_request(self, chat_messages: list):
    response = requests.post(
    'https://api.deepseek.com/chat/completions',
      headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
      },
      json = {
        'model': 'deepseek-chat',
        'messages': chat_messages,
        'stream': True
      }, stream = True )
    return response
  
  #TODO This function is useless (for now)
  def create_instant_response(self):
    actual_messages = [ self.create_item(self.system, self.system_content) ]
    stream_response = self.post_deepseek(actual_messages)
    if stream_response == False: return False
    assistant_item = self.process_stream(stream_response)
    return assistant_item