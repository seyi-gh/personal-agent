import os
from dotenv import load_dotenv
load_dotenv()

api_keys = {
  'openai': os.getenv('OPENAI_APIKEY'),
  'deepseek': os.getenv('DEEPSEEK_APIKEY')
}