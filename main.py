from config import config
from datetime import datetime
from source.util import json_load, open_read
from source.Interaction import Interaction, Addon, GroupAddons

personality_content = open_read('./identity/personality.txt')
thinker_content = open_read('./identity/thinker.txt')

addons = GroupAddons([
  Addon('Datetime now', datetime.now)
])

def main():
  cli_interaction = Interaction(personality_content)

  while True:
    user = input('User: ')

    if user == 'exit': break

    print('CLI: ', end='')
    response = cli_interaction.create_response(user, addons=addons)
    #! Chunk response lambda

    print(f'\n<Chat lenght {len(cli_interaction.chat_messages.raw())}>\n')

if '__main__' == __name__:
  main()